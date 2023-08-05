import copy

class __AnxXML:
    _names = []
    _tagname = None
    def __getattr__(self, key):
        if key in self._attrs:
            return self._attrs[key]
        raise AttributeError

    def __getitem__(self, key):
        return self._attrs[key]

    def __setitem__(self, key, value):
        self._attrs[key] = value

    def _xml(self, depth=0):
        out = " " * depth + "<%s" % (self._tagname)
        full_close = 0
        new_line = 0

        for key, value in self._attrs.items():
            if value is None:
                continue
            out += ' %s="%s"' % (key, value)
        
        if hasattr(self, "cdata"):
            full_close = 1
            out += ">%s" % self.cdata
        else:
            for key in self._names:
                each = getattr(self, key)
                if each is None:
                    continue
                if not new_line:
                    out += ">\n"
                    full_close = 1
                    new_line = 1
                if type(each) != type([]):
                    out += "%s\n" % each._xml(depth+1)
                else:
                    for obj in each:
                        out += "  %s\n" % (obj._xml())
        if full_close:
            if new_line:
                out += " " * depth + "</%s>" % (self._tagname)
            else:
                out += "</%s>" % (self._tagname)
        else:
            out += " />"
        return out

    get_cmml = _xml

    def __str__(self):
        if hasattr(self, "cdata") and len(self._names) == 0:
            return self.cdata
        else:
            return "<%s instance at 0x%s>" %  (self.__class__.__name__, id(self))


class NPT:
    def __init__(self, time):
        self.time = time

    def __str__(self):
        mm, ss = divmod(self.time, 60)
        hh, mm = divmod(mm, 60)
        return "npt:%d:%02d:%06.3f" % (hh, mm, ss)

class Title(__AnxXML):
    _tagname = "title"
    
    def __init__(self, attrs = {}, data = None):
        self._attrs = copy.copy(attrs)
        self.cdata = data

class Base(__AnxXML):
    _tagname = "base"
    def __init__(self, id = None, href = None):
        self._attrs = {}
        self["id"] = id
        self["href"] = href

class Anchor(__AnxXML):
    _tagname = "a"
    def __init__(self, id = None, lang = None, dir = None, anchor_class = None, href = None,
                 text = None):
        self._attrs = {}
        self["id"] = id
        self["lang"] = lang
        self["dir"] = dir
        self["class"] = anchor_class
        self["href"] = href
        self.cdata = text

class Img(__AnxXML):
    _tagname = "img"
    def __init__(self, id = None, lang = None, dir = None, src = None, alt = None):
        self._attrs = {}
        self["id"] = id
        self["lang"] = lang
        self["dir"] = dir
        self["src"] = src
        self["alt"] = alt

class Head(__AnxXML):
    _names = ["title", "meta"]
    _tagname = "head"
    def __init__(self, attrs = {}, title = None, meta = []):
        self._attrs = copy.copy(attrs)
        self.meta = meta
        self.title = title

class Desc(__AnxXML):
    _tagname = "desc"
    def __init__(self, id = None, lang = None, dir = None, desc = None):
        self._attrs = {}
        self["id"] = id
        self["lang"] = lang
        self["desc"] = dir
        self.cdata = desc

class Clip(__AnxXML):
    _names = ["anchor", "img", "desc", "meta"]
    _tagname = "clip"
    def __init__(self, start = None, 
                 id = None, lang = None, dir = None,
                 track = None, end = None,
                 anchor = None, img = None, desc = None, meta = []):
        self._attrs = {}
        self["id"] = id
        self["start"] = start
        self["end"] = end
        self["lang"] = lang
        self["dir"] = dir
        self["track"] = track

        self.anchor = anchor
        self.img = img
        self.desc = desc
        self.meta = meta

class Meta(__AnxXML):
    _tagname = "meta"
    def __init__(self, id = None, lang = None, dir = None, name = None,
                 content = None, scheme = None):
        self._attrs = {}
        self["id"] = id
        self["lang"] = lang
        self["dir"] = dir
        self["name"] = name
        self["content"] = content
        self["scheme"] = scheme

class Track:
    def __getitem__(self, key):
        return self._attrs[key]

    def __setitem__(self, key, value):
        self._attrs[key] = value

    def __init__(self, serialno = None, id = None, content_type = None,
                 nr_header_packets = None, granule_rate_n = None,
                 granule_rate_d = None, preroll = None,
                 granuleshift = None):
        self._attrs = {}
        self["serialno"] = serialno
        self["id"] = id
        self["content_type"] = content_type
        self["nr_header_packets"] = nr_header_packets
        self["granule_rate_n"] = granule_rate_n
        self["granule_rate_d"] = granule_rate_d
        self["preroll"] = preroll
        self["granuleshift"] = granuleshift
