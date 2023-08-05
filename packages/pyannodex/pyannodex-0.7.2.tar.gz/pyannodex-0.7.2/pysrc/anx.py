from annodex import *
import copy
import urlparse, urllib2

class EndOfFile(Exception):
    pass

xml_header = '<?xml version="1.0" encoding="UTF-8"?>\n'
cmml_header = '<!DOCTYPE cmml SYSTEM "cmml.dtd">\n'

init_importers("*/*")

class Reader:
    class __event_generator:
        def __init__(self, anx, filter):
            self.anx = anx
            self.anx.anx.set_read_clip_callback(self.read_clip)
            self.anx.anx.set_read_raw_callback(self.read_raw)
            self.__filter = filter
            self.__clip = None

        def read_clip(self, anx, clip):
            clip["start"] = NPT(anx.tell_time())
            self.__object = clip

        def read_raw(self, buff, serialno, granulepos, happy):
            self.__object = (buff, serialno, granulepos)

        def __iter__(self):
            return self

        def next(self):
            while self.__object is None or not self.__filter(self.__object):
                try:
                    self.anx._readmore()
                except EndOfFile:
                    raise StopIteration
            ret = self.__object
            self.__object = None
            return ret

    def __init__(self, fn):
        # Test what fn is...
        protocol = urlparse.urlparse(fn)[0]
        if protocol:
            fn = urllib2.urlopen(fn)
        self.anx = Anx(fn, "r")
        self.anx.set_read_head_callback(self.__read_head)
        self.anx.set_read_stream_callback(self.__read_stream)
        self.tracks = self.anx.get_track_list()
        self.__props = {
            "head" : None,
            "timebase" : None,
            "utc" : None
            }
        self.__head = None
        self.__end_of_stream = 0
        def is_clip(x):
            return x.__class__ == Clip
        self.clips = self.__event_generator(self, is_clip)

    def __read_stream(self, anx, timebase, utc):
        self.__props["timebase"] = timebase
        self.__props["utc"] = utc

    def __read_head(self, anx, head):
        self.__props["head"] = head

    def _readmore(self):
        x = self.anx.read(1024)
        if x <= 0:
            raise EndOfFile

    def __getattr__(self, attr):
        if attr in self.__props:
            while self.__props[attr] is None:
                try:
                    self._readmore()
                except EndOfFile:
                    raise "Can't find %s" % attr
            return self.__props[attr]
        raise "NotFound"

    def _xml(self):
        out = ""
        out += xml_header
        out += cmml_header
        out += "<cmml>\n"
        out += "%s\n" % self.head._xml()
        for clip in self.clips:
            out += "%s\n" % clip._xml()
        out += "</cmml>\n"
        return out

    get_cmml = _xml


class Writer:
    def __init__(self, filename = None):
        self.anx = Anx(filename, "w")

    def import_file(self, *args, **kargs):
        self.anx.writer_import(*args, **kargs)

    def insert(self, *args, **kargs):
        self.anx.insert(*args, **kargs)

    def write(self, *args, **kargs):
        self.anx.write(*args, **kargs)
