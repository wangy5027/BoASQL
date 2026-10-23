import os
from Tree_Running.paths import PROJECT_ROOT
from Tree_Running.Task_Tree_Running import *
from Tree_Running.Tools.test_file_related import *

current_file_path = os.path.dirname(os.path.abspath(__file__))
record_path = str(PROJECT_ROOT)
printlog_path = os.path.join(record_path, 'printlog.txt')

def main():

    test_file = get_test_queries_data()
    print(len(test_file))
    for i in range(len(test_file)):
        print("题目编号为：",i);
        db_id, query, question = get_test_db_id_query_question(test_file[i])
        print("数据库为：",db_id)
        kg_file_success_or_not = change_kg(db_id)
        if kg_file_success_or_not:
            signal, Task_tree, final_code = Task_Tree_Running(root_task = question, root_task_iden = "0", db_id=db_id)
            
            if signal == 'Success':
                print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
                info = "\n" + "&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&"
                with open(printlog_path, 'a') as file:
                    file.write(info)
                print("题目编号为：",i,"具体题目为: ", question, "db_id为：", db_id)
                info = "\n" + "题目编号为："+ str(i) + "具体题目为: " + str(question) + "db_id为：" + str(db_id)
                with open(printlog_path, 'a') as file:
                    file.write(info)
                print("参考答案：", query)
                info = "\n" + "参考答案："+ str(query)
                with open(printlog_path, 'a') as file:
                    file.write(info)
                print("SmarterDB的执行状态：", signal)
                info = "\n" + "SmarterDB的执行状态："+ str(signal)
                with open(printlog_path, 'a') as file:
                    file.write(info)
                print("SmarterDB的最终output：")
                print(final_code)
                info = "\n" + "SmarterDB的最终output："+ str(final_code) + "\n"
                with open(printlog_path, 'a') as file:
                    file.write(info)
                
                if len(final_code) == 0:
                    final_code = "No answer generated"
                    write_tree_to_json_file(Task_tree)
                    write_gold_txt_file(query, db_id)
                    write_question_txt_file(i,question)
                    write_predict_txt_file(final_code)
                else:
                    write_tree_to_json_file(Task_tree)
                    write_gold_txt_file(query, db_id)
                    write_question_txt_file(i,question)
                    write_predict_txt_file(final_code)
            else:
                print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                print("题目：", question)
                print("参考答案：", query)
                print("db_id", db_id)
                print(signal)
                print(final_code)
                break
        else:
            print("!!!!!!!!!!!!!!!!!!!!!!!!")
            print("db_id:", db_id)
            print("题目编号为：",i,"具体题目为: ", question)
            break
        
if __name__ == "__main__":
    main()
