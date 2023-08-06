# -*- coding: iso-8859-15 -*-
import utilities
import messages

__author__ = """ David Gonzalez Gonzalez -- dgg15@alu.ua.es """

class ListRecords:
   def __init__(self):
      pass
   def getListRecordsXML(self, context, date_start, date_end):
     record = utilities.searchRecords(context,date_start,date_end)
     response = ""
     if record !=None:
         for a in record:
            response = response + "<record>"
            response = response + (messages.xmlListRecordsHeader%(a.getObject().getId(), a.getObject().Date().replace(' ','T')+'Z', a.getObject().getId()))
            response = response + (messages.xmlListRecordsBody%(a.getObject().Subject(), a.getObject().Creator(), 
                                  a.getObject().Type(), a.getObject().Format(), a.getObject().Language())) +"</record>"
         return "<ListRecords>"+response+"</ListRecords>"
     else:
         return """<error code="noRecordsMatch">No records were found</error> """
      

