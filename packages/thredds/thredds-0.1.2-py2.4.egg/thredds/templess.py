"""
 Copyright (c) 2005-2006 Guido Wesdorp. All rights reserved.
 This software is distributed under the terms of the Templess
 License. See LICENSE.txt for license text.
 E-mail: johnny@johnnydebris.net

 A very compact, XML based templating system. It has only 5 different 
 directives, and doesn't allow any logic inside the templates, but
 instead expects the application to provide a dict with all the data (as
 strings or XML nodes) completely prepared. This makes it quite restrictive,
 and harder to seperately work on design and logic (the template has to very
 strictly adhere to the format of the dict), but makes it an environment
 extremely suitable for developers (since all development is done from code
 rather than from the template, and they don't have to learn a new, quirky 
 templating language).
 
"""

import nanosax

__appname__ = 'templess'
__version__ = '0.2'
__author__ = 'Guido Wesdorp <johnny@johnnydebris.net>'
__last_modified_date__ = \
    '$Date: 2006-10-06 13:20:37 +0200 (Fri, 06 Oct 2006) $'
__last_author__ = '$Author: johnny $'
__revision__ = '$Revision: 86 $'
__footer__ = '%s v%s, (c) %s 2005' % (__appname__, __version__, __author__)

XMLNS = 'http://johnnydebris.net/xmlns/templess'

# some classes for templess users
class xmlstring(unicode):
    """wrapper around unicode to mark a string as XML

        when Templess encounters this object, it will not escape entities
    """

def iterwrapper(iterable):
    for i in iterable:
        yield objectcontext(i)

class objectcontext(object):
    """wrapper around objects to allow Templess to traverse attributes

        this is similar to the nastyness Zope exposes to its users in TAL,
        when Templess retrieves a key from the context, if the context is
        an objectcontext wrapping an object, instead of just doing a 
        __getitem__ the following will be done:

        - first a __getitem__ is tried, then a __getattr_, if the value is
          still not found a KeyError is raised

        - before the value is returned, a check is done whether it's callable,
          and if so it's called (without arguments)
    """
    # XXX do we want to allow arguments in something like "@key,key" form or
    # something scary like that? this is nasty already anyway ;)
    def __init__(self, o):
        self.object = o

    __marker__ = []
    def __getitem__(self, name):
        try:
            ret = self.object[name]
        except (TypeError, KeyError):
            try:
                ret = self.object.__dict__[name]
            except KeyError:
                raise KeyError, name
        if callable(ret):
            ret = ret()
        return self.wrap(ret)

    def __str__(self):
        return getattr(self.object, '__str__', self.object.__repr__)()

    def __repr__(self):
        return '<objectcontext for "%s">' % (self.object.__class__.__name__,)

    def __getattr__(self, name):
        # XXX this is _so_ nasty... :|
        ret = self.wrap(getattr(self.object, name))

    def wrap(self, obj):
        if is_iterable_not_string(obj):
            return iterwrapper(obj)
        return objectcontext(obj)

    def __hasattr__(self, name):
        return hasattr(self.object, name)

# helper methods
def is_iterable_not_string(v):
    """determine if something is iterable but not a string"""
    if (type(v) in [str, unicode, xmlstring, objectcontext]
            or isinstance(v, node)):
        return False
    try:
        iter(v)
    except TypeError:
        pass
    else:
        return True
    return False

# tree to string conversion stuff
def entitize(s):
    """entitize a string so it can be used in XML content and attrs"""
    return s.replace('&', '&amp;').replace('"', '&quot;').replace(
                '<', '&lt;').replace('>', '&gt;').replace("'", '&apos;')

# tree stuff
class node(object):
    """node base
    
        very specific to Templess, the nodes contain as little functionality
        as possible
    """

    def find(self, name):
        return []

class elnode(list, node):
    """XML element"""

    def __init__(self, name, attrs, parent, charset='UTF-8'):
        self.name = name
        self.attrs = dict(attrs)
        self.parent = parent
        self.charset = charset
        if parent is not None:
            parent.append(self)

    def unicode(self):
        """return a string (XML) representation of ourselves (unrendered!)"""
        ret = [self._start_node_start(self.attrs)]
        if not len(self):
            ret.append(u' />')
        else:
            ret.append(u'>')
            for child in self:
                ret.append(child.unicode())
            ret.append(self._end_node())
        return ''.join(ret)

    def generate(self, context):
        """returns self as a generator (yielding unicode strings)"""
        issingle = not len(self)
        for chunk in self._start_node(self.attrs, issingle):
            yield chunk
        for child in self:
            for chunk in child.generate(context):
                yield chunk
        if len(self):
            yield self._end_node()

    def __repr__(self):
        return '<%s "%s">' % (self.__class__.__name__, self.name)

    def find(self, name):
        if self.name == name:
            yield self
        for child in self:
            for found in child.find(name):
                yield found

    def _strconvert(self, s):
        if isinstance(s, node):
            return s
        elif isinstance(s, xmlstring):
            return unicode(s)
        elif isinstance(s, str):
            s = unicode(s, self.charset)
        elif not isinstance(s, unicode):
            s = str(s)
        return entitize(s)

    def _start_node(self, attrs, single):
        yield self._start_node_start(attrs)
        if single:
            yield u' />'
        else:
            yield u'>'

    def _start_node_start(self, attrs):
        return u'<%s%s' % (self.name, self._serialize_attrs(attrs))

    def _end_node(self):
        return u'</%s>' % (self.name,)

    def _serialize_attrs(self, attrs):
        """return the attributes as a string"""
        if not len(attrs):
            return ''
        items = sorted(attrs.items())
        return ' %s' % ' '.join(['%s="%s"' % (k, self._strconvert(v))
                                    for (k, v) in items])

class templessnode(elnode):
    """templess element node

        has a special method 'convert' that makes it conver itself to a
        normal elnode by processing all templess directives (returns a new
        node, doesn't process in-place)
    """

    def __init__(self, name, attrs, parent, t_prefix, charset='UTF-8'):
        self.name = name
        self.attrs = dict(attrs)
        self.parent = parent
        self.t_prefix = t_prefix
        self.charset = charset
        if parent is not None:
            parent.append(self)

    def convert(self, context, parent=None):
        """process the templess directives
        
            returns a copy of self, or a list of copies of self (in case of
            t:content), can return unexpected results in case of t:replace,
            use only on root nodes of documents in production situation
            (iow: if you want to convert a tree, always make sure there's no
            t:repeat on the node you call convert() on)

            context is a context dict (see docs), parent is an internal helper
            argument
        """
        attrs = self.attrs.copy()
        # first see if we need to be rendered at all
        cont = self._handle_cond(attrs, context)
        if not cont:
            return ''
        replacekey = self._get_replace(attrs)
        contentkey = self._get_content(attrs)
        attrs = self._process_attr(attrs, context)

        # find out what context we need to use for rendering our children, or
        # what data we need to interpolate
        cvalue = None
        if replacekey:
            cvalue = context[replacekey]
        elif contentkey:
            cvalue = context[contentkey]

        # render our children
        if cvalue is None:
            retnode = parent
            if not replacekey:
                retnode = elnode(self.name, attrs, parent, self.charset)
            for child in self:
                child.convert(context, retnode)
            return retnode
        elif is_iterable_not_string(cvalue):
            ret = []
            for ccontext in cvalue:
                if (isinstance(ccontext, dict) or 
                        isinstance(ccontext, objectcontext)):
                    newparent = parent
                    if not replacekey:
                        # create a similar node to retnode
                        newparent = elnode(self.name, attrs, parent,
                                            self.charset)
                    for child in self:
                        child.convert(ccontext, newparent)
                        # return the last of the new nodes
                    ret.append(newparent)
                else:
                    newparent = parent
                    if not replacekey:
                        newparent = elnode(self.name, attrs, parent,
                                            self.charset)
                    if isinstance(ccontext, node):
                        if ccontext.parent:
                            ccontext.parent.remove(ccontext)
                        ccontext.parent = newparent
                        newparent.append(ccontext)
                    else:
                        textnode(self._strconvert(ccontext), newparent,
                                    self.charset)
                    ret.append(newparent)
            return ret
        else:
            retnode = parent
            if not replacekey:
                retnode = elnode(self.name, attrs, parent, self.charset)
            if isinstance(cvalue, node):
                if cvalue.parent:
                    cvalue.parent.remove(cvalue)
                cvalue.parent = retnode
                retnode.append(cvalue)
            else:
                textnode(self._strconvert(cvalue), retnode, self.charset)
            return retnode

    def _handle_cond(self, attrs, context):
        """handle the 't:cond' and 't:not' directives
        
            returns False if there's a t:cond or t:not that doesn't allow 
            rendering, True otherwise
        """
        attrkey = '%s:cond' % (self.t_prefix,)
        cond = attrs.pop(attrkey, False)
        if cond:
            return not not context[cond]
        attrkey = '%s:not' % (self.t_prefix,)
        cnot = attrs.pop(attrkey, False)
        if cnot:
            return not context[cnot]
        return True

    def _process_attr(self, attrs, context):
        attrkey = '%s:attr' % (self.t_prefix,)
        strvalue = attrs.pop(attrkey, False)
        if strvalue:
            pairs = [v.strip() for v in strvalue.split(';')]
            for pair in pairs:
                k, v = pair.split(' ')
                value = context[v]
                if not value:
                    attrs.pop(k, None)
                else:
                    attrs[k] = value
        return attrs

    def _get_replace(self, attrs):
        attrkey = '%s:replace' % (self.t_prefix,)
        replace = attrs.pop(attrkey, False)
        return replace

    def _get_content(self, attrs):
        attrkey = '%s:content' % (self.t_prefix,)
        content = attrs.pop(attrkey, False)
        return content

class textnode(node):
    """text element"""

    def __init__(self, text, parent, charset='UTF-8'):
        if not isinstance(text, unicode):
            text = unicode(text, charset)
        self.text = text
        self.parent = parent
        self.charset = charset
        if parent is not None:
            parent.append(self)

    def unicode(self):
        return self.text

    def generate(self, context):
        yield self.unicode()

    def convert(self, context, parent):
        return self.__class__(self.text, parent)

    def __repr__(self):
        reprtext = self.text[10:]
        if len(reprtext) < len(self.text):
            reprtext += '...'
        return '<%s "%s">' % (self.__class__.__name__, reprtext)

class cdatanode(textnode):
    """cdata node"""

    def unicode(self):
        return '<![CDATA[%s]]>' % (self.text,)

class commentnode(textnode):
    """comment node"""

    def unicode(self):
        return '<!--%s-->' % (self.text,)

# nanosax handler
class treebuilderhandler(nanosax.nshandler):
    """nanosax handler to convert XML to a node tree"""
    def __init__(self, charset):
        self.charset = charset

    def startdoc(self):
        self.current = None
        self.root = None
        self.templess_prefix = None

    def enddoc(self):
        pass

    def startel(self, name, attrs):
        for key, value in attrs.items():
            if key.startswith('xmlns') and value == XMLNS:
                if not ':' in key:
                    self.templess_prefix = ''
                else:
                    self.templess_prefix = key.split(':')[1]
        self.current = templessnode(name, attrs,
                        self.current, self.templess_prefix,
                                self.charset)
        if self.root is None:
            self.root = self.current

    def endel(self, name):
        self.current = self.current.parent

    def text(self, text):
        textnode(text, self.current, self.charset)

    def comment(self, text):
        commentnode(text, self.current, self.charset)

    def cdata(self, text):
        cdatanode(text, self.current, self.charset)

class template(object):
    """a Templess template

        call 'unicode()' to get a unicode string, 'generate()' to get a 
        generator that yields bits of string, and 'render()' to get a node
    """
    def __init__(self, data, charset='UTF-8'):
        self.charset = charset
        if hasattr(data, 'read'):
            data = data.read()
        if charset != 'UTF-8':
            data = unicode(data, charset)
        if isinstance(data, unicode):
            data = data.encode('UTF-8')
        handler = treebuilderhandler(charset)
        parser = nanosax.nsparser(handler)
        parser.parse(data)
        self.tree = handler.root

    def render_to_string(self, context, charset='UTF-8'):
        """returns a complete string with the rendered template"""
        # not preferred anymore...
        return self.unicode(context).encode(charset)

    def unicode(self, context):
        """returns a unicode rendering of the template"""
        node = self.tree.convert(context)
        return node.unicode()

    def generate(self, context):
        """returns a generator that generates bits of string on demand"""
        node = self.tree.convert(context)
        return node.generate()

    def render(self, context):
        """render the tree to a 'normal' node
        
            processes all templess directives and returns the resulting tree
        """
        node = self.tree.convert(context)
        return node

class cgitemplate:
    """simple cgi engine for serving templess templates"""
    def __init__(self, template, content_type='text/html; charset=UTF-8',
                    error_template='templates/cgierror.html', headers={}):
        self.template = template
        self.content_type = content_type
        self.error_template = error_template
        self.headers = headers

    def render(self, context):
        """render and output the document

            this also prints the Content-Type header, if you want it to print
            other headers use the headers arg of the constructor
        """
        if not context.has_key('footer'):
            context['footer'] = __footer__
        try:
            fp = open(self.template)
            try:
                t = template(fp)
                ret = t.render_to_string(context)
            finally:
                fp.close()
            assert type(ret) == str
            self.print_output(self.content_type, ret)
        except:
            import sys
            exc, e, tb = sys.exc_info()
            ret = self.handle_exception(exc, e, tb)

    def handle_exception(self, exc, e, tb):
        """internal method that generates and prints an exception page"""
        from traceback import format_tb
        tblist = format_tb(tb)
        fp = open(self.error_template)
        try:
            t = template(fp)
            context = {
                'exception': str(exc),
                'message': str(e),
                'traceback': '\n'.join(tblist),
                'tblist': [{'line': str(l)} for l in tblist],
                'footer': __footer__,
            }
            ret = t.render_to_string(context)
        finally:
            fp.close()
        self.print_output('text/html; charset=UTF-8', ret)

    def print_output(self, content_type, body):
        """actually print the output"""
        print 'Content-Type: %s' % content_type
        for kv in self.headers.items():
            print '%s: %s' % kv
        print
        print body

if __name__ == '__main__':
    # some test code
    import sys
    if len(sys.argv) != 2:
        print 'usage: %s <xmlfile>' % (sys.argv[0],)
        sys.exit()
    xml = open(sys.argv[1]).read()
    handler = treebuilderhandler('UTF-8')
    parser = nanosax.nsparser(handler)
    parser.parse(xml)
    print handler.root
