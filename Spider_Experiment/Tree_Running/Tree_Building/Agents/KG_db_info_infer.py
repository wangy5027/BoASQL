from Tree_Running.Tree_Building.Agents.agents_init import *
from Tree_Running.Tree_Building.Agents.Tools.zhengze import *
from Tree_Running.Tree_Building.Agents.Tools.KG_DB_foundamental_functions import *

# from Tree_Building.Agents.agents_init import *
# from Tree_Building.Agents.Tools.zhengze import *
# from Tree_Building.Agents.Tools.KG_DB_foundamental_functions import *


table_created_meaages = get_table_created_meaages()

catch_tables_names_prompt = """
You are now my personal human assistant, I'm going to give you a goal and several tables, you need to think step by step, abd help me find the tables that may be used when accomplishing the goal. As you only know the table name, to make sure all needed tables are included, you should think more carefully and return all the relevant tables.  for each [goal] provided below, extract and list the tables that might be used.

Input:
[goal]:The goal that should be accomplished,given externally.
[tables]:All the data tables that are provided in the database, given externally.

Output:
[thinking]:Your thinking about related tables.
[related tables]:The list of related tables.

warn:
1. Reply in strict accordance with format requirements above.
2. Do not repeat the input content.
3. Don't think too much, just return the MOST POSSIBLE answer.
4. Never assume the table names by yourself, if no table is useful, just return the most possible ones.
5. The tables in your respond must be those included in the [tables] in just this round, never generate table name by yourself, and never use the tables from last round.

example:
Input:
[goal]:I want to see the open price of stock 000002 in 20210101
[tables]: ['stock_price', 'stock_info', 'company_risk', 'company_info', 'factor_info'] 

Output:
[thinking]: According to the goal, stock open price and stock number are mentioned. In order to get the stock price and stock number information, 'stock_price' table is the most related one. However, just according to the table name, I cannot make sure that everything you need are included in just one 'stock_price' table, so I recommend you to also look at table 'stock_info' and 'company_info'
[related tables]:['stock_price','stock_info','company_info']
"""
#output variable: tables_needed, list.
def catch_database_info(goal,attempts = 3):
    table_created_meaages = get_table_created_meaages()
    if isinstance(table_created_meaages,list):
        table_names = []
        for table in table_created_meaages:
            table_name = catch_table_name(table)
            table_names.append(table_name)
    else:
        table_names = table_created_meaages
    table_names = list(filter(lambda x: x != '', table_names))
    messages=[{"role": "system", "content": catch_tables_names_prompt}]
    table_agent = LlmAgent(messages=messages)
    response = table_agent.continue_conversation(user_input = "Let's begin:[goal]:"+goal+"/n[tables]:"+str(table_names))
    print(response)
    
    tables_needed = get_related_tables(response)
    tables_needed = list(filter(lambda x: x in table_names, tables_needed))
    
    # if len(tables_needed) == 0:
    #     tables_needed = table_names
    #     flag = 0
    # elif len(tables_needed) < 3:
    #     flag = 0
    # else:
    #     flag = 1
    
    database_info_dict = get_paths_dict(tables_needed)
    if_empty_info_dict = if_empty_table_kg(database_info_dict)
    if attempts > 0:
        if if_empty_info_dict != 1:
            signal = "Sucess"
            # database_info_dict = filter_dict_table(database_info_dict, tables_needed)
            return database_info_dict, signal
        else:
            return catch_database_info(goal, attempts = attempts - 1)
    else:
        signal = "Fail"
        return {}, signal

#kg_dict:dict
def catch_database_info_from_dict(goal, kg_dict, attempts = 3):
    flag, kg_table_names = get_table_names_from_kg_dict(kg_dict)
    if flag == 1:
        messages=[{"role": "system", "content": catch_tables_names_prompt}]
        table_agent = LlmAgent(messages=messages)
        response = table_agent.continue_conversation(user_input = "Let's begin:[goal]:"+goal+"/n[tables]:"+str(kg_table_names))
        print(response)
        
        table_needed_names = get_related_tables(response)
        
        database_info_dict = get_goal_related_kg_dict(table_needed_names, kg_table_names, kg_dict)
        if_empty_info_dict = if_empty_table_kg(database_info_dict)
        
        if attempts > 0:
            if if_empty_info_dict != 1:
                signal = "Sucess"
                return database_info_dict, signal
            else:
                return catch_database_info_from_dict(goal, attempts = attempts - 1)
        else:
            signal = "Fail"
            return {}, signal

select_useful_columns_prompt = """
You are now a professional SQL engineer, I'm going to give you a [database description] and a [task], the [database description] includes the table names and their relevant column information. you need to think step by step, and help me find all the potential columns that may be used when accomplishing the goal. To make sure all potentially needed columns are included, you should think more carefully and return all relevant columns.

Input:
[task]:The goal that should be accomplished,given externally.
[database description]:All the data tables information, given externally.

Output:
[thinking]:Your thinking about useful columns.
[useful columns]:The list of all potential useful columns.

warn:
1. Referring the example below, reply in STRICT accordance with the format requirements.
2. Don't think too much, just return the MOST POSSIBLE answers.
3. Never assume the column names by yourself, if no column in one table is useful, just pass it.
4. Make sure that all columns that may be used are selected, if you cannot make sure, preserve those columns that you cannot make decisions.

example:
Input:
[task]: I want to see the spot London price of gold and silver at 2012-12-12.
[database description]:
{'23_golden': {'have_column': {'time': {'time': {'data_type': {'datetime': {}, 'date': {}}}}, 'spot_china_gold': {'spot_china_gold': {'data_type': {'double': {}}}}, 'spot_london_gold': {'spot_london_gold': {'data_type': {'double': {}}}}, 'futures_china_gold': {'futures_china_gold': {'data_type': {'double': {}}}}, 'futures_comex_gold': {'futures_comex_gold': {'data_type': {'double': {}}}}}}}
{'24_silver': {'have_column': {'time': {'time': {'data_type': {'datetime': {}, 'date': {}}}}, 'spot_china_silver': {'spot_china_silver': {'data_type': {'double': {}}}}, 'spot_london_silver': {'spot_london_silver': {'data_type': {'double': {}}}}, 'futures_china_gold': {'futures_china_gold': {'data_type': {'double': {}}}}, 'futures_comex_silver': {'futures_comex_silver': {'data_type': {'double': {}}}}}}}

Output:
[thinking]: According to the goal, to select the spot London price of gold at 2012-12-12, we need at least a column of time, and a column of spot london gold price.
[useful columns]: '23_golden.time','23_golden.spot_london_gold','24_silver.time','24_silver.spot_london_silver'
"""
def select_useful_columns(flag, goal, related_table_kg_information):
        #final_kg: dict
    # if flag == 1 or flag ==0:
    if flag == 1:
        messages=[{"role": "system", "content": select_useful_columns_prompt}]
        select_useful_columns_agent = LlmAgent(messages=messages)
        response = select_useful_columns_agent.continue_conversation(user_input = "Let's begin:[task]:"+goal+"/n[database description]:"+str(related_table_kg_information))
        print(response)
        useful_columns = get_useful_columns(response)
        if len(useful_columns) != 0:
            final_kg = filter_dict_column(related_table_kg_information,useful_columns)
            for k,v in final_kg.items():
                for k1, v1 in v.items():
                    if len(v1) == 0:
                        return related_table_kg_information
                    else:
                        continue
            return final_kg
        else:
            return related_table_kg_information
    else:
        return related_table_kg_information
    
if_table_useful_prompt = """
Now you are a professional SQL engineer, I'm going to give you a [task] and [tables information] that seems to be useful for accomplishing the task. According to the given [task] and [tables information], tell me the tables that contains effective information to the [task]. your one action should follow the framework below:

input:
[task]: The goal that should be accomplished,given externally.
[tables information]: Relevant descriptions of all possible relevant tables,given externally.

output:
[thinking]: Your thinking about useful columns.
[useful tables]: The list of useful tables.In this part, your answer should be like this :"[useful tables]: ['table_1', 'table_2', 'table_3']"

warn:
1. Don't think too much, just return the MOST POSSIBLE answers.
2. Never assume the table names by yourself, if no table is useful, just return all the tables.
3. Tell me the table name, not column name.
4. Do not modify the original format of the table name, including the case of the letters.
5. When selecting tables, please make sure that all tables that may be used are selected if possible. 
"""

def select_useful_tables(task, ori_kg_dict):
    messages=[{"role": "system", "content": if_table_useful_prompt}]
    check_if_table_useful_agent = LlmAgent(messages=messages)
    response = check_if_table_useful_agent.continue_conversation(user_input = "Let's begin:[task]:"+task+"/n[tables information]:"+str(ori_kg_dict))
    print(response)
    
    useful_tables = get_useful_tables(response)
    if len(useful_tables) < 2:
        flag = 0
    else:
        flag = 1
        
    if len(useful_tables) != 0:
        final_kg = filter_dict_table(ori_kg_dict, useful_tables)
        return flag, final_kg
    else:
        return flag, ori_kg_dict
    # return ori_kg_dict

def Get_kg_inferred_info(goal):
    related_table_kg_information, signal = catch_database_info(goal)
    if signal == "Sucess":
        flag, final_kg = select_useful_tables(goal, related_table_kg_information)
        final_kg = select_useful_columns(flag, goal, final_kg)
        # final_kg = select_useful_columns(flag, goal, related_table_kg_information)
        if final_kg:
            return final_kg, flag, signal
        else:
            return related_table_kg_information, flag, signal
        # return related_table_kg_information, flag, signal
    else:
        return {},flag,signal
    
# ori_kg_dict = {'23_golden': {'23_golden': {'have_column': {'time': {'data_type': {'datetime': {}, 'date': {}}}, 'spot_london_gold': {'data_type': {'double': {}}}}}}, 
#            '24_silver': {'24_silver': {'have_column': {'time': {'data_type': {'datetime': {}, 'date': {}}}, 'spot_london_silver': {'data_type': {'double': {}}}}}}, 
#            '25_platinum': {'25_platinum': {'have_column': {'time': {'data_type': {'datetime': {}, 'date': {}}}, 'spot_london_platinum': {'data_type': {'double': {}}}}}}, 
#            '26_copper': {'26_copper': {'have_column': {'time': {'data_type': {'datetime': {}, 'date': {}}}}}}, 
#            '27_aluminum': {'27_aluminum': {'have_column': {'time': {'data_type': {'datetime': {}, 'date': {}}}}}}, 
#            '28_zinc': {'28_zinc': {'have_column': {'time': {'data_type': {'datetime': {}, 'date': {}}}}}}, 
#            '29_lead': {'29_lead': {'have_column': {'time': {'data_type': {'datetime': {}, 'date': {}}}}}}, 
#            '30_nickel': {'30_nickel': {'have_column': {'time': {'data_type': {'datetime': {}, 'date': {}}}}}}}

# # ori_kg_dict = get_paths_dict(['23_golden','24_silver','25_platinum','26_copper','27_aluminum','28_zinc','29_lead','30_nickel'])
# task = "I want to see the spot London prices of all metals at 2012-12-12."
# x = check_if_table_useful(task, ori_kg_dict)
# print(x)