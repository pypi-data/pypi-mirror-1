class ListFile(object):

    def __init__(self, file_):
        super(ListFile, self).__init__()
        self.file = file_
        self.positions = []
        self.eof = 0
        self.step = 1
        self.lazy = True

    def __iter__(self):
        idx = 0
        while True:
            try:
                yield self[idx]
            except IndexError:
                break
            idx += 1

    def __len__(self):
        if not self.lazy:
            return len(self.positions)
            
        idx = len(self.positions)
        while True:
            try:
                self[idx]
            except IndexError:
                break
            idx += 1
        self.lazy = False
        return idx

    def __getitem__(self, key):
        if isinstance(key, slice):
            result = ListFile(self.file)
            if key.start < 0 or key.stop < 0:
                len(self)
                result.positions = self.positions[key]
                result.eof = self.eof
                result.lazy = False
            elif key.stop < len(self.positions):
                result.positions = self.positions[key]
                result.eof = self.eof
                result.lazy = False
            elif key.start < len(self.positions):
                result.positions = self.positions[
                    key.start:len(self.positions)-1:key.step]
                result.eof = self.eof
            return result
         
        if not self.lazy:
            self.file.seek(self.positions[key])
            return self.file.readline()

        if key < 0:
            # For negative indexes the whole file must be stepped
            # through anyways. Use len() to do so and then delegate to
            # the non-lazy version
            len(self)
            return self[key]

        idx = len(self.positions)-1
        if idx < key:
            self.file.seek(self.eof)
            idx += 1
            while idx < key:
                self.positions.append(self.file.tell())
                for step in xrange(self.step):
                    self.file.readline()
                idx += 1
            pos = self.file.tell()
            line = self.file.readline()
            self.eof = self.file.tell()
            if line == '':
                self.lazy = False
                raise IndexError('Reached EOF')
            self.positions.append(pos)
            return line

        else:
            self.file.seek(self.positions[key])
            return self.file.readline()

