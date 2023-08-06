# -*- coding: iso-8859-15 -*-
import messages
import utilities
from Products.CMFCore.utils import getToolByName

___author__ = """David Gonzalez Gonzalez - dgg15@alu.ua.es"""

class ListSets:
   def __init__(self):
      pass

   def getListSetsXML(self,context):
      result = utilities.searchSets(context)
      response = " "
      if result!=None:
         for a in result:
            message = messages.xmlListSets%(a.getObject().getId(),a.getObject().getId())
            response =  response +  message
         return "<ListSets>"+response+"</ListSets>"
      else:
         return "<error code=\"noSetHierarchy\">No sets.</error>"
