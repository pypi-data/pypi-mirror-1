#!/usr/bin/python
#############################################################################
# Name:         rdf.py
# Purpose:      Defines generic functions to support RDF representations
# Maintainers:  Uwe Oestermeier <u.oestermeier@iwm-kmrc.de>
# Copyright:    (c) iwm-kmrc.de KMRC - Knowledge Media Research Center
# License:      GPLv2
#############################################################################
__docformat__ = 'restructuredtext'
from StringIO import StringIO
from datetime import datetime
import tempfile
import os.path
import zipfile

try:
    from cElementTree import ElementTree
except ImportError:    
    from elementtree import ElementTree

import zope.interface
import zope.schema
import zope.schema.interfaces
import zope.dublincore.interfaces
import zope.filerepresentation.interfaces
import zope.lifecycleevent
import zope.dottedname.resolve
import zope.datetime
import zope.app.appsetup.product

from bebop.protocol import protocol
from bebop.protocol import browser

from bop import helper
from bop import shortref
from bop import shortcut
from bop import startup

import interfaces

# Register two basic format interfaces as named utilities. This allows
# to choose the format by name and add more formats later on.

protocol.utility(interfaces.IZoteroFormat,
    provides=interfaces.IRDFFormat,
    name='Zotero')

protocol.utility(interfaces.IBebopFormat,
    provides=interfaces.IRDFFormat,
    name='Bebop')


class Node(object):
    """Represents a node within a RDFGraph."""
    
    namespace = 'RDF'
    tagname = 'Description'
    
    def __init__(self, ns=None, tagname=None):
        if ns is not None:
            self.namespace=ns
        if tagname is not None:
            self.tagname = tagname
        self.namespaces = dict()
        self.nodes = []
        self.triples = []
        
    def bind(self, namespace):
        self.namespaces[namespace.name] = namespace
            
    def add(self, triple):
        """Adds a subject, predicate, object triple to the node."""
        subject = triple[0]
        if subject == self:
            self.triples.append(triple)
        else:
            if subject not in self.nodes:
                self.nodes.append(subject)
            subject.add(triple)
        
    def serialize(self, inset=0):
        """Adjoin triples of the node to the result list."""
        
        def triple2attr(triple):
            key = triple[1].namespace.name
            attr = triple[1].name
            value = triple[2]
            return ' %s:%s="%s"' % (key, attr, value)
            
        result = [' '*inset + '<%s:%s' % (self.namespace, self.tagname)]
        if self.triples:
            result[-1] += triple2attr(self.triples[0])     
            if (len(self.triples) > 1):
                for triple in self.triples[1:]:
                    result.append('         ' + triple2attr(triple))
          
        if self.nodes:
            result[-1] += '>'
            for n in self.nodes:
                result.append(n.serialize(inset+2))
            result.append(' ' * inset + ('</%s:%s>' % (self.namespace, 
                                                       self.tagname)))
        else:
            result[-1] += '/>'
        return '\n'.join(result)     
        
        
class Graph(Node):
    """Represents a graph which can be written as a RDF document."""

    def __init__(self, ns='RDF', tagname='RDF'):
        super(Graph, self).__init__(ns, tagname)
        
    def add(self, triple):
        subject = triple[0]
        if subject not in self.nodes:
            self.nodes.append(subject)
        subject.add(triple)
            
    def serialize(self):
        result = ['<?xml version="1.0" encoding="UTF-8" ?>']
        result.append('<%s:%s' % (self.namespace, self.tagname))
        for key, value in sorted(self.namespaces.items()):
            result.append('    xmlns:%s="%s"' % (key, value.namespace))
        result[-1] += '>'
        for n in self.nodes:
            result.append(n.serialize())
        result.append('</%s:%s>' % (self.namespace, self.tagname))
        return '\n'.join(result).encode('utf-8')

    
class Namespace(object):
    """A rdf namespace."""

    def __init__(self, name, ns):
        self.namespace = ns
        self.name = name
    
    def __getitem__(self, key):
        return Attribute(self, key)

    def __getattr__(self, key):
        return Attribute(self, key)
        
    def etreename(self, tag=''):
        """Returns the elementtree tag name."""
        return '{%s}%s' % (self.namespace, tag)
        

class Attribute(object):
    """A attribute within a namespace."""
    
    def __init__(self, ns, name):
        self.namespace = ns
        self.name = name
    

class Literal(unicode):
    """A literal value."""
        

zopens = Namespace('zope', 'http://namespaces.zope.org/zope')
bopns = Namespace('bop', 'http://www.iwm-kmrc.de/namespaces/bebop')
dc = Namespace('dc', 'http://purl.org/dc/elements/1.1/')
dcterms = Namespace('dcterms', 'http://purl.org/dc/terms/')
z = Namespace('z', 'http://www.zotero.org/namespaces/export#')
RDF = Namespace('RDF', 'http://www.w3.org/1999/02/22-rdf-syntax-ns#')


class Converter(object):
    """Convenient base class for converters.
    
    A converter translates Zope content objects into RDF triples depending
    on the type of the request, which may be marked with format specific
    interfaces.
    """
    
    namespace = RDF
    
    def __init__(self, context, request):
        self.context = context
        self.request = request
        
    def convert(self, graph, node):
        """Convert the adapted objects into RDF triples."""
        pass
        
    def restore(self, node):
        """Read RDF triples from an element tree node."""
        pass
        

class FunctionConverter(Converter):
    """A converter that uses setter and getter functions."""
    
    predicate = None # must be specialized
    getter = None    # must be specialized
    setter = None    # must be specialized
    type = None      # type of the set/get value, must be specialized or None
    
    def convert(self, graph, node):
        """Adds the value as a subject / predicate / object triple."""
        graph.bind(self.namespace)
        graph.add((node,
                   self.namespace[self.predicate],
                   Literal(self.getter(self.context))))
                   
    def restore(self, node):
        """Sets the value from a subject / predicate / object triple."""
        attr = self.namespace.etreename(self.predicate)
        value = node.get(attr)
        if self.type is not None:
            value = self.type(value)
        # we need the setter as a function and not as a bound or unbound method 
        setter = self.__class__.__dict__['setter']
        setter(self.context, value)

    
class ReferenceConverter(Converter):
    """Generates a triple that describes a reference to the object itself or
    another object.
    
    """

    predicate = None  # must be specialized

    def convert(self, graph, node):
        graph.bind(self.namespace)
        value = self.identifier()
        if value:
            graph.add((node,
                   self.namespace[self.predicate],
                   Literal(value)))
                   
    def identifier(self):
        """Returns the identifer. Must be specialized."""
        return None 

        
class ResourceConverter(ReferenceConverter):
    """Generates a subnode that describes the resource of the object."""

    def identifier(self):
        return shortcut.path(self.context)[1:]
    
    def convert(self, graph, node):
        ns = self.namespace
        graph.bind(ns)
        node.add((Node(ns.name, self.predicate),
                  ns[self.predicate],
                  Literal(self.identifier())))

    
class SchemaConverter(Converter):
    """A converter that uses zope schemas to generate RDF triples."""

    interface = None # must be specialized
    fields = None    # must be specialized, None means all fields of the
                     # interface
     
    def fieldnames(self):
        return self.fields or zope.schema.getFieldNamesInOrder(self.interface)
        
    def convert(self, graph, node):
        """Writes a context object to a graph."""
        ns = self.namespace
        graph.bind(ns)
        obj = self.interface(self.context, None)
        if obj is None:
            return
        for name in self.fieldnames():
            value = getattr(obj, name)
            if value is None:
                continue
            field = self.interface[name]
            value = fieldLiteral(field, value)
            if not value:
                continue
            if '\n' in value:
                node.add((Node(ns.name, name),
                       self.namespace[name],
                       value)) 
            else:
                graph.add((node, self.namespace[name], value))

    def restore(self, node):
        """Sets the value from a subject / predicate / object triple."""
        for name in self.fieldnames():
            ename = self.namespace.etreename(name)
            undefined = object()
            value = node.get(ename, undefined)
            if value == undefined:
                subnode = node.find(ename)
                if subnode is None:
                    continue
                value = subnode.gettext()
            attr = self.interface[name]
            adapter = self.interface(shortcut.unsecure(self.context))
            if zope.schema.interfaces.IField.providedBy(attr):
                from_unicode = zope.schema.interfaces.IFromUnicode(attr, None)
                if from_unicode is not None:
                    if not isinstance(value, unicode):
                        value = unicode(value, encoding='utf-8')
                    value = from_unicode.fromUnicode(value)
                attr.set(adapter, value)
            else:
                helper.warning('No schema field %s' % name)

 
class ContainerConverter(Converter):
    """Converts a container into collection triples.
    
    Uses the part predicate and the refer function to generate
    partonomic relations.
    """
    
    predicate = None    # must be specialized
    attribute = None    # must be specialized
        
    def reference(self, context):
        return '#' + shortref.ensureRef(context)
            
    def convert(self, graph, node):
        """Writes a container and its parts to a graph."""
        ns = self.namespace
        graph.bind(self.namespace)
        for value in self.context.values():
            node.add((Node(ns.name, self.predicate),
                       self.attribute,
                       Literal(self.reference(value))))
        
        for value in self.context.values():
            serialize(value, self.request, graph)
        
        
class ZoteroTitle(FunctionConverter):
    """Converts the name into the dc:title within IZoteroFormat.
    
    Zotero encodes filenames as dc title
    """
    
    protocol.adapter(
        None,
        interfaces.IZoteroFormat,
        provides=interfaces.IRDFConverter,
        name='dc:title')
        
    namespace = dc
    predicate = 'title'
    getter = shortcut.name
    setter = shortcut.setname
    type = unicode


class DCZope(SchemaConverter):
    """Converts all IZopeDublinCore elements into dc predicates."""
    
    protocol.adapter(
        interfaces.IAttributeAnnotatable,
        interfaces.IZopeFormat,
        provides=interfaces.IRDFConverter,
        name='dc:zope')

    namespace = dc
    interface = zope.dublincore.interfaces.IZopeDublinCore


class RDFId(ReferenceConverter):
    """Registers a id for all contained objects."""

    protocol.adapter(
        None,
        None,
        provides=interfaces.IRDFConverter,
        name='RDF:ID')

    namespace = RDF
    predicate = 'ID'
    
    def identifier(self):
        return shortref.ref(self.context)


class RDFAbout(ReferenceConverter):
    """Registers a path for all contained objects."""

    protocol.adapter(
        None,
        interfaces.IZopeFormat,
        provides=interfaces.IRDFConverter,
        name='RDF:about')

    namespace = RDF
    predicate = 'about'
    
    def identifier(self):
        return shortcut.path(self.context)


class RDFResource(ResourceConverter):
    """Registers a RDF:resource predicate for all all files."""
    
    protocol.adapter(
        interfaces.IFile,
        zope.interface.Interface,
        provides=interfaces.IRDFConverter,
        name='RDF:resource')

    namespace = RDF
    predicate = 'resource'


class DCTerms(ContainerConverter):
    """Registers a dc:hasPart predicate for all contained objects."""
    
    protocol.adapter(
        interfaces.IFolder,
        zope.interface.Interface,
        provides=interfaces.IRDFConverter,
        name='dc:hasPart')

    namespace = dcterms
    predicate = 'hasPart'
    attribute = Attribute(RDF, 'resource')


class ZoteroItemType(ReferenceConverter):
    """Registers a z:itemType predicate."""
    
    protocol.adapter(
        interfaces.IFile,
        interfaces.IZoteroFormat,
        provides=interfaces.IRDFConverter,
        name='z:itemType')

    namespace = z
    predicate = 'itemType'

    def identifier(self):
        return zItemType(self.context)


class ZopeFactory(ReferenceConverter):
    """Registers a zope:factory predicate."""
    
    protocol.adapter(
        zope.interface.Interface,
        interfaces.IZopeFormat,
        provides=interfaces.IRDFConverter,
        name='zope:factory')

    namespace = zopens
    predicate = 'factory'
    
    def identifier(self):
        return helper.dottedname(self.context.__class__)


class ZopeName(ReferenceConverter):
    """Registers a zope:factory predicate."""
    
    protocol.adapter(
        zope.interface.Interface,
        interfaces.IZopeFormat,
        provides=interfaces.IRDFConverter,
        name='zope:name')

    namespace = zopens
    predicate = 'name'
    
    def identifier(self):
        return self.context.__name__


class ZopeMarker(ReferenceConverter):
    """Registers a zope:marker predicate."""
    
    protocol.adapter(
        zope.interface.Interface,
        interfaces.IZopeFormat,
        provides=interfaces.IRDFConverter,
        name='zope:marker')

    namespace = zopens
    predicate = 'marker'
    
    def identifier(self):
        """Returns the marker interfaces as dotted names.
        
        XXX: This doesn't work for location proxied objects. This has
        to be investigated.
        """
        dottednames = []
        for iface in zope.interface.directlyProvidedBy(self.context):
            dottednames.append(helper.dottedname(iface))
        return ' '.join(dottednames)

    def restore(self, node):
        attr = self.namespace.etreename(self.predicate)
        value = node.get(attr)
        if value is None:
            return
        for dn in value.split():
            iface = zope.dottedname.resolve.resolve(dn)
            zope.interface.alsoProvides(self.context, iface)


class DefaultNodeFactory(Node):
    """Defines a export/import node and factory. 
    
    Uses the Zope factory predicate to resolve the dottedname of the
    underlying content class. Reads also the name if available.
    """

    factory_predicate = 'factory'
    name_predicate = 'name'
    
    @classmethod
    def create(cls, context, etreenode):
        attr = zopens.etreename(cls.factory_predicate)
        dottedname = etreenode.get(attr, None)
        factory = zope.dottedname.resolve.resolve(dottedname)
        obj = factory()
        
        attr = zopens.etreename(cls.name_predicate)
        name = etreenode.get(attr, None)
        shortcut.setname(obj, name)
        return obj
        
        
protocol.utility(
    DefaultNodeFactory,
    provides=interfaces.IRDFFactory,
    name=RDF.etreename('Description'))     

    

class ZAttachmentNode(Node):
    """Defines a export/import node and factory."""
    
    zope.interface.implements(interfaces.IRDFFactory)
    
    namespace = 'z'
    tagname = 'Attachment'
    
    @classmethod
    def create(cls, context, etreenode):
        return shortcut.File()
            
protocol.utility(
    ZAttachmentNode,
    provides=interfaces.IRDFFactory,
    name=z.etreename('Attachment'))     
        

class ZCollectionNode(Node):
    """Defines a export/import node and factory."""
    
    zope.interface.implements(interfaces.IRDFFactory)
    
    namespace = 'z'
    tagname = 'Collection'
    
    @classmethod
    def create(cls, context, etreenode):
        return shortcut.Folder()
            
protocol.utility(
    ZCollectionNode,
    provides=interfaces.IRDFFactory,
    name=z.etreename('Collection'))     


export = protocol.GenericFunction('IExport')
@export.when(None, None)
def default_export(context, request):
    """By default objects are only exportable if they are namespace aware."""
    graph = Graph()
    serialize(context, request, graph)
    return graph.serialize()

serialize = protocol.GenericFunction('ISerialize')
@serialize.when(None, None, None)
def default_serialize(context, request, graph):
    """Serializes an object into a sequence of RDF triples."""
    node = Node()
    for c in converter(context, request):
        c.convert(graph, node)


# The following generic functions define the Zotero format specific nodes
@serialize.when(interfaces.IFile, interfaces.IZoteroFormat, None)
def serialize_zotero_file(context, request, graph):
    node = Node('z', 'Attachment')
    for c in converter(context, request):
        c.convert(graph, node)

@serialize.when(interfaces.IFolder, interfaces.IZoteroFormat, None)
def serialize_zotero_folder(context, request, graph):
    node = Node('z', 'Collection')
    for c in converter(context, request):
        c.convert(graph, node)


def converter(context, request):
    """Convenience functions which returns all registered converters."""
    registered = zope.component.getAdapters(
        (context, request),
        interfaces.IRDFConverter)
    for name, adapter in sorted(registered):
        yield adapter

zItemType = protocol.GenericFunction('IZoteroItemType')
@zItemType.when(None)
def default_zItemType(context):
    """By default objects cannot beconverted to Zotero."""
    return None

@zItemType.when(interfaces.IFile)    
def file_zItemType(context):
    return 'attachment'

@zItemType.when(interfaces.IFolder)    
def file_zItemType(context):
    return 'collection'

fieldLiteral = protocol.GenericFunction('ILiteral')
@fieldLiteral.when(None, None)
def default_literal(field, value):
    return Literal(value)

@fieldLiteral.when(zope.schema.interfaces.ITuple, None)
def sequence_literal(field, value):
    return u', '.join([Literal(escape(x)) for x in value])
    
@fieldLiteral.when(zope.schema.interfaces.IList, None)
def list_literal(field, value):
    return sequence_literal(field, value)
    

export_zip = browser.ViewFunction()
@export_zip.when(
    interfaces.IReadContainer,
    name='export_rdf.zip',
    permission='zope.ManageContent')
def export_zip_container(context, request):
    """Exports a RDF description and the file contents into a Zip archive."""

    IReadFile = zope.filerepresentation.interfaces.IReadFile
    IReadDirectory = zope.filerepresentation.interfaces.IReadDirectory    
    context = shortcut.unsecure(context)
    tmpfile = tempfile.mktemp(".zip")
    archive = zipfile.ZipFile(tmpfile, 'w')
    format = helper.parameter(request, 'format', default='Bebop')
    marker = shortcut.query(
        interfaces.IRDFFormat,
        name=format,
        context=context)
    
    if marker is not None:
        zope.interface.alsoProvides(request, marker)
        
    def write(path, data):
        t = datetime.now()
        date_time = (t.year, t.month, t.day, t.hour, t.minute, int(t.second))
        archive.writestr(
            zipfile.ZipInfo(
                filename=path.encode("UTF-8"),
                date_time=date_time),
            data)
             
    def walk(obj, path):
        file = IReadFile(obj, None)
        if file is None:
            directory = IReadDirectory(obj, None)
            if directory is None:
                helper.warning(
                    'Cannot export %s' % helper.dottedname(obj.__class__))
            else:
                for key, value in directory.items():
                    walk(value, os.path.join(path, key))
        else:
            write(path, file.read())            

    write('bebop.rdf', export(context, request))
    walk(context, context.__name__)
    archive.close()
    
    request.response.setHeader('Content-Type', 'application/zip')
    return open(tmpfile, "rb")


class Snapshot(object):
    """Exports/imports a RDF description and the file 
    contents to/from a directory.
    
    """
    
    rdffile = 'bebop.rdf'
    
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.dirpath = self.directory()
        format = helper.parameter(request, 'format', default='Bebop')
        marker = shortcut.query(
            interfaces.IRDFFormat,
            name=format,
            context=context)
        
        if marker is not None:
            zope.interface.alsoProvides(request, marker)

    def directory(self):
        """Returns the path of the rdf dump directory.""" 
        path = shortcut.query(interfaces.IDumpDirectory)
        if path is not None:
            return path
        config = zope.app.appsetup.product.getProductConfiguration('bebop.dump')
        if config is not None:
            path = os.path.join(startup.HERE, config.get('dumpdir'))
            if not os.path.exists(path):
                helper.warning(
                    "Directory %s is configured but doesn't exist." % path) 
        path = path or os.environ.get('BEBOP_DUMPDIR')
        if path is None or not os.path.exists(path):
            path = tempfile.mkdtemp(prefix='dumpdir')
        return os.path.abspath(path)
  
    def ensurePath(self):
        parts = shortcut.path(self.context).split('/')
        rootpath = os.path.join(self.dirpath, *parts)
        helper.makeDirectories(rootpath)
        return rootpath
        
    def dump(self):
        """Dumps the data to a directory."""
        IReadFile = zope.filerepresentation.interfaces.IReadFile
        IReadDirectory = zope.filerepresentation.interfaces.IReadDirectory    
        context = shortcut.unsecure(self.context)
            
        def write(path, data):
            fp = open(path, 'wb')
            fp.write(data)
            fp.close()
    
        def walk_annotations(obj, path):
            attachments = shortcut.attachments(obj)
            if not attachments:
                return
            dir, base = os.path.split(path)
            att_dir = os.path.join(dir, '++attachments', base)
            helper.makeDirectories(att_dir)
            for attachment in attachments:
                attachment_path = os.path.join(att_dir, shortcut.name(attachment))
                snappable = interfaces.ISnapshot(attachment, None)
                if snappable is not None:
                    return snappable.dump(attachment_path)    
                file = IReadFile(attachment, None)
                if file is not None:
                    write(attachment_path, file.read())    
    
        def walk(obj, path):
            snappable = interfaces.ISnapshot(obj, None)
            if snappable is not None:
                return snappable.dump(path)
            file = IReadFile(obj, None)
            if file is None:
                directory = IReadDirectory(obj, None)
                if directory is None:
                    helper.warning(
                        'Cannot dump %s' % helper.dottedname(obj.__class__))
                else:
                    helper.makeDirectories(path)
                    for key, value in directory.items():
                        walk(value, os.path.join(path, key))
            else:
                write(path, file.read())
            walk_annotations(obj, path)

        rootpath = self.ensurePath()
        write(
            os.path.join(rootpath, self.rdffile),
            export(context, self.request))
        walk(context, rootpath)
        return rootpath


    def load(self):
        """Restores content objects from a snapshot directory."""

        IWriteFile = zope.filerepresentation.interfaces.IWriteFile
        IReadDirectory = zope.filerepresentation.interfaces.IReadDirectory    
        context = shortcut.unsecure(self.context)
        
        def read(path, file):
            fp = open(path, 'rb')
            data = fp.read()
            fp.close()
            file.write(data)

        def walk_annotations(obj, path):
            attachments = shortcut.attachments(obj)
            if not attachments:
                return
            dir, base = os.path.split(path)
            att_dir = os.path.join(dir, '++attachments', base)
            for attachment in attachments:
                attachment_path = os.path.join(att_dir, shortcut.name(attachment))
                snappable = interfaces.ISnapshot(attachment, None)
                if snappable is not None:
                    return snappable.load(attachment_path)    
                file = IWriteFile(attachment, None)
                if file is not None:
                    read(attachment_path, file)    
        
        def walk(obj, path):
            snappable = interfaces.ISnapshot(obj, None)
            if snappable is not None:
                return snappable.load(path)
            file = IWriteFile(obj, None)
            if file is None:
                directory = IReadDirectory(obj, None)
                for key, value in directory.items():
                    walk(value, os.path.join(path, key))
            else:
                read(path, file)
            walk_annotations(obj, path)

        rootpath = self.ensurePath()
        path = os.path.join(rootpath, self.rdffile)
        rdf = open(path).read()
        container = self.context.__parent__
        name = self.context.__name__
       
        importGraph(rdf, container, self.request)
        walk(self.context, rootpath)
        return rootpath
    

snapshot_dir = browser.ViewFunction()
@snapshot_dir.when(
    interfaces.IReadContainer,
    name='snapshot',
    permission='zope.ManageSite')
def snapshot_dir(context, request):
    pat = u'Objects dumped to %s'
    return pat % Snapshot(context, request).dump()


restore_dir = browser.ViewFunction()
@restore_dir.when(
    interfaces.IReadContainer,
    name='restore',
    permission='zope.ManageSite')
def restore_dir(context, request):
    pat = u'Objects restored from %s'
    return pat % Snapshot(context, request).load()

def importGraph(rdf, container, request, debug=True):
    """Imports objects from a RDF description into an existing container.
    
    Existing objects of the same type are reused.
    """
    tree = ElementTree()
    tree.parse(StringIO(rdf))
    root = tree.getroot()
    mapping = dict()        # maps RDF:ID to imported objects
    parts = dict()
    
    def insert(container, name, obj):
        if name in container:
            existing = container[name]
            if existing.__class__ == obj.__class__:
                state = obj.__getstate__()
                existing.__setstate__(state)
                zope.event.notify(
                    zope.lifecycleevent.ObjectModifiedEvent(existing))
                return
            del container[name]
        zope.event.notify(
                zope.lifecycleevent.ObjectCreatedEvent(obj))    
        container[name] = obj
        
    for node in root.getchildren():
        factory = shortcut.query(interfaces.IRDFFactory, name=node.tag)
        if factory is None:
            helper.warning('No factory found for %s' % node.tag)
        else:
            obj = factory.create(container, node)
            rid = node.get(RDF.etreename('ID'))
            for c in converter(obj, request):
                c.restore(node)
            mapping[rid] = obj
            for n in node.findall(dcterms.etreename('hasPart')):
                pid = n.get(RDF.etreename('resource'))[1:]
                parts.setdefault(rid, []).append(pid)

    toplevel = set(mapping.keys())
    for parent_id, part_ids in parts.items():
        parent = mapping[parent_id]
        for part_id in part_ids:
            part = mapping[part_id]
            insert(parent, shortcut.name(part), part)
            toplevel.remove(part_id)

    for root_id in toplevel:
        root = mapping[root_id]
        insert(container, shortcut.name(root), root)


def importMetadata(rdf, container, request):
    """Imports RDF descriptions into an existing object hierarchy."""
    tree = ElementTree()
    tree.parse(StringIO(rdf))
    eroot = tree.getroot()
    dbroot = shortcut.root(container)
    for node in eroot.getchildren():
        attr = zopens.etreename('factory')
        factory = node.get(attr, None)
        path = node.get(RDF.etreename('about'))
        obj = helper.traversePath(dbroot, path)
        for c in converter(obj, request):
            c.restore(node)

    
class DateTimeFromUnicode(protocol.Adapter):
    """Implements IFromUnicode for datetime fields."""
    
    zope.interface.implements(zope.schema.interfaces.IFromUnicode)
    
    protocol.adapter(
        zope.schema.interfaces.IDatetime,
        provides=zope.schema.interfaces.IFromUnicode)

    def fromUnicode(self, value):
        return zope.datetime.parseDatetimetz(value)
 
 
class TupleFromUnicode(protocol.Adapter):
    """Implements IFromUnicode for tuple fields.
    
    Uses the value_type to lookup converter for the tuple objects.
    """
    
    zope.interface.implements(zope.schema.interfaces.IFromUnicode)
    
    protocol.adapter(
        zope.schema.interfaces.ITuple,
        provides=zope.schema.interfaces.IFromUnicode)

    def fromUnicode(self, value):
        items = ()
        for item in value.split(', '):
            item = unescape(item)
            type = self.context.value_type
            from_unicode = zope.schema.interfaces.IFromUnicode(type, None)
            if from_unicode is not None:
                item = from_unicode.fromUnicode(item)
            items += (item,)
        return items

 
class ListFromUnicode(TupleFromUnicode):
    """Implements IFromUnicode for list fields."""
    
    zope.interface.implements(zope.schema.interfaces.IFromUnicode)
    
    protocol.adapter(
        zope.schema.interfaces.IList,
        provides=zope.schema.interfaces.IFromUnicode)

    def fromUnicode(self, value):
        return list(super(ListFromUnicode, self).fromUnicode(value))

        
def escape(str):
    return str.replace(',', '%2C').replace('"', '%22')
    
def unescape(str):
    return str.replace('%2C', ',').replace('%22', '"')
    