#sednaobject.py

"""
sednaobject has a few classes: SednaXQuery, SednaContainer, and
SednaObjectifiedElement, that abstract fetches and updates for a Sedna server.

SednaXQuery is for readonly query results.  It provides list-like behavior.
Access query result items by index, slice, or iteration.  It's for operations
like working with the results of a SELECT in SQL.

SednaContainer provides a read-write elementtree-like interface to a single
element and its children.  It provides mutable access to children by index.
It's for operations like working with a table or view in SQL.

SednaObjectifiedElement is a thin wrapper around lxml.objectify for a single
(object-like) element.  It's for operations like working with a record in SQL.
It you do not want to use lxml.objectify, it provides a pattern for doing
something similar with your preferred parser.

sednaobject requires lxml.  Items based on lxml Element are fully supported, so
functionality provided by lxml.etree and lxml.objectify may be used for item
creation and editing.  Plain-text XML may also be used.

sednaobject is transparent with regard to XML namespaces.  Namespace handling
is something your application and the Sedna server do.
"""


from lxml import objectify
from lxml.etree import _Element, tostring,fromstring, XMLSyntaxError
from lxml.doctestcompare import norm_whitespace
from dbapiexceptions import DatabaseError

def checkobj(obj,wf=True):
    """
    local converter.  everything sent to the server needs to be a string

    if wf is True, we also check for well-formed-ness...
    """
    if isinstance(obj,_Element):
        item = tostring(obj,encoding=unicode)
    elif isinstance(obj,SednaContainer):
        item = str(obj)
    else:
        if wf:
            try:
                t = fromstring(obj)
            except XMLSyntaxError:
                raise ValueError("Item is not well-formed.")
        item = obj
    return item

class SednaXQuery(object):
    """class for read-only xpath queries.  Makes the query result sequence-like.
      slices and stuff...
    """
    def __init__(self,cursor,path, parser=None):
        self.cursor = cursor
        while path.endswith('/'):
            path = path[:-1]
        self.path = path
        self._count = None
        self._attrib = None
        self.parser = parser

    def count(self):
        """
        return a count of the items returned by the query
        """
        if self._count is not None:
            return self._count
        q = u'let $i := %s' % (self.path)
        q += u' return <i><c>{count($i)}</c></i>'
        s = self.cursor.execute(q)
        f = objectify.fromstring(s.value)
        self._count = int(f.c)
        return self._count

    def xpath(self,path):
        """
        Send another query to the server for the current document.
        """
        if path.startswith('/'):
            base = self.path.split('/')[0]
            return SednaXQuery(self.cursor,base+path)
        else:
            return SednaXQuery(self.cursor,self.path + '/' + path)

    def _localKey(self,key):
        """
        convert 0-based indices to 1-based for use in generated queries,
        accounting for negative indices
        """
        local = key+1
        count = self.count()
        if local < 1:
            local = count + local
        if local > count or local < 1:
            raise IndexError('list index out of range')
        return local

    def __getitem__(self,index):
        """
        retrieve the item at index
        """
        if index < 0:
            index += self.count()
        item = self[index:index+1][0]
        return item

    def index0(self,obj):
        """
        get the (0-based) index of the item in the list

        This uses a brute-force technique, and may not be suitable for large
        items in long lists
        """
        item = checkobj(obj, wf=False)
        normed = norm_whitespace(item)
        q = u'declare namespace se = "http://www.modis.ispras.ru/sedna";'
        q += 'declare option se:output "indent=no";'
        q += u' %s' % self.path
        s = self.cursor.execute(q)
        count = -1
        found = False
        for k in s:
            count += 1
            if norm_whitespace(k) == normed:
                found = True
                break
        if found:
            return count
        else:
            raise ValueError('item not in list')

    def index(self,obj):
        """
        get the (0-based) index of the item in the list
        """
        item = checkobj(obj, wf=False)
        normed = norm_whitespace(item)
        q = u'declare namespace se = "http://www.modis.ispras.ru/sedna";'
        q += 'declare option se:output "indent=no";'
        q += u' let $p := %s ,' % self.path
        q += u' $i := %s ' % item
        q += u' return <i>{index-of($p,$i)}</i>'
        try:
            s = self.cursor.execute(q)
        except DatabaseError:
            # this is probably an XQuery expression, not an XPath, so
            # do brute-force evaluation
            return self.index0(obj)
        if s:
            y = fromstring(s.value)
            if y.text is not None:
                val = int(y.text)
                return val-1
        raise ValueError('item not in list')

    def xenumerate(self):
        for idx,value in enumerate(self):
            yield idx + 1, value

    def xindex(self,obj):
        return self.index(obj) + 1

    def __contains__(self,obj):
        item = checkobj(obj, wf=False)
        wf = True
        try:
            t = fromstring(item)
        except XMLSyntaxError:
            wf = False
        if wf:
            q = u' for $i in %s ' % (self.path,)
            q += u' where $i = %s ' % item
            q += u' return $i'
            s = self.cursor.execute(q)
        else:
            q = u' for $i in %s ' % (self.path,)
            q += u' where $i = %(item)s '
            q += u' return $i'
            s = self.cursor.execute(q,{'item':item})
        j = s.value
        if j:
            return True
        return False

    def __getslice__(self,start,stop):
        #start,stop,step = key.indices(self.count())
        #if step <> 1:
        #    raise NotImplementedError('cannot do steps')
        rlen = stop - start
        rstart = self._localKey(start)
        q =  u'declare namespace se = "http://www.modis.ispras.ru/sedna";'
        q += u'declare option se:output "indent=no";'
        q += u'for $i in subsequence(%s,%s,%s) ' % (self.path,rstart,rlen)
        q += u'return $i'
        s = list(self.cursor.execute(q))
        if self.parser:
            return [self.parser(item) for item in s]
        return s

    def _iterparse(self,s):
        for item in s:
            i = self.parser(item)
            yield i

    def __iter__(self):
        q = u' %s' % self.path
        s = self.cursor.execute(q)
        if self.parser:
            return self._iterparse(s)
        return s

    def __str__(self):
        q = u'%s' % self.path
        s = self.cursor.execute(q)
        return s.value

    def __len__(self):
        return self.count()


class SednaContainer(SednaXQuery):
    """a class to emulate read-write ElementTree functionality on an element in
       the Sedna database.

    initialize with a cursor and a path to the element.

    """
    def __init__(self,cursor,path,parser=None, check=True):
        """
        init the class with cursor and path
        set check to false to eliminate a server request, but only if you
        know what you are doing...
        """
        super(SednaContainer,self).__init__(cursor,path, parser)
        if check:
            self._checkElement()

    def _checkElement(self):
        """
        do a check to see that this is a single element
        """
        q = u'let $i := %s' % (self.path,)
        q += u' return <i><c>{count($i)}</c></i>'
        s = self.cursor.execute(q)
        f = objectify.fromstring(s.value)
        c = int(f.c)
        if c == 1:
            return
        elif c == 0:
            raise LookupError(
            'The path did not return an element. ([0] might need to be [1]?)')
        else:
            raise ValueError(
        'Cannot init SednaContainer with multiple elements.')

    def getparent(self):
        """
        return parent as a SednaContainer or None if at root
        """
        c = self.path + '/..'
        t = SednaContainer(self.cursor,c,self.parser, check=False)
        if t.tag is None:
            return None
        return t

    parent = property(getparent)

    def count(self,tag=None):
        if self._count is not None and tag is None:
            return self._count
        if tag:
            pt = tag
        else:
            pt = '*'
        q = u'let $i := %s/%s' % (self.path,pt)
        q += u' return <i><c>{count($i)}</c></i>'
        s = self.cursor.execute(q)
        f = objectify.fromstring(s.value)
        self._count = int(f.c)
        return self._count

    def append(self,obj):
        item = checkobj(obj)
        if self.count() > 0:
            q = u'update insert %s following %s/*[last()]' % (item,self.path)
        else:
            q = u'update insert %s into %s' % (item,self.path)
        self.cursor.execute(q)
        self._count = None

    def __contains__(self,obj):
        try:
            s = self.index(obj)
            return True
        except ValueError:
            return False

    def index(self,obj):
        """
        get the first (0-based) index of the item in the list
        """
        item = checkobj(obj)
        normed = norm_whitespace(item)
        q = u'declare namespace se = "http://www.modis.ispras.ru/sedna";'
        q += 'declare option se:output "indent=no";'
        q += u' let $p := %s/* ,' % self.path
        q += u' $i := %s ' % item
        q += u' return <i>{index-of($p,$i)}</i>'
        try:
            s = self.cursor.execute(q)
        except DatabaseError:
            raise ValueError('item not in list')
        if s:
            y = fromstring(s.value)
            if y.text is not None:
                val = int(y.text.split()[0])
                return val-1
        raise ValueError('item not in list')

    def extend(self,items):
        for item in items:
            self.append(item)
        self._count = None

    def insert(self,key,item):
        local = key+1
        count = self.count()
        self._count = None
        if local < 1:
            local = count + local
        if local > count:
            self.append(item)
            return
        elif local < 1:
            local = 1
        item = checkobj(item)
        if count > 0:
            q = u'update insert %s preceding %s/*[%s]' % (item,self.path,local)
            self.cursor.execute(q)
        else:
            self.append(item)

    def remove(self,obj):
        index = self.index(obj) + 1
        q = u'update delete %s/*[%s]' % (self.path,index)
        self.cursor.execute(q)
        self._count = None

    def __iter__(self):
        q = u' %s/*' % self.path
        s = self.cursor.execute(q)
        if self.parser:
            return self._iterparse(s)
        return s

    def __delitem__(self,key):
        local = self._localKey(key)
        q = u'update delete %s/*[%s]' % (self.path,local)
        self.cursor.execute(q)
        self._count = None

    @property
    def tag(self):
        q = u"let $i := %s return <t>{$i/name()}</t>" % self.path
        t1 = self.cursor.execute(q)
        r = fromstring(t1.value)
        return r.text
        #t = self.path.split('/')[-1]
        #t1 = t.split('[')[0]
        #return t1.strip()

    def __getitem__(self,key):
        """we get the item at index inside the element"""
        if isinstance(key,slice):
            start,stop,step = key.indices(self.count())
            if step <> 1:
                raise NotImplementedError('cannot do steps')
            return self.__getslice__(start,stop)
        local = self._localKey(key)
        q = u'declare namespace se = "http://www.modis.ispras.ru/sedna";'
        q += 'declare option se:output "indent=no";'
        q += u' %s/*[%s]' % (self.path,local)
        s = self.cursor.execute(q)
        z = self.cursor.fetchone()
        if self.parser:
            return self.parser(z)
        return z

    def __setitem__(self,key,value):
        item = checkobj(value)
        local = self._localKey(key)
        q = u'update replace $i in %s/*[%s] ' % (self.path,local)
        q += ' with %s' % item
        s = self.cursor.execute(q)

    def replace(self,obj):
        """ replace item at self.path with the object"""
        item = checkobj(obj)
        q = u'update replace $i in %s ' % (self.path,)
        q += ' with %s' % (item,)
        self.cursor.execute(q)
        self._attrib = None
        self._count = None

    def __getslice__(self,start,stop):
        #start,stop,step = key.indices(self.count())
        #if step <> 1:
        #    raise NotImplementedError('cannot do steps')
        rlen = stop - start
        rstart = self._localKey(start)
        q = u'declare namespace se = "http://www.modis.ispras.ru/sedna";'
        q += 'declare option se:output "indent=no";'
        q += u'for $i in subsequence(%s/*,%s,%s) ' % (self.path,rstart,rlen)
        q += 'return $i'
        s = list(self.cursor.execute(q))
        if self.parser:
            return [self.parser(item) for item in s]
        return s

#Element attribute access

    @property
    def attrib(self):
        """get the attributes dict for the element

        do not directly modify this. use set('attr','value')
        If you need to remove an atribute, str -> edit -> replace is the best
        option.
        """
        if self._attrib is not None:
            return self._attrib
        q = u' for $i in %s/@* ' % (self.path)
        q += u' let $nm := name($i), '
        q += u' $vl:= data($i)'
        q += u' return <d><k>{$nm}</k><v>{$vl}</v></d>'
        s = self.cursor.execute(q)
        attrs = {}
        for k in s:
            t = objectify.fromstring(k)
            attrs[str(t.k)] = str(t.v)
        self._attrib = attrs
        return self._attrib

    def set(self,key,value):
        q = u'%s' % self.path
        s = self.cursor.execute(q)
        fromdb = self.cursor.fetchone()
        item = objectify.fromstring(fromdb)
        item.set(key,value)
        self.replace(item)

    def get(self,key):
        """
        obtain the value of an attribute
        """
        q = u'%s/data(@%s)' % (self.path,key)
        s = self.cursor.execute(q)
        t = s.value.strip()
        if t:
            return t
        else:
            raise KeyError("KeyError %s" % key)

    def keys(self):
        """ get the keys of the attributes
        """
        return self.attrib.keys()

    def values(self):
        return self.attrib.values()

    def items(self):
        return self.attrib.items()

class SednaObjectifiedElement(object):
    """
       An abstraction of a single Element and its children, objectified with
       lxml.objectify.

       init with the path and a cursor
       path must refer to a single element that already exists in the database.

       Usage would be:

       - init with path and cursor,
       - use the objectify API to modify the element
       - update() or save() I have not decided...

       The following attributes are used internally, and cannot be used in
       your objects:
        "_cursor"
        "_path"
        "_element"

    """
    def __init__(self,cursor,path,check=True):
        """
        init the class with cursor and path to item
        set check to false to eliminate a server request, but only if you
        know what you are doing...
        """
        self._cursor = cursor
        while path.endswith('/'):
            path = path[:-1]
        self._path = path
        if check:
            self._checkElement()
        g = self._fromdb()
        self._element = objectify.fromstring(g)

    def _checkElement(self):
        """
        do a check to see that this is a single element
        """
        q = u'let $i := %s' % (self._path,)
        q += u' return <i><c>{count($i)}</c></i>'
        s = self._cursor.execute(q)
        f = objectify.fromstring(s.value)
        c = int(f.c)
        if c == 1:
            return
        elif c == 0:
            raise LookupError(
            'The path did not return an element. ([0] might need to be [1]?)')
        else:
            raise ValueError(
        'Cannot init SednaObjectifiedElement with multiple elements.')

    def replace(self,obj):
        """ replace item at self._path with the object"""
        item = checkobj(obj)
        q = u'update replace $i in %s ' % (self._path,)
        q += ' with %s' % (item,)
        self._cursor.execute(q)

    def _fromdb(self):
        q = u'%s' % self._path
        s = self._cursor.execute(q)
        t = s.value
        return t

    def getparent(self):
        """
        return parent as a SednaContainer or None if at root
        """
        c = self.path + '/..'
        t = SednaContainer(self.cursor,c,self.parser, check=False)
        if t.tag is None:
            return None
        return t

    parent = property(getparent)

    def update(self):
        self.replace(self._element)

    save = update

    def __str__(self):
        return lxml.etree.tostring(self._element, encoding=unicode)

    def __setattr__(self,x,value):
        if x in ('_cursor','_path','_element'):
            try:
                if x == '_cursor':
                    assert hasattr(value,'execute')
                elif x == '_path':
                    assert isinstance(value,basestring)
                elif x == '_element':
                    assert isinstance(value,_Element)
            except AssertionError:
                raise ValueError(
            "Oops. _cursor, _path, and _element are used internally.")
            self.__dict__[x]=value
        else:
            setattr(self._element,x,value)

    def __setitem__(self,x,value):
        """dict setter"""
        self._element[x] = value

    def __getitem__(self,x):
        """dict getter"""
        return self._element[x]

    def __getattr__(self,x):
        """self.x getter.
        this is only called when x is not in the local dict, so we
        obtain it from the _element
        """
        return getattr(self._element,x)
