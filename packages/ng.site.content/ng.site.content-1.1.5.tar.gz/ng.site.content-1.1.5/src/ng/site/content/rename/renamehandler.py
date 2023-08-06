### -*- coding: utf-8 -*- #############################################
#######################################################################
"""handleAdded, handleModified and handleRemoved scripts for the Zope 3
based ng.app.objectqueue package

$Id: renamehandler.py 53390 2009-07-08 11:01:43Z cray $
"""
__author__  = "Yegor Shershnev, 2008"
__license__ = "GPL"
__version__ = "$Revision: 53390 $"

from zope.interface import Interface
from zope.interface import implements,implementedBy
from zope.proxy import removeAllProxies
from renameexception import RenameException

#from ng.content.article.interfaces import IDocShort

from zope.copypastemove.interfaces import IContainerItemRenamer
from zope.app.container.interfaces import IContained
from zope.app.container.interfaces import INameChooser

def renameHandler(ob, event) :

    print ob
    parent = IContained(ob).__parent__
    
    title = INameChooser(parent).chooseName(None,ob)
    name = IContained(ob).__name__
    print name, title
    if name != title :
        print "Raise!"
        IContainerItemRenamer(parent).renameItem(name,title)
            
        raise RenameException(ob)
        