# -*- coding: iso-8859-1 -*-
from os.path import join

import sys

from Fiscal.Controlador import PyFiscalPrinter
from Fiscal.Hasar import HasarPrinter

# printer = HasarPrinter()
# printer.model = "320"
# printer.pathFileCommand = join("u:\\","comandos")
# printer.pathFileAnswer = join("u:\\","respues")

#genero factura B
# printer.openBillTicket("B","Jose oscar vogel","suiza s/n","23.347.203","2","C")
# printer.setHeader(["","Facundo Quiroga 298"])
# printer.setTrailer(["Contado Efectivo 15% de descuento"])
# printer.addItem("CAnilla",1,125.32,21)
# printer.addPayment("Contado Efectivo",125.32)
# printer.closeDocument()
# printer.close()
# factura = printer.getLastNumber()
# print("Factura generada {}".format(factura))
#
# #factura A
# printer.openBillTicket("A","Ferreteria Avenida SA", "Facundo Quiroga 298","30522884363",
#                        printer.DOC_TYPE_CUIT, printer.IVA_TYPE_RESPONSABLE_INSCRIPTO)
# printer.setHeader(["","Facundo Quiroga 298"])
# printer.setTrailer(["Contado Efectivo 15% de descuento"])
# printer.addItem("CHAPA CANAL.GALVA.1086 C-27  1.00 MTS   ",100,171.597,21)
# printer.addPayment("Contado Efectivo",17159.7)
# printer.closeDocument()
# printer.close()
# factura = printer.getLastNumber()

# #factura B exento
# printer.openBillTicket("B","Municipalidad de Garuhapé", "Av. las americas","30999157315",
#                        printer.DOC_TYPE_CUIT, printer.IVA_TYPE_EXENTO)
# printer.setHeader(["","Facundo quiroga 298"])
# printer.setTrailer(["","Licitacion"])
# printer.addItem("CHAPA CANAL.GALVA.1086 C-27  1.00 MTS   ",100,171.597,21)
# printer.addPayment("Cuenta Corriente",17159.7)
# printer.closeDocument()
# printer.close()

#nota de credito b
# printer.openBillCreditTicket("B","jose oscar vogel","suiza s/n","23347203",
#                              printer.DOC_TYPE_DNI,printer.IVA_TYPE_CONSUMIDOR_FINAL,"000100000001")
# printer.setHeader(["","Facundo Quiroga 298"])
# printer.setTrailer(["Contado Efectivo 15% de descuento"])
# printer.addItem("CHAPA CANAL.GALVA.1086 C-27  1.00 MTS   ",100,171.597,21)
# printer.addPayment("Cuenta Corriente",17159.7)
# printer.closeDocument()
# printer.close()
# factura = printer.getLastNumber()
# print("Factura generada {}".format(factura))

controlador = PyFiscalPrinter()
controlador.LanzarExcepciones = True

marca = 'hasar'
modelo = '715v2'
carpetacomando = join("u:\\", "comandos")
carpetarespuesta = join("u:\\", "respues")
archivo = 'PC-Oscar'

controlador.Conectar(marca=marca, modelo=modelo,
                     carpetacomando=carpetacomando,
                     carpetarespuesta=carpetarespuesta)
controlador.FijarTextoCabecera("Facundo Quiroga 298")
controlador.FijarTextoPie("Contado efectivo 15% descuento")

tipo_cbte = 1
tipo_doc = 80;
nro_doc = "20267565393"
nombre_cliente = 'Joao Da Silva'
domicilio_cliente = 'Rua 76 km 34.5'
tipo_responsable = 1
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

codigo = "P0002"
ds = "Descripcion del producto P0002"
qty = 1.00
precio = 100.00
bonif = 0.00
alic_iva = 21.00
importe = 121.00
ok = controlador.ImprimirItem(ds, qty, importe, alic_iva)
ok = controlador.Percepcion(0.00,"RG 031/2012 DGR",121.23)
ok = controlador.ImprimirPago("efectivo", importe)
ok = controlador.CerrarComprobante()
print("Comprobante generado {}".format(controlador.factura))
