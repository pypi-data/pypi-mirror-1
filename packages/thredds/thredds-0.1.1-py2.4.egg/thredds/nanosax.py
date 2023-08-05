"""
 Copyright (c) 2005-2006 Guido Wesdorp. All rights reserved.
 This software is distributed under the terms of the Templess
 License. See LICENSE.txt for license text.
 E-mail: johnny@johnnydebris.net

 NanoSax is a very simple event-based XML processing library, much like SAX. 
 
"""

import re

class XMLError(Exception):
    def __init__(self, lineno, message):
        self.lineno = lineno
        self.message = message

    def __str__(self):
        return 'parse error in line %s: %s' % (self.lineno, self.message)

class nsparser(object):
    """very simple parser for XML

        emits events like SAX, except the API is a lot ('even' ;) simpler
    """
    TYPE_TEXT = 1
    TYPE_START = 2
    TYPE_END = 3
    TYPE_COMMENT = 4
    TYPE_CDATA = 5

    _reg_name = re.compile(r'^[\w\:\-]+$', re.U)
    _reg_start = re.compile(
        r'^([\w\:\-]+)(\s+(([\w\:\-]+)=(("(?=([^"]*)")[^"]*")|'
            "('(?=([^']*)')[^']*'))))*$")
    _reg_attr = re.compile(
        r'([\w\:\-]+)((\="(?=([^">]*)"))|(\=\'(?=([^\'>]*)\')))', re.U)
    _reg_xml_decl = re.compile(r'<\?xml.*?>', re.S)
    _reg_encoding = re.compile(r'encoding="([^"]+)"')
    _reg_pi = re.compile(r'<\?.*?>', re.S)
    _reg_dtd_1 = re.compile(r'<!DOCTYPE\s+[\w\:\-]+\s+\[.*?\]>', re.S)
    _reg_dtd_2 = re.compile(r'<!DOCTYPE\s+[\w\:\-]+\s+SYSTEM\s+.*?>')

    def __init__(self, handler):
        self.handler = handler

    def parse(self, xml):
        """parse the xml using self.handler
        
            xml is supposed to be either a unicode or ascii string, or a 
            string with the character set as defined in the xml declaration
        """
        xml = self._handle_pis(xml)
        self.handler.startdoc()
        for type, lineno, chunk in self._parse_into_chunks(xml):
            if type == self.TYPE_TEXT:
                self.handler.text(chunk)
            elif type == self.TYPE_START:
                self.handler.startel(*self._parse_start(lineno, chunk))
            elif type == self.TYPE_END:
                self.handler.endel(chunk)
            elif type == self.TYPE_COMMENT:
                self.handler.comment(chunk)
            elif type == self.TYPE_CDATA:
                self.handler.cdata(chunk)
        self.handler.enddoc()

    def _handle_pis(self, xml):
        """handle processing instructions
        
            takes care of handling (if appropriate) the XML declaration, and
            of discarding any processing instructions and document type 
            declarations etc. the lib can't deal with

            returns unicode, if the input string is not already unicode the
            charset mentioned in the XML declaration will be used for
            conversion (if any)
        """
        match = self._reg_xml_decl.search(xml)
        charset = 'UTF-8'
        if match:
            decl = match.group(0)
            xml = xml.replace(decl, '')
            encmatch = self._reg_encoding.search(decl)
            if encmatch:
                charset = encmatch.group(1)
        for reg in (self._reg_dtd_1, self._reg_dtd_2, self._reg_pi):
            while 1:
                match = reg.search(xml)
                if not match:
                    break
                xml = xml.replace(match.group(0), '')
        if isinstance(xml, str):
            xml = unicode(xml, charset)
        return xml

    def _parse_into_chunks(self, xml):
        xml = xml.strip()
        offset = 0
        currline = 1
        namestack = [] # for error checking
        self._test(xml.startswith('<'), currline, 'text before document start')
        while xml:
            offset = 0
            if xml.startswith('<![CDATA['):
                endpos = xml.find(']]>')
                self._test(endpos > -1, currline, 'CDATA section not closed')
                data = xml[9:endpos]
                offset += endpos + 3
                yield self.TYPE_CDATA, currline, data
                currline += data.count('\n')
            elif xml.startswith('<!--'):
                endpos = xml.find('-->')
                self._test(endpos > -1, currline, 'comment not closed')
                data = xml[4:endpos]
                offset += endpos + 3
                yield self.TYPE_COMMENT, currline, data
                currline += data.count('\n')
            elif xml.startswith('</'):
                endpos = xml.find('>')
                self._test(endpos > -1, currline, 'end tag not closed')
                data = xml[2:endpos]
                name = data.strip()
                self._test(self._reg_name.match(name), currline,
                            'illegal element name \'%s\' in end tag' % (name,))
                startname = namestack.pop()
                self._test(name.strip() == startname.strip(), currline,
                            ('closing tag \'%s\' doesn\'t match opening'
                                'tag \'%s\'') % (name, startname))
                offset += endpos + 1
                yield self.TYPE_END, currline, name
                currline += data.count('\n')
            elif xml.startswith('<'):
                endpos = xml.find('>')
                self._test(endpos > -1, currline, 'start tag not closed')
                data = xml[1:endpos]
                issingle = False
                if data[-1] == '/':
                    data = data[:-1]
                    issingle = True
                name = data.split()[0]
                self._test(self._reg_name.match(name), currline,
                            'illegal element name \'%s\' for tag' % (name,))
                offset += endpos + 1
                if not issingle:
                    # opening tag
                    namestack.append(name)
                    yield self.TYPE_START, currline, data
                else:
                    # singleton
                    yield self.TYPE_START, currline, data
                    yield self.TYPE_END, currline, name
                currline += data.count('\n')
            else:
                endpos = xml.find('<')
                self._test(endpos > -1, currline, 'text after document end')
                data = xml[:endpos]
                offset += endpos
                yield self.TYPE_TEXT, currline, data
                currline += data.count('\n')
            xml = xml[offset:]
        self._test(not namestack, currline, 'document not closed')

    def _parse_start(self, lineno, data):
        match = self._reg_start.match(data.strip())
        self._test(match, lineno, 'illegal start tag content \'%s\'' % (data,))
        name = match.group(1)
        data = match.group(0)[len(name):].strip()
        attrs = {}
        while 1:
            match = self._reg_attr.search(data)
            if not match:
                break
            # XXX really strange... for some reason group(0) doesn't contain
            # the whole matched string
            data = data.replace('%s%s' % (match.group(0), match.group(4)), '')
            attrs[match.group(1)] = match.group(4)
        return name, attrs

    def _test(self, assertion, lineno, message):
        """raises an exception with message as text when assertion is false"""
        if not assertion:
            raise XMLError(lineno, message)

class nshandler(object):
    """handler for nsparser
    
        this provides the interface to implement, and can serve as a base
        class when you don't want to implement everything
    """
    def startdoc(self):
        pass

    def enddoc(self):
        pass
    
    def startel(self, name, attrs):
        pass

    def endel(self, name):
        pass

    def text(self, text):
        pass

    def comment(self, text):
        pass

    def cdata(self, text):
        pass

class echohandler(nshandler):
    def startdoc(self):
        self.buffer = []

    def enddoc(self):
        self.xml = ''.join(self.buffer)

    def startel(self, name, attrs):
        self.buffer += ['<', name]
        if len(attrs):
            self.buffer.append(' ')
            self.buffer += ' '.join('%s="%s"' % (k, v)
                                    for (k, v) in attrs.iteritems())
        self.buffer.append('>')

    def endel(self, name):
        if self.buffer[-1] == '>':
            # singleton
            self.buffer.pop()
            self.buffer.append('/>')
        else:
            self.buffer += ['</', name, '>']

    def text(self, text):
        self.buffer.append(text)

    def comment(self, text):
        self.buffer += ['<!--', text, '-->']

    def cdata(self, text):
        self.buffer += ['<![CDATA[', text, ']]>']

if __name__ == '__main__':
    """as an example we use the empty handler (base implementation), which 
        means nothing is produced, but the document is checked for 
        well-formedness (and the lib can be tested a bit)
    """
    import sys
    if len(sys.argv) != 2:
        print 'usage: %s <xmlfile>' % (sys.argv[0],)
        sys.exit()
    fname = sys.argv[1]
    xml = open(fname).read()
    h = nshandler()
    p = nsparser(h)
    p.parse(xml)
