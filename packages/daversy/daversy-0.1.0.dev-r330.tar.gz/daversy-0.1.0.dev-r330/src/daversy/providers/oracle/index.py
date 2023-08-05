from daversy.utils      import *
from daversy.dbobjects  import Index, IndexColumn

class IndexColumnBuilder(object):
    """ Represents a builder for a column in an index. """

    DbClass = IndexColumn
    XmlTag  = 'index-column'

    Query = """
        SELECT c.column_name, lower(c.descend) AS sort, i.index_name,
               i.table_name, c.column_position AS position
        FROM   sys.user_indexes i, sys.user_ind_columns c
        WHERE  i.index_name = c.index_name
        AND    i.table_name = c.table_name
        AND    i.generated = 'N'
        AND    i.index_name NOT LIKE '%$%'
        ORDER BY i.index_name, c.column_position
    """

    PropertyList = odict(
        ('COLUMN_NAME',  Property('name')),
        ('SORT',         Property('sort')),
        ('INDEX_NAME',   Property('index-name', exclude=True)),
        ('TABLE_NAME',   Property('table-name', exclude=True)),
        ('POSITION',     Property('position',   exclude=True)),
    )

    @staticmethod
    def addToState(state, column):
        index = state.indexes.get(column['index-name'])
        if index:
            index.columns[column.name] = column

class IndexBuilder(object):
    """ Represents a builder for a index on a table. """

    DbClass = Index
    XmlTag  = 'index'

    Query = """
        SELECT i.index_name, i.table_name,
               decode(i.uniqueness, 'UNIQUE', 'true', 'false') AS is_unique
        FROM   sys.user_indexes i
        WHERE  i.generated = 'N'
        AND    i.index_name NOT LIKE '%$%'
        ORDER BY i.index_name
    """

    PropertyList = odict(
        ('INDEX_NAME', Property('name')),
        ('IS_UNIQUE',  Property('unique')),
        ('TABLE_NAME', Property('table-name'))
    )

    @staticmethod
    def addToState(state, index):
        # ensure that the table exists and the index is not for a PK/UK
        table = state.tables.get(index['table-name'])
        if table:
            if table.primary_keys.has_key(index.name) or table.unique_keys.has_key(index.name):
                return
            state.indexes[index.name] = index

    @staticmethod
    def createSQL(index):
        sql = "CREATE %(unique)s INDEX %(name)s ON %(table-name)s (\n" \
              "  %(column_sql)s\n)\n/\n"

        column_def = ["%(name)-30s %(sort)s" % column for column
                                                      in index.columns.values()]
        column_sql = ",\n  ".join(column_def)

        unique = index.unique == 'true' and 'UNIQUE' or ''

        return render(sql, index, unique=unique, column_sql=column_sql)

