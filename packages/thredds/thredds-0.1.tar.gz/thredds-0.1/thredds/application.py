"""
THREDDS catalog generator implemented as a WSGI application.

This WSGI app generates a THREDDS catalog for a given directory.
It can be used to serve static data, or combined with the pydap DAP
server.

For static data, use the following configuration together with Paste
Deploy::

    [composit:main]
    use = egg:Paste#cascade
    app1 = static
    app2 = thredds
    catch = 404

    [app:static]
    use = egg:Paste#static
    document_root = /path/to/data

    [app:thredds]
    use = egg:thredds
    name = myserver
    root = /path/to/data
    type = HTTPServer

With pydap, try this::

    [composit:main]
    use = egg:Paste#cascade
    app1 = thredds
    app2 = pydap
    catch = 404

    [app:thredds]
    use = egg:thredds
    name = myserver
    root = /path/to/data
    type = OpenDAP

    [app:pydap]
    use = egg:dap
    root = /path/to/data
"""

__author__ = 'Roberto De Almeida <rob@pydap.org>'

import os

from paste.request import construct_url
from paste.httpexceptions import HTTPException, HTTPNotFound

try:
    from dap.plugins.lib import loadhandler
except ImportError:
    pass

from thredds import templess


catalog = """<catalog t:attr="name name" version="1.0.1" 
    xmlns="http://www.unidata.ucar.edu/namespaces/thredds/InvCatalog/v1.0"
    xmlns:xlink="http://www.w3.org/1999/xlink"
    xmlns:t="http://johnnydebris.net/xmlns/templess">

    <service t:attr="name service; base base; serviceType type" />

    <dataset t:attr="serviceName service">
        <dataset t:replace="datasets" />
    </dataset>

    <catalogRef t:replace="subdirs" />
</catalog>"""

dataset = """<dataset xmlns:t="http://johnnydebris.net/xmlns/templess"
    t:attr="name name; urlPath url" />"""

catalogRef = """<catalogRef xmlns:t="http://johnnydebris.net/xmlns/templess"
    t:attr="xlink:href url; xlink:title name; name name" />"""


def make_app(global_conf, root, **kwargs):
    return ThreddsCatalog(root, **kwargs)


class ThreddsCatalog(object):
    def __init__(self, root, name=None, type='File'):
        self.root = root
        self.name = name or 'THREDDS catalog'
        self.type = type

        # Load templates.
        self._catalog_template = templess.template(catalog)
        self._dataset_template = templess.template(dataset)
        self._catalogRef_template = templess.template(catalogRef)

    def __call__(self, environ, start_response):
        self.environ = environ
        self.start = start_response

        path_info = environ.get('PATH_INFO', '')
        if path_info.endswith('/catalog.xml'):
            path = path_info[:-len('/catalog.xml')]
            path = path.lstrip('/')
            return self._catalog(path)
        else:
            raise HTTPNotFound

    def _catalog(self, basepath):
        dir = os.path.join(self.root, basepath)

        # Build link to file. Local files with ``File`` type should use the ``file:``
        # protocol, but ``catalogRef`` elements should always have a ``http://``
        # protocol to be discovered.
        location = construct_url(self.environ, with_query_string=False, with_path_info=False)
        if self.type.lower() == 'file': link = 'file://%s' % self.root
        else: link = location

        dirs, files = [], []
        for item in os.listdir(dir):
            path = os.path.join(dir, item)
            if os.path.isdir(path):
                context = {'name': item, 'url': '%s/%s/%s' % (location, item, 'catalog.xml')}
                subdir = self._catalogRef_template.render(context)
                dirs.append(subdir)
            else:
                if self.type.lower() in ['opendap', 'dods']:
                    try:
                        # Try to open file.
                        H = loadhandler(path)
                        context = {'name': H.description, 'url': '%s/%s' % (link, item)}
                        dataset = self._dataset_template.render(context)
                        files.append(dataset)
                        H.close()
                    except:
                        pass
                else:
                    context = {'name': item, 'url': '%s/%s' % (link, item)}
                    dataset = self._dataset_template.render(context)
                    files.append(dataset)

        context = {'name': self.name,
                   'base': link + '/',
                   'service': self.name,
                   'type': self.type,
                   'datasets': files,
                   'subdirs': dirs}
        output = [self._catalog_template.unicode(context).encode('utf-8')]
        headers = [('Content-type', 'application/xml; charset=utf-8')] 

        self.start('200 OK', headers)
        for line in output: yield line

