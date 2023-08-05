from daversy.dbobjects import *
from daversy.utils import *
from code  import OraclePackage

class OracleState(DbObject):
    """This represents the elements that are available in an oracle database."""
    Provider = 'oracle'
    SubElements = odict( ('tables',       Table),
                         ('sequences',    Sequence),
                         ('indexes',      Index),
                         ('foreign_keys', ForeignKey),
                         ('views',        View),
                         ('procedures',   StoredProcedure),
                         ('functions',    Function),
                         ('packages',     OraclePackage),
                         ('triggers',     Trigger )          )

class OracleStateBuilder(object):
    DbClass = OracleState
    XmlTag  = 'dvs-state'

    PropertyList = odict(
        ('NAME',  Property('name'))
    )
