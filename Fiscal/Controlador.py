#!/usr/bin/python
# -*- coding: utf8 -*-

"Interfaz de alto nivel para automatización de controladores fiscales"
import traceback
from functools import wraps
from io import StringIO

import sys

from os.path import join

from Fiscal.EpsonFiscalDriver import EpsonPrinter
from Fiscal.Hasar import HasarPrinter

"Basado en https://github.com/reingart/pyfiscalprinter"

__version__ = "0.01"

def inicializar_y_capturar_excepciones(func):
    "Decorador para inicializar y capturar errores"
    @wraps(func)
    def capturar_errores_wrapper(self, *args, **kwargs):
        try:
            # inicializo (limpio variables)
            self.Traceback = self.Excepcion = ""
            return func(self, *args, **kwargs)
        except Exception as e:
            ex = traceback.format_exception( sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
            self.Traceback = ''.join(ex)
            self.Excepcion = traceback.format_exception_only( sys.exc_info()[0], sys.exc_info()[1])[0]
            if self.LanzarExcepciones:
                raise
        finally:
            pass
    return capturar_errores_wrapper

class PyFiscalPrinter(object):

    def __init__(self):
        self.Version = __version__
        self.Exception = self.Traceback = ""
        self.LanzarExcepciones = False
        self.printer = None
        self.log = StringIO()
        self.header = []
        self.trailer = []

    @inicializar_y_capturar_excepciones
    def Conectar(self, marca='hasar', modelo='320',
                 puerto=None,
                 carpetacomando=None, carpetarespuesta=None):

        if marca == 'hasar':
            Printer = HasarPrinter
        elif marca == 'epson':
            Printer = EpsonPrinter

        printer = Printer(model=modelo)
        printer.pathFileAnswer = carpetarespuesta
        printer.pathFileCommand = carpetacomando

        self.printer = printer
        self.cbte_fiscal_map = {
                                1: 'FA', 2: 'NDA', 3: 'NCA',
                                6: 'FB', 7: 'NDB', 8: 'NCB',
                                11: 'FC', 12: 'NDC', 13: 'NDC',
                                81:	'FA', 82: 'FB', 83: 'T',      # tiques
                                }
        self.pos_fiscal_map = {
                                1:  printer.IVA_TYPE_RESPONSABLE_INSCRIPTO,
                                2:	printer.IVA_TYPE_RESPONSABLE_NO_INSCRIPTO,
                                3:	printer.IVA_TYPE_NO_RESPONSABLE,
                                4:	printer.IVA_TYPE_EXENTO,
                                5:	printer.IVA_TYPE_CONSUMIDOR_FINAL,
                                6:	printer.IVA_TYPE_RESPONSABLE_MONOTRIBUTO,
                                7:	printer.IVA_TYPE_NO_CATEGORIZADO,
                                12:	printer.IVA_TYPE_PEQUENIO_CONTRIBUYENTE_EVENTUAL,
                                13: printer.IVA_TYPE_MONOTRIBUTISTA_SOCIAL,
                                14:	printer.IVA_TYPE_PEQUENIO_CONTRIBUYENTE_EVENTUAL_SOCIAL,
                                }
        self.doc_fiscal_map = {
                                96: printer.DOC_TYPE_DNI,
                                80: printer.DOC_TYPE_CUIT,
                                89: printer.DOC_TYPE_LIBRETA_ENROLAMIENTO,
                                90: printer.DOC_TYPE_LIBRETA_CIVICA,
                                00: printer.DOC_TYPE_CEDULA,
                                94: printer.DOC_TYPE_PASAPORTE,
                                99: printer.DOC_TYPE_SIN_CALIFICADOR,
                              }

    def DebugLog(self):
        "Devolver bitácora de depuración"
        msg = self.log.getvalue()
        return msg

    @inicializar_y_capturar_excepciones
    def AbrirComprobante(self,
                     tipo_cbte=83,                              # tique
                     tipo_responsable=5,                        # consumidor final
                     tipo_doc=99, nro_doc=0,                    # sin especificar
                     nombre_cliente="", domicilio_cliente="",
                     referencia=None,                           # comprobante original (ND/NC)
                     **kwargs
                     ):
        "Creo un objeto factura (internamente) e imprime el encabezado"
        # crear la estructura interna
        self.factura = {"encabezado": dict(tipo_cbte=tipo_cbte,
                                           tipo_responsable=tipo_responsable,
                                           tipo_doc=tipo_doc, nro_doc=nro_doc,
                                           nombre_cliente=nombre_cliente,
                                           domicilio_cliente=domicilio_cliente,
                                           referencia=referencia),
                        "items": [], "pagos": []}
        printer = self.printer

        # mapear el tipo de comprobante según RG1785/04:
        cbte_fiscal = self.cbte_fiscal_map[int(tipo_cbte)]
        letra_cbte = cbte_fiscal[-1] if len(cbte_fiscal) > 1 else None
        # mapear el tipo de cliente (posicion/categoria) según RG1785/04:
        pos_fiscal = self.pos_fiscal_map[int(tipo_responsable)]
        # mapear el numero de documento según RG1361
        doc_fiscal = self.doc_fiscal_map[int(tipo_doc)]
        # cancelar y volver a un estado conocido
        printer.cancelAnyDocument()
        # enviar texto de cabecera y pie de pagina:
        printer.setHeader(self.header)
        printer.setTrailer(self.trailer)
        # enviar los comandos de apertura de comprobante fiscal:
        if cbte_fiscal.startswith('T'):
            if letra_cbte:
                ret = printer.openTicket(letra_cbte)
            else:
                ret = printer.openTicket()
        elif cbte_fiscal.startswith("F"):
            ret = printer.openBillTicket(letra_cbte, nombre_cliente, domicilio_cliente,
                                         nro_doc, doc_fiscal, pos_fiscal)
        elif cbte_fiscal.startswith("ND"):
            ret = printer.openDebitNoteTicket(letra_cbte, nombre_cliente,
                                              domicilio_cliente, nro_doc, doc_fiscal,
                                              pos_fiscal)
        elif cbte_fiscal.startswith("NC"):
            #if isinstance(referencia, str):
            referencia = referencia.encode("latin1", "ignore")
            ret = printer.openBillCreditTicket(letra_cbte, nombre_cliente,
                                               domicilio_cliente, nro_doc, doc_fiscal,
                                               pos_fiscal, referencia)
        return True

    @inicializar_y_capturar_excepciones
    def ImprimirItem(self, ds, qty, importe, alic_iva=21.):
        "Envia un item (descripcion, cantidad, etc.) a una factura"
        self.factura["items"].append(dict(ds=ds, qty=qty,
                                          importe=importe, alic_iva=alic_iva))
        ##ds = unicode(ds, "latin1") # convierto a latin1
        # Nota: no se calcula neto, iva, etc (deben venir calculados!)
        discount = discountDescription =  None
        self.printer.addItem(ds, float(qty), float(importe), float(alic_iva),
                                    discount, discountDescription)
        return True

    @inicializar_y_capturar_excepciones
    def ImprimirPago(self, ds, importe):
        "Imprime una linea con la forma de pago y monto"
        self.factura["pagos"].append(dict(ds=ds, importe=importe))
        self.printer.addPayment(ds, float(importe))
        return True

    @inicializar_y_capturar_excepciones
    def CerrarComprobante(self):
        "Envia el comando para cerrar un comprobante Fiscal"
        self.printer.closeDocument()
        self.printer.close()
        nro = self.printer.getLastNumber()
        self.factura["nro_cbte"] = nro
        return True

    @inicializar_y_capturar_excepciones
    def FijarTextoCabecera(self, ds, linea=None):
        if linea:
            self.header[linea] = ds
        else:
            self.header.append(ds)
        return True

    @inicializar_y_capturar_excepciones
    def FijarTextoPie(self, ds, linea=None):
        if linea:
            self.trailer[linea] = ds
        else:
            self.trailer.append(ds)
        return True

    @inicializar_y_capturar_excepciones
    def Percepcion(self, alicuota=0.00, mensaje='', monto=0.00):
        return self.printer.perceptions(alicuota, mensaje, monto)

if __name__ == '__main__':
    DEBUG = '--debug' in sys.argv
    controlador = PyFiscalPrinter()
    controlador.LanzarExcepciones = True

    marca = 'hasar'
    modelo = '715v2'
    carpetacomando = join("u:\\","comandos")
    carpetarespuesta = join("u:\\","respues")
    archivo = 'PC-Oscar'

    controlador.Conectar(marca=marca, modelo=modelo,
                         archivo=archivo, carpetacomando=carpetacomando,
                         carpetarespuesta=carpetarespuesta)
    controlador.FijarTextoCabecera("Facundo Quiroga 298")
    controlador.FijarTextoPie("Contado efectivo 15% descuento")

    tipo_cbte = 83 if not "--nc" in sys.argv else 3
    tipo_doc = 80;
    nro_doc = "20267565393"
    nombre_cliente = 'Joao Da Silva'
    domicilio_cliente = 'Rua 76 km 34.5'
    tipo_responsable = 5 if not "--nc" in sys.argv else 1  # R.I. ("A)
    referencia = None if not "--nc" in sys.argv else "F 1234"


    ok = controlador.AbrirComprobante(tipo_cbte, tipo_responsable,
                                      tipo_doc, nro_doc,
                                      nombre_cliente, domicilio_cliente,
                                      referencia)
    codigo = "P0001"
    ds = "Descripcion del producto P0001"
    qty = 1.00
    precio = 100.00
    bonif = 0.00
    alic_iva = 21.00
    importe = 121.00
    ok = controlador.ImprimirItem(ds, qty, importe, alic_iva)
    ok = controlador.ImprimirPago("efectivo", importe)
    ok = controlador.CerrarComprobante()
