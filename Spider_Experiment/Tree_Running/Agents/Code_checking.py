import os
from Tree_Running.paths import PROJECT_ROOT
from Tree_Running.Agents.agents_init import *
from Tree_Running.Agents.Tools.zhengze import *
from Tree_Running.Agents.Tools.KG_DB_foundamental_functions import *

# from Agents.agents_init import *
# from Agents.Tools.zhengze import *
# from Agents.Tools.KG_DB_foundamental_functions import *

current_file_path = os.path.dirname(os.path.abspath(__file__))
record_path = str(PROJECT_ROOT)
printlog_path = os.path.join(record_path, 'printlog.txt')

CodeChecking_prompt="""
You are a professional SQL engineer, I'm going to give you a task, a sql code and a description of database.According to the given information, if there are any problems, fix them. If there are no issues, return the SQLite SQL QUERY as is. Your one action should follow the framework below:

Use the following instructions for fixing the SQL QUERY:
1) Avoid redundent COUNT(), SUM(), MAX(), MIN() in SELECT, HAVING and ORDER BY part, when meet redundancy, preserve the HAVING or ORDER BY part and delete the COUNT(), MAX(), MIN() that exists after the SELECT.
2) Use the value that directly given by the [task], if it gives "france", just use it, do not change it into "France". If no value is provided, use the lowercase values
3) Never use CAST! Never use CAST! Never use CAST! If it exist, delete it!
4) Pay attention to the columns that are used for the JOIN by using the Foreign_keys.
5) Use DESC and DISTINCT when needed.
6) Pay attention to the columns that are used for the GROUP BY statement.
7) Pay attention to the columns that are used for the SELECT statement.
8) Only change the GROUP BY clause when necessary (Avoid redundant columns in GROUP BY).
9) Use GROUP BY on one column only.
10) Select only the columns that are directly asked to selected by the [goal].

input:
[task]: Task that should be finished, given externally.
[sql code]: Half-completed sql code, given externally.
[database description]:Description of database, given externally.

output:
[thinking]:According to the given [task], [sql code], and [database description], think step by step, figure out if the code given to you could achieve the task, if not, where is the problem.
[correct or not]: Based on the given information and your thinking, if the code is correct, return yes, if not, return no.(Just return "yes" or "no"!!)
[final sql]:Sql code that you generated.

warn: 
1. Reply in strict accordance with format requirements.
2. The [final sql] you output must end with ";".

example:
input:
[task]: We need to select the stock data that the stkcd is '000002'
[sql code]: SELECT Stock FROM Stock_data WHERE stkcd == '000002' and trddt == '2012-01-01';
[database description]:
{'Factor_data': {'have_column': {'Trddt': {'Trddt': {'data_type': {'datetime': {}, 'date': {}}}}, 'Stkcd': {'Stkcd': {'data_type': {'str': {}}}}, 'Factor': {'Factor': {'data_type': {'double': {}}}}}}}
{'Stock_data': {'have_column': {'Trddt': {'Trddt': {'data_type': {'datetime': {}, 'date': {}}}}, 'Stkcd': {'Stkcd': {'data_type': {'str': {}}}}, 'Stock': {'Stock': {'data_type': {'double': {}}}}}}}

output:
[thinking]: The task is to select the stock data that the stkcd is '000002'. The code provided adds a restriction on date, which is unnecessary.
[correct or not]:no
[final sql]: SELECT Stock FROM Stock_data WHERE stkcd == '000002';
"""

def CodeChecking(goal, final_code, Database_discription):
    messages = [{"role":"system","content":"You are a precise, efficient and concise SQL engineer."}]
    CodeChecking_agent = LlmAgent(messages=messages)
    CodeChecking_agent.environmental_feedback(CodeChecking_prompt)
    response = CodeChecking_agent.continue_conversation(user_input = "let us begin: " + "[task]: " + goal + "[sql code]: " + final_code + "[database description]: " + str(Database_discription))
    print(response)

    info = "\n" + response
    with open(printlog_path, 'a') as file:
        file.write(info)
    
    match = re.search(r"\[correct or not\]:\s*(.*)", response)
    if match:
        correct_or_not = match.group(1)
        if  "yes" in correct_or_not or "Yes" in correct_or_not:
            return final_code
        else:
            final_code = get_final_sql(response)
            return final_code
    else:
        match = re.search(r"\[correct or not\]\s*(.*)", response)
        if match:
            correct_or_not = match.group(1)
            if  "yes" in correct_or_not or "Yes" in correct_or_not:
                return final_code
            else:
                final_code = get_final_sql(response)
                return final_code
        else:
            return final_code
    
def Call_CodeChecking(goal,half_code,Database_discription,db_id):
    final_code = CodeChecking(goal, half_code, Database_discription)
    codechecking_count = 0
    while len(final_code) == 0:
        final_code = CodeChecking(goal, half_code, Database_discription)
        codechecking_count = codechecking_count + 1
        if codechecking_count > 2:
            signal = "Fail to make the sql code satisfy user's need"
            sql_suitable_or_not = if_sql_code_not_createupdateinsert(half_code)
            if sql_suitable_or_not == 1:   
                df_final = get_data_from_database(db_id, half_code)
                return signal,df_final
            else:
                return signal, """pymysql.err.ProgrammingError: (1146, "Table doesn't exist")"""
    signal = "Success"
    return signal,final_code