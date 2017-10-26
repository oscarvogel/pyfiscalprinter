# -*- coding: iso-8859-1 -*-

class PrinterException(Exception):
    pass

class ComunicationError(PrinterException):
    errorNumber = 2
