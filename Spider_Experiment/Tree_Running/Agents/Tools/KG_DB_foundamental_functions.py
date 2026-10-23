from Tree_Running.paths import PROJECT_ROOT
import sqlite3
import pandas as pd
import re
import traceback
import os
import copy

current_file_path = os.path.dirname(os.path.abspath(__file__))
project_file_path = str(PROJECT_ROOT)

dkg_file = os.path.join(current_file_path, 'Database_kg.txt')

def get_data_from_database(db_id, sql_code):
    db_path = os.path.join(project_file_path, 'spider', 'test_database', db_id, db_id + '.sqlite')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute(sql_code)
        result = cursor.fetchall()
        df = pd.DataFrame(result, columns=[i[0] for i in cursor.description])
        return df
    except Exception as e:
        bug = traceback.format_exc()
        return bug
    
# X = get_data_from_database("SELECT * FROM Spot_china_gold JOIN Spot_china_silver ON Spot_china_gold.time = Spot_china_silver.time JOIN Spot_china_copper ON Spot_china_gold.time = Spot_china_copper.time")
# print(X)

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
    
def read_KG_from_file(filename):
    KG = []
    with open(filename, 'r') as file:
        for line in file:
            # Remove the square brackets and split by comma
            triplet = [item.strip() for item in line.strip().replace("[", "").replace("]", "").split(',')]
            KG.append(triplet)
    return KG
KG = read_KG_from_file(dkg_file)  

# This function call will read your KG.txt and store each line as a list in KG
def find_paths(entity, kgs, current_path=None):
    if current_path is None:
        current_path = []

    # Find matches where the head of the KG matches the current entity
    #matches = [kg for kg in kgs if kg[0] == entity]
    pattern = re.compile(r'\b' + re.escape(entity.lower()) + r'\b')

    matches = [kg for kg in kgs if pattern.search(kg[0].lower())]
    

    # If no matches found, just return the current path as a list of paths
    if not matches:
        return [current_path]

    paths = []
    for match in matches:
        # Create a new path extending from the current path
        new_path = current_path + [match]
        paths.extend(find_paths(match[2], kgs, new_path))

    return paths

def build_tree(paths, limit = 0):
    # limit: only longest
    # Find the longest length among the paths
    #max_length = max(len(path) for path in paths)
    #print(max_length)
    # Filter out the longest path(s)
    #longest_paths = [path for path in paths if len(path) == max_length - limit]
    #pprint.pprint(longest_paths)
    #tree = defaultdict(dict)
    tree = {}

    def add_path_to_tree(node, path):
        if not path:
            return
        src, rel, dest = path[0]
        if src not in node:
            node[src] = {}
        if rel not in node[src]:
            node[src][rel] = {}
        if dest not in node[src][rel]:
            node[src][rel][dest] = {}
        add_path_to_tree(node[src][rel][dest], path[1:])

    for path in paths:
    #for path in longest_paths:
        add_path_to_tree(tree, path)

    return tree

def get_paths_dict(entities_list):
    paths_dict = {}
    
    for entity in entities_list:
        path = find_paths(entity, KG)

        path_tree = build_tree(paths = path)
        paths_dict[entity] = path_tree
    return paths_dict

def read_create_table_messages(file_path):
    with open(file_path, 'r') as file:
        content = file.read()

    paragraphs = content.split(';')

    print("第一张表：")
    print(paragraphs[0])
    
    return paragraphs

table_created_meaages = read_create_table_messages(os.path.join(current_file_path, 'CREATE_TABLE_MESSAGE.txt'))

def get_table_created_meaages():
    return table_created_meaages

def kg_to_description(kg):
    x = ""
    for k,v in kg.items():
        x = x+str(v)+"\n"
    return x

def if_empty_table_kg(database_info_dict):
    flag = 0
    for k,v in database_info_dict.items():
        if v == {}:
            flag = flag + 1
            
    if flag == len(database_info_dict):
        return 1
    else:
        return 0
    
# columns_needed = ['14_stockmarketindex.time', '14_stockmarketindex.china', '15_housepriceindex.time', '15_housepriceindex.china']
# database_info_dict = get_paths_dict(['14_stockmarketindex','15_housepriceindex'])

# import copy
def split_table_from_columns(columns_needed):
    tables_list = []
    for i in columns_needed:
        i_p = i.split('.')
        if i_p[0] not in tables_list:
            tables_list.append(i_p[0])
    return tables_list

def split_columns_from_columns(table_name, columns_needed):
    columns_list = []
    for i in columns_needed:
        i_p = i.split('.')
        if len(i_p) == 2:
            if table_name == i_p[0]:
                if i_p[1] not in columns_list:
                    columns_list.append(i_p[1])
                else:
                    continue
            else:
                continue
        else:
            continue
    return columns_list

def filter_dict_column(dict_obj, columns_needed):
    if not columns_needed:
        return dict_obj
    
    tables_list = split_table_from_columns(columns_needed)
    dict_obj_tmp = {}
    ans_dict_obj = copy.deepcopy(dict_obj)
    for table in tables_list:
        if table in dict_obj:
            table_columns = split_columns_from_columns(table, columns_needed)
            for column in table_columns:
                if column in dict_obj[table][table]['have_column']:
                    if len(table_columns) != 0:
                        tmp = copy.deepcopy(dict_obj[table][table]['have_column'][column])
                        dict_obj_tmp.update(tmp)
            
            ans_dict_obj[table][table]['have_column'] = copy.deepcopy(dict_obj_tmp)
            dict_obj_tmp = {}
        else:
            dict_obj_tmp = {}
    return ans_dict_obj

def filter_dict_table(dict_obj, tables_needed):
    if not tables_needed:
        return dict_obj
    
    dict_obj_tmp = {}
    for table in tables_needed:
        if table in dict_obj:
            tmp = copy.deepcopy(dict_obj[table][table])
            dict_obj_tmp[table] = tmp
        else:
            continue
    return dict_obj_tmp

# dict_obj = {'23_golden': {'23_golden': {'have_column': {'time': {'data_type': {'datetime': {}, 'date': {}}}, 'spot_london_gold': {'data_type': {'double': {}}}}}}, 
#            '24_silver': {'24_silver': {'have_column': {'time': {'data_type': {'datetime': {}, 'date': {}}}, 'spot_london_silver': {'data_type': {'double': {}}}}}}, 
#            '25_platinum': {'25_platinum': {'have_column': {'time': {'data_type': {'datetime': {}, 'date': {}}}, 'spot_london_platinum': {'data_type': {'double': {}}}}}}, 
#            '26_copper': {'26_copper': {'have_column': {'time': {'data_type': {'datetime': {}, 'date': {}}}}}}, 
#            '27_aluminum': {'27_aluminum': {'have_column': {'time': {'data_type': {'datetime': {}, 'date': {}}}}}}, 
#            '28_zinc': {'28_zinc': {'have_column': {'time': {'data_type': {'datetime': {}, 'date': {}}}}}}, 
#            '29_lead': {'29_lead': {'have_column': {'time': {'data_type': {'datetime': {}, 'date': {}}}}}}, 
#            '30_nickel': {'30_nickel': {'have_column': {'time': {'data_type': {'datetime': {}, 'date': {}}}}}}}
# tables_needed = ['23_golden', '24_silver']
# x = filter_dict_table(dict_obj, tables_needed)
# print(x)


#kg_dict: dict
def get_table_names_from_kg_dict(kg_dict):
    if isinstance(kg_dict, dict):
        table_names_in_kg_dict = []
        for k,v in kg_dict.items():
            table_names_in_kg_dict.append(k)
        flag = 1
        return flag, table_names_in_kg_dict
    else:
        print("kg_dict type wrong, there needs dict!")
        return 0, []

#tables_needed: list
#kg_tables: list
#kg_dict: dict
def get_goal_related_kg_dict(tables_needed, kg_tables, kg_dict):
    if not tables_needed:
        return kg_dict
    
    kg_dict_needed = {}
    for i in tables_needed:
        if i in kg_tables:
            tmp = copy.deepcopy(kg_dict[i])
            kg_dict_needed.update(tmp)
        else:
            continue
    return kg_dict_needed
    
    