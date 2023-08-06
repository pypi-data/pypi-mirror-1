#!/usr/bin/python
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

import wx
import BPGR
import sys, os
from pkg_resources import resource_filename
picdir=resource_filename(__name__, 'guipics')
import locale
try:
    locale.resetlocale()
except:
    pass
import string
import gettext
#MARKING
_=lambda x:None
_('wings')
_('tail')
_('feathers')
_('beak')
_('engine')
_('chassis')
_('bird')
_('plane')
_('glider')
_('rocket')
_('ufo')
del _
if sys.platform[:3]=='win':
        x=gettext.translation('BPGR', resource_filename(__name__, 'locale'),
                languages=['ru', 'en'])
else:
        x=gettext.translation('BPGR', resource_filename(__name__, 'locale'))
x.install(True)
UNKNOWN='ufo'
#UNKNOWN='unknown'
class ApplicationFrame(wx.Frame):
    def __init__(self, parent, id):
        wx.Frame.__init__(self, parent, id,
                title=_('Bird-Plane-Glider-Rocket'),
                style=wx.MINIMIZE_BOX|wx.CLOSE_BOX|wx.CAPTION|wx.SYSTEM_MENU)
        sizer=wx.GridBagSizer(4, 3)
        self.bitmap=wx.StaticBitmap(self)
        self.bitmap.SetBitmap(wx.Bitmap(os.path.join(picdir, 'unknown.png')))
        sizer.Add(self.bitmap, (0, 0), (1, 4),
                flag=wx.ALIGN_CENTER|wx.TOP|wx.BOTTOM, border=5)
        labels=map(_, BPGR.evidences)
        self.checkbox_list=[CheckboxWithSlider(self, -1, label.capitalize())
                for label in labels]
        for i, chk in enumerate(self.checkbox_list):
            sizer.Add(chk, (i//3+1, i%3), (1, 1), wx.LEFT|wx.EXPAND)
        okbutton=wx.BitmapButton(self, -1,
                wx.Bitmap(os.path.join(picdir, 'okbutton.png')))
        sizer.Add(okbutton, (3, 1), flag=wx.TOP|wx.BOTTOM|wx.ALIGN_CENTER)
        cancelbutton=wx.BitmapButton(self, -1,
                wx.Bitmap(os.path.join(picdir, 'cancelbutton.png')))
        sizer.Add(cancelbutton, (3, 2), flag=wx.TOP|wx.BOTTOM|wx.ALIGN_CENTER)
        sizer.AddGrowableRow(0)
        sizer.AddGrowableCol(0)
        sizer.AddGrowableCol(1)
        sizer.AddGrowableCol(2)
        self.SetSizerAndFit(sizer)
        self.waitcursor=wx.StockCursor(wx.CURSOR_WAIT)
        self.Bind(wx.EVT_BUTTON, self.Calculate, okbutton)
        self.Bind(wx.EVT_BUTTON, self.OnClose, cancelbutton)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Bind(wx.EVT_SIZE, self.ReLayout)
        self.Centre()
        self.Layout()
        self.decider=BPGR.create_glob()
        self.count=0

    def OnClose(self, event):
        di=wx.MessageDialog(self, _('Do you really want to kill such useful,'
        ' beautiful and smart application?'), _('Do you want?'),
        wx.YES_NO|wx.YES_DEFAULT|wx.CENTRE|wx.ICON_EXCLAMATION)
        res=di.ShowModal()
        if res==wx.ID_YES:
            self.Destroy()
        else:
            event.StopPropagation()

    def Calculate(self, event):
        values=[chk.GetValue() for chk in self.checkbox_list]
        values=[(x-50)/50 for x in values]
        for k, v in zip(BPGR.evidences, values):
            self.decider.nodes[k].set(v)
        self.Update()
        self.decider.calculate(doubly=False)
        self.Update()
        res=self.decider.get_result()
        if res>=0:
            obj=BPGR.objects.keys()[res]
        else:
            obj=UNKNOWN
        path=os.path.join(picdir, obj+'.png')
        self.bitmap.SetBitmap(wx.Bitmap(path))
        self.Update()
        dial=wx.MessageDialog(self, _('Is it %s?')%_(obj), _('Question'),
                wx.YES_NO|wx.CENTRE|wx.ICON_QUESTION)
        code=dial.ShowModal() if obj!=UNKNOWN else wx.ID_NO
        if code==wx.ID_YES:
            self.decider.teach(+1)
        elif code==wx.ID_NO:
            self.decider.teach(-1)
            secondial=wx.SingleChoiceDialog(self, _('Ok, how do you think, what is it?'),
                 _('What is it?'), map(_, BPGR.objects.keys()))
            if secondial.ShowModal()==wx.ID_OK:
                obj2=BPGR.objects.keys()[secondial.GetSelection()]
                if obj2!=obj:
                    path=os.path.join(picdir, obj2+'.png')
                    self.bitmap.SetBitmap(wx.Bitmap(path))
                    self.Update()
                    for x in BPGR.objects.keys():
                        if x==obj2:
                            self.decider.nodes[x].teach_feed(+.5)
                        elif x==obj:
                            self.decider.nodes[x].teach_feed(-.5)
                        else:
                            self.decider.nodes[x].teach_feed(0)


    def ReLayout(self, event):
        if self.GetAutoLayout():
            self.Layout()

class CheckboxWithSlider(wx.Panel):
    def __init__(self, parent, id, label):
        wx.Panel.__init__(self, parent, id)
        self.checkbox=wx.CheckBox(self, -1, label)
        self.checkbox.SetValue(True)
        self.slider=wx.Slider(self, -1, 100, 0, 100, (-1, -1), (100, -1), wx.SL_HORIZONTAL|wx.SL_LABELS)
        sizer=wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.checkbox, 0, wx.LEFT|wx.TOP)
        sizer.Add(self.slider, 1, wx.LEFT, 3)
        self.SetSizer(sizer)
        self.Bind(wx.EVT_CHECKBOX, self.CheckNSet, id=self.checkbox.GetId())
        self.Bind(wx.EVT_SLIDER, self.AjustNSet, id=self.slider.GetId())

    def GetValue(self):
        return self.slider.GetValue()

    def SetValue(self, val):
        if isinstance(val, bool):
            self.checkbox.SetValue(val)
            self.slider.SetValue(int(val)*100)
        else:
            self.checkbox.SetValue(val==100)
            self.slider.SetValue(val)

    def CheckNSet(self, event):
        if self.checkbox.GetValue():
            self.slider.SetValue(100)
        else:
            self.slider.SetValue(0)

    def AjustNSet(self, event):
        if self.slider.GetValue()==100:
            self.checkbox.SetValue(True)
        else:
            self.checkbox.SetValue(False)


def main():
    app=wx.App()
    ApplicationFrame(None, -1).Show(True)
    app.MainLoop()

if __name__=='__main__':
    main()
