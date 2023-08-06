# -*- coding: iso-8859-15 -*-
import utilities
import messages

__author__ = "David Gonzalez Gonzalez -- dgg15@alu.ua.es"

class ListIdentifiers:
   def __init__(self):
      pass
   def getListIdentifiersXML(self,context,start_date,end_date):
      identifiers = utilities.searchRecords(context,start_date,end_date)
      response = ""
      if identifiers!= None:
         for a in identifiers:
            response = response + messages.xmlListIdentifiers%(a.getObject().getId(),a.getObject().Date().replace(' ','T')+'Z',a.getObject().getId())
         return "<ListIdentifiers>"+response+"</ListIdentifiers>"
      else:
         return "<error code=\"noRecordsMatch\">No records were found</error>"
      
