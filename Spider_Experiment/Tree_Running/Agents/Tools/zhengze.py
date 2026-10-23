import re

def get_table_name(table):
    table_name_pattern = r'CREATE TABLE `([^`]+)`'
    table_name_matches = re.search(table_name_pattern, table)
    if table_name_matches:
        table_name = table_name_matches.group(1)
    else:
        table_name = ""
    return table_name

def get_columns_name(table):        
    column_name_pattern = r'\n  `([^`]+)`'
    column_name_matches = re.findall(column_name_pattern, table)
    if column_name_matches:
        column_name = [match.strip() for match in column_name_matches]
    else:
        column_name = []
    return column_name

def get_final_sql(response):
    pattern = r'\[final sql\]:\s*(.*?);'
    matches = re.search(pattern, response, re.DOTALL)
    
    pattern_2 = r'\[final sql\]: \s*(.*?);'
    matches_2 = re.search(pattern_2, response, re.DOTALL)
    
    matches_3 = re.search(r'\[?final\s*SQL\]?:\s*(.+)', response, re.DOTALL | re.IGNORECASE)

    prefix = "[final sql]"
    start_index = response.find(prefix) + len(prefix)

    if matches:
        final_sql = matches.group(1)
        final_sql = final_sql.replace('\n', ' ')
        if "sql" in final_sql:
            pattern = r"(?<=```sql).*"
            matches = re.search(pattern, final_sql, re.DOTALL)
            if matches:
                final_sql = matches.group(0)
                final_sql = re.sub(r' {2,}', " ", final_sql)
                final_sql = final_sql.replace('\n', ' ')
                return final_sql
            else:
                final_sql = ""
        else:
            final_sql = re.sub(r' {2,}', " ", final_sql)
            final_sql = final_sql.replace('\n', ' ')
            return final_sql
    elif matches_2:
        final_sql = matches_2.group(1)
        final_sql = final_sql.replace('\n', ' ')
        if "sql" in final_sql:
            pattern = r"(?<=```sql).*"
            matches = re.search(pattern, final_sql, re.DOTALL)
            if matches:
                final_sql = matches.group(0)
                final_sql = re.sub(r' {2,}', " ", final_sql)
                final_sql = final_sql.replace('\n', ' ')
                return final_sql
            else:
                final_sql = ""
        else:
            final_sql = re.sub(r' {2,}', " ", final_sql)
            final_sql = final_sql.replace('\n', ' ')
            return final_sql
    elif matches_3:
        final_sql = matches_3.group(1)
        final_sql = final_sql.replace('\n', ' ')
        return final_sql
    elif start_index != -1:
        final_sql = response[start_index:]
        final_sql = re.sub(r' {2,}', " ", final_sql)
        final_sql = final_sql.replace('\n', ' ')
        return final_sql
    else:
        final_sql = ""
    
    return final_sql

def get_translation(response):
    prefix = "[translated sentence]: "
    start_index = response.find(prefix) + len(prefix)

    translated = response[start_index:]
    return translated

def get_missing_info(response):
    pattern = r'\[missing information\]:\s*(.*?)$'
    matches = re.search(pattern, response, re.DOTALL)
    if matches:
        missing_info = matches.group(1)
        missing_info = missing_info.replace('\n', ' ')
    else:
        missing_info = ""
    return missing_info

def get_related_tables(response):
    pattern = r'\[related tables\]: \[(.*?)\]'
    matches = re.search(pattern, response, re.DOTALL)
    if matches:
        tables_str = matches.group(1)
        tables_str = tables_str.replace("'","")
        tables_list = tables_str.split(', ')
        return tables_list
    else:
        pattern = r'\[related tables\]:\[(.*?)\]'
        matches = re.search(pattern, response, re.DOTALL)
        if matches:
            tables_str = matches.group(1)
            tables_str = tables_str.replace("'","")
            tables_list = tables_str.split(', ')
            return tables_list
        else:
            return []
        
def get_useful_tables(response):
    pattern = r'\[useful tables\]: \[(.*?)\]'
    matches = re.search(pattern, response, re.DOTALL)
    if matches:
        tables_str = matches.group(1)
        tables_str = tables_str.replace("'","")
        tables_list = tables_str.split(', ')
        return tables_list
    else:
        pattern = r'\[useful tables\]:\[(.*?)\]'
        matches = re.search(pattern, response, re.DOTALL)
        if matches:
            tables_str = matches.group(1)
            tables_str = tables_str.replace("'","")
            tables_list = tables_str.split(', ')
            return tables_list
        else:
            return []
        
def get_useful_columns(response):
    prefix = "[useful columns]: "
    start_index = response.find(prefix) + len(prefix)

    useful_columns = response[start_index:]
    column_names = re.findall(r"'(.*?)'", useful_columns)
    return column_names

def get_decompose_correct_or_not(response):
    if "yes" in response:
        return "Success", 1
    elif "no" in response:
        return "Success", 0
    else:
        return "Fail", 0
    
def if_sql_code_not_createupdateinsert(sql_code):
    signal = 1
    
    if "CREATE" in sql_code:
        signal = 0
    elif "UPSERT" in sql_code:
        signal = 0
    elif "INSERT" in sql_code:
        signal = 0
    elif "UPDATE" in sql_code:
        signal = 0

    return signal