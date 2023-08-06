# -*- coding: iso-8859-15 -*-
import utilities
import messages
__author__ = """David Gonzalez Gonzalez - dgg15@alu.ua.es"""


class Identify:
   """ This class represents an Indentify verb Petition """

   def __init__(self):
      pass

   def getIdentifyXML(self,repo_name, portal_url, email, repo_identifier):
      """ Returns xml about Indentify verb """
      xml = messages.xmlIdentify%(repo_name,portal_url,email,repo_identifier)
      return xml
