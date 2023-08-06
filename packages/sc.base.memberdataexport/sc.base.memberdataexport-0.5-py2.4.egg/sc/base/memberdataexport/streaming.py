from ZPublisher.Iterators import IStreamIterator

class FileStreamer:
    """A mixin class which can be mixed in with a file or file-like class
    and implements an iterator that returns a fixed-sized sequence of bytes.
    """
    __implements__ = (IStreamIterator,)
    streamsize = 1<<16
    
    def __init__(self, file):
        self._file=file
    
    def __getattr__(self, name):
        if self.__dict__.has_key(name):
            return self.__dict__[name]
        
        return getattr(self.__dict__["_file"], name)
    
    def next(self):
        data = self._file.read(self.streamsize)
        if not data:
            raise StopIteration
        return data
    
    def __nonzero__(self):
        return bool(self._file)
    
    def __len__(self):
        cur_pos = self._file.tell()
        self._file.seek(0, 2)
        size = self._file.tell()
        self._file.seek(cur_pos, 0)
        
        return int(size)
    
