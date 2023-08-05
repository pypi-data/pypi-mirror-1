from daversy.utils import *
from daversy.dbobjects import DbObject, Function, StoredProcedure

class StoredProcedureBuilder(object):
    """Represents a builder for a stored procedure."""

    DbClass = StoredProcedure
    XmlTag  = 'stored-procedure'

    Query = """
        SELECT object_name,
               replace(dbms_metadata.get_ddl(object_type, object_name),
                       '"' || user || '".') AS source
        FROM   sys.user_objects
        WHERE  object_type = 'PROCEDURE'
        AND    object_name NOT LIKE 'BIN$%'
        ORDER BY object_name
    """
    PropertyList = odict(
        ('OBJECT_NAME', Property('name')),
        ('SOURCE',      Property('source', None, lambda x: x.read()))
    )

    @staticmethod
    def addToState(state, procedure):
        procedure.source = trim_spaces(procedure.source)
        state.procedures[procedure.name] = procedure

    @staticmethod
    def createSQL(procedure):
        return procedure.source + '\n\n'

class FunctionBuilder(object):
    """Represents a builder for a database function."""

    DbClass = Function
    XmlTag  = 'function'

    Query = """
        SELECT object_name,
               replace(dbms_metadata.get_ddl(object_type, object_name),
                       '"' || user || '".') AS source
        FROM   sys.user_objects
        WHERE  object_type = 'FUNCTION'
        AND    object_name NOT LIKE 'BIN$%'
        ORDER BY object_name
    """
    PropertyList = odict(
        ('OBJECT_NAME', Property('name')),
        ('SOURCE',      Property('source', None, lambda x: x.read()))
    )

    @staticmethod
    def addToState(state, function):
        function.source = trim_spaces(function.source)
        state.functions[function.name] = function

    @staticmethod
    def createSQL(function):
        return function.source + '\n\n'

#############################################################################

class OraclePackage(DbObject):
    """ A class that represents an oracle package. """

#############################################################################

class OraclePackageBuilder(object):
    """Represents a builder for an oracle package."""

    DbClass = OraclePackage
    XmlTag  = 'package'

    Query = """
        SELECT object_name,
               replace(dbms_metadata.get_ddl(object_type, object_name),
                       '"' || user || '".') AS source
        FROM   sys.user_objects
        WHERE  object_type = 'PACKAGE'
        AND    object_name NOT LIKE 'BIN$%'
        ORDER BY object_name
    """
    PropertyList = odict(
        ('OBJECT_NAME', Property('name')),
        ('SOURCE',      Property('source', None, lambda x: x.read()))
    )

    @staticmethod
    def addToState(state, package):
        package.source = trim_spaces(package.source)
        state.packages[package.name] = package

    @staticmethod
    def createSQL(package):
        return package.source + '\n\n'
