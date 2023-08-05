###########################################################################

from os       import path
from StringIO import StringIO
from state       import OracleStateBuilder, OracleState
from table       import TableBuilder
from column      import TableColumnBuilder, ViewColumnBuilder
from primary_key import PrimaryKeyBuilder, PrimaryKeyColumnBuilder
from unique_key  import UniqueKeyBuilder, UniqueKeyColumnBuilder
from constraint  import CheckConstraintBuilder
from sequence    import SequenceBuilder
from index       import IndexBuilder, IndexColumnBuilder
from foreign_key import ForeignKeyBuilder, ForeignKeyColumnBuilder
from view        import ViewBuilder
from code        import StoredProcedureBuilder, FunctionBuilder
from code        import OraclePackageBuilder
from trigger     import TriggerBuilder
from connection  import OracleConnection
from state_xsd   import schema
###########################################################################

NAME            = 'oracle'
VERSION         = 1.0
DESCRIPTION     = 'Adapter for Oracle 10g schema'
NAMESPACE_URI   = 'http://www.daversy.org/schemas/state/oracle'
XMLSCHEMA_FILE  = StringIO(schema)
CONNECTION      = OracleConnection

STATE_OBJECT    = OracleState
SCHEMA_BUILDERS = [ OracleStateBuilder(),
                    TableBuilder(),
                    TableColumnBuilder(),
                    PrimaryKeyBuilder(),
                    PrimaryKeyColumnBuilder(),
                    UniqueKeyBuilder(),
                    UniqueKeyColumnBuilder(),
                    CheckConstraintBuilder(),
                    SequenceBuilder(),
                    IndexBuilder(),
                    IndexColumnBuilder(),
                    ForeignKeyBuilder(), 
                    ForeignKeyColumnBuilder(),
                    ViewBuilder(),
                    ViewColumnBuilder(),
                    StoredProcedureBuilder(),
                    FunctionBuilder(),
                    OraclePackageBuilder(),
                    TriggerBuilder()              ]

###########################################################################

