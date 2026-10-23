import os
from Tree_Running.paths import PROJECT_ROOT
from treelib import Node, Tree
import time
from Tree_Running.Tree_Building.Agents import Task_decompose
from Tree_Running.Tree_Building.Agents import KG_db_info_infer
from Tree_Running.Tree_Building.Agents.Tools.KG_DB_foundamental_functions import *
# from Tree_Building.Agents import Task_decompose
# from Tree_Building.Agents import KG_db_info_infer

current_file_path = os.path.dirname(os.path.abspath(__file__))
record_path = str(PROJECT_ROOT)
printlog_path = os.path.join(record_path, 'printlog.txt')

def obtain_full_db_kg():
    table_created_meaages = get_table_created_meaages()
    if isinstance(table_created_meaages,list):
        table_names = []
        for table in table_created_meaages:
            table_name = catch_table_name(table)
            table_names.append(table_name)
    else:
        table_names = table_created_meaages
    
    database_info_dict = get_paths_dict(table_names)
    return database_info_dict
    
def Nodes_adding(father_task, sub_tasks, Task_tree):
    for i in range(len(sub_tasks)):
        iden = father_task + "_" + str(i)
        Task_tree.create_node(iden, iden, parent = father_task, data = sub_tasks[i])

def Leaf_nodes_building_need_checking(task, task_iden, related_KG_information, Task_tree):
    signal, decompose_judgement, thinking = Task_decompose.Decompose_or_not(task, str(related_KG_information))
    Task_tree[task_iden].tag = thinking
    # signal = True 
    # decompose_judgement = "complicated"
    depth = Task_tree.depth()
    if depth < 1:
        if signal == "Success":
            if decompose_judgement.lower() == "complicate":
                signal, tasks_list = Task_decompose.Decompose_PlanMaking(task, str(related_KG_information))
                if signal == 'missing information':
                    signal = 0.5
                    return signal
                elif len(tasks_list) <= 1:
                    signal = 0
                    return signal
                elif len(tasks_list) <= 5:
                    Nodes_adding(task_iden, tasks_list, Task_tree)
                    signal = 1
                    return signal
                else:
                    signal = 0
                    return signal
            else:
                signal = 0
                return signal
        else:
            signal = 0
            return signal
    else:
        signal = 0
        return signal

def Leaf_nodes_building_no_checking(task, task_iden, related_KG_information, Task_tree):
    signal, tasks_list = Task_decompose.Decompose_PlanMaking(task, str(related_KG_information))
    if signal == "Sucess":
        Nodes_adding(task_iden, tasks_list, Task_tree)
        
def Leaf_nodes_building_no_checking_with_fail_cases(task, wrong_steps, wrong_reason, related_KG_information, task_iden, Task_tree):
    signal, tasks_list = Task_decompose.Decompose_PlanMaking_with_fail_cases(task, wrong_steps, wrong_reason, str(related_KG_information))
    if task_iden == "0":
        if len(tasks_list) != 0:
            Nodes_adding(task_iden, tasks_list, Task_tree)
    elif signal == "Sucess":
        Nodes_adding(task_iden, tasks_list, Task_tree)

def Task_Tree_Building(task_iden, task_data, kg_missing_information_count = 0):
    Task_tree = Tree()
    Task_tree.create_node(task_iden, task_iden, data  = task_data)
    
    kg_dict, flag, kg_signal = KG_db_info_infer.Get_kg_inferred_info(task_data)
    print(kg_dict)

    info = "\n" + "kg_dict: " + str(kg_dict)
    with open(printlog_path, 'a') as file:
        file.write(info)
        
    already_decomposed_nodes_list = []
    if kg_signal == "Sucess":
        time.sleep(1)
        lf_signal = Leaf_nodes_building_need_checking(task_data, task_iden, str(kg_dict), Task_tree)
        signal = lf_signal
        if signal == 0.5 and kg_missing_information_count < 1:
            kg_missing_information_count = kg_missing_information_count + 1
            Task_Tree_Building(task_iden, task_data, kg_missing_information_count)
        elif signal == 0.5 and kg_missing_information_count >= 1:
            kg_dict = obtain_full_db_kg()
            Leaf_nodes_building_no_checking(task_data, task_iden, kg_dict, Task_tree)
            return kg_dict, Task_tree
        
        if kg_missing_information_count == 0 and Task_tree.depth() < 1:
            while signal != 0:
                signal = 0
                leaf_nodes_list = Task_tree.leaves(task_iden)
                need_decompose_nodes_list = [x for x in leaf_nodes_list if x not in already_decomposed_nodes_list]
                print("These nodes start decomposing",need_decompose_nodes_list)

                info = "\n" + "These nodes start decomposing: " + str(need_decompose_nodes_list)
                with open(printlog_path, 'a') as file:
                    file.write(info)
                
                for leaf_node in need_decompose_nodes_list:
                    time.sleep(1)
                    lf_signal = Leaf_nodes_building_need_checking(leaf_node.data, leaf_node.identifier, str(kg_dict), Task_tree)
                    signal = signal + lf_signal
                    if lf_signal == 0:
                        already_decomposed_nodes_list.append(leaf_node)
    
    print(Task_tree.leaves(task_iden))

    info = "\n" + "Task_tree.leaves: " + str(Task_tree.leaves(task_iden))
    with open(printlog_path, 'a') as file:
        file.write(info)

    return kg_dict, Task_tree

# root_task = "I want to see the spot China prices of all metals at 2012-12-12."
# root_task_iden = "0" 
# Task_tree = Task_Tree_Building(root_task_iden, root_task)





