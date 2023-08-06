from zope import schema
from zope.interface import Interface

from zope.app.container.constraints import contains
from zope.app.container.constraints import containers

from fez.atcsv import atcsvMessageFactory as _

class ICSVImport(Interface):

    def do_import(portal_type, delimiter, file_path=None, fp=None):
        """
        Import the CSV
        
        delimiter - single-char delimiter to use
        
        file_path - path on the filesystem to load
        
        fp - file-like object to load
        
        You should specify either fp or file_path. Behaviour is 
        undefined if you specify both.        
        """