""" Support for internationalization (I18N is the usual abbreviation) 

The I18N class allows access to the data stored in the I18N CSV file.
The CSV file will have an arbitrary number of columns, the first being
the key by which localizable elements are identified. The subsequent 
columns are named according to ISO language conventions. Each language
has one and only one column (this should be checked!) Some values
may be missing and defaults provided. So something like this:

    key,en,vn
    dn1,The All Embracing Net of Views,Kinh Phạm võng
    dn2,The Fruits of Recluseship,,

This data is slurped up into memory along with the rest of the IMM.
At this point we ignore issues of performance and memory usage, but
I'm happy to change things as the design becomes more clear.

USAGE:

>>> from sc import I18N
>>> localizer = I18N.I18N()
>>> english = localizer.localize('dn1', 'en')
>>> print(english)
The All-embracing Net of Views

"""

import csv
import sc

from sc.util import ScCsvDialect

class I18N:
    def __init__(self):
        self.i18n_data = {}
        self.file_name = 'I18N.csv'

    # Open the CSV file containing our localizations
    # with & as used to make sure the file is unlocked
    # if an exception is thrown.
    def read_data(self):
        with (sc.table_dir / self.file_name).open('r',
              encoding='utf-8', newline='') as f:
            reader = csv.reader(f, dialect=ScCsvDialect)
            field_names = next(reader)

            # This gives us all the column headings
            for index, field_name in enumerate(field_names):
                print(str(index) + ' ' + field_name)

            # Each row may contain several translations
            # We need to pair each translation with its
            # language code specified in the first row
            for row in reader:
                if not any(row): # Drop entirely blank lines
                    continue
                if row[0].startswith('#'):
                    continue

                key = row[0]
                for index, translation in enumerate(row[1:]):
                    print(str(index) + ' ' + translation)
    
    # Add a language to which translations can be added.
    def add_language(self, language):
        self.i18n_data[language] = {}

    # Add a translation for a given key and language
    def add_translation(self, language, key, translation):
        self.i18n_data[language][key] = translation


