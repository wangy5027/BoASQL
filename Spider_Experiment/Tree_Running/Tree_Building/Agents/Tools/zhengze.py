import re

def get_smaller_tasks_list(response):
    pattern = r'\[smaller tasks\]:\s*(.*?)\n\n'
    matches = re.search(pattern, response, re.DOTALL)

    if matches:
        tasks_text = matches.group(1)
        tasks_list = tasks_text.split('\n')
    else:
        tasks_list = []
    
    if len(tasks_list)== 0:
        pattern = r'\[smaller tasks\]:\s+(.+)'
        matches = re.search(pattern, response, re.DOTALL)

        if matches:
            tasks_text = matches.group(1)
            tasks_list = tasks_text.split('\n')
        else:
            tasks_list = []
    
    for i in tasks_list:
        if "missing information" in i:
            signal = "missing information"
            return signal, response
    signal = "Sucess"
    
    return signal,tasks_list

def get_easy_or_complicate(response):
    pattern = r'\[easy_or_complicate\]:\s+(.+)'
    matches = re.search(pattern, response, re.DOTALL)
    
    pattern_2 = r'\[easy_or_complicate\]: \s+(.+)'
    matches_2 = re.search(pattern_2, response, re.DOTALL)
    
    if matches:
        easy_or_complicate = matches.group(1)
        easy_or_complicate = easy_or_complicate.replace('\n', ' ')
        signal = "Success"
        return signal, easy_or_complicate
    else:
        easy_or_complicate = ""
    
    if matches_2:
        easy_or_complicate = matches_2.group(1)
        easy_or_complicate = easy_or_complicate.replace('\n', ' ')
        signal = "Success"
        return signal, easy_or_complicate
    else:
        easy_or_complicate = ""
        signal = "Fail"
        return signal, easy_or_complicate

def get_thinking_from_Decompose_or_not(response):
    pattern = r"\[thinking\]:\s*(.*?)\s*\[easy_or_complicate\]"
    match = re.search(pattern, response)
    
    start_index = response.find("[thinking]")
    end_index = response.find("[easy_or_complicate]")
    if match:
        result = match.group(1)
        print(result)
        return "Success", result
    elif start_index != -1 and end_index != -1:
        start_index = response.find("[thinking]") + len("[thinking]:")
        end_index = response.find("[easy_or_complicate]")
        result = response[start_index:end_index]
        print(result)
        return "Success", result
    else:
        return "Fail", ""

def catch_table_name(table):
    table_name_pattern = r'CREATE TABLE\s+"([^"]+)"' 
    table_name_matches = re.search(table_name_pattern, table)
    if table_name_matches:
        table_name = table_name_matches.group(1)
        return table_name
    else:
        table_name_pattern_1 = r'CREATE TABLE `([^`]+)`'
        table_name_matches_1 = re.search(table_name_pattern_1, table)
        if table_name_matches_1:
            table_name = table_name_matches.group(1)
            return table_name
        else:
            return ""
    

def catch_columns_name(table):        
    column_name_pattern = r'"([^"]+)"\s+\w+'
    column_name_matches = re.findall(column_name_pattern, table)
    if column_name_matches:
        column_name = [match.strip() for match in column_name_matches]
        return column_name
    else:
        column_name_pattern_1 = r'`([^`]+)`\s+\w+'
        column_name_matches_1 = re.findall(column_name_pattern_1, table)
        if column_name_matches_1:
            column_name = [match.strip() for match in column_name_matches_1]
            return column_name
        else:
            return []
    

def catch_column_data_type(table,column):
    column_data_type_pattern = r'`{}` (\w+)'.format(column)
    column_data_type_match = re.search(column_data_type_pattern, table)
    if column_data_type_match:
        column_data_type = column_data_type_match.group(1)
        return column_data_type
    else:
        column_data_type_pattern_1 = r'"{}" (\w+)'.format(column)
        column_data_type_match_1 = re.search(column_data_type_pattern_1, table)
        if column_data_type_match_1:
            column_data_type = column_data_type_match_1.group(1)
            return column_data_type
        else:
            return ""

def catch_primary_key_info(table):
    primary_key = ""
    primary_key_pattern = r'PRIMARY KEY \("([^"]+)"'
    primary_key_matches = re.search(primary_key_pattern, table)
    if primary_key_matches:
        primary_key = primary_key_matches.group(1)
        return primary_key
    else:
        primary_key_pattern_1 = r'PRIMARY KEY \(`([^`]+)`'
        primary_key_matches_1 = re.search(primary_key_pattern_1, table)
        if primary_key_matches_1:
            primary_key = primary_key_matches.group(1)
            return primary_key
        else:
            return ""
    

def catch_foreign_keys_info(table):
    keys_info = []
    self_foreign_key_column_pattern = r'FOREIGN KEY \("([^"]+)"'
    self_foreign_key_column_matches = re.findall(self_foreign_key_column_pattern, table)
    if self_foreign_key_column_matches:
        for key in self_foreign_key_column_matches:
            reference_table_pattern = r'FOREIGN KEY \("{}"\) REFERENCES "([^"]+)"'.format(key)
            reference_table_match = re.search(reference_table_pattern, table)
            if reference_table_match:
                reference_table = reference_table_match.group(1)
                reference_table_column_pattern = r'FOREIGN KEY \("{}"\) REFERENCES "{}" \("([^"]+)"'.format(key,reference_table)
                reference_table_column_match = re.search(reference_table_column_pattern, table)
                if reference_table_column_match:
                    reference_table_column = reference_table_column_match.group(1)
                    keys_info.append([key,reference_table,reference_table_column])
                else:
                    reference_table_column = ""
            else:
                reference_table = ""
        return keys_info
    else:
        self_foreign_key_column_pattern_1 = r'FOREIGN KEY \(`([^`]+)`'
        self_foreign_key_column_matches_1 = re.findall(self_foreign_key_column_pattern_1, table)
        if self_foreign_key_column_matches_1:
            for key in self_foreign_key_column_matches:
                reference_table_pattern = r'FOREIGN KEY \(`{}`\) REFERENCES `([^`]+)`'.format(key)
                reference_table_match = re.search(reference_table_pattern, table)
                if reference_table_match:
                    reference_table = reference_table_match.group(1)
                    reference_table_column_pattern = r'FOREIGN KEY \(`{}`\) REFERENCES `{}` \(`([^`]+)`'.format(key,reference_table)
                    reference_table_column_match = re.search(reference_table_column_pattern, table)
                    if reference_table_column_match:
                        reference_table_column = reference_table_column_match.group(1)
                        keys_info.append([key,reference_table,reference_table_column])
                    else:
                        reference_table_column = ""
                else:
                    reference_table = ""
            return keys_info
        else:
            return ""





def get_final_sql(response):
    pattern = r'\[final sql\]:\s*(.*?);'
    matches = re.search(pattern, response, re.DOTALL)
    
    pattern_2 = r'\[final sql\]: \s*(.*?);'
    matches_2 = re.search(pattern_2, response, re.DOTALL)
    
    if matches:
        final_sql = matches.group(1)
        final_sql = final_sql.replace('\n', ' ')
        if "sql" in final_sql:
            pattern = r"(?<=```sql).*"
            matches = re.search(pattern, final_sql, re.DOTALL)
            if matches:
                final_sql = matches.group(0)
                final_sql = final_sql.replace('\n', ' ')
                return final_sql
            else:
                final_sql = ""
    else:
        final_sql = ""
    
    if matches_2:
        final_sql = matches_2.group(1)
        final_sql = final_sql.replace('\n', ' ')
        if "sql" in final_sql:
            pattern = r"(?<=```sql).*"
            matches = re.search(pattern, final_sql, re.DOTALL)
            if matches:
                final_sql = matches.group(0)
                final_sql = final_sql.replace('\n', ' ')
                return final_sql
            else:
                final_sql = ""
        
    return final_sql
    
def get_missing_info(response):
    pattern = r'\[missing information\]:\s*(.*?)$'
    matches = re.search(pattern, response, re.DOTALL)
    if matches:
        missing_info = matches.group(1)
        missing_info = missing_info.replace('\n', ' ')
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
    print(start_index)

    useful_columns = response[start_index:]
    print(useful_columns)
    column_names = re.findall(r"'(.*?)'", useful_columns)
    return column_names

def get_decompose_correct_or_not(response):
    if "yes" in response:
        return "Success", 1
    elif "no" in response:
        return "Success", 0
    else:
        return "Fail", 0