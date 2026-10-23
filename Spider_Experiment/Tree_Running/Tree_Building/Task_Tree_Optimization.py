# from Tree_Building.Task_Tree_Building import *
# from Tree_Building.Tools.Sql_operations_detection import *
# from Tree_Building.Tools.Extract_similar_decompose_example import *
# from Tree_Building.Agents.Decompose_checking import *

from Tree_Running.Tree_Building.Task_Tree_Building import *
from Tree_Running.Tree_Building.Tools.Sql_operations_detection import *
from Tree_Running.Tree_Building.Tools.Extract_similar_decompose_example import *
from Tree_Running.Tree_Building.Agents.Decompose_checking import *

def get_no_leaf_nodes_list(Treee):
    all_nodes = [i for i in Treee.expand_tree()]
    leaf_nodes = [i.identifier for i in Treee.leaves(Treee.root)]
    no_leaf_nodes_list = [i for i in all_nodes if all(y not in i for y in leaf_nodes)]
    return no_leaf_nodes_list

# def sub_tree_rebuild(extracted_example, father_node_iden, related_KG_information, Task_tree, ):
#     # # d_c_signal, correct_or_not = Decomopose_checking(extracted_example, Task_tree[father_node_iden].data, str(child_data))
#     # d_c_signal = "Success"
#     # correct_or_not = 0
#     # if d_c_signal == "Success":
#     #     if correct_or_not == 1:
#     #         continue
#     #     else:
#     #         print("This node's decompose need rebuild.")
#     #         for i in Task_tree.children(father_node_iden):
#     #             Task_tree.remove_node(i.identifier)

#     #         l_n_b_signal = Leaf_nodes_building(Task_tree[father_node_iden].data, father_node_iden, related_KG_information, Task_tree)
#     #         print(Task_tree)

#############← 1.0 Start Original Task Tree Building →#################
# root_task = "I want to see the spot China prices of all metals at 2012-12-12."
# root_task_iden = "0"  
# root_task_thinking = """Based on the given information, this task involves selecting spot China prices of all metals at a specific date. It requires retrieving data from multiple tables and filtering based on the date. Since there are multiple tables involved and we need to retrieve specific columns, the complexity of this task can be considered as "complicate".""" 

# Task_tree = Tree()
# Task_tree.create_node(root_task_thinking,"0", data = root_task)

# node_0_0 = "Based on the given information, the task requires joining three tables ('23_golden', '24_silver', '25_platinum') on the 'time' column. Since the tables have the same structure and only need to be joined on a single column, the complexity of this task is relatively low. There is no data filtering, grouping, or complex operations involved. Therefore, this task can be considered easy."
# node_0_1 = "Based on the given information, this task involves selecting specific columns from a joined table and filtering the data based on a specific date. The number of tables that need to be joined is not mentioned, so we cannot determine the complexity of the join operation. However, the task does not involve any complex operations like grouping or nested querying. It only requires selecting columns and applying a simple filter. Therefore, we can consider this task as easy."
# node_0_2 = "Based on the given information, this task involves selecting specific columns from a joined table and filtering the data based on a specific date. The number of tables that need to be joined is not mentioned, so we cannot determine the complexity of the join operation. However, the task does not involve any complex operations like grouping or nested querying. It only requires selecting columns and applying a simple filter. Therefore, we can consider this task as easy."

# Task_tree.create_node(node_0_0, "0_0", parent = "0", data = "1. Select the 'china' column from table '23_golden' where time = '2012-12-12'.") 
# Task_tree.create_node(node_0_1, "0_1", parent = "0", data = "2. Select the 'china' column from table '24_silver' where time = '2012-12-12'.") 
# Task_tree.create_node(node_0_2, "0_2", parent = "0", data = "3. Select the 'china' column from table '25_platinum' where time = '2012-12-12'.") 

# related_KG_information = {'23_golden': {'23_golden': {'have_column': {'time': {'data_type': {'datetime': {}, 'date': {}}}, 'spot_london_gold': {'data_type': {'double': {}}}}}}, 
#            '24_silver': {'24_silver': {'have_column': {'time': {'data_type': {'datetime': {}, 'date': {}}}, 'spot_london_silver': {'data_type': {'double': {}}}}}}, 
#            '25_platinum': {'25_platinum': {'have_column': {'time': {'data_type': {'datetime': {}, 'date': {}}}, 'spot_london_platinum': {'data_type': {'double': {}}}}}}}

# print(Task_Tree.leaves("0"))
# print(Task_Tree["0"])
# Task_tree = Task_Tree_Building(root_task_iden, root_task)

#############← 2.0 Task Tree optimization →#################

def if_need_rebuild(no_leaf_node_iden, Task_tree):
    child_data = []
    if no_leaf_node_iden in Task_tree:
        father_operation_tags = extract_used_sql_operations_from_thinking(Task_tree[no_leaf_node_iden].tag)
        for m in Task_tree.children(no_leaf_node_iden):
            child_data.append(m.data)
        extracted_example = find_most_similar_case(father_operation_tags)
        d_c_signal, correct_or_not = Decomopose_checking(extracted_example, Task_tree[no_leaf_node_iden].data, str(child_data))
        return d_c_signal, correct_or_not
    else:
        d_c_signal = 'Success'
        correct_or_not = 1
        return d_c_signal, correct_or_not

def Tree_optimization(Task_tree, related_KG_information):
    no_leaf_nodes_list = get_no_leaf_nodes_list(Task_tree)
    for no_leaf_node_iden in no_leaf_nodes_list:
        d_c_signal, correct_or_not = if_need_rebuild(no_leaf_node_iden, Task_tree)
        re_count = 0
        while correct_or_not != 1:
            re_count = re_count + 1
            if re_count <= 3:
                if d_c_signal == "Success":
                    print("This node's decompose need rebuild.")
                    for i in Task_tree.children(no_leaf_node_iden):
                        Task_tree.remove_node(i.identifier)
                    Leaf_nodes_building_no_checking(Task_tree[no_leaf_node_iden].data, no_leaf_node_iden, related_KG_information, Task_tree)
                    d_c_signal, correct_or_not = if_need_rebuild(no_leaf_node_iden, Task_tree)
                else:
                    d_c_signal, correct_or_not = if_need_rebuild(no_leaf_node_iden, Task_tree)
            else:
                correct_or_not = 0
            
    return Task_tree

# Tree_optimization(Task_tree)
# print(Task_tree)
