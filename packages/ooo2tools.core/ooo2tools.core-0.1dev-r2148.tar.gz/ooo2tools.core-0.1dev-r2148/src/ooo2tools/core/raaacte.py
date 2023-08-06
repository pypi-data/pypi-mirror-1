# -*- coding: utf-8 *- 
#################################################################
#       EN TETE
#
#################################################################

"""
DOCUMENTATION

L'objectif de ce script est de générer un recueil
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

import os
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
    l = list()
    f = open(file_seq,'r')
    lines = str(f.read()).splitlines()
    for line in lines:
        if line is None:
            continue
        cmd = line.split(':')
        if len(cmd) == 2:
            l.append(line.decode("UTF-8"))
        else:
            print "cmd invalide :%s"%cmd
    return l


def cmd_open(ooo_info,syspath_doc):
    """
    ooo_info:
    {ctx:l objet, desktop: , ....}
    """
    url = systemPathToFileUrl(syspath_doc)
    #load as template:
    #pp_template = PropertyValue()
    #pp_template.Name  = "AsTemplate"
    #pp_template.Value = True
    pp_hidden = PropertyValue()
    pp_hidden.Name = "Hidden"
    pp_hidden.Value = True
    load_pp = ()
    ooo_info['doc'] = ooo_info['desktop'].loadComponentFromURL(url,"_blank",0,load_pp)
    ooo_info['cursor'] = ooo_info['doc'].Text.createTextCursor()


def cmd_set_title(ooo_info,titre):
    """
    Set le titre du document (equivalent a fichier->pp)
    du template ouvert
    """
    ooo_info['doc'].DocumentInfo.Title = '%s'%titre


def cmd_save_as(ooo_info,doc,dest_file,format):
    """
    sauvegarde le document courant.
    Le format correspond au format natif ou au format du premier document
    A verifier
    """
    from unohelper import systemPathToFileUrl
    dest_url = systemPathToFileUrl(dest_file)
    print "save as %s from %s"%(format,dest_file)
    pp_filter = PropertyValue()
    pp_filter.Name = "FilterName"
    if format == 'pdf':
        pp_filter.Value = "writer_pdf_Export"
        outprop = (pp_filter, PropertyValue( "Overwrite" , 0, True , 0 ),)
        doc.storeToURL(dest_url, outprop)

    elif format == 'txt':
        pp_filter.Value = "TEXT"
        outprop = (pp_filter, )
        doc.storeToURL(dest_url, outprop)

    elif format == 'html':
        pp_filter.Value = "HTML (StarWriter)"
        outprop = (pp_filter,)
        doc.storeToURL(dest_url, outprop)

    else:
        pp_filter.Value = "MS Word 97"
        outprop = (pp_filter,)
        doc.storeAsURL(dest_url, outprop)



def execute_cmd(ooo_info,cmd_args,b_toc=False):
    """
    """
    cmd = cmd_args.split(':')[0]
    args = cmd_args.split(':')[1]
    if os.path.isfile(args):
        print "execute cmd %s:%s a detecter un fichier en argument"%(cmd,args)
    if cmd == 'open':
        cmd_open(ooo_info,args)
    if cmd == 'save':
        cmd_save_as(ooo_info,ooo_info['doc'],args,'word')
    if cmd == 'save_pdf':
        cmd_save_as(ooo_info,ooo_info['doc'],args,'pdf')
    if cmd == 'save_txt':
        cmd_save_as(ooo_info,ooo_info['doc'],args,'txt')
    if cmd == 'save_html':
        cmd_save_as(ooo_info,ooo_info['doc'],args,'html')

    if cmd == 'set_titre':
        if bool(args):
            cmd_set_title(ooo_info,args)


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
if ooo_info:
    #generation du recueil doc et pdf
    for cmd in list_cmd:
        execute_cmd(ooo_info,cmd)

    ooo_info['doc'].close(False)
else:
    raise 'problem de connexion au serveur OOo2'
