
class IOWarning(RuntimeWarning):
    pass

class InvalidFormatWarning(IOWarning):
    pass

class InvalidFormatError(IOError):
    pass

class CorruptedWarning(IOWarning):
    pass

class CorruptedError(IOError):
    pass

class MismatchError(TypeError):
    pass

