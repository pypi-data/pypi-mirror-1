class GNotaException(Exception):
    pass

class NoSuchGradeException(GNotaException):
    pass

class NoSuchClassException(GNotaException):
    pass

class NoSuchScoreSystemException(GNotaException):
    pass

class ScoresystemException(GNotaException):
    pass

class GNotaDatabaseInconsistencyException(GNotaException):
    pass

class GNotaTypeException(GNotaException):
    pass

class NoSelectedClassException(GNotaException):
    pass

class GNotaConversionException(GNotaException):
    pass

class CategoryWithNoWeightException(GNotaException):
    pass
