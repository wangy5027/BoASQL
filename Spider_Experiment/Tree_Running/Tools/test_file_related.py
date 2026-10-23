from Tree_Running.paths import PROJECT_ROOT
import json
import re
import os
import subprocess
import sys

current_directory = os.path.dirname(os.path.abspath(__file__))
project_path = str(PROJECT_ROOT)
print(project_path)
test_file_path = os.path.join(project_path, 'spider', 'dev.json')
test_database_path = os.path.join(project_path, 'spider', 'test_database')

def read_json_file(queries_file):
    with open(queries_file, 'r') as file:
        data = json.load(file)
    return data

def get_test_queries_data():
    test_file = read_json_file(test_file_path)
    return test_file

def get_test_db_id_query_question(test_file_object):
    db_id = ""
    query = ""
    question = ""
    for k,v in test_file_object.items():
        if k == 'db_id':
            db_id = v
            continue
        elif k == 'query':
            query = v
            continue
        elif k == 'question':
            question = v
            break
    return db_id, query, question

def write_gold_txt_file(query, db_id):
    gold_content = query + '\t' + db_id + '\n'
    gold_text_path = os.path.join(project_path, 'DEV_gold.txt')
    with open(gold_text_path, 'a') as file:
        file.write(gold_content)
        
def write_predict_txt_file(predict):
    gold_content = predict + '\n'
    predict_text_path = os.path.join(project_path, 'DEV_predict.txt')
    with open(predict_text_path, 'a') as file:
        file.write(gold_content)
        
def write_predict_txt_file_tmp(predict):
    gold_content = predict + '\n'
    predict_text_path = os.path.join(project_path, 'DEV_predict_tmp.txt')
    with open(predict_text_path, 'a') as file:
        file.write(gold_content)
        
def write_question_txt_file(index, question):
    question_content = str(index) + ' ' + question + '\n'
    question_text_path = os.path.join(project_path, 'DEV_question.txt')
    with open(question_text_path, 'a') as file:
        file.write(question_content)

def write_ini_table_message_file(pure_schema):
    ini_table_message_file_path = os.path.join(project_path, 'DB-KG-Initialization', 'CREATE_TABLE_MESSAGE.txt')
    with open(ini_table_message_file_path, 'w') as file:
        file.write(pure_schema)

def select_pure_schema(schema_text):
    create_commands = re.findall(r'CREATE TABLE[^;]+;', schema_text)
    commands = ""
    # Print the CREATE commands
    for command in create_commands:
        commands = commands + "\n\n" + command
    return commands
    
def get_sql_schema(db_id):
    schema_path = os.path.join(project_path, 'spider', 'test_database', db_id, 'schema.sql')
    with open(schema_path, 'r', encoding='utf-8') as file:
        schema_text = file.read()
    pure_schema = select_pure_schema(schema_text)
    return pure_schema

def read_kg_file():
    kg_file_path = os.path.join(project_path, 'DB-KG-Initialization', 'Database_kg.txt')
    with open(kg_file_path, 'r') as file:
        file_contents = file.read()
    if len(file_contents) < 2:
        return False
    else:
        return True
        
def change_kg(db_id):
    pure_schema = get_sql_schema(db_id)
    write_ini_table_message_file(pure_schema)
    ini_kg_tool_path = PROJECT_ROOT / 'DB-KG-Initialization' / 'Get_local_db_kg.py'
    subprocess.run([sys.executable, str(ini_kg_tool_path)], check=True)
    
    kg_file_success_or_not = read_kg_file()
    return kg_file_success_or_not

def tree_to_dict(tree):
    tree_dict = {}

    def traverse(node):
        current_key = str(node.identifier)
        current_value = {"tag": node.tag, "data": node.data}

        parent_node = tree.parent(node.identifier)
        if parent_node is not None:
            current_value["parent"] = str(parent_node.identifier)
        else:
            current_value["parent"] = None

        children = []
        for child_id in node.fpointer:
            child_node = tree.get_node(child_id)
            children.append(traverse(child_node))

        current_value["children"] = children
        tree_dict[current_key] = current_value

        return current_value

    root_node = tree.get_node(tree.root)
    traverse(root_node)

    return tree_dict

def write_tree_to_json_file(tree):
    tree_dict = tree_to_dict(tree)
    file_path = os.path.join(project_path, 'trees.json')
    with open(file_path, "a") as file:
        json.dump(tree_dict, file, indent=4)
    
# Example usage

# tree = treelib.Tree()
# tree.create_node("Root", "root", data = "root")
# tree.create_node("Child 1", "child1", parent="root", data = "child1")
# tree.create_node("Child 2", "child2", parent="root", data = "child2")
# tree.create_node(tag = "Grandchild", identifier = "grandchild", parent="child1", data = "grandchild")
# tree_dict = tree_to_dict(tree)

# # Write the tree dictionary to a JSON file
#     json.dump(tree_dict, file, indent=4)

# print("Tree successfully written to JSON file.")
# test_file = get_test_queries_data()   
# db_id, query, question = get_test_db_id_query_question(test_file[0])
# write_gold_txt_file(query, db_id)
# change_kg(db_id)





