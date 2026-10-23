import sqlite3
import pandas as pd
import re
import traceback
import os
import csv
import time
from func_timeout import func_set_timeout
from process_sql import get_schema, Schema, get_sql


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

def obtain_gold_csv(gold_file_path, project_name): 
    gold_folder_path = os.path.join(current_file_path, project_name + '_target_ouput')
    if not os.path.exists(gold_folder_path):
        # Create the new folder
        os.makedirs(gold_folder_path)
        print("Spider Gold Folder created successfully.")
    else:
        print("Folder already exists.")

    with open(gold_file_path, 'r') as file:
        index = 0
        for line in file:
            line = line.strip()  # Remove leading/trailing whitespaces
            sql_code, database_name = line.split('\t')
            
            db = os.path.join(upper_file_path, 'spider', 'test_database', database_name, database_name + '.sqlite')
            schema = Schema(get_schema(db))
            g_sql = get_sql(schema, sql_code)
            level = eval_hardness(g_sql)

            # Print the SQL code and database name
            print("SQL Code:", sql_code)
            print("Database Name:", database_name)
            try:
                df = get_data_from_database(database_name, sql_code)
            except:
                df = "time exceed"
            if type(df) == type("str"):
                print("wrong")
                print(df)
                txt_name = str(index) + '_' + level + '_txt_output.txt'
                file_path = os.path.join(gold_folder_path, level, txt_name)
                if not os.path.exists(file_path):
                    os.makedirs(file_path)
                with open(file_path, "w") as file:
                    file.write(df)
                index += 1
            else:
                print("yes")
                print(df)
                csv_name = str(index) + '_' + level + '_target_output.csv'
                print(csv_name)
                file_path = os.path.join(gold_folder_path, level, csv_name)
                if not os.path.exists(os.path.join(gold_folder_path, level)):
                    os.makedirs(os.path.join(gold_folder_path, level))
                df.to_csv(file_path, index=False)
                index += 1
                
def obtain_predict_csv(gold_file_path, predict_file_path, project_name): 
    
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

#######Three Metrics#######
# ER rate
def ER_rate(project_name):
    predict_folder_path = os.path.join(current_file_path, project_name + '_predict_ouput')
    hardness_levels = ['easy','medium','hard','extra']
    hardness_ers = {'easy': 0, 'medium': 0, 'hard': 0, 'extra': 0}

    for i in hardness_levels:
        hardness_predict_folder_path = os.path.join(predict_folder_path, i)
        # Get the list of files in the directory
        file_list = os.listdir(hardness_predict_folder_path)

        # Count the number of CSV files
        csv_count = 0
        for file in file_list:
            if file.endswith('.csv'):
                csv_count += 1
        # Count the number of files
        all_count = len(file_list)
        
        er = csv_count / all_count
        hardness_ers[i]= er
    
    for k,v in hardness_ers.items():
        print("ER of", k, ":", v)
    return hardness_ers

def extract_file_index(file_name):
    # Extract the numeric part using regular expressions
    match = re.search(r"\d+", file_name)
    if match:
        selected = match.group()
        return selected           
            
# PR rate
def PR_rate(project_name):
    hardness_levels = ['easy','medium','hard','extra']
    hardness_prs = {'easy': 0, 'medium': 0, 'hard': 0, 'extra': 0, 'overall': 0}

    sum_pass_count = 0
    sum_instance_count = 0
    unmatch_list_1 = []
    unmatch_list_2 = []
    for i in hardness_levels:
        
        predict_csv_folder_path = os.path.join(current_file_path, project_name + '_predict_ouput', i)
        gold_csv_folder_path = os.path.join(current_file_path, project_name + '_target_ouput', i)
        predict_file_list = os.listdir(predict_csv_folder_path)
        predict_file_names = [file for file in predict_file_list if os.path.isfile(os.path.join(predict_csv_folder_path, file))]
        predict_file_names = sorted(predict_file_names, key=lambda x: int(re.search(r"\d+", x).group()))

        gold_file_list = os.listdir(gold_csv_folder_path)
        gold_file_names = [file for file in gold_file_list if os.path.isfile(os.path.join(gold_csv_folder_path, file))]
        gold_file_names = sorted(gold_file_names, key=lambda x: int(re.search(r"\d+", x).group()))
        
        #     results = str(gold_file_names)
        #     file.write(results)
        if len(gold_file_list) == len(predict_file_list):
            pass_count = 0
            for gold_file in gold_file_names:
                current_gold_file_path = os.path.join(gold_csv_folder_path, gold_file)
                current_gold_file = open(current_gold_file_path, 'r', errors=None, encoding='utf-8')
                index = re.findall("\d+\.?\d*", gold_file)
                current_predict_file_path = os.path.join(predict_csv_folder_path, index[0] + '_' + i + '_' + 'target_output.csv')
                try:
                    current_predict_file = open(current_predict_file_path, 'r', errors=None, encoding='utf-8')
                except:
                    current_predict_file_path = os.path.join(predict_csv_folder_path, index[0] + '_' + i + '_' + 'target_output.txt')
                
                csv_data_gold = csv.reader(current_gold_file)
                if "txt" not in current_predict_file_path:
                    csv_data_predict = csv.reader(current_predict_file)
                            
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
                    # Compare the content of the CSV files
                    # if is_subset:
                    if is_subset and len_csv_data_gold == len_csv_data_predict:
                    # if csv_data_gold == csv_data_predict:
                        pass_count += 1
                    else:
                        unmatch_list_1.append(gold_file)
                        unmatch_list_2.append(index[0] + "_" + i + "_" + "target_output.csv")
                else:
                    unmatch_list_1.append(gold_file)
                    unmatch_list_2.append(index[0] + "_" + i + "_" + "target_output.csv")
        else:
            pass_count = 0
            print("您提供的predict和gold的实例总数不同，请检查所提供的文件")
        
        pr = pass_count / len(gold_file_names)
        hardness_prs[i]= pr
        sum_pass_count += pass_count
        sum_instance_count += len(gold_file_names)
    
    hardness_prs['overall'] = sum_pass_count / sum_instance_count
    
    for k,v in hardness_prs.items():
        print("PR of", k, ":", v)
    return hardness_prs, unmatch_list_1, unmatch_list_2


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Summarize previously generated evaluation outputs.")
    parser.add_argument("project_name", help="Prefix of existing target/prediction output directories")
    args = parser.parse_args()
    er_dict = ER_rate(args.project_name)
    pr, unmatch_list_1, unmatch_list_2 = PR_rate(args.project_name)
    print(er_dict)
    print(pr)
