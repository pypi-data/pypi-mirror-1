# -*- coding: utf-8 -*-
# File: raa.py
# new fcts for RAA
#
# Copyright (c) 2006 by ['Jean-Michel FRANCOIS']
# Generator: ArchGenXML Version 1.5.0
#            http://plone.org/products/archgenxml
#
# GNU General Public License (GPL)
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.


def cmd_add_niveau(ooo_info,args):
    """
    Ajoute un titre de niveau %level
    """
    #args -> level,str_content
    doc = ooo_info['doc']
    cursor = ooo_info['cursor']
    cursor.gotoEnd(False)
    cursor.BreakType = NONE
    
    doc_toc = ooo_info['doc_toc']
    cursor_toc = ooo_info['cursor_toc']
    cursor_toc.gotoEnd(False)
    cursor_toc.BreakType = NONE
    
    cursor.ParaStyleName = "RAATitre%s"%level
    cursor_toc.ParaStyleName = "RAATitre%s"%level

    doc.Text.insertString(cursor,str_content,False) # False:[in]  bAbsorb
    doc.Text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
    
    doc_toc.Text.insertString(cursor_toc,str_content,False) # False:[in]  bAbsorb
    doc_toc.Text.insertControlCharacter(cursor_toc, PARAGRAPH_BREAK, False)


def cmd_add_detail(ooo_info,args):
    """
    Ajoute un type de détails.
    """
    #couper args pour recup details et value
    doc = ooo_info['doc']
    cursor = ooo_info['cursor']
    cursor.gotoEnd(False)
    cursor.BreakType = NONE
    old_style = cursor.ParaStyleName
    cursor.ParaStyleName = "RAAMetadatas"
    str_type = ""
    if detail == "numero":
        str_type = "Numéro: ".decode("UTF-8")
    if detail == "date_depot":
        str_type = "Date de dépôt: ".decode("UTF-8")
    if detail == "date_publication":
        str_type = "Date de publication: ".decode("UTF-8")
    if detail == "service":
        str_type = "Service: ".decode("UTF-8")
    
    doc.Text.insertString(cursor,str_type+value,False)
    doc.Text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
    cursor.ParaStyleName = old_style