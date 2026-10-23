import os
from Tree_Running.paths import PROJECT_ROOT
from Tree_Running.Agents.agents_init import *
from Tree_Running.Agents.Tools.zhengze import *
from Tree_Running.Agents.Tools.KG_DB_foundamental_functions import *
from Tree_Running.Agents.Bug_fixing import *
from Tree_Running.Agents.Code_checking import *

# from Agents.agents_init import *
# from Agents.Tools.zhengze import *
# from Agents.Tools.KG_DB_foundamental_functions import *
# from Agents.Bug_fixing import *
# from Agents.Code_checking import *

current_file_path = os.path.dirname(os.path.abspath(__file__))
record_path = str(PROJECT_ROOT)
printlog_path = os.path.join(record_path, 'printlog.txt')

CodeGenerating_prompt_1="""
Please think step by step. You are a professional SQL engineer, I'm going to give you a sql task and a description of database.According to the given information, generate a sql code to accomplish the task.Your one action should follow the framework below:

input:
[database description]:Description of database, given externally
[task]: Task that should be finished, given externally

output:
[thinking]:According to the given [task], [half-completed sql code], and [database description], think step by step, and try to generate a sql code that could accomplish the task. If I have given you a half-finished sql, please generate new sql code based on it.
[final sql]:Sql code that you generated.(Must end with ;)

warn: 
1. Reply in STRICT accordance with format requirements.
2. The [final sql] must end with ";".
3. If the [task] does not directly ask for the count or max or min data, All the aggregation like COUNT, AVE, MAX, MIN can be used only in HAVING, ORDER BY, GROUP BY parts and should never exists in the SELECT part.
4. DO NOT join tables that are not necessary for accomplishing the [task], if one table is enough to finish the task, do not join other tablesS;
5. Select ONLY the columns that are DIRECTLY asked by the [task], never select the extra columns. for example, if asking "who is the tallest boy", just "select name from students order by height desc limit 1", do not select the height column.
6. The columns exist in ORDER BY or HAVING should not be selected if the [goal] does not exactly asked to show it.
7. Use the value that directly given by the [task]. For example, if asking "what's mike's phone number", just "select phone_num from num_book where name = "mike"; ". If no value is provided, use the lowercase values.
8. When asking for a highest or lowest value of something, instead of using the MAX or MIN, use the DESC LIMIT 1 or ASC LIMIT 1, this can make the task much easier.
9. DESC LIMIT 1 is preferred than SELECT MAX().

example:
input:
[database description]:
{'Factor_data': {'have_column': {'Trddt': {'Trddt': {'data_type': {'datetime': {}, 'date': {}}}}, 'Stkcd': {'Stkcd': {'data_type': {'str': {}}}}, 'Factor': {'Factor': {'data_type': {'double': {}}}}}}}
{'Stock_data': {'have_column': {'Trddt': {'Trddt': {'data_type': {'datetime': {}, 'date': {}}}}, 'Stkcd': {'Stkcd': {'data_type': {'str': {}}}}, 'Stock': {'Stock': {'data_type': {'double': {}}}}}}}
[task]:We need to select the factor data that the stkcd is '000002', trddt is '2012-01-01'

output:
[thinking]:Since the task is to select the factor data that the stkcd is '000002', trddt is '2012-01-01', we need to generate a simple 'SELECT X FROM Y WHERE Z' code.
[final sql]:SELECT Factor FROM Factor_data WHERE stkcd == '000002' and trddt == '2012-01-01';
"""

def code_generation_simple(task, kg_dict, db_id):

    info = "\n" + "current sub_task: " + task
    with open(printlog_path, 'a') as file:
            file.write(info)

    messages = [{"role":"system","content":"You are a precise, efficient and concise SQL engineer."}]
    CodeGenerating_agent = LlmAgent(messages=messages)
    CodeGenerating_agent.environmental_feedback(CodeGenerating_prompt_1)
    
    response = CodeGenerating_agent.continue_conversation(user_input = "let us begin: " + "\n" + str(kg_dict) + "\n" + task)
    
    if "missing information" in response:
        missing_info = get_missing_info(response)
        print("Missing information error. Please provide more information")
        print(response)

        info = "\n" + "code_generation_simple response: " + response
        with open(printlog_path, 'a') as file:
            file.write(info)
        
        signal = "missing information"
        return signal, missing_info, ""
    else:
        print(response)
        final_sql = get_final_sql(response)
        print("未检验语法问题的sql：")
        print(final_sql)

        info = "\n" + "未检验语法问题的sql: " + final_sql
        with open(printlog_path, 'a') as file:
            file.write(info)
        
        signal, final_sql, df_half = Call_BugFixing(final_sql, str(kg_dict), db_id)
        if signal == "Success!":
            print("检验过语法问题后的sql")
            print(final_sql)

            info = "\n" + "检验过语法问题后的sql: " + final_sql
            with open(printlog_path, 'a') as file:
                file.write(info)
        else:
            print("当前sql的语法问题暂时无法得到纠正：")
            print(final_sql)
            signal = "fail"

            info = "\n" + "当前sql的语法问题暂时无法得到纠正：" + final_sql
            with open(printlog_path, 'a') as file:
                file.write(info)
            return signal, final_sql, df_half
    
    print("** Step4:检查sql是否符合goal的要求")

    info = "\n" + "** Step4:检查sql是否符合goal的要求"
    with open(printlog_path, 'a') as file:
        file.write(info)

    signal,final_code = Call_CodeChecking(task, final_sql, str(kg_dict),db_id)
    if signal == "Fail to make the sql code satisfy user's need":

        info = "\n" + "Fail to make the sql code satisfy user's need"
        with open(printlog_path, 'a') as file:
            file.write(info)

        return signal,final_code, ""

    signal, final_code, df_half = Call_BugFixing(final_code, str(kg_dict), db_id)
    print("")
    print("** 最终的sql为：")
    print(final_code)

    info = "\n" + "** 最终的sql为：" + final_code
    with open(printlog_path, 'a') as file:
        file.write(info)

    return signal, final_code, ""

CodeGenerating_prompt="""
Please think step by step. You are a professional SQL engineer, I'm going to give you a sql task, a pre-finished sql code and its corresponding task, and a description of database.According to the given information, generate a sql code to accomplish the task.Your one action should follow the framework below:

input:
[database description]:Description of database, given externally.
[current task]: Task that should be finished, given externally.
[tasks already finished]: Tasks that have finished, the [half-completed sql code] is the code that could accomplish those tasks.
[half-completed sql code]: Half-completed sql code, given externally

output:
[thinking]:According to the given [task], [pre-finished task], [half-completed sql code], and [database description], think step by step, and try to generate a sql code based on the [half-completed sql code] that could accomplish the task.
[final sql]:Sql code that you generated.

warn: 
1. Reply in STRICT accordance with format requirements.
2. The [final sql] must end with ";".
3. You don't have to use all the given tables.
4. Select ONLY the columns that are DIRECTLY asked by the [task], never select the extra columns. for example, if asking "who is the tallest boy", just "select name from students order by height desc limit 1", do not select the height column.
5. The columns exist in ORDER BY or HAVING should not be selected if the [goal] does not exactly asked to show it.
6. Use the value that directly given by the [current task]. For example, if asking "what's mike's phone number", just "select phone_num from num_book where name = "mike"; ". If no value is provided, use the lowercase values.
7. When asking for a highest or lowest value of something, instead of using the MAX or MIN, use the DESC LIMIT 1 or ASC LIMIT 1, this can make the task much easier.

example:
input:
[database description]:
{'stock_open_price': {'have_column': {'time': {'time': {'data_type': {'datetime': {}, 'date': {}}}}, 'stock_000001': {'stock_000001': {'data_type': {'double': {}}}}, 'stock_000002': {'stock_000002': {'data_type': {'double': {}}}}}}}
{'factor_1': {'have_column': {'time': {'time': {'data_type': {'datetime': {}, 'date': {}}}}, 'stock_000001': {'stock_000001': {'data_type': {'double': {}}}}, 'stock_000002': {'stock_000002': {'data_type': {'double': {}}}}}}}
{'factor_2': {'have_column': {'time': {'time': {'data_type': {'datetime': {}, 'date': {}}}}, 'stock_000001': {'stock_000001': {'data_type': {'double': {}}}}}}}
[current task]: 2. Select the stock_000001 and time columns from the joined table where time = '2012-01-01'.
[tasks already finished]: 1. Join the table stock_open_price and factor_1 on column 'stock_000001'.
[half-completed sql code]: SELECT * FROM stock_open_price JOIN factor_1 ON stock_open_price.time = factor_1.time;

output:
[thinking]:Based on the [current task], [tasks already finished] and [half-completed sql code], I need to add a column filtering "time = '2012-01-01" and select the needed columns 'stock_000001' and 'time' above the [half-completed sql code].
[final sql]:SELECT stock_open_price.stock_000001 , factor_1.stock_000001, time FROM stock_open_price JOIN factor_1 ON stock_open_price.time = factor_1.time WHERE time = '2012-01-01';
"""

def code_generation_merging(pre_tasks, pre_sql, task, kg_dict, db_id):
    messages = [{"role":"system","content":"You are a precise, efficient and concise SQL engineer."}]
    CodeGenerating_agent = LlmAgent(messages=messages)
    CodeGenerating_agent.environmental_feedback(CodeGenerating_prompt)
    
    response = CodeGenerating_agent.continue_conversation(user_input = "let us begin: " + str(kg_dict) + "\n"+ task +"\n"+ pre_tasks +"\n"+ pre_sql)
    if "missing information" in response:
        missing_info = get_missing_info(response)
        print("Missing information error. Please provide more information")
        print(response)

        info = "\n" + "code_generation_simple response: " + response
        with open(printlog_path, 'a') as file:
            file.write(info)

        signal = "missing information"
        return signal, missing_info, ""
    else:
        print(response)
        final_sql = get_final_sql(response)
        print("未检验语法问题的sql：")
        print(final_sql)

        info = "\n" + "未检验语法问题的sql: " + final_sql
        with open(printlog_path, 'a') as file:
            file.write(info)

        signal, final_sql, df_half = Call_BugFixing(final_sql, str(kg_dict), db_id)
        if signal == "Success!":
            print("检验过语法问题后的sql")
            print(final_sql)

            info = "\n" + "检验过语法问题后的sql: " + final_sql
            with open(printlog_path, 'a') as file:
                file.write(info)

        else:
            print("当前sql的语法问题暂时无法得到纠正：")
            print(final_sql)
            signal = "fail"

            info = "\n" + "当前sql的语法问题暂时无法得到纠正：" + final_sql
            with open(printlog_path, 'a') as file:
                file.write(info)

            return signal, final_sql, df_half
    
    print("** Step4:检查sql是否符合goal的要求")

    info = "\n" + "** Step4:检查sql是否符合goal的要求"
    with open(printlog_path, 'a') as file:
        file.write(info)

    signal,final_code = Call_CodeChecking(task, final_sql, str(kg_dict), db_id)
    if signal == "Fail to make the sql code satisfy user's need":
        return signal,final_code, ""

    signal, final_code, df_half = Call_BugFixing(final_code, str(kg_dict), db_id)
    print("")
    print("** 最终的sql为：")
    print(final_code)

    info = "\n" + "Fail to make the sql code satisfy user's need"
    with open(printlog_path, 'a') as file:
        file.write(info)

    return signal, final_code, ""

# pre_tasks = "1. Join the tables '23_golden', '24_silver', '26_copper', '27_aluminum', '28_zinc', '29_lead', and '30_nickel' on the 'time' column."
# pre_sql = """SELECT * FROM 23_golden JOIN 24_silver ON 23_golden.time = 24_silver.time JOIN 26_copper ON 23_golden.time = 26_copper.time JOIN 27_aluminum ON 23_golden.time = 27_aluminum.time JOIN 28_zinc ON 23_golden.time = 28_zinc.time JOIN 29_lead ON 23_golden.time = 29_lead.time JOIN 30_nickel ON 23_golden.time = 30_nickel.time"""
# task = "2. Select the spot China prices from the joined table where the time is '2012-12-12'."

# kg_dict = {'23_golden': {'have_column': {'time': {'data_type': {'datetime': {}, 'date': {}}}, 'spot_china_gold': {'data_type': {'double': {}}}}}, 
#             '24_silver': {'have_column': {'time': {'data_type': {'datetime': {}, 'date': {}}}, 'spot_china_silver': {'data_type': {'double': {}}}}}, 
#             '26_copper': {'have_column': {'time': {'data_type': {'datetime': {}, 'date': {}}}, 'spot_china_copper': {'data_type': {'double': {}}}}}, 
#             '27_aluminum': {'have_column': {'time': {'data_type': {'datetime': {}, 'date': {}}}, 'spot_china_aluminum': {'data_type': {'double': {}}}}}, 
#             '28_zinc': {'have_column': {'time': {'data_type': {'datetime': {}, 'date': {}}}, 'spot_china_zinc': {'data_type': {'double': {}}}}}, 
#             '29_lead': {'have_column': {'time': {'data_type': {'datetime': {}, 'date': {}}}, 'spot_china_lead': {'data_type': {'double': {}}}}}, 
#             '30_nickel': {'have_column': {'time': {'data_type': {'datetime': {}, 'date': {}}}, 'spot_china_nickel': {'data_type': {'double': {}}}}}}

# final_sql = code_generation_merging(pre_tasks, pre_sql, task, kg_dict)
# print(final_sql)

    
    
