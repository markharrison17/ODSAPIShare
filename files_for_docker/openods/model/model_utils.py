
# def assign_sql_table_alias(table_list, table_name, table_alias):
#     table_list[table_name] = set([table_alias])


def add_table_and_alias_to_dict(table_dict, table_name, table_alias):
    if table_name in table_dict:
        table_dict[table_name] = table_dict[table_name] | {table_alias}
    else:
        table_dict[table_name] = {table_alias}


