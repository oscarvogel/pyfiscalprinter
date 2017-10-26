# -*- coding: iso-8859-1 -*-
import unicodedata
import platform
import time

from os.path import isfile

import shutil

from pathlib import Path

import os

from Fiscal import EpsonFiscalDriver
from Fiscal.EpsonFiscalDriver import ComunicationError
from Fiscal.Generico import PrinterInterface
import tempfile
import logging


def formatText(text):
    asciiText = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore')
    asciiText = asciiText.decode()
    asciiText = asciiText.replace("\t", " ").replace("\n", " ").replace("\r", " ")
    return asciiText

class ValidationError(Exception):
    pass

class FiscalPrinterError(Exception):
    pass

class PrinterException(Exception):
    pass

class HasarPrinter(PrinterInterface):

    filename = None

    model = None

    fileSocket = None

    lastCommand = None

    commands = []

    lastNumber = ''

    pathFileCommand = ''

    pathFileAnswer = ''

    outputFileName = ''

    CMD_OPEN_FISCAL_RECEIPT = 0x40

    CMD_OPEN_CREDIT_NOTE = 0x80

    CMD_PRINT_TEXT_IN_FISCAL = 0x41
    CMD_PRINT_LINE_ITEM = 0x42
    CMD_PRINT_SUBTOTAL = 0x43
    CMD_ADD_PAYMENT = 0x44
    CMD_CLOSE_FISCAL_RECEIPT = 0x45
    CMD_DAILY_CLOSE = 0x39
    CMD_STATUS_REQUEST = 0x2a

    CMD_CLOSE_CREDIT_NOTE = 0x81

    CMD_CREDIT_NOTE_REFERENCE = 0x93

    CMD_SET_CUSTOMER_DATA = 0x62
    CMD_LAST_ITEM_DISCOUNT = 0x55
    CMD_GENERAL_DISCOUNT = 0x54


    CMD_OPEN_NON_FISCAL_RECEIPT = 0x48
    CMD_PRINT_NON_FISCAL_TEXT = 0x49
    CMD_CLOSE_NON_FISCAL_RECEIPT = 0x4a

    CMD_CANCEL_ANY_DOCUMENT = 0x98

    CMD_OPEN_DRAWER = 0x7b

    CMD_SET_HEADER_TRAILER = 0x5d

    # Documentos no fiscales homologados (remitos, recibos, etc.)
    CMD_OPEN_DNFH = 0x80
    CMD_PRINT_EMBARK_ITEM = 0x82
    CMD_PRINT_ACCOUNT_ITEM = 0x83
    CMD_PRINT_QUOTATION_ITEM = 0x84
    CMD_PRINT_DNFH_INFO = 0x85
    CMD_PRINT_RECEIPT_TEXT = 0x97
    CMD_CLOSE_DNFH = 0x81

    CMD_REPRINT = 0x99

    CURRENT_DOC_TICKET = 1
    CURRENT_DOC_BILL_TICKET = 2
    CURRENT_DOC_NON_FISCAL = 3
    CURRENT_DOC_CREDIT_BILL_TICKET = 4
    CURRENT_DOC_CREDIT_TICKET = 5
    CURRENT_DOC_DNFH = 6

    AVAILABLE_MODELS = ["615", "715v1", "715v2", "320", "PL23", "441"]

    textSizeDict = {
        "615": {'nonFiscalText': 40,
                'customerName': 30,
                'custAddressSize': 40,
                'paymentDescription': 30,
                'fiscalText': 20,
                'lineItem': 20,
                'lastItemDiscount': 20,
                'generalDiscount': 20,
                'embarkItem': 108,
                'receiptText': 106,
                },
        "320": {'nonFiscalText': 120,
                'customerName': 50,
                'custAddressSize': 50,
                'paymentDescription': 50,
                'fiscalText': 50,
                'lineItem': 50,
                'lastItemDiscount': 50,
                'generalDiscount': 50,
                'embarkItem': 108,
                'receiptText': 106,
                }
    }

    ivaTypeMap = {
        PrinterInterface.IVA_TYPE_RESPONSABLE_INSCRIPTO: 'I',
        PrinterInterface.IVA_TYPE_RESPONSABLE_NO_INSCRIPTO: 'N',
        PrinterInterface.IVA_TYPE_EXENTO: 'E',
        PrinterInterface.IVA_TYPE_NO_RESPONSABLE: 'A',
        PrinterInterface.IVA_TYPE_CONSUMIDOR_FINAL: 'C',
        PrinterInterface.IVA_TYPE_RESPONSABLE_NO_INSCRIPTO_BIENES_DE_USO: 'B',
        PrinterInterface.IVA_TYPE_RESPONSABLE_MONOTRIBUTO: 'M',
        PrinterInterface.IVA_TYPE_MONOTRIBUTISTA_SOCIAL: 'S',
        PrinterInterface.IVA_TYPE_PEQUENIO_CONTRIBUYENTE_EVENTUAL: 'V',
        PrinterInterface.IVA_TYPE_PEQUENIO_CONTRIBUYENTE_EVENTUAL_SOCIAL: 'W',
        PrinterInterface.IVA_TYPE_NO_CATEGORIZADO: 'T',
    }

    ADDRESS_SIZE = 40

    def __init__(self, filename=None, model="615"):

        if not filename:
            self.filename = self.getFileName()
        else:
            self.filename = filename

        self.fileSocket = open(self.filename, "w", encoding='latin')
        self.model = model
        self.outputFileName = platform.node()

    def getFileName(self, filename='hasar'):
        tf = tempfile.NamedTemporaryFile(prefix=filename, mode='w+b')

        return tf.name

    def close(self):
        self.fileSocket.close()
        if not self.pathFileCommand.endswith("\\"):
            self.pathFileCommand += "\\"
        shutil.copyfile(self.filename, self.pathFileCommand + self.outputFileName + ".fis")

    def _setHeaderTrailer(self, line, text):
        self._sendCommand(self.CMD_SET_HEADER_TRAILER, (str(line), text))

    def setHeader(self, header=None):
        "Establecer encabezados"
        if not header:
            header = []
        line = 3
        for text in (header + [chr(0x7f)]*3)[:3]: # Agrego chr(0x7f) (DEL) al final para limpiar las
                                                  # líneas no utilizadas
            self._setHeaderTrailer(line, text)
            line += 1

    def setTrailer(self, trailer=None):
        "Establecer pie"
        if not trailer:
            trailer = []
        line = 11
        for text in (trailer + [chr(0x7f)] * 9)[:9]:
            self._setHeaderTrailer(line, text)
            line += 1

    def _sendCommand(self, commandNumber, parameters=(), skipStatusErrors=False):
        try:
            commandString = "SEND|0x{}|{}|{}".format(commandNumber, skipStatusErrors and "T" or "F",parameters)
            logging.getLogger().info("sendCommand: %s" % commandString)
            ret = self.sendCommand(commandNumber, parameters, skipStatusErrors)
            logging.getLogger().info("reply: %s" % ret)
            return ret
        except EpsonFiscalDriver.PrinterException as e:
            logging.getLogger().error("epsonFiscalDriver.PrinterException: %s" % str(e))
            raise PrinterException("Error de la impresora fiscal: %s.\nComando enviado: %s" % \
                (str(e), commandString))

    def sendCommand(self, commandNumber, parameters, skipStatusErrors):
        #message = chr(0x02) + chr( self._sequenceNumber ) + chr(commandNumber)
        message = chr(commandNumber)
        if parameters:
            message += chr(0x1c)
        message += chr(0x1c).join( parameters )
        message += '\n'
        reply = self._sendMessage( message )

        return reply

    def _sendMessage(self, message):
        self.lastCommand = message
        self.commands.append(message)
        self.fileSocket.write(message)

    def _formatText(self, text, context):
        sizeDict = self.textSizeDict.get(self.model)
        if not sizeDict:
            sizeDict = self.textSizeDict["615"]
        return formatText(text)[:sizeDict.get(context, 20)]

    def openBillTicket(self, type, name, address, doc, docType, ivaType):
        self.deleteAnswerFile()
        self._setCustomerData(name, address, doc, docType, ivaType)
        if type == "A":
            type = "A"
        else:
            type = "B"
        self._currentDocument = self.CURRENT_DOC_BILL_TICKET
        self._savedPayments = []
        return self._sendCommand(self.CMD_OPEN_FISCAL_RECEIPT, [type, "T"])

    def openTicket(self, defaultLetter="B"):
        self.deleteAnswerFile()
        if self.model == "320":
            self._sendCommand(self.CMD_OPEN_FISCAL_RECEIPT, [defaultLetter, "T"])
        else:
            self._sendCommand(self.CMD_OPEN_FISCAL_RECEIPT, ["T", "T"])
        self._currentDocument = self.CURRENT_DOC_TICKET
        self._savedPayments = []

    def _setCustomerData(self, name, address, doc, docType, ivaType):
        # limpio el header y trailer:
        self.setHeader()
        self.setTrailer()
        doc = doc.replace("-", "").replace(".", "")
        #if doc and docType != "3" and filter(lambda x: x not in string.digits, doc):
            # Si tiene letras se blanquea el DNI para evitar errores, excepto que sea
            # docType="3" (Pasaporte)
        #    doc, docType = " ", " "
        if not doc.strip():
            docType = " "

        ivaType = self.ivaTypeMap.get(ivaType, "C")
        if ivaType != "C" and (not doc or docType != self.DOC_TYPE_CUIT):
            raise ValidationError("Error, si el tipo de IVA del cliente NO es consumidor final, "
                "debe ingresar su número de CUIT.")
        parameters = [self._formatText(name, 'customerName'),
                       doc or " ",
                       ivaType,   # Iva Comprador
                       docType or " ", # Tipo de Doc.
                       ]
        if self.model in ["715v1", "715v2", "320", "441", "PL23"]:
            parameters.append(self._formatText(address, 'custAddressSize') or " ") # Domicilio
        return self._sendCommand(self.CMD_SET_CUSTOMER_DATA, parameters)

    def closeDocument(self):
        if self._currentDocument in (self.CURRENT_DOC_TICKET, self.CURRENT_DOC_BILL_TICKET):
            for desc, payment in self._savedPayments:
                self._sendCommand(self.CMD_ADD_PAYMENT, [self._formatText(desc, "paymentDescription"),
                                   payment, "T", "1"])
            del self._savedPayments
            reply = self._sendCommand(self.CMD_CLOSE_FISCAL_RECEIPT)
            return reply
        if self._currentDocument in (self.CURRENT_DOC_NON_FISCAL, ):
            return self._sendCommand(self.CMD_CLOSE_NON_FISCAL_RECEIPT)
        if self._currentDocument in (self.CURRENT_DOC_CREDIT_BILL_TICKET, self.CURRENT_DOC_CREDIT_TICKET):
            for desc, payment in self._savedPayments:
                self._sendCommand(self.CMD_ADD_PAYMENT, [self._formatText(desc, "paymentDescription"),
                                   payment, "T", "1"])
            del self._savedPayments
            reply = self._sendCommand(self.CMD_CLOSE_CREDIT_NOTE)
            return reply
        if self._currentDocument in (self.CURRENT_DOC_DNFH, ):
            reply = self._sendCommand(self.CMD_CLOSE_DNFH)
            # Reimprimir copias (si es necesario)
            for copy in range(self._copies - 1):
                self._sendCommand(self.CMD_REPRINT)
            return reply
        raise NotImplementedError

    def addPayment(self, description, payment):
        paymentStr = ("%.2f" % round(payment, 2)).replace(",", ".")
        self._savedPayments.append((description, paymentStr))

    def addItem(self, description, quantity, price, iva, discount=0, discountDescription='', negative=False):
        if type(description) in (str,):
            description = [description]
        if negative:
            sign = 'm'
        else:
            sign = 'M'
        quantityStr = str(float(quantity)).replace(',', '.')
        priceUnit = price
        priceUnitStr = str(priceUnit).replace(",", ".")
        ivaStr = str(float(iva)).replace(",", ".")
        for d in description[:-1]:
            self._sendCommand(self.CMD_PRINT_TEXT_IN_FISCAL, [self._formatText(d, 'fiscalText'), "0"])
        reply = self._sendCommand(self.CMD_PRINT_LINE_ITEM,
                                   [self._formatText(description[-1], 'lineItem'),
                                     quantityStr, priceUnitStr, ivaStr, sign, "0.0", "1", "T"])
        if discount:
            discountStr = str(float(discount)).replace(",", ".")
            self._sendCommand(self.CMD_LAST_ITEM_DISCOUNT,
                [self._formatText(discountDescription, 'discountDescription'), discountStr,
                  "m", "1", "T"])
        return reply

    def getLastNumber(self):
        if not self.pathFileAnswer.endswith("\\"):
            self.pathFileAnswer += "\\"
        timeout = time.time() + self.WAIT_TIME
        retries = 30
        answerFile = self.pathFileAnswer + self.outputFileName + ".ans"
        while retries > 0:
            if time.time() > timeout:
                raise ComunicationError(
                    "Expiró el tiempo de espera para una respuesta de la impresora. Revise la conexión."
                " Archivo generado {}".format(self.pathFileAnswer + self.outputFileName) )

            if isfile(answerFile):
                with open(answerFile, 'r') as f:
                    lines = f.read().splitlines()
                    last_line = lines[-1]
                    self.lastNumber = last_line[34:].zfill(8)
                    return self.lastNumber
            else:
                time.sleep(1)
                timeout += self.WAIT_TIME
                retries -= 1

        if retries == 0:
            raise ComunicationError(
                "Expiró los reintentos para una respuesta de la impresora. Revise la conexión."
                " Archivo generado {}".format(self.pathFileAnswer + self.outputFileName))

    def deleteAnswerFile(self):
        if not self.pathFileAnswer.endswith("\\"):
            self.pathFileAnswer += "\\"
        answerFile = Path(self.pathFileAnswer + self.outputFileName + ".ans")
        if answerFile.is_file():
            file = self.pathFileAnswer + self.outputFileName + ".ans"
            try:
                os.unlink(file)
            except Exception as e:
                print(e)

    def openBillCreditTicket(self, type, name, address, doc, docType, ivaType, reference="NC"):
        self.deleteAnswerFile()
        self._setCustomerData(name, address, doc, docType, ivaType)
        if type == "A":
            type = "R"
        else:
            type = "S"
        self._currentDocument = self.CURRENT_DOC_CREDIT_BILL_TICKET
        self._savedPayments = []
        self._sendCommand(self.CMD_CREDIT_NOTE_REFERENCE, ["1", reference])
        return self._sendCommand(self.CMD_OPEN_CREDIT_NOTE, [type, "T"])

    def cancelDocument(self):
        if not hasattr(self, "_currentDocument"):
            return
        if self._currentDocument in (self.CURRENT_DOC_TICKET, self.CURRENT_DOC_BILL_TICKET,
                self.CURRENT_DOC_CREDIT_BILL_TICKET, self.CURRENT_DOC_CREDIT_TICKET):
            try:
                status = self._sendCommand(self.CMD_ADD_PAYMENT, ["Cancelar", "0.00", 'C', "1"])
            except:
                self.cancelAnyDocument()
                status = []
            return status
        if self._currentDocument in (self.CURRENT_DOC_NON_FISCAL, ):
            self.printNonFiscalText("CANCELADO")
            return self.closeDocument()
        if self._currentDocument in (self.CURRENT_DOC_DNFH, ):
            self.cancelAnyDocument()
            status = []
            return status
        raise NotImplementedError

    def cancelAnyDocument(self):
        try:
            self._sendCommand(self.CMD_CANCEL_ANY_DOCUMENT)
#            return True
        except:
            pass
        try:
            self._sendCommand(self.CMD_ADD_PAYMENT, ["Cancelar", "0.00", 'C', '1'])
            return True
        except:
            pass
        try:
            self._sendCommand(self.CMD_CLOSE_NON_FISCAL_RECEIPT)
            return True
        except:
            pass
        try:
            logging.getLogger().info("Cerrando comprobante con CLOSE")
            self._sendCommand(self.CMD_CLOSE_FISCAL_RECEIPT)
            return True
        except:
            pass
        return False