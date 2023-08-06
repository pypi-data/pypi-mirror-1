# -*- coding: iso-8859-15 -*-

from Products.CMFCore.utils import getToolByName
import utilities
import messages
import re
__author__ = """ David Gonzalez Gonzalez -- dgg15@alu.ua.es"""

class GetRecord:

   def __init__(self):
      pass

   def getGetRecordXML(self,context,form):

      identifier = form["identifier"]
      search_result = utilities.searchRecord(context,identifier)

      if search_result != None:
         return messages.xmlGetRecord%(identifier,
                              search_result.Date().replace(' ','T')+'Z',
                              identifier,
                              search_result.Title(),
                              search_result.Description(),
                              search_result.Subject(),
                              search_result.Creator(),
                              search_result.Type(),
                              search_result.Format(),
                              search_result.Language(),
                              search_result.absolute_url())
      else:
         return messages.xmlErrorIllegal%(identifier)

