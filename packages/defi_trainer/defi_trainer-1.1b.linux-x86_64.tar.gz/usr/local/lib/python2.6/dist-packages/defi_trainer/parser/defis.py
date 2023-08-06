"""
Copyright 2008,2009 Steven Mohr

This file is part of DefiTrainer.

    DefiTrainer is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    DefiTrainer is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with DefiTrainer.  If not, see <http://www.gnu.org/licenses/>.
 
"""

import logging, copy
import docutils.parsers.rst

class Defis(object):
    """
    Defis is the container class of our definition file.
    """
    def __init__(self, data):
        """
        Defis parses a list of string and allows access to its intern tree-like
        data structure.
        @param data: definitions to parse
        @type data: list of strings
        """
        
        self.data = self.parse_defis(data)

    def get_section_list(self):
        return self.data.keys()

    def parse_defis(self, data):
        """
        Parses definition and returns a tree-like structure
        @argument data: list of string that should be parsed
        @return: definitions loaded from file
        @rtype: list of 2-tuple (topic, definition)
        """

        parser = docutils.parsers.rst.Parser()
        document = docutils.utils.new_document("test")
        document.settings.tab_width = 4
        document.settings.pep_references = 1
        document.settings.rfc_references = 1
        parser.parse(data, document)
        dom = document.asdom()

        self.__parse_document(dom.firstChild)
        return self.data

    def __parse_document(self, document_obj):
        """
        parse_document calls recursively functions to parse its children
        and sets self.data
        @param document_obj: document object that should be parsed
        """
        
        returnValue = dict()
        temp = document_obj.firstChild
        self.section_list = []
        self.text_temp = []
        self.defi_temp = []
        while temp is not None:
            self.__choose_parsing_func(temp)
            if len(self.section_list) > 0:
                section = self.section_list[0]
            else:
                section = "__STANDARD__"
            data = self.defi_temp
            returnValue[section] = data
            self.section_list = list()
            self.defi_temp = list()
            self.text_temp = list()
            temp = temp.nextSibling

        self.data = returnValue
        del self.text_temp
        del self.defi_temp
        del self.section_list

    def __parse_section(self, section):
        self.__choose_parsing_func(section.firstChild)
        if self.text_temp != []:
            self.defi_temp.append((self.section_list.pop(),self.text_temp))
            self.text_temp = []
        if section.nextSibling is not None and section.parentNode.localName != 'document':
            self.__choose_parsing_func(section.nextSibling)

    def __parse_enum_list(self, section):
        raise Exception("Not implemented yet")

    def __parse_block_quote(self, block_qoute):
        pass

    def __parse_bullet_list(self, blist):
        self.text_temp.append(u"<ul>")
        self.__choose_parsing_func(blist.firstChild)
        self.text_temp.append(u"</ul>")
        if blist.nextSibling is not None:
            self.__choose_parsing_func(blist.nextSibling)

    def __parse_list_item(self, bullet):
        self.text_temp.append(u"<li>")
        self.__choose_parsing_func(bullet.firstChild)
        self.text_temp.append(u"</li>")
        if bullet.nextSibling is not None:
            self.__choose_parsing_func(bullet.nextSibling)

    def __parse_definition_list(self, defiList):
        self.__choose_parsing_func(defiList.firstChild)
        if defiList.nextSibling is not None:
            self.__choose_parsing_func(defiList.nextSibling)

    def __parse_definition_list_item(self, item):
        self.__choose_parsing_func(item.firstChild)
        if self.text_temp != []:
            self.defi_temp.append((self.section_list.pop(),self.text_temp))
            self.text_temp = []
        if item.nextSibling is not None:
            self.__choose_parsing_func(item.nextSibling)

    def __parse_definition(self, defi):
        self.__choose_parsing_func(defi.firstChild)

        if defi.nextSibling is not None:
            self.__choose_parsing_func(defi.nextSibling)

    def __parse_title(self, title):
        self.section_list.append(title.firstChild.nodeValue)
        if title.nextSibling is not None:
            self.__choose_parsing_func(title.nextSibling)

    def __parse_term(self, term):
        self.section_list.append(term.firstChild.nodeValue)
        if term.nextSibling is not None:
            self.__choose_parsing_func(term.nextSibling)

    def __parse_enumerated_list(self, block_qoute):
        raise Exception("Not implemented yet")

    def __parse_system_message(self, msg):
        logging.debug(msg.firstChild.nodeValue)

    def __parse_paragraph(self, paragraph):
        self.text_temp.append(paragraph.firstChild.nodeValue)
        if paragraph.nextSibling is not None:
            self.__choose_parsing_func(paragraph.nextSibling)

    def __choose_parsing_func(self, item):
        """
        choose_parsing_func determines the type of object and calls
        the correct parsing function
        """
        option_dict = {'section': self.__parse_section,
                       'enumerated_list': self.__parse_enum_list,
                       'block_quote': self.__parse_block_quote,
                       'bullet_list' : self.__parse_bullet_list,
                       'list_item' : self.__parse_list_item,
                       'definition_list' : self.__parse_definition_list,
                       'definition_list_item': self.__parse_definition_list_item,
                       'definition': self.__parse_definition,
                       'title': self.__parse_title,
                       'term': self.__parse_term,
                       'paragraph': self.__parse_paragraph,
                       'block_qoute': self.__parse_block_quote,
                       'system_message': self.__parse_system_message
                       }
        try:
            if item.localName in option_dict:
                option_dict[item.localName](item)
            else:
                logging.warning("Unknown element: %s" % item.localName)
        except AttributeError:
            logging.warning("Error in definition file after:%s" %
                            self.text_temp)