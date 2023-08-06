# -*- coding: utf-8 *- 
#################################################################
#       EN TETE
#
#################################################################

"""
DOCUMENTATION

L'objectif de ce script est de generer un recueil
Les arguments:

- Le premier (--sequence=) est un fichier de configuration perso contenant
   l ensemble des commandes que devra executer le script sur OOo2.
   En voici un exemple:
open:/home/sit15/model.odt
set_titre_recueil:Mon Titre
add_niveau1:Mon Titre de niveau 1 
merge_files:/home/sit15/toto.doc ...
add_niveau1:Mon Titre de niveau 2
add_niveau2:Mon Titre de niveau 2
save:

"""

import sys, os
from optparse import OptionParser
parser = OptionParser()
parser.add_option("", "--port",
                type="int", dest="port", default=2002,
                help="specify the port")
parser.add_option("", "--sequence",
                type="string", dest="seq", default=2002,
                help="specify the file that contains command sequences")

(options, args) = parser.parse_args()

ooo_info = dict()





#################################################################

#                       DEF

#################################################################

def parse_seq(file_seq):
    """
    Parse le fichier de sequence
    -> dictionnary
    {cmd:args}
    """
    #d = dict()
    l = list()
    f = open(file_seq,'r')
    lines = str(f.read()).splitlines()
    for line in lines:
        if line is None:
            continue
        cmd = line.split(':')
        if len(cmd) == 2:
            #d[cmd[0]] = cmd[1]
            l.append(line.decode("UTF-8"))
        else:
            print "cmd invalide :%s"%cmd
    #print l
    return l


def cmd_open(ooo_info,syspath_doc):
    """
    ooo_info:
    {ctx:l objet, desktop: , ....}
    """
    url = systemPathToFileUrl(syspath_doc)
    #load as template:
    pp_template = PropertyValue()
    #pp_template.Name  = "AsTemplate"
    #pp_template.Value = True
    pp_hidden = PropertyValue()
    pp_hidden.Name = "Hidden"
    pp_hidden.Value = True
    load_pp = ()
    ooo_info['doc'] = ooo_info['desktop'].loadComponentFromURL(url,"_blank",0,load_pp)
    ooo_info['cursor'] = ooo_info['doc'].Text.createTextCursor()

def cmd_open_toc(ooo_info,syspath_doc):
    """
    ooo_info:
    {ctx:l objet, desktop: , ....}
    """
    url = systemPathToFileUrl(syspath_doc)
    #load as template:
    pp_template = PropertyValue()
    #pp_template.Name  = "AsTemplate"
    #pp_template.Value = True
    pp_hidden = PropertyValue()
    pp_hidden.Name = "Hidden"
    pp_hidden.Value = True
    load_pp = ()
    ooo_info['doc_toc'] = ooo_info['desktop'].loadComponentFromURL(url,"_blank",0,load_pp)
    ooo_info['cursor_toc'] = ooo_info['doc_toc'].Text.createTextCursor()

def cmd_extract_toc(ooo_info):
    """
    On extrait la toc du document originale et on la colle dans le doc_toc
    """
    index = ooo_info['doc'].DocumentIndexes.getByIndex(0)
    cursor = ooo_info['cursor_toc']
    cursor.gotoEnd(False)
    ooo_info['doc_toc'].Text.insertTextContent(cursor, index, False)
    
def cmd_set_title(ooo_info,titre):
    """
    Set le titre du document (equivalent a fichier->pp)
    du template ouvert
    """
    ooo_info['doc'].DocumentInfo.Title = u'%s'%titre
    ooo_info['doc_toc'].DocumentInfo.Title = u'Sommaire - %s'%titre

def cmd_add_niveau(ooo_info,level,str_content):
    """
    Ajoute un titre de niveau %level
    """
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


def cmd_add_detail(ooo_info,detail,value):
    """
    Ajoute un type de détails.
    """
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

def cmd_merge_file(ooo_info,file):
    """
    Ajoute a  l endroit du cursor l ensemble des documents present dans list_files
    """
    if os.path.isfile(file):
        cursor = ooo_info['cursor']
        try:
            fileUrl = systemPathToFileUrl(file)

            print "Appending %s" % fileUrl
            try:
                cursor.gotoEnd(False)
                #peut etre je l'ai mis une fois de trop.
                cursor.PageDescName="Standard"
                cursor.insertDocumentFromURL(fileUrl, ())
                cursor.PageDescName="Standard"
            except IOException, e:
                sys.stderr.write("Error during opening ( " + e.Message + ")\n")
            except IllegalArgumentException, e:
                sys.stderr.write("The url is invalid ( " + e.Message + ")\n")

        except IOException, e:
            sys.stderr.write( "Error during opening: " + e.Message + "\n" )
        except UnoException, e:
            sys.stderr.write( "Error ("+repr(e.__class__)+") during conversion:" + 
                    e.Message + "\n" )
    else:
        raise IOException



def cmd_save_as(ooo_info,doc,dest_file,format):
    """
    sauvegarde le document courant.
    Le format correspond au format natif ou au format du premier document
    A verifier
    """
    from unohelper import systemPathToFileUrl
    dest_url = systemPathToFileUrl(dest_file)
    print "save as %s from %s"%(format,dest_file)
    
    if format == 'pdf':
        pp_filter = PropertyValue()
        pp_filter.Name = "FilterName"
        pp_filter.Value = "writer_pdf_Export"
        outprop = (pp_filter, PropertyValue( "Overwrite" , 0, True , 0 ),)
        doc.storeToURL(dest_url, outprop)
    else:
        #pp_filter = PropertyValue()
        #pp_filter.Name = "FilterName"
        #pp_filter.Value = "MS Word 97"
        #outprop = (pp_filter,)
        doc.storeAsURL(dest_url, ())



def cmd_refresh_toc(ooo_info):
    """
    Si une TOC est presente, elle est rafraichie
    """
    #list_names = ooo_info['doc'].DocumentIndexes.getElementNames()
    #co = ooo_info['doc'].DocumentIndexes.getCount()
    index = ooo_info['doc'].DocumentIndexes.getByIndex(0)
    index.update()

def insert_sautdepage(ooo_info):
    """
    Insert un saut de page
    """
    print 'saut de page'
    ooo_info['cursor'].gotoEnd(False)
    ooo_info['cursor'].gotoEndOfSentence(False)
    ooo_info['cursor'].BreakType = PAGE_AFTER
    ooo_info['doc'].Text.insertControlCharacter(ooo_info['cursor'], PARAGRAPH_BREAK, False)
    ooo_info['cursor'].PageDescName="Standard"
    #TEST
    #ooo_info['cursor'].gotoEnd(False)
    #page_styles = ooo_info['doc'].StyleFamilies.getByName("PageStyles")
    #mapage_style = page_styles.getByName("Standard")
    #mapage_style.setPropertyValue('FooterIsOn',True)
    #cursor2 = mapage_style.FooterText.createTextCursor()
    #mapage_style.FooterText.insertString(cursor2,'test',False)

def execute_cmd(ooo_info,cmd_args,b_toc=False):
    """
    Cette methode est responsable de choisir la methode qui va bien sur la commande fournie
    open:/home/sit15/model.odt
    set_titre_recueil:Mon Titre
    add_niveau1:Mon Titre de niveau 1 
    merge_files:/home/sit15/toto.doc
    add_niveau1:Mon Titre de niveau 2
    add_niveau2:Mon Titre de niveau 2
    save:dest_file
    
    b_toc : mode toc ou non
    """
    cmd = cmd_args.split(':')[0]
    args = cmd_args.split(':')[1]
    
    if cmd == "add_detail":
        detail = args.split(',')[0]
        value = args.split(',')[1]
        cmd_add_detail(ooo_info,detail,value)
    if cmd == "merge_file":
        if os.path.isfile(args):
            cmd_merge_file(ooo_info,args)
        else:
            print "merge_file argument invalide: %s"%args

    if cmd.startswith('add_niveau'):
        if bool(args):
            level = int(cmd.replace('add_niveau',''))
            cmd_add_niveau(ooo_info,level,args)


    if cmd == 'open':
        if os.path.isfile(args):
            cmd_open(ooo_info,args)
        else:
            print "open argument invalide: %s"%args

    if cmd == "save":
        #if os.path.isfile(args):
        cmd_save_as(ooo_info,ooo_info['doc'],args,'word')

    if cmd == 'save_pdf':
        cmd_save_as(ooo_info,ooo_info['doc'],args,'pdf')

    if cmd == 'set_titre':
        if bool(args):
            cmd_set_title(ooo_info,args)

    if cmd == 'insert_sautdepage':
        insert_sautdepage(ooo_info)

    if cmd == 'refresh_toc':
        cmd_refresh_toc(ooo_info)

    #la toc:
    if cmd == 'open_toc':
        cmd_open_toc(ooo_info,args)

    #if cmd == 'extract_toc':
    #    cmd_extract_toc(ooo_info)

    if cmd == 'save_toc':
        cmd_save_as(ooo_info,ooo_info['doc_toc'],args,'word')

    if cmd == 'save_toc_pdf':
        cmd_save_as(ooo_info,ooo_info['doc_toc'],args,'pdf')


#################################################################

#                       SEQUENCE

#################################################################

import uno

def ooo_connect():
    """
    Connection to open office server.
    Fill a dictionnary and return it
    """
    # get the uno component context from the PyUNO runtime
    localContext = uno.getComponentContext()

    # create the UnoUrlResolver
    resolver = localContext.ServiceManager.createInstanceWithContext("com.sun.star.bridge.UnoUrlResolver", localContext )

    # connect to the running office
    try:
        ctx = resolver.resolve("uno:socket,host=localhost,port=%s;urp;StarOffice.ComponentContext"%(options.port))
    except:
        raise "impossible de se connecter au serveur openoffice"

    smgr = ctx.ServiceManager

    # get the central desktop object
    desktop = smgr.createInstanceWithContext("com.sun.star.frame.Desktop",ctx)
    d = dict()
    d['ctx'] = ctx
    d['smgr'] = smgr
    d['doc'] = None
    d['desktop'] = desktop
    return d


#################################################################
#       / /     EN TETE
#################################################################

#les imports qui vont bien
from unohelper import systemPathToFileUrl, absolutize
from com.sun.star.beans import PropertyValue
from com.sun.star.style.BreakType import PAGE_BEFORE, PAGE_AFTER, PAGE_BOTH, NONE
from com.sun.star.uno import Exception as UnoException, RuntimeException
from com.sun.star.connection import NoConnectException
from com.sun.star.lang import IllegalArgumentException
from com.sun.star.io import IOException
from com.sun.star.text.ControlCharacter import PARAGRAPH_BREAK 

#os.system("oowriter -accept='socket,host=localhost,port=2002;urp;StarOffice.Service.Manager'")
#parse arguments and connect to ooo server:
list_cmd = parse_seq(options.seq)
ooo_info = ooo_connect()
#generation du recueil doc et pdf
for cmd in list_cmd:
    execute_cmd(ooo_info,cmd)
if ooo_info:
    ooo_info['doc'].close(False)
    ooo_info['doc_toc'].close(False)
else:
    raise 'problem de connexion au serveur OOo2'
