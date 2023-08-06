# coding=utf-8
#	Copyright (c) Alexander Sedov 2008

#	This file is part of Nodes.
#
#	Nodes is free software: you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation, either version 3 of the License, or
#	(at your option) any later version.
#
#	Nodes is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#
#	You should have received a copy of the GNU General Public License
#	along with Nodes.  If not, see <http://www.gnu.org/licenses/>.
"""
Ядро Nodes.
Реализует:
    * базовый класс Нода -- Node,
    * Синапса (соединительной дуги) -- Synaps,
    * базовое взаимодействие со Стекером (stacker),
      как-то: проверка корректности связи, etc.
"""
import sigmoids #here
from numpy import array, zeros, ones, float32, isfinite, empty, nan
import numpy.random
import twist
import warnings
flotype=float32 #type of NumPy arrays
class Stop(Exception):
    """Останов. Вызывается из метода :meth:`Node.calculate`
    для останова вычисления."""
    pass

class Node(object):
    """Базовый класс Нода."""

    __itemtype__=flotype
    """Тип данных по умолчанию"""

    __shape__=[None], [None]
    """Топология Нода (два списка значений).
    ``[None]`` в качестве одного из списков означает
    "сколько угодно чего угодно";
    ``""`` в качестве элемента  -- "что угодно";
    "a b c" или ('a', 'b', 'c') -- "a, b или c";
    "a" -- само себя;
    None (использоваться не должно) -- несоответствие ничему.
    Первый из списков определяет топологию входов, второй -- выходов.
    Соединяться могут только соответствующие вход/выход
    (имеющие общий элемент).
    """

    def __init__(self, inputs, outputs, iweights=None, oweights=None,
            sysname=''):
        """Инициализация.
        :param inputs, outputs:     списки Синапсов
        :param iweights, oweights:  списки/массивы весов (по умолчанию единицы)
        :param sysname:			    условное имя. Используется для отладки"""
        self.input_weights=iweights
        self.output_weights=oweights
        self.inputs=inputs
        self.outputs=outputs
        self.sysname=sysname
        self.init_prepare()
        self.check_valid()
        self.pending=False
        self.calculated=False
        self.deferred=twist.deferred.Deferred()

    def calc(self):
        """Внутренний метод, используемый :meth:`compute` и :meth:`touch`.
        Производит собственно вычисления.
        """
        if self.pending:
            return False
        self.pending=True
        try:
            self.prepare_calc()
            self._check_values()
            self._mul_iweights()
            self.preprocess()
            self.calculate()
            self.postprocess()
            self._mul_oweights()
            self._put_values()
            self.fix_calc() #XXX Логичнее в finally
            self.teach()
        except Stop:
            pass
        else:
            if not self.calculated:
                self.calculated=True
                self.deferred.callback(self)
        self.pending=False
        return True

    def prepare_calc(self):
        """Подготовка. Выполняется перед какими-либо действиями."""
        pass

    def fix_calc(self):
        """Фиксация. Выполняется после вычислений."""
        pass

    def init_prepare(self):
        """Окончательная инициализация."""
        self.iN=len(self.inputs)
        self.oN=len(self.outputs)
        #Создание массивов значений и, если нужно, весов
        self.ivalues=empty(self.iN, self.__itemtype__)+nan
        self.ovalues=empty(self.oN, self.__itemtype__)+nan
        if self.input_weights is None:
            self.input_weights=ones(self.iN, self.__itemtype__)
        else:
            self.input_weights=array(self.input_weights, self.__itemtype__)
        if self.output_weights is None:
            self.output_weights=ones(self.oN, self.__itemtype__)
        else:
            self.output_weights=array(self.output_weights, self.__itemtype__)
        self.input=array(self.ivalues)
        self.output=array(self.ovalues) #С этими массивами оперирует
                                        # :meth:`calculate`
        #Создание массивов истории
        self.ilog=array(self.ivalues)
        self.olog=array(self.ovalues)
        self.iwlast=array(self.input_weights)
        self.owlast=array(self.output_weights)
        self.N=0	#Количество проделанных обучений
        self.T=numpy.sqrt(
                self.__itemtype__(self.iN+self.oN)
                )#начальная температура отжига
        self.result=0
        self.lastres=0	#Оценка последнего вычисления
        self.justfeed=False
        self.velocity=1/8. #Множитель скорости обучения

    def check_valid(self):
        """Проверка корректности соединений.

        :raise:     :exc:`TypeError`/:exc:`AssertionError` при неудачном завершении."""
        assert len(self.input_weights)==self.iN
        assert len(self.output_weights)==self.oN
        inputs, outputs=self.__shape__
        for (arr, nam, N) in ((inputs, 'inputs', self.iN),
                                (outputs, 'outputs', self.oN)):
            if arr:
                if arr[-1] is None:
                    assert N>=len(arr)-1, 'Too less %s: %d of %d or more'%\
                            (nam, N, len(arr)-1)
                else:
                    assert N==len(arr), 'Wrong number of %s: %d (%d)'%\
                            (nam, N, len(arr))

    def check_sufficient(self, getted, values):
        return getted.all()

    def _check_values(self):
        """Внутренний метод для получения значений от других Нодов.
        """
        getted=isfinite(self.ivalues)
        if not self.check_sufficient(getted, self.ivalues):
            raise Stop

    def _mul_iweights(self):
        """Внутренний метод, умножающий полученные значения на входные веса."""
        self.input=self.ivalues*self.input_weights
        #:class:`NumPy.ndarray` - хорошая вещь!

    def _mul_oweights(self):
        """Внутренний метод, умножающий вычисленные значения
        на выходные веса."""
        self.ovalues=self.output*self.output_weights

    def _put_values(self):
        """Внутренний метод для передачи значений другим Нодам.
        """
        for j in range(self.oN):
            self.outputs[j].go()

    def preprocess(self):
        """Непосредственная подготовка к вычислению."""
        self.output[:]=0.

    def postprocess(self):
        """Обработка результатов вычислений."""
        self.input[:]=0.

    def calculate(self):
        """Собственно вычисление. Метод должен быть переопределён
        в подклассах."""
        raise NotImplementedError, "вычисления должны быть реализованы"\
                " в подклассах."

    def teach(self):
        """Обучение. По умолчанию вызывает метод прогрессивного обучения
        и берёт на себя работу по моделированию отжига.
        Энергией в моделировании считается качественная оценка
        последнего результата. Каждые новые вычисленные точки
        временно принимаются, чтобы дать возможность оценить новый результат
        извне."""
        prob=sigmoids.sigmoid((self.result-self.lastres)*self.N/self.T)
        if numpy.random.random()>prob:
            self.input_weights[:]=self.iwlast
            self.output_weights[:]=self.owlast
        else:
            self.iwlast[:]=self.input_weights
            self.owlast[:]=self.output_weights
        self.forth_propagation()
        #self.back_propagation() # нужны :var:`targets`

    def forth_propagation(self):
        """Прогрессивное, или прямое, обучение.
        Моделирует такие вещи, как *доверие* (1й этап), *внимание* (2й этап),
        *привыкание* (3й этап).
        Также используется быстрое (по Коши) одномерное моделирование отжига
        с понижением температуры как в скалярном случае, что не даёт
        математической гарантии на оптимум, но определённо даёт надежду :).

        При моделировании используются следующие подобранные опытным путём
        математические функции:
            * :func:`believing` от разности нового и старого значений. Чем
              меньше по модулю разность, тем больше значение функции.
              :math:`E=(0; 1]`. Используется для вычисления "новых старых"
              значений и как множитель случайной величины, используемой в
              отжиге.
            * :func:`keyness` от значения - насколько оно, вероятнее всего,
              важно. Функция имеет колоколообразный вид с максимумом.
              приблизительно в точке :math:`(0, 30)`.
              :math:`E\\approxeq(0; 0.3]`
            * :func:`mutability` от веса - насколько вес неустойчив.  Наиболее
              неустойчивы веса :math:`\\pm\\frac12`, наиболее устойчив ``0``.
        """
        #Моделирование отжига

        T=self.T/(self.N+1)#температура
        def rfactor(size):
            arr=empty(size)
            for i in range(size):
                rnum=-100
                while not -10<rnum<10:
                    rnum=numpy.random.standard_cauchy()
                arr[i]=rnum
            return arr/10*T
        iweights=array(self.input_weights)
        oweights=array(self.output_weights)

        #Первый этап. Отжиг с учётом факторов.

        #Степень доверия новому значению.
        if isfinite(self.ilog).all():
            pows=sigmoids.believing(self.ivalues-self.ilog)
            k=pows*self.velocity
            news=(self.N*self.ilog+k*self.ivalues)/(self.N+k)
            iweights+=k*rfactor(self.iN)
            self.ilog=news
        else:
            self.ilog[:]=self.ivalues

        if isfinite(self.olog).all():
            pows=sigmoids.believing(self.ovalues-self.olog)
            k=pows*self.velocity
            news=(self.N*self.olog+k*self.ovalues)/(self.N+k)
            oweights+=k*rfactor(self.oN)
            self.olog=news
        else:
            self.olog[:]=self.ovalues

        #Второй этап. Поиск ключевых факторов.
        keynesses=sigmoids.keyness(self.ivalues)
        iweights+=iweights*keynesses*self.velocity*rfactor(self.iN)

        keynesses=sigmoids.keyness(self.ovalues)
        oweights+=oweights*keynesses*self.velocity*rfactor(self.oN)

        #Третий этап. Объединение.

        #Изменчивость весов.
        mut=sigmoids.mutability(self.input_weights)
        force=sigmoids.dsigmoid(iweights)
        k=mut+force
        self.input_weights=(self.N*self.input_weights+k*iweights)/(self.N+k)

        mut=sigmoids.mutability(self.output_weights)
        force=sigmoids.dsigmoid(oweights)
        k=mut+force
        self.output_weights=(self.N*self.output_weights+k*oweights)/(self.N+k)

        #Wow! We were teached one time more!
        self.N+=1

    def hertz(self, index):
        self.input_weights[index]*=(1+1./self.N)

    def back_propagation(self, targets):
        """Обратное распространение. описано в литературе по нейросетям."""
        if self.pending:
            return
        self.pending=True
        assert len(targets)==self.oN
        targets=array(targets)
        delta=(targets-self.ovalues)/self.output_weights*\
                array([self.calc_drv(x) for x in self.ovalues])
        d=sum(delta)
        self.input_weights+=(d*self.ivalues)*self.velocity
        map(lambda x, y: x.back_propagate(d*y),self.inputs, self.input_weights)
        self.pending=False

    def calc_drv(self, val):
        """Вычисление производной. В случае Нода
        математического смысла не имеет."""
        raise NotImplementedError, "derivative calculation"\
                " depends on calculations."

    def teach_feed(self, result):
        """Обучение с аргументом. Если аргумент - массив, происходит обратное
        распространение, а аргумент расценивается как целевые значения;
        в противном случае аргумент расценивается как качественная оценка
        последнего результата.

        :param result: аргумент"""
        if hasattr(result, '__iter__'):
            self.back_propagation(result)
        else:
            self.feed_success(result)

    def feed_success(self, success):
        """Распространение информации о последнем результате по сети.

        :param success: информация об успехе (по шкале :math:`\\pm`)"""
        #feeding success
        self.lastres=self.result
        self.result=success

    def add_input(self, synaps):
        """Добавление одного входа."""
        self.inputs.append(synaps)
        self.input_weights=list(self.input_weights)+[1.]
        self.init_prepare()
        self.check_valid()

    def add_output(self, synaps):
        """Добавление одного выхода."""
        self.outputs.append(synaps)
        self.output_weights=list(self.output_weights)+[1.]
        self.init_prepare()
        self.check_valid()

    #Pickling :-)
    def __getstate__(self):
        return self.inputs, self.outputs, self.input_weights, \
                self.output_weights, self.ilog, self.olog, \
                self.__getstate_extra__()

    def __setstate__(self, state):
        self.inputs, self.outputs, self.input_weights,\
                self.output_weights, self.ilog, self.olog,\
                extra_state=state
        self.iN=len(self.inputs)
        self.oN=len(self.outputs)
        self.ivalues=zeros(self.iN)
        self.ovalues=zeros(self.oN)
        self.__setstate_extra__(extra_state)

    def __getstate_extra__(self):
        return None

    def __setstate_extra__(self, state):
        pass

    def __repr__(self):
        if self.sysname:
            return self.sysname
        return self.__class__.__name__+':'+repr(id(self))

    def reset(self):
        """Сброс всех флагов (к примеру, после аварийного завершения)."""
        self.pending=False
        self.deferred=twist.deferred.Deferred()
        self.justfeed=False
        self.calculated=False

from stacker.connect import check as checksynaps
#Синапсы (связи)
class Synaps(object):
    """Синапс, или связь, дуга графа... Служит для связи Нодов."""
    def __init__(self):
        self.bound=False
        self._call=True

    def bind(self, node1, index1, node2, index2):
        """Связывание Синапса с Нодами. Помещает Синапс в списки
        :attr:`Node.input`/:attr:`Node.output` и проверяет связь
        на корректность (см. :mod:`stacker`)."""
        if index1==-1:
            index1=len(node1.outputs)
            node1.add_output(self)
        else:
            node1.outputs[index1]=self
        if index2==-1:
            index2=len(node2.inputs)
            node2.add_input(self)
        else:
            node2.inputs[index2]=self
        self.innode, self.inindex=node1, index1
        self.outnode, self.outindex=node2, index2
        self.bound=True
        self.check_valid()

    def check_valid(self):
        """Проверка корректности Синапса. Спецификация интерфейса совпадает
        с :meth:`Node.check_valid`."""
        self._check_bound()
        assert checksynaps(self)
        return True

    def _check_bound(self):
        """Проверка, связан ли Синапс с Нодами."""
        if not self.bound:
            raise ValueError, 'synaps is unbound'

    def _setupval(self):
        """Простое копирование значения из входного Нода в выходной."""
        self.outnode.ivalues[self.outindex]=self.innode.ovalues[self.inindex]

    def go(self):
        """Запрос на пропуск значения через Синапс."""
        self._check_bound()
        x=self.innode.ovalues[self.inindex]
        y=self.outnode.ivalues[self.outindex]
        if x!=y or not self.outnode.calculated:
            self._setupval()
            if self.outnode.pending:
                self.innode.hertz(self.inindex)
            else:
                twist.asyncall(self.outnode.calc)

    @property
    def iweight(self):
        """Входной вес Синапса."""
        return self.innode.oweights[self.inindex]

    @property
    def oweight(self):
        """Выходной вес Синапса."""
        return self.outnode.oweights[self.outindex]
