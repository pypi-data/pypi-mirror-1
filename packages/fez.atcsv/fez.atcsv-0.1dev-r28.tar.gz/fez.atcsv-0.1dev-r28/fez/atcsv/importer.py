import csv
from ZODB.POSException import ConflictError
from zope.interface import implements
from zope.component import adapts
from Products.CMFCore.interfaces import IFolderish
from fez.atcsv.interfaces import ICSVImport
minimise_every = 100

class CSVImport(object):

    implements(ICSVImport)
    adapts(IFolderish)
    
    def __init__(self, context):
        self.context = context
    
    def do_import(self, portal_type, delimiter, file_path=None, fp=None):
        file_opened = False
        if file_path is not None:
            fp = open(file_path, 'r')
            file_opened = True
        reader = csv.DictReader(fp, delimiter=delimiter)
        count = 0
        success = 0
        failed_records = []
        
        for record in reader:
            if count > 0 and count % minimise_every == 0:
                self.context._p_jar.cacheMinimize()
            try:
                ob_id = self.context.generateUniqueId(portal_type)
                self.context.invokeFactory(type_name=portal_type, id=ob_id)
                ob = getattr(self.context, ob_id)
                ob_schema = ob.Schema()
                for field in record.keys():
                    if ob_schema.has_key(field):
                        mutator = ob_schema[field].getMutator(ob)
                        mutator(record[field])
                
                if ob._at_rename_after_creation:
                    ob._renameAfterCreation(check_auto_id=False)
                ob.reindexObject()
                success += 1
            except ConflictError:
                raise
            except Exception, e:
                failed_records.append((record, e))
            count += 1
        if file_opened:
            f.close()
        return count, success, failed_records