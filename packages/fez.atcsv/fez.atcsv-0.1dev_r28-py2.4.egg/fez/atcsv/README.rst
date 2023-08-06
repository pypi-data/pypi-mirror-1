Introduction
============

fez.atcsv is a lightweight product for importing CSV files into Plone sites.
Unlike other implementations, it leaves no persistent data in the database
aside from imported content.

To use, install the product onto your pythonpath using easy_install or pip:

  easy_install fez.atcsv
  
or

  pip install fez.atcsv
  
  
You should then add 'fez.atcsv' to your eggs = and zcml = sections in your buildout.
Restart Zope, and you should see AT CSV in your quickinstaller page. Install it,
and you should see a 'CSV Import' tab on all folder-like content objects.

The CSV you upload *must* have a first line of titles, and these titles *must* correspond
to the Archetype field names of the type you're importing. So, if you had an Archtype content
type that had a schema like this:

    atapi.TextField(
        'Title',
        searchable = 1,
        required = 0,
        storage = atapi.AnnotationStorage(),
        widget = atapi.StringWidget(label='Title'),
        ),
       
    atapi.TextField(
        'Colour',
        searchable = 1,
        required = 0,
        storage = atapi.AnnotationStorage(),
        widget = atapi.StringWidget(label='Colour'),
        ),
        
Then a valid CSV might look like this:

    "Title","Colour","Size"
    "Apple", "Green", "small"
    "Banana", "Red", "Medium"

Note that in this case, the 'size' column won't be imported as it's not in the AT schema.

Further, notice that no validation is run on the imported data. It is assumed that
the data will be clean. (Validation may be added at a later point.)

Be aware that large file uploads may take some time.


