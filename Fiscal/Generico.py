# -*- coding: iso-8859-1 -*-
"""
Interfaz para la impresora fiscal

Basado en PyFiscalPrinter desde https://github.com/reingart/pyfiscalprinter

GNU Lesser General Public License v3.0

"""

class PrinterInterface:

    """Interfaz que deben cumplir las impresoras fiscales."""

    # Documentos no fiscales

    WAIT_TIME = 10
    RETRIES = 4
    WAIT_CHAR_TIME = 0.1
    NO_REPLY_TRIES = 200

    def openNonFiscalReceipt(self):
        """Abre documento no fiscal"""
        raise NotImplementedError

    def printNonFiscalText(self, text):
        """Imprime texto fiscal. Si supera el l?mite de la linea se trunca."""
        raise NotImplementedError

    NON_FISCAL_TEXT_MAX_LENGTH = 40 # Redefinir

    def closeDocument(self):
        """Cierra el documento que est? abierto"""
        raise NotImplementedError

    def cancelDocument(self):
        """Cancela el documento que est? abierto"""
        raise NotImplementedError

    def addItem(self, description, quantity, price, iva, discount, discountDescription, negative=False):
        """Agrega un item a la FC.
            @param description          Descripci?n del item. Puede ser un string o una lista.
                Si es una lista cada valor va en una l?nea.
            @param quantity             Cantidad
            @param price                Precio (incluye el iva si la FC es B o C, si es A no lo incluye)
            @param iva                  Porcentaje de iva
            @param negative             True->Resta de la FC
            @param discount             Importe de descuento
            @param discountDescription  Descripci?n del descuento
        """
        raise NotImplementedError

    def addPayment(self, description, payment):
        """Agrega un pago a la FC.
            @param description  Descripci?n
            @param payment      Importe
        """
        raise NotImplementedError

    DOC_TYPE_CUIT = 'C'
    DOC_TYPE_LIBRETA_ENROLAMIENTO = '0'
    DOC_TYPE_LIBRETA_CIVICA = '1'
    DOC_TYPE_DNI = '2'
    DOC_TYPE_PASAPORTE = '3'
    DOC_TYPE_CEDULA = '4'
    DOC_TYPE_SIN_CALIFICADOR = ' '

    IVA_TYPE_RESPONSABLE_INSCRIPTO = 'I'
    IVA_TYPE_RESPONSABLE_NO_INSCRIPTO = 'N'
    IVA_TYPE_EXENTO = 'E'
    IVA_TYPE_NO_RESPONSABLE = 'A'
    IVA_TYPE_CONSUMIDOR_FINAL = 'C'
    IVA_TYPE_RESPONSABLE_NO_INSCRIPTO_BIENES_DE_USO = 'B'
    IVA_TYPE_RESPONSABLE_MONOTRIBUTO = 'M'
    IVA_TYPE_MONOTRIBUTISTA_SOCIAL = 'S'
    IVA_TYPE_PEQUENIO_CONTRIBUYENTE_EVENTUAL = 'V'
    IVA_TYPE_PEQUENIO_CONTRIBUYENTE_EVENTUAL_SOCIAL = 'W'
    IVA_TYPE_NO_CATEGORIZADO = 'T'

    # Ticket fiscal (siempre es a consumidor final, no permite datos del cliente)

    def openTicket(self):
        """Abre documento fiscal"""
        raise NotImplementedError

    def openBillTicket(self, type, name, address, doc, docType, ivaType):
        """
        Abre un ticket-factura
            @param  type        Tipo de Factura "A", "B", o "C"
            @param  name        Nombre del cliente
            @param  address     Domicilio
            @param  doc         Documento del cliente seg�n docType
            @param  docType     Tipo de documento
            @param  ivaType     Tipo de IVA
        """
        raise NotImplementedError

    def openBillCreditTicket(self, type, name, address, doc, docType, ivaType, reference="NC"):
        """
        Abre un ticket-NC
            @param  type        Tipo de Factura "A", "B", o "C"
            @param  name        Nombre del cliente
            @param  address     Domicilio
            @param  doc         Documento del cliente seg�n docType
            @param  docType     Tipo de documento
            @param  ivaType     Tipo de IVA
            @param  reference
        """
        raise NotImplementedError

    def openDebitNoteTicket(self, type, name, address, doc, docType, ivaType):
        """
        Abre una Nota de D�bito
            @param  type        Tipo de Factura "A", "B", o "C"
            @param  name        Nombre del cliente
            @param  address     Domicilio
            @param  doc         Documento del cliente seg�n docType
            @param  docType     Tipo de documento
            @param  ivaType     Tipo de IVA
            @param  reference
        """
        raise NotImplementedError

    def openRemit(self, name, address, doc, docType, ivaType):
        """
        Abre un remito
            @param  name        Nombre del cliente
            @param  address     Domicilio
            @param  doc         Documento del cliente seg�n docType
            @param  docType     Tipo de documento
            @param  ivaType     Tipo de IVA
        """
        raise NotImplementedError

    def openReceipt(self, name, address, doc, docType, ivaType, number):
        """
        Abre un recibo
            @param  name        Nombre del cliente
            @param  address     Domicilio
            @param  doc         Documento del cliente seg�n docType
            @param  docType     Tipo de documento
            @param  ivaType     Tipo de IVA
            @param  number      N�mero de identificaci�n del recibo (arbitrario)
        """
        raise NotImplementedError

    def addRemitItem(self, description, quantity):
        """Agrega un item al remito
            @param description  Descripci�n
            @param quantity     Cantidad
        """
        raise NotImplementedError

    def addReceiptDetail(self, descriptions, amount):
        """Agrega el detalle del recibo
            @param descriptions Lista de descripciones (lineas)
            @param amount       Importe total del recibo
        """
        raise NotImplementedError

    def addAdditional(self, description, amount, iva, negative=False):
        """Agrega un adicional a la FC.
            @param description  Descripci�n
            @param amount       Importe (sin iva en FC A, sino con IVA)
            @param iva          Porcentaje de Iva
            @param negative True->Descuento, False->Recargo"""
        raise NotImplementedError

    def getLastNumber(self, letter):
        """Obtiene el �ltimo n�mero de FC"""
        raise NotImplementedError

    def getLastCreditNoteNumber(self, letter):
        """Obtiene el �ltimo n�mero de FC"""
        raise NotImplementedError

    def getLastRemitNumber(self):
        """Obtiene el �ltimo n�mero de Remtio"""
        raise NotImplementedError

    def cancelAnyDocument(self):
        """Cancela cualquier documento abierto, sea del tipo que sea.
           No requiere que previamente se haya abierto el documento por este objeto.
           Se usa para destrabar la impresora."""
        raise NotImplementedError

    def dailyClose(self, type):
        """Cierre Z (diario) o X (parcial)
            @param type     Z (diario), X (parcial)
        """
        raise NotImplementedError

    def close(self):
        """Cierra la impresora"""
        raise NotImplementedError

    def getWarnings(self):
        return []

    def openDrawer(self):
        """Abrir caj�n del dinero - No es mandatory implementarlo"""
        pass

    def perceptions(self, alicuota=0.00, msg='', amount=0.00):
        """Envia percepciones al impresor fiscal"""
        pass

    CPBTE_FACTURA_A = 1
    CPBTE_DEBITO_A = 2
    CPBTE_CREDITO_A = 3
    CPBTE_FACTURA_B = 6
    CPBTE_DEBITO_B = 7
    CPBTE_CREDITO_B = 8