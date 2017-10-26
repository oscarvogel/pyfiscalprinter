# -*- coding: iso-8859-1 -*-
from Fiscal.Generico import PrinterInterface


class PrinterException(Exception):
    pass

class ComunicationError(PrinterException):
    errorNumber = 2

class EpsonPrinter(PrinterInterface):
    pass