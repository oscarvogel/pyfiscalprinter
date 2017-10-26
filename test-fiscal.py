# -*- coding: iso-8859-1 -*-
from os.path import join

from Fiscal.Hasar import HasarPrinter

printer = HasarPrinter()
printer.model = "320"
printer.pathFileCommand = join("u:\\","comandos")
printer.pathFileAnswer = join("u:\\","respues")

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
printer.openBillCreditTicket("B","jose oscar vogel","suiza s/n","23347203",
                             printer.DOC_TYPE_DNI,printer.IVA_TYPE_CONSUMIDOR_FINAL,"000100000001")
printer.setHeader(["","Facundo Quiroga 298"])
printer.setTrailer(["Contado Efectivo 15% de descuento"])
printer.addItem("CHAPA CANAL.GALVA.1086 C-27  1.00 MTS   ",100,171.597,21)
printer.addPayment("Cuenta Corriente",17159.7)
printer.closeDocument()
printer.close()
factura = printer.getLastNumber()
print("Factura generada {}".format(factura))