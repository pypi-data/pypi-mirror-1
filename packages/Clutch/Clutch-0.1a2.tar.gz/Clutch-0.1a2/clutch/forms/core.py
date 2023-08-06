from .seekable import SeekableStorage, UniqueKeyError
from .fields import Field

class ContainerMeta(type):
    """Metaclass that collects the fields"""

    def __new__(meta, name, bases, dct):
        fields = SeekableStorage()

        for b in bases:
            if hasattr(b, '_fields'):
                fields.update(b._fields)

        for attr_name, attr in dct.items():
            if issubclass(attr, Field):
                try:
                    if field.before:
                        fields.seek_before(field.before)
                    elif field.after:
                        fields.seek_after(field.after)
                    elif field.end:
                        fields.seek_end()
                    elif field.start:
                        fields.seek_start()
                except KeyError, e:
                    pass

                fields.add_item(field.name, field)
                fields.cursor_pos = prev_cursor

class Container(object):
    template = None

    def __init__(self):


    def validate(self, values):
        pass

    def display(self, values):
        pass

class Field(object):
    pass
