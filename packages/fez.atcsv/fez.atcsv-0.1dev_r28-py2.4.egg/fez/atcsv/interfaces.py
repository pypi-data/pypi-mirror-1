from zope import schema
from zope.interface import Interface

from zope.app.container.constraints import contains
from zope.app.container.constraints import containers

from fez.atcsv import atcsvMessageFactory as _

class ICSVImport(Interface):

    def do_import(portal_type, delimiter, file_path=None, fp=None):
        """
        Import the CSV
        """