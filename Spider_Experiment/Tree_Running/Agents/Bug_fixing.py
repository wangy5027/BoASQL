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

BugFixing_prompt="""
You are a professional SQL engineer, I'm going to give you a wrong sql code, a description of database, and a error message.For the given question, use the provided database description to fix the given SQLite SQL QUERY for any issues. If there are any problems, fix them.

Use the following instructions for fixing the [wrong sql code]:
1) Use the database values that are explicitly mentioned in the question.
2) Pay attention to the columns that are used for the JOIN by using the Foreign_keys.
3) Use DESC and DISTINCT when needed.
4) Pay attention to the columns that are used for the GROUP BY statement.
5) Pay attention to the columns that are used for the SELECT statement.
6) Only change the GROUP BY clause when necessary (Avoid redundant columns in GROUP BY).
7) Use GROUP BY on one column only.

Your one action should follow the framework below:
input:
[wrong sql code]: wrong sql code, given externally
[database description]:Description of database, given externally
[error message]:Error caused when using the sql code

output:
[thinking]:According to the given [wrong sql code], [database description] and [error message], think step by step, figure out where is the problem and give a suggestion on code modification.
[final sql]:Sql code that you generated.

warn: 
1. Reply in strict accordance with format requirements.
2. Do not add ANY extra syntax in the [final sql] part.
3. The [final sql] you generate must end with ";".

example:
input:
[wrong sql code]:
SELECT *
FROM (SELECT *
      FROM students
      JOIN grades ON students.Stu_id = grades.Stu_id) AS step1
JOIN health ON step1.Stu_id = health.Stu_id;
[database description]:
{'Factor_data': {'have_column': {'Trddt': {'Trddt': {'data_type': {'datetime': {}, 'date': {}}}}, 'Stkcd': {'Stkcd': {'data_type': {'str': {}}}}, 'Factor': {'Factor': {'data_type': {'double': {}}}}}}}
{'Stock_data': {'have_column': {'Trddt': {'Trddt': {'data_type': {'datetime': {}, 'date': {}}}}, 'Stkcd': {'Stkcd': {'data_type': {'str': {}}}}, 'Stock': {'Stock': {'data_type': {'double': {}}}}}}}
[error message]:Duplicate column name 'Stu_id'

output:
[thinking]:According to sql code, this code is trying to join health,students and grades tables on stu_id. While the error message said that there is a Duplicate column name 'Stu_id', this is normal when people trying to join two sub-sql-code. To fix this erro when maintaining the same functionality, it is better to change this nested sql code into a simpler one.
[final sql]:SELECT * FROM students JOIN grades on students.Stu_id = grades.Stu_id JOIN health on grades.Stu_id = health.Stu_id;
"""

def BugFixing(wrong_sql,Database_discription,error_message):
    messages = [{"role":"system","content":"You are a precise, efficient and concise SQL engineer."}]
    BugFixing_agent = LlmAgent(messages=messages)
    BugFixing_agent.environmental_feedback(BugFixing_prompt)
    
    response = BugFixing_agent.continue_conversation(user_input = "let us begin: " + "[wrong sql code]: "+ wrong_sql + "[database description]:" + Database_discription + "[error message]:"+error_message)
    print(response)

    info = "\n" + response
    with open(printlog_path, 'a') as file:
        file.write(info)

    modified_sql = get_final_sql(response)
    return modified_sql

def Call_BugFixing(final_sql, step_Database_discription, db_id):
    sql_suitable_or_not = if_sql_code_not_createupdateinsert(final_sql)
    if sql_suitable_or_not == 1:
        df_half = get_data_from_database(db_id, final_sql)
        bugfixing_count = 0
        while type(df_half) == str:
            wrong_sql = final_sql
            error_message = re.search(r'sqlite3.*', df_half)
            if error_message:
                error_message = error_message.group(0)
            else:
                error_message = df_half             
            if error_message:
                print("sql命令报错，错误如下：")
                info = "\n" + "sql命令报错，错误如下："
                with open(printlog_path, 'a', encoding="utf-8") as file:
                    file.write(info)
                print(error_message)
                info = "\n" + error_message
                with open(printlog_path, 'a', encoding="utf-8") as file:
                    file.write(info)
                print("出错的sql如下：")
                info = "\n" + "出错的sql如下："
                with open(printlog_path, 'a', encoding="utf-8") as file:
                    file.write(info)
                print(wrong_sql)
                info = "\n" + wrong_sql
                with open(printlog_path, 'a', encoding="utf-8") as file:
                    file.write(info)
                print("开始纠错流程：")
                info = "\n" + "开始纠错流程："
                with open(printlog_path, 'a', encoding="utf-8") as file:
                    file.write(info)
                bugfixing_count = bugfixing_count +1
                modified_sql = BugFixing(wrong_sql,step_Database_discription,error_message)
                print("这一轮纠错后的sql命令为：")
                info = "\n" + "这一轮纠错后的sql命令为："
                with open(printlog_path, 'a', encoding="utf-8") as file:
                    file.write(info)
                print(modified_sql)
                info = "\n" + modified_sql
                with open(printlog_path, 'a', encoding="utf-8") as file:
                    file.write(info)
                sql_suitable_or_not = if_sql_code_not_createupdateinsert(modified_sql)
                if sql_suitable_or_not == 1:
                    df_half = get_data_from_database(db_id,modified_sql)
                    final_sql = modified_sql
                else:
                    signal = "Fail to fix the bug of sql code in this turn."
                    df_half = """pymysql.err.ProgrammingError: (1146, "Table doesn't exist")"""
                    return signal, "", df_half
                    
                if bugfixing_count> 2:
                    signal = "Fail to fix the bug of sql code in this turn."
                    return signal,final_sql,df_half
            else:
                final_sql = modified_sql
                signal = "Success!"
                return signal,final_sql,""
            
        signal = "Success!"
        return signal,final_sql,""
    else:
        signal = "Fail to fix the bug of sql code in this turn."
        df_half = """pymysql.err.ProgrammingError: (1146, "Table doesn't exist")"""
        return signal, "", df_half