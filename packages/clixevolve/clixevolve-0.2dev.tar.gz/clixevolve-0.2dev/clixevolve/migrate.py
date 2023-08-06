import argparse

def main():
    parser = argparse.ArgumentParser(description="Apply an evolution file", prog="clixevolve", version='ClixEvolve 0.2dev')
    parser.add_argument('schema', type=argparse.FileType('r'), metavar='SCHEMA_FILE', help='the evolution to apply to the database')
    parser.add_argument('-u', '--user', action='store', metavar='DB_USER', nargs=1, help="specify the datbase user to use")
    parser.add_argument('-d', '--host', action='store', metavar='DB_HOST', nargs=1, help="specify the datbase host", default=["localhost"])
    parser.add_argument('-p', '--password', action='store', metavar='DB_PASSWORD', nargs='?', const='', help="use a password to connect to the database.")
    args = parser.parse_args()
    
    with args.schema:
        whole_schema = eval(args.schema.read())
    
    output_sql = "use `%s`;\n" % whole_schema['database']
    for table in whole_schema['tables']:
        if table['action'] == 'drop':
            output_sql += "DROP TABLE `%s`;\n" % table['name']
            continue
        for column in table['columns']:
            if column['action'] == 'drop':
                output_sql += "ALTER TABLE `%s` DROP COLUMN `%s`;\n" % (table['name'], column['name'])
                continue
            if column['action'] == 'add':
                output_sql += "ALTER TABLE `%s` ADD COLUMN `%s` %s" %(table['name'], column['name'], column['type'])
                if column['character_set_name'] != 'None':
                    output_sql += " CHARACTER SET %s" % column['character_set_name']
                if column['collation_name'] != 'None':
                    output_sql += " COLLATE %s" % column['collation_name']
                if column['nullable'] == 'YES':
                    output_sql += " NULL"
                else:
                    output_sql += " NOT NULL"
                if column['default'] != 'None':
                    if 'char' not in column['type']:
                        output_sql += " DEFAULT %s" % (table['default'])
                    else:
                        output_sql += " DEFAULT '%s'" % (table['default'])
                output_sql += " %s;\n" % (column['extra'])
                continue
            if column['action'] == 'modify':
                output_sql += "ALTER TABLE `%s` ALTER COLUMN `%s`"

if __name__ == "__main__": main()