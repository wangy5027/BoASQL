import os
import re

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
            table_name = table_name_matches_1.group(1)
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
            primary_key = primary_key_matches_1.group(1)
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
                reference_table_column_pattern = r'FOREIGN KEY \("{}"\) REFERENCES "{}"\("([^"]+)"'.format(key,reference_table)
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
table = """
CREATE TABLE "countries" (
	"CountryId" INTEGER PRIMARY KEY, 
	"CountryName" TEXT, 
	"Continent" INTEGER,
	FOREIGN KEY ("Continent") REFERENCES "continents"("ContId")
);
"""
catch_foreign_keys_info(table)

def build_columns_basic_knowledge(table_list):
    columns_basic_knowledge = []
    for table in table_list:
        table_name = catch_table_name(table)
        column_name = catch_columns_name(table)
        if table_name and column_name:
            for column in column_name:
                data_type = catch_column_data_type(table,column)
                column_data_type_info_tmp = str(column)+", data_type, "+str(data_type)
                print(column_data_type_info_tmp)
                columns_basic_knowledge.append(column_data_type_info_tmp)
    return columns_basic_knowledge

def build_table_column_knowledge(table_list):
    table_column_knowledge = []
    for table in table_list:
        table_name = catch_table_name(table)
        column_name = catch_columns_name(table)
        if table_name and column_name:
            for column in column_name:
                table_column_knowledge_tmp = str(table_name)+", have_column, "+str(column)
                print(table_column_knowledge_tmp)
                table_column_knowledge.append(table_column_knowledge_tmp)
    return table_column_knowledge

def build_table_key_knowledge(table_list):
    table_key_knowledge = []
    for table in table_list:
        table_name = catch_table_name(table)
        if table_name:
            primary_key_info = catch_primary_key_info(table)
            foreign_keys_info = catch_foreign_keys_info(table)

            if primary_key_info:
                table_key_knowledge_tmp = str(table_name)+", have_primary_key, "+str(primary_key_info)
                table_key_knowledge.append(table_key_knowledge_tmp)
            if foreign_keys_info:
                for i in foreign_keys_info:
                    table_key_knowledge_tmp_1 = str(table_name)+", have_foreign_key, "+str(i[0])
                    table_key_knowledge_tmp_2 = str(i[0])+", reference_to, "+str(i[1])+"'s column "+str(i[2])
                    table_key_knowledge.append(table_key_knowledge_tmp_1)
                    table_key_knowledge.append(table_key_knowledge_tmp_2)
    
    for i in table_key_knowledge:
        print(i)
    return table_key_knowledge

def read_create_table_messages(file_path):

    with open(file_path, 'r') as file:
        content = file.read()

    paragraphs = content.split(';')

    print("第一张表：")
    print(paragraphs[0])
    
    return paragraphs

def write_c_t_m_file(table_list, project_path):
    old_c_t_m_file_path_1 = os.path.join(project_path, 'Tree_Running', 'Tree_Building', 'Agents', 'Tools', 'CREATE_TABLE_MESSAGE.txt')
    old_c_t_m_file_path_2 = os.path.join(project_path, 'Tree_Running', 'Agents', 'Tools', 'CREATE_TABLE_MESSAGE.txt')
    with open(old_c_t_m_file_path_1, "w") as file:
        for i in table_list:
            file.write(i + ";\n")
    file.close()
    
    with open(old_c_t_m_file_path_2, "w") as file:
        for i in table_list:
            file.write(i + ";\n")
    file.close()
    print("Congradulations, your create_table_message is updated!")

def write_kg_file(table_list, path):
    columns_basic_knowledge = build_columns_basic_knowledge(table_list)
    table_column_knowledge = build_table_column_knowledge(table_list)
    table_key_knowledge = build_table_key_knowledge(table_list)
    with open(path, "w") as file:
        for i in columns_basic_knowledge:
            file.write("["+i + "]\n")
        for i in table_column_knowledge:
            file.write("["+i + "]\n")
        for i in table_key_knowledge:
            file.write("["+i + "]\n")
    file.close()
    print("Congradulations, your local db kg is finished!")