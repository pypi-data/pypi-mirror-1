from cStringIO import StringIO
from zope import component
from zope import interface
from zope import schema
from zope.schema.vocabulary import SimpleVocabulary
from z3c.form import field
from z3c.form import form
from z3c.form import button
from z3c.form import validator
from plone.app.z3cform.layout import wrap_form
from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage

from fez.atcsv.interfaces import ICSVImport

class ICSVImportForm(interface.Interface):
    
    portal_type = schema.Choice(
        title=u"Portal type",
        vocabulary="fez.atcsv.AddableContentTypesFactory"
    )
    
    delimiter = schema.TextLine(
        title=u"Delimiter", 
    )
    
    csv_file = schema.Bytes(title=u"CSV File")
    
class InvalidDelimiterError(schema.ValidationError):
    __doc__ = "Invalid delimiter, must be single character or \\t"
    
class DelimiterValidator(validator.SimpleFieldValidator):
    """
    Validate that the field has either only one character, or that the
    character is a tab.
    
    >>> d = DelimiterValidator(None, None, None, ICSVImportForm['delimiter'], None)
    >>> d.validate(u',')
    >>> d.validate(u'aa')
    Traceback (most recent call last):
    ...
    InvalidDelimiterError
    >>> d.validate(u'\\\\t')
    """
    def validate(self, value):
        super(DelimiterValidator, self).validate(value)
        if value not in ('\\t') and len(value) != 1:
            raise InvalidDelimiterError()
            
validator.WidgetValidatorDiscriminators(
    DelimiterValidator, 
    field=ICSVImportForm['delimiter']
    )
                        
class CSVImportForm(form.Form):
    fields = field.Fields(ICSVImportForm)
    ignoreContext = True
    ignoreRequest = True
    label = u"Import a CSV file"
    
    @button.buttonAndHandler(u"Save")
    def handleSave(self, action):
        data, errors = self.extractData()
        if errors:
            return
        if data['delimiter'] == '\\t':
            delimiter = '\t'
        else:
            delimiter = data['delimiter']
        fp = StringIO(data['csv_file'])
        importer = ICSVImport(self.context)
        count, success, failed = importer.do_import(
            data['portal_type'].getId(), 
            delimiter=delimiter, 
            fp=fp
            )
        status = IStatusMessage(self.request)
        status.addStatusMessage(u'%s records processed, %s successful' % (count, success), type='info')
        errors = []
        for record, exception in failed:
            message = ['Record failed: %s' % record]
            message.append('Error was: %s' % str(exception))
            errors.append('\n'.join(message))

        if errors:
            status.addStatusMessage('\n'.join(errors), type='error')
        self.request.RESPONSE.redirect(self.context.absolute_url())
        
CSVImport = wrap_form(CSVImportForm)