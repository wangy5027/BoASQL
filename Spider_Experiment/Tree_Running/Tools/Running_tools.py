import re
# from Tree_Building.Task_Tree_Building import *
from Tree_Running.Tree_Building.Task_Tree_Building import *

def get_code_gen_nodes_list(Tree, start_node):
    depth_node_list = [Tree[node].identifier for node in Tree.expand_tree(mode=Tree.DEPTH, sorting=False)]
    if len(depth_node_list) == 1:
        code_gen_nodes_list = depth_node_list
        return code_gen_nodes_list
    else:
        code_gen_nodes_list = []

    # print([i for i in Task_tree.rsearch("0_0_1")])
    for node in depth_node_list:
        if len(Tree.children(node)) == 0:
            code_gen_nodes_list.append(node)
        else:
            continue
    
    if start_node in code_gen_nodes_list:
        code_gen_nodes_list = code_gen_nodes_list[code_gen_nodes_list.index(start_node)+1:]
        return code_gen_nodes_list
    else:
        return code_gen_nodes_list

def rebuild_sub_tree_with_wrong_cases(Task_tree, wrong_node, wrong_reason, kg_dict):
    if wrong_node != "0":
        parent_node = Task_tree.parent(wrong_node).identifier
        wrong_steps = []
        for i in Task_tree.children(parent_node):
            wrong_steps.append(i.data)
            Task_tree.remove_node(i.identifier)
        Leaf_nodes_building_no_checking_with_fail_cases(Task_tree[parent_node].data, wrong_steps, wrong_reason, kg_dict, parent_node, Task_tree)
    else:
        Leaf_nodes_building_no_checking_with_fail_cases(Task_tree[wrong_node].data, Task_tree[wrong_node].data, wrong_reason, kg_dict, wrong_node, Task_tree)

def is_chinese(content):
    pattern = re.compile(r'[\u4e00-\u9fa5\uF900-\uFA2D]')
    match = re.search(pattern, content)
    return match is not None