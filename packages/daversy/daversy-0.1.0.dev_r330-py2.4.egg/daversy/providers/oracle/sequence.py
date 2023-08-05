from daversy.utils import *
from daversy.dbobjects import Sequence


YESNO_MAPPING    = {'Y':'true', 'N': 'false'}

class SequenceBuilder(object):
    """Represents a builder for an oracle sequence. The current value of
       the sequence is never extracted."""

    DbClass = Sequence
    XmlTag  = 'sequence'

    Query = """
        SELECT sequence_name, increment_by, min_value, max_value,
               cache_size, cycle_flag, order_flag
        FROM   sys.user_sequences
        ORDER BY sequence_name
    """
    PropertyList = odict(
        ('SEQUENCE_NAME',   Property('name')),
        ('INCREMENT_BY',    Property('increment-by', 1)),
        ('MIN_VALUE',       Property('min-value', 1)),
        ('MAX_VALUE',       Property('max-value', 999999999999999999999999999)),
        ('CACHE_SIZE',      Property('cache-size', 20)),
        ('CYCLE_FLAG',      Property('cycle-after-last', 'false',
                                     lambda flag: YESNO_MAPPING[flag])),
        ('ORDER_FLAG',      Property('guaranteed-order', 'false',
                                     lambda flag: YESNO_MAPPING[flag]))
    )

    @staticmethod
    def addToState(state, sequence):
        state.sequences[sequence.name] = sequence

    @staticmethod
    def createSQL(seq):
        flagFormat = {'true': ' %s ', 'false':' NO%s '}

        sql =  "CREATE SEQUENCE %(name)-30s INCREMENT BY %(increment-by)s "  \
               "MINVALUE %(min-value)s MAXVALUE %(max-value)30s " \
               "CACHE %(cache-size)s " % seq

        sql +=  flagFormat[seq['cycle-after-last']] % 'CYCLE'
        sql +=  flagFormat[seq['guaranteed-order']] % 'ORDER' + ';\n'

        return sql
