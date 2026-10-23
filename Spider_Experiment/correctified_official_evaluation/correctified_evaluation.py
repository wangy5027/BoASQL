import sqlite3
import pandas as pd
import re
import traceback
import os
import csv
import time
import sys
import chardet
from func_timeout import func_set_timeout
from process_sql import get_schema, Schema, get_sql
from tabulate import tabulate

current_file_path = os.path.dirname(os.path.abspath(__file__))
upper_file_path = os.path.dirname(current_file_path)
print(upper_file_path)

#######Level of difficulty(Spider)#######
CLAUSE_KEYWORDS = ('select', 'from', 'where', 'group', 'order', 'limit', 'intersect', 'union', 'except')
JOIN_KEYWORDS = ('join', 'on', 'as')

WHERE_OPS = ('not', 'between', '=', '>', '<', '>=', '<=', '!=', 'in', 'like', 'is', 'exists')
UNIT_OPS = ('none', '-', '+', "*", '/')
AGG_OPS = ('none', 'max', 'min', 'count', 'sum', 'avg')
TABLE_TYPE = {
    'sql': "sql",
    'table_unit': "table_unit",
}

COND_OPS = ('and', 'or')
SQL_OPS = ('intersect', 'union', 'except')
ORDER_OPS = ('desc', 'asc')


HARDNESS = {
    "component1": ('where', 'group', 'order', 'limit', 'join', 'or', 'like'),
    "component2": ('except', 'union', 'intersect')
}

def get_nestedSQL(sql):
    nested = []
    for cond_unit in sql['from']['conds'][::2] + sql['where'][::2] + sql['having'][::2]:
        if type(cond_unit[3]) is dict:
            nested.append(cond_unit[3])
        if type(cond_unit[4]) is dict:
            nested.append(cond_unit[4])
    if sql['intersect'] is not None:
        nested.append(sql['intersect'])
    if sql['except'] is not None:
        nested.append(sql['except'])
    if sql['union'] is not None:
        nested.append(sql['union'])
    return nested

def has_agg(unit):
    return unit[0] != AGG_OPS.index('none')

def count_agg(units):
    return len([unit for unit in units if has_agg(unit)])

def count_component1(sql):
    count = 0
    if len(sql['where']) > 0:
        count += 1
    if len(sql['groupBy']) > 0:
        count += 1
    if len(sql['orderBy']) > 0:
        count += 1
    if sql['limit'] is not None:
        count += 1
    if len(sql['from']['table_units']) > 0:  # JOIN
        count += len(sql['from']['table_units']) - 1

    ao = sql['from']['conds'][1::2] + sql['where'][1::2] + sql['having'][1::2]
    count += len([token for token in ao if token == 'or'])
    cond_units = sql['from']['conds'][::2] + sql['where'][::2] + sql['having'][::2]
    count += len([cond_unit for cond_unit in cond_units if cond_unit[1] == WHERE_OPS.index('like')])

    return count


def count_component2(sql):
    nested = get_nestedSQL(sql)
    return len(nested)


def count_others(sql):
    count = 0
    # number of aggregation
    agg_count = count_agg(sql['select'][1])
    agg_count += count_agg(sql['where'][::2])
    agg_count += count_agg(sql['groupBy'])
    if len(sql['orderBy']) > 0:
        agg_count += count_agg([unit[1] for unit in sql['orderBy'][1] if unit[1]] +
                            [unit[2] for unit in sql['orderBy'][1] if unit[2]])
    agg_count += count_agg(sql['having'])
    if agg_count > 1:
        count += 1

    # number of select columns
    if len(sql['select'][1]) > 1:
        count += 1

    # number of where conditions
    if len(sql['where']) > 1:
        count += 1

    # number of group by clauses
    if len(sql['groupBy']) > 1:
        count += 1

    return count

def eval_hardness(sql):
    # g_sql = get_sql(schema, g_str)
    count_comp1_ = count_component1(sql)
    count_comp2_ = count_component2(sql)
    count_others_ = count_others(sql)

    if count_comp1_ <= 1 and count_others_ == 0 and count_comp2_ == 0:
        return "easy"
    elif (count_others_ <= 2 and count_comp1_ <= 1 and count_comp2_ == 0) or \
            (count_comp1_ <= 2 and count_others_ < 2 and count_comp2_ == 0):
        return "medium"
    elif (count_others_ > 2 and count_comp1_ <= 2 and count_comp2_ == 0) or \
            (2 < count_comp1_ <= 3 and count_others_ <= 2 and count_comp2_ == 0) or \
            (count_comp1_ <= 1 and count_others_ == 0 and count_comp2_ <= 1):
        return "hard"
    else:
        return "extra"

####### Obtain SQL operation result#######

@func_set_timeout(5)
def get_data_from_database(db_id, sql_code):
    db_path = os.path.join(upper_file_path, 'spider', 'test_database', db_id, db_id + '.sqlite')
    conn = sqlite3.connect(db_path)
    conn.text_factory = lambda x : str(x, 'gbk', 'ignore')
    cursor = conn.cursor()
    try:
        cursor.execute(sql_code)
        result = cursor.fetchall()
        df = pd.DataFrame(result, columns=[i[0] for i in cursor.description])
        return df
    except Exception as e:
        bug = traceback.format_exc()
        return str(bug)

def extract_file_index(file_name):
    # Extract the numeric part using regular expressions
    match = re.search(r"\d+", file_name)
    if match:
        selected = match.group()
        return selected    

def if_last_letter_(file_name):
    name_letter_list = [i for i in file_name]
    if name_letter_list[-1] == "_":
        return True
    else:
        return False

def if_subset_len(target_file, project_file):
    csv_data_gold = csv.reader(target_file)
    csv_data_predict = csv.reader(project_file)
                
    next(csv_data_gold)
    next(csv_data_predict)
                
    # Replace spaces with empty strings
    csv_data_gold = [[col.replace(' ', '') for col in row] for row in csv_data_gold]
    csv_data_predict = [[col.replace(' ', '') for col in row] for row in csv_data_predict]
                
    # Lower
    csv_data_gold = [[col.lower() for col in row] for row in csv_data_gold]
    csv_data_predict = [[col.lower() for col in row] for row in csv_data_predict]
        
    len_csv_data_gold = len(csv_data_gold)
    len_csv_data_predict = len(csv_data_predict)
        
    csv_data_gold = sorted([item for sublist in list(csv_data_gold) for item in sublist])
    csv_data_predict = sorted([item for sublist in list(csv_data_predict) for item in sublist])

    is_subset = set(csv_data_gold).issubset(set(csv_data_predict))
    
    if is_subset and len_csv_data_gold == len_csv_data_predict:
        return True
    else:
        return False

def if_exactly_same(target_file, project_file):
    csv_data_gold = csv.reader(target_file)
    csv_data_predict = csv.reader(project_file)
                
    next(csv_data_gold)
    next(csv_data_predict)
                
    # Replace spaces with empty strings
    csv_data_gold = [[col.replace(' ', '') for col in row] for row in csv_data_gold]
    csv_data_predict = [[col.replace(' ', '') for col in row] for row in csv_data_predict]
                
    # Lower
    csv_data_gold = [[col.lower() for col in row] for row in csv_data_gold]
    csv_data_predict = [[col.lower() for col in row] for row in csv_data_predict]
        
    csv_data_gold = sorted([item for sublist in list(csv_data_gold) for item in sublist])
    csv_data_predict = sorted([item for sublist in list(csv_data_predict) for item in sublist])

    if csv_data_gold == csv_data_predict:
        return True
    else:
        return False
       
def obtain_predict_csv(predict_file_path, gold_file_path, project_name): 
    
    predict_folder_path = os.path.join(current_file_path, project_name + '_predict_ouput')
    if not os.path.exists(predict_folder_path):
        # Create the new folder
        os.makedirs(predict_folder_path)
        print("Folder created successfully.")
    else:
        print("Folder already exists.")
    
    predict_list = []
    with open(predict_file_path, 'r') as file:
        for line in file:
            predict_list.append(line)
    
    with open(gold_file_path, 'r') as file:
        index = 0
        for line in file:
            line = line.strip()  # Remove leading/trailing whitespaces
            print(line)
            sql_code, database_name = line.split('\t')
            db = os.path.join(upper_file_path, 'spider', 'test_database', database_name, database_name + '.sqlite')
            schema = Schema(get_schema(db))
            g_sql = get_sql(schema, sql_code)
            level = eval_hardness(g_sql)
            
            try:
                predict_df = get_data_from_database(database_name, predict_list[index])
            except:
                predict_df = "time exceed"
                
            if type(predict_df) == type("str"):
                txt_name = str(index) + '_' + level + '_txt_output.txt'
                file_path = os.path.join(predict_folder_path, level, txt_name)
                if not os.path.exists(os.path.join(predict_folder_path, level)):
                    os.makedirs(os.path.join(predict_folder_path, level))

                with open(file_path, "w") as file:
                    file.write(predict_df)
                index += 1
                # break
            else:
                # print("yes")
                # print(predict_df)
                csv_name = str(index) + '_' + level + '_target_output.csv'
                # print(csv_name)
                file_path = os.path.join(predict_folder_path, level, csv_name)
                if not os.path.exists(os.path.join(predict_folder_path, level)):
                    os.makedirs(os.path.join(predict_folder_path, level))
                predict_df.to_csv(file_path, index=False)
                index += 1

#######Correctified EX#######
def correctified_eval_result(predict_file_path, gold_file_path,project_name):
    correctified_dev_target_output_path = os.path.join(current_file_path, 'Correctified_Spider_dev_target_ouput')
    project_path = os.path.join(current_file_path, project_name + '_predict_ouput')
    hardness_levels = ['easy','medium','hard','extra']
    hardness_ex = {'easy': 0, 'medium': 0, 'hard': 0, 'extra': 0, 'overall': 0}
    
    wrong_list = []
    
    for hardness in hardness_levels:
        target_folder_path = os.path.join(correctified_dev_target_output_path, hardness)
        project_folder_path = os.path.join(project_path, hardness)
        
        try:
            project_file_list = os.listdir(project_folder_path)
        except:
            obtain_predict_csv(predict_file_path, gold_file_path, project_name)
            project_file_list = os.listdir(project_folder_path)
            
        project_file_list = sorted(project_file_list, key=lambda x: int(re.search(r"\d+", x).group()))
        
        target_upper_folder_list = os.listdir(target_folder_path)
        for upper in target_upper_folder_list:
            target_file_path = os.path.join(target_folder_path, upper)
            target_thisfolder_file_list = os.listdir(target_file_path)
            subset_len_or_exactly = if_last_letter_(upper)
            index = extract_file_index(upper)
            key = 0
            for target_file in target_thisfolder_file_list:
 
                current_target_file_path = os.path.join(target_file_path, target_file)
                with open(current_target_file_path, 'rb') as f:
                        target_result = chardet.detect(f.read())
                target_encoding = target_result['encoding']
                current_target_file = open(current_target_file_path, 'r', errors=None, encoding=target_encoding)

                current_project_file_path = os.path.join(project_folder_path, index + '_' + hardness + '_target_output.csv')
                try:
                    with open(current_project_file_path, 'rb') as f:
                            project_result = chardet.detect(f.read())
                    project_encoding = project_result['encoding'] 
                    current_project_file = open(current_project_file_path, 'r', errors=None, encoding=project_encoding)
                    
                    if subset_len_or_exactly:
                        if if_subset_len(current_target_file, current_project_file):
                            key += 1
                        else:
                            key += 0
                    else:
                        if if_exactly_same(current_target_file, current_project_file):
                            key += 1
                        else:
                            key += 0
                except:
                    key += 0
            if key > 0:
                if hardness == "easy":
                    hardness_ex["easy"] += round(1/245, 3) * 100
                elif hardness == "medium":
                    hardness_ex["medium"] += round(1/446, 3) * 100
                elif hardness == "hard":
                    hardness_ex["hard"] += round(1/173, 3) * 100
                elif hardness == "extra":
                    hardness_ex["extra"] += round(1/169, 3) * 100
            else:
                wrong_list.append(target_file)
                if hardness == "easy":
                    hardness_ex["easy"] -= round(1/245, 3) * 100
                elif hardness == "medium":
                    hardness_ex["medium"] -= round(1/446, 3) * 100
                elif hardness == "hard":
                    hardness_ex["hard"] -= round(1/173, 3) * 100
                elif hardness == "extra":
                    hardness_ex["extra"] -= round(1/169, 3) * 100
    
    hardness_ex["overall"] = round(245/1034*hardness_ex["easy"] + 446/1034*hardness_ex["medium"] + 173/1034*hardness_ex["hard"] + 169/1034*hardness_ex["extra"], 1)
    return hardness_ex, wrong_list

def main(predict_file_path, gold_file_path, project_name):
    if predict_file_path and gold_file_path and project_name:
        hardness_ex, wrong_list = correctified_eval_result(predict_file_path, gold_file_path,project_name)
        table_data = [project_name]
        for hard_level, scores in hardness_ex.items():
            table_data.append(scores)
        table = [table_data]
        print("========================================================================")
        print("The official ex should be modified according to the following outcome:")
        print(tabulate(table, headers=['EASY', 'MEDIUM', "HARD", "EXTRA", "OVERALL"]))
        # print("*** The wrong instances are:")
        # print(wrong_list)
    else:
        print("Please make sure you have input the predict_file_path, gold_file_path, and project name accordingly.!!!")

if __name__ == "__main__":
    if len(sys.argv) == 4:
        predict_file_path = sys.argv[1]
        gold_file_path = sys.argv[2]
        project_name = sys.argv[3]
        main(predict_file_path, gold_file_path, project_name)
    else:
        print(len(sys.argv))
        print("Please make sure you have input the predict_file_path, gold_file_path, and project name accordingly.")
