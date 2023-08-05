import os, sys, re, tempfile, ConfigParser
from os   import path
from lxml import etree, _elementpath
import providers

#############################################################################

class FileState:
    def can_load(self, location):
        return path.isfile(location)

    def can_save(self, location):
        return ':' not in location or re.match('^[a-z]:', location, re.I)

    def load(self, location, encoding, filters = {}):
        document = etree.parse(location)
        provider = self._detect_provider(document.getroot().tag)
        if not provider:
            raise LookupError('Unable to detect the provider')

        self._setup(provider)

        schema   = etree.XMLSchema( etree.parse(provider.XMLSCHEMA_FILE) )
        schema.assertValid(document)

        return self._load_element(document.getroot(),
                                   provider.STATE_OBJECT, filters)

    def save(self, state, location, info):
        provider = self._lookup_provider(state.__class__)
        if not provider:
            raise LookupError('Unable to detect the provider')

        self._setup(provider)

        output = file(location, 'w')
        dummy  = etree.Element('dummy')
        self._save_element(dummy, state)

        root = dummy[0]
        root.attrib['xmlns'] = provider.NAMESPACE_URI

        etree.ElementTree(root).write(output, pretty_print=True)
        output.close()

    def save_sql(self, state, location, info, type='all'):
        provider = self._lookup_provider(state.__class__)
        if not provider:
            raise LookupError('Unable to detect the provider')

        self._setup(provider)

        sql = ''
        comment = []
        for key in state.SubElements:
            for item in state[key].values():
                builder = self.db_mapping[item.__class__]
                sql += builder.createSQL(item)
                if hasattr(builder, 'commentSQL'):
                    comment.extend(builder.commentSQL(item))
                    
        commentSQL = "\n".join(comment)

        if type == 'all':
            sql += commentSQL
        elif type == 'comment':
            sql = commentSQL

        stream = file(location, 'w')
        stream.write(sql.encode('utf-8'))
        stream.close()

    def _detect_provider(self, tag):
        match = re.match('^{([^}]+)}', tag)
        if not match:
            return None

        namespace = match.group(1)
        for provider in providers.DATABASES.values():
            if namespace == provider.NAMESPACE_URI:
                return provider
        return None

    def _lookup_provider(self, dbclass):
        for provider in providers.DATABASES.values():
            if provider.STATE_OBJECT == dbclass:
                return provider
        return None

    def _setup(self, provider):
        self.db_mapping, self.xml_mapping = {}, {}
        for builder in provider.SCHEMA_BUILDERS:
            self.db_mapping[builder.DbClass] = builder
            self.xml_mapping[builder.XmlTag] = "{%s}%s" % (provider.NAMESPACE_URI,
                                                            builder.XmlTag)

    def _load_element(self, node, dbclass, filters):
        builder = self.db_mapping[dbclass]
        if not node.tag == self.xml_mapping[builder.XmlTag]:
            return None

        # load attributes
        object = builder.DbClass()
        if hasattr(builder, 'PropertyList'):
            for prop in builder.PropertyList.values():
                if not prop.exclude:
                    object[prop.name] = node.get(prop.name) or prop.default

        # check if it is excluded
        if not is_allowed( object, filters.get(builder.XmlTag) ):
            return None

        # load sub-elements
        if hasattr(object, 'SubElements'):
            for key, dbclass in object.SubElements.items():
                for child in node:
                    childObject = self._load_element(child, dbclass, filters)
                    if childObject:
                        object[key][childObject.name] = childObject

        return object

    def _save_element(self, node, object):
        builder = self.db_mapping[object.__class__]
        subnode = etree.SubElement(node, builder.XmlTag)

        # save attributes
        if hasattr(builder, 'PropertyList'):
            for key, value in builder.PropertyList.items():
                if not value.exclude and object[value.name]:
                    subnode.attrib[value.name] = object[value.name]

        # save sub-elements
        if hasattr(object, 'SubElements'):
            for key in object.SubElements.keys():
                for item in object[key].values():
                    self._save_element(subnode, item)

#############################################################################

class DatabaseState(object):
    def can_load(self, location):
        provider, params = self._detect_adapter(location)
        return provider and provider.CONNECTION

    def can_save(self, location):
        return False

    def _detect_adapter(self, location):
        keys = location.split(':')
        if len(keys) < 2:
            return None, None

        return providers.DATABASES.get(keys[0]), keys[1:]

    def load(self, location, encoding, filters = {}):
        if not self.can_load(location):
            return None

        provider, params = self._detect_adapter(location)

        state      = provider.STATE_OBJECT()
        connection = provider.CONNECTION(params)

        for builder in provider.SCHEMA_BUILDERS:
            print "Extracing %s" % builder.DbClass.__name__
            if hasattr(builder, 'Query'):
                self._load_object(connection.cursor(), state, encoding,
                                  builder, filters.get(builder.XmlTag))

        connection.close()
        return state

    def _load_object(self, cursor, state, encoding, builder, filters):
        cursor.execute(builder.Query)

        # find the column position and names
        columnNames = [c[0] for c in cursor.description]
        columnIndex = dict(map(None, columnNames, range(len(columnNames))))

        for row in cursor:
            # set the object properties
            newObject = builder.DbClass()
            for name in columnNames:
                setProperty = builder.PropertyList[name]
                setProperty(newObject, row[columnIndex[name]], encoding)

            if is_allowed(newObject, filters):
                builder.addToState(state, newObject)

        cursor.close()

class VersionControlState(object):
    def can_load(self, location):
        provider, params = self._detect_provider(location)
        return provider and provider.available()

    def can_save(self, location):
        return self.can_load(location)

    def _detect_provider(self, location):
        keys = location.split(':')
        if len(keys) < 2:
            return None, None

        return providers.VERSIONCONTROL.get(keys[0]), keys[1:]

    def load(self, location, encoding, filters = {}):
        if not self.can_load(location):
            return None

        provider, params = self._detect_provider(location)
        data = provider.load_file(params, None)
        if not data:
            return None
        return FileState().load(data, encoding, filters)

    def save(self, state, location, info):
        if not self.can_save(location):
            return None

        provider, params = self._detect_provider(location)
        handle, temp_location = tempfile.mkstemp()
        os.close(handle)
        FileState().save(state, temp_location, info)
        provider.save_file(params, temp_location, info)

    def save_sql(self, state, location, info, type):
        if not self.can_save(location):
            return None

        provider, params = self._detect_provider(location)
        handle, temp_location = tempfile.mkstemp()
        os.close(handle)
        FileState().save_sql(state, temp_location, info, type)
        provider.save_file(params, temp_location, info)

#############################################################################

PROVIDERS = [ FileState(), DatabaseState(), VersionControlState() ]

#############################################################################

def create_filter(filename, selected_tags):
    config = ConfigParser.ConfigParser()
    if not config.read(filename):
        return None

    parse_tag = lambda x: [t.strip() for t in x.split(',') if t.strip()]

    tags = parse_tag(selected_tags)
    filters = {}
    for section in config.sections():
        section_list = []
        for name, tag_spec in config.items(section):
            name_tags = parse_tag(tag_spec)
            for tag in tags:
                if tag in name_tags and not tag in section_list:
                    section_list.append( re.compile('^%s$' % name, re.I) )

        filters[section] = section_list

    return filters

def is_allowed(object, filters):
    if filters is None or not object.has_key('name'):
        return True

    for filter in filters:
        if filter.match(object['name']):
            return True

    return False
