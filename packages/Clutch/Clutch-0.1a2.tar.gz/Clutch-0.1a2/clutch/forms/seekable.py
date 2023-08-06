
class SeekableError(Exception):
    pass

class UniqueKeyError(SeekableError):
    pass

class SeekableStorage(object):

    def __init__(self):
        self.objects = {}
        self.keys = []
        self.cursor_pos = -1

    def _find_key_position(self, key):
        try:
            return self.keys.index(key)
        except ValueError, e:
            return None

    def add_item(self, key, value):
        if key in self.keys:
            raise UniqueKeyError("%s is already stored, update values using dict-like access" % key)

        self.objects[key] = value

        if self.cursor_pos == -1:
            self.keys.append(key)
        else:
            self.keys.insert(self.cursor_pos, key)
            self.cursor_pos += 1

    def update(self, store):
        if not isinstance(store, SeekableStorage):
            raise TypeError
        for k, v in store:
            self.add_item(k, v)

    def seek_end(self):
        self.cursor_pos = -1

    def seek_start(self):
        self.cursor_pos = 0

    def seek_before(self, key):
        pos = self._find_key_position(key)
        if not pos:
            raise KeyError("Key '%s' does not exist" % key)
        self.cursor_pos = pos

    def seek_after(self, key):
        pos = self._find_key_position(key)
        if not pos:
            raise KeyError("Key '%s' does not exist" % key)
        self.cursor_pos = pos + 1

    def __getitem__(self, key):
        return self.objects[key]

    def __setitem__(self, key, value):
        if not key in self.keys:
            self.add_item(key, value)
        else:
            self.objects[key] = value

    def __delitem__(self, key):
        del self.objects[key]
        self.keys.remove(key)

    def __iter__(self):
        for k in self.keys:
            yield (k, self.objects[k])
