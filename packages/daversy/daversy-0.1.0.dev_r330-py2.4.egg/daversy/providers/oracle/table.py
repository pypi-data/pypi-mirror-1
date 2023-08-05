from daversy.utils       import *
from daversy.dbobjects   import TableColumn, Table
from column      import TableColumnBuilder
from primary_key import PrimaryKeyBuilder
from unique_key  import UniqueKeyBuilder
from constraint  import CheckConstraintBuilder

YESNO_MAPPING    = {'Y':'true', 'N': 'false'}

class TableBuilder(object):
    """Represents a builder for a database table."""

    DbClass = Table
    XmlTag  = 'table'

    Query = """
        SELECT t.table_name, t.temporary, c.comments
        FROM   sys.user_tables t, sys.user_tab_comments c
        WHERE  t.table_name = c.table_name
        AND    c.table_type = 'TABLE'
        AND    t.table_name NOT LIKE 'BIN$%'
        ORDER BY t.table_name
    """
    PropertyList = odict(
        ('TABLE_NAME',  Property('name')),
        ('TEMPORARY',   Property('temporary', 'false', lambda flag: YESNO_MAPPING[flag])),
        ('COMMENTS',    Property('comment'))
    )

    @staticmethod
    def addToState(state, table):
        table.comment = trim_spaces(table.comment)
        state.tables[table.name] = table

    @staticmethod
    def createSQL(table):
        sql = "CREATE %(temp)sTABLE %(name)s (\n  %(table_sql)s\n)\n/\n"

        definition = []
        for col in table.columns.values():
            definition.append(TableColumnBuilder.sql(col))
        for key in table.primary_keys.values():
            definition.append(PrimaryKeyBuilder.sql(key))
        for key in table.unique_keys.values():
            definition.append(UniqueKeyBuilder.sql(key))
        for constraint in table.constraints.values():
            definition.append(CheckConstraintBuilder.sql(constraint))

        table_sql = ",\n  ".join(definition)
        is_temp = table.temporary == 'true' and 'TEMPORARY ' or ''

        return render(sql, table, temp=is_temp, table_sql=table_sql)

    @staticmethod
    def commentSQL(table):
        comments = []
        if table.comment:
            comments.append("COMMENT ON TABLE %s IS '%s';" % (table.name,
                                                                sql_escape(table.comment)))
        for column in table.columns.values():
            col_comment = TableColumnBuilder.commentSQL(table, column)
            if col_comment:
                comments.append(col_comment)

        return comments
