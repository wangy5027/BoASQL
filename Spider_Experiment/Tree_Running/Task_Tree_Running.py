import os
from Tree_Running.paths import PROJECT_ROOT
from Tree_Running.Tree_Building.Task_Tree_Building import *
from Tree_Running.Tree_Building.Task_Tree_Optimization import *
from Tree_Running.Agents.Code_generation import *
from Tree_Running.Agents.Translate import *
from Tree_Running.Tools.Running_tools import *

# from Tree_Building.Task_Tree_Building import *
# from Tree_Building.Task_Tree_Optimization import *
# from Agents.Code_generation import *
# from Agents.Translate import *
# from Tools.Running_tools import *

current_file_path = os.path.dirname(os.path.abspath(__file__))
record_path = str(PROJECT_ROOT)
printlog_path = os.path.join(record_path, 'printlog.txt')

def node_execution(Task_tree, kg_dict, start_node, pre_tasks, pre_sql, db_id, count = 0):
    
    pre_tasks = pre_tasks
    pre_sql = pre_sql
    pre_nodes = []
    
    code_gen_nodes_list = get_code_gen_nodes_list(Task_tree, start_node)
    if len(code_gen_nodes_list) > 0:
        first_node_task = Task_tree[code_gen_nodes_list[0]].data
    else:
        code_gen_nodes_list.append(Task_tree[Task_tree.root].identifier)
        first_node_task = Task_tree[Task_tree.root].data
        
    if start_node == Task_tree.root:
        time.sleep(1)
        signal, first_node_sql, df_half = code_generation_simple(first_node_task, kg_dict, db_id)
    else:
        if len(pre_sql) != 0:
            time.sleep(1)
            signal, first_node_sql, df_half = code_generation_merging(str(pre_tasks), pre_sql[-1], first_node_task, kg_dict, db_id)
        else:
            time.sleep(1)
            signal, first_node_sql, df_half = code_generation_merging(str(pre_tasks), "", first_node_task, kg_dict, db_id)
        
    if signal == "Success!":
        pre_tasks.append(first_node_task)
        pre_nodes.append(code_gen_nodes_list[0])
        pre_sql.append(first_node_sql) 
        code_gen_nodes_list = code_gen_nodes_list[1:]
    else:
        count = count + 1
        if count > 1:
            time.sleep(1)
            signal, first_node_sql, df_half = code_generation_simple(Task_tree[Task_tree.root].data, kg_dict, db_id)
            pre_sql.append(first_node_sql)
            time.sleep(1)
            signal, final_code = Call_CodeChecking(Task_tree[Task_tree.root].data,first_node_sql,kg_dict,db_id)
            if signal == "Success":
                return signal, final_code
            else:
                if len(pre_sql) != 0:
                    return signal, pre_sql[-1]
                else:
                    return signal, "Fail"
        else:
            print("This sub-tree needs re-build.")

            info = "\n" + "This sub-tree needs re-build."
            with open(printlog_path, 'a') as file:
                file.write(info)

            time.sleep(1)
            rebuild_sub_tree_with_wrong_cases(Task_tree, code_gen_nodes_list[0], df_half, kg_dict)
            if len(pre_sql) != 0:
                time.sleep(1)
                node_execution(Task_tree, kg_dict, code_gen_nodes_list[0], pre_tasks, pre_sql, db_id, count)
            else:
                time.sleep(1)
                node_execution(Task_tree, kg_dict, code_gen_nodes_list[0], pre_tasks, pre_sql, db_id, count)
        
    for node in code_gen_nodes_list:
        cur_node_task = Task_tree[node].data
        time.sleep(1)
        signal, cur_node_sql, df_half = code_generation_merging(str(pre_tasks), pre_sql[-1], cur_node_task, kg_dict, db_id)
        if signal == "Success!":
            pre_tasks.append(cur_node_task)
            pre_sql.append(cur_node_sql)
            pre_nodes.append(node)
        else:
            count = count + 1
            if count > 1:
                time.sleep(1)
                signal, first_node_sql, df_half = code_generation_simple(Task_tree[Task_tree.root].data, kg_dict, db_id)
                pre_sql.append(first_node_sql)
                break
            else:
                node_siblings_iden = [i.identifier for i in Task_tree.siblings(node)]
                node_siblings_data = [i.data for i in Task_tree.siblings(node)]
                len_pre = len(pre_nodes)
                pre_nodes = [i for i in pre_nodes if i not in node_siblings_iden]
                pre_tasks = [i for i in pre_tasks if i not in node_siblings_data]
                len_after = len(pre_nodes)
                if len_pre - len_after != 0:
                    pre_sql = pre_sql[:-(len_pre - len_after)]
                else:
                    pre_sql = pre_sql
                    
                print("This sub-tree needs re-build.")

                info = "\n" + "This sub-tree needs re-build."
                with open(printlog_path, 'a') as file:
                    file.write(info)

                time.sleep(1)
                rebuild_sub_tree_with_wrong_cases(Task_tree, Task_tree[node].identifier, df_half, kg_dict)
                if len(pre_nodes) != 0:
                    time.sleep(1)
                    node_execution(Task_tree, kg_dict, pre_nodes[-1], pre_tasks, pre_sql, db_id, count)
                else:
                    time.sleep(1)
                    node_execution(Task_tree, kg_dict, [], pre_tasks, pre_sql, db_id, count)
    time.sleep(1)
    signal, final_code = Call_CodeChecking(Task_tree[Task_tree.root].data,pre_sql[-1],kg_dict,db_id)
    if signal == "Success":
        return signal, final_code
    else:
        if len(pre_sql) != 0:
            return signal, pre_sql[-1]
        else:
            return signal, "Fail"
    
def Task_Tree_Running(root_task = "", root_task_iden = "0", db_id="", count = 0):
    root_task = root_task
    root_task_iden = root_task_iden
    db_id = db_id
    count = count

    basic_task_info = "\n" + "root_task_iden: " + root_task_iden + "root_task: " + root_task + "db_id: " + db_id
    with open(printlog_path, 'a') as file:
        file.write(basic_task_info)

    kg_dict, Task_tree = Task_Tree_Building(root_task_iden, root_task)
    # if len(Task_tree[root_task_iden].tag) > 0:
    #     Task_tree = Tree_optimization(Task_tree, kg_dict)
            
    signal, final_code = node_execution(Task_tree, kg_dict, "0", [], [], db_id)
    if signal == 'Success':
        print(Task_tree)

        info = "\n" + str(Task_tree)
        with open(printlog_path, 'a') as file:
            file.write(info)
        
        return signal, Task_tree, final_code
    else:
        if count < 2:
            count = count + 1
            Task_Tree_Running(root_task, root_task_iden, db_id, count)
        else:
            print(Task_tree)

            info = "\n" + str(Task_tree)
            with open(printlog_path, 'a') as file:
                file.write(info)

            return signal, Task_tree, final_code
            
    # print("&&&&&&&&&&&&&&&&")
    # print("[final signal]:" + signal)
    # print("[final sql]:" + final_code)
    

# Task_Tree_Running(root_task = "How many clubs are there?", db_id="soccer_3")