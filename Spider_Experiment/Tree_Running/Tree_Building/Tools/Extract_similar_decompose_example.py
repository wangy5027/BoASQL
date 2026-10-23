import re
import json
import os

current_file_path = os.path.dirname(os.path.abspath(__file__))
cases_file = os.path.join(current_file_path, 'Decompose_cases.json')

def read_cases_file(cases_file_path):
    with open(cases_file, 'r') as file:
        data = json.load(file)
    return data

cases = read_cases_file(cases_file)

def find_most_similar_case(task_tag):
    marks_dict = {}
    irrelevant_tags = ['father task', 'children tasks']
    for case_index, case_content in cases.items():
        case_count = 0
        match_count = 0
        for k,v in case_content.items():
            if k in task_tag:
                match_count = match_count + 1
            if k not in irrelevant_tags:
                case_count = case_count + 1
        if len(task_tag) != 0:
            first_part = match_count / len(task_tag)
            second_part = match_count / case_count
        else:
            first_part = 0
            second_part = match_count / case_count

        marks_dict.update({case_index: first_part * second_part})
    
    ini = 0
    ini_tag = ""
    for tag,mark in marks_dict.items():
        if mark > ini:
            ini_tag = tag
            ini = mark
    return cases[ini_tag]
