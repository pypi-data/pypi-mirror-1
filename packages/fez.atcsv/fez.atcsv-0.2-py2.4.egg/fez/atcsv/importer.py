import csv
import transaction
import logging
from datetime import datetime
from ZODB.POSException import ConflictError
from zope.interface import implements
from zope.component import adapts
from Products.CMFCore.interfaces import IFolderish
from Products.CMFCore.utils import getToolByName
from fez.atcsv.interfaces import ICSVImport
from Products.BTreeFolder2.BTreeFolder2 import BTreeFolder2Base

logger = logging.getLogger('fez.atcsv.CSVImport')

minimise_every = 2000
log_every = 100

class CSVImport(object):

    implements(ICSVImport)
    adapts(IFolderish)
    
    type_info = None
    
    def __init__(self, context):
        self.context = context
        self.types_tool = getToolByName(context, 'portal_types')
    
    def do_import(self, portal_type, delimiter, file_path=None, fp=None):
        logger.info('do_import: portal_type %s, delimiter %s, file_path %s, fp is %s' % (portal_type,
                      delimiter, file_path, fp is None and 'None' or 'not None'))
        file_opened = False
        if file_path is not None:
            fp = open(file_path, 'r')
            file_opened = True
            
        # CSV module doesn't like unicode delimiters
        delimiter = delimiter.encode('ASCII', 'ignore')
        reader = csv.DictReader(fp, delimiter=delimiter)
        count = 0
        success = 0
        failed_records = []
        schema = None
        
        # Look up the type info object for later
        self.type_info = self.types_tool.getTypeInfo(portal_type)
        if self.type_info is None:
            raise ValueError('No such content type: %s' % portal_type)
            
        # If we don't think we're importing into a BTree-based folder, log a message.
        if not isinstance(self.context, BTreeFolder2Base):
            logger.info("It appears that the container is not BTree-based (is not a Large Plone Folder)."
                        " If this is the case, then imports may slow down as more reocrds are added.")
        
        logger.info("Starting import")
        for record in reader:
            if count % log_every == 0:
                logger.info("Processed %d records, %d success, %d fails" % (count, success, len(failed_records)))
            if count > 0 and count % minimise_every == 0:
                logger.info("Processed %d records, minimising ZODB cache" % count)
                self.context._p_jar.cacheMinimize()
            try:
                ob_id = self.context.generateUniqueId(portal_type)
                
                # Rather than doing a self.context.invokeFactory(), use the 
                # type info construction methods directly. This avoids an
                # unnecessary reindexObject() call.
                ob = self.type_info._constructInstance(self.context, ob_id)
                                
                if schema is None:
                    schema = ob.Schema()
                for field in record.keys():
                    if schema.has_key(field):
                        mutator = schema[field].getMutator(ob)
                        mutator(record[field], schema=schema)
                
                if ob._at_rename_after_creation:
                    ob._renameAfterCreation(check_auto_id=False)
                
                # We can now index and fire events and stuff
                self.type_info._finishConstruction(ob)
                success += 1
            except ConflictError:
                raise
            except Exception, e:
                logger.warn('%s processing %s' % (str(record), str(e)))
                failed_records.append((record, e))
            count += 1
            
        logger.info("Import complete")
        if file_opened:
            f.close()
        return count, success, failed_records
        