from Tree_Running.Tree_Building.Agents.agents_init import *
from Tree_Running.Tree_Building.Agents.Tools.zhengze import *
# from Tree_Building.Agents.agents_init import *
# from Tree_Building.Agents.Tools.zhengze import *


Decomopose_checking_prompt = """
Now you are a professional SQL engineer, I'm going to give you a [root task] and [smaller tasks] that are supposed to accomplish [root task]. At last, I would give you an example, to show you how similar tasks are decomposed. According to the given example and your own thinking, tell me if the [smaller tasks] are correctly setted to finish the [root task]. your one action should follow the framework below:

input:
[father task]: given externally.
[children tasks]: given externally.

example:
[father task]: example, given externally
[children tasks]: example, given externally

your output:
[correct or not]: in this part, your answer should be like this :"[correct or not]: ('yes' or 'no')"
"""

def Decomopose_checking(extracted_example, root_task, smaller_tasks):
    messages = [{"role":"system","content":"You are a precise, efficient and concise SQL engineer."}]
    BugFixing_agent = LlmAgent(messages=messages)
    BugFixing_agent.environmental_feedback(Decomopose_checking_prompt)
    
    response = BugFixing_agent.continue_conversation(user_input = "let us begin:/n" + "[father task]: " + str(root_task) + "/n[children task]: " + str(smaller_tasks) + "/n[example:]: " + str(extracted_example))
    
    print(response)
    c_signal, correct_or_not = get_decompose_correct_or_not(response)

    return c_signal, correct_or_not

# extracted_example = """
# {'father task': 'I want to see the open price of stock 000002 at the day of 2022-10-11, and also its factor_1 data at that day.', 
# 'children tasks': ["1. Join the table 'stock_data','factor_1' on the 'stock_id' column.", "2. Select the 'open price', 'data' columns from the joined table where time = '2022-10-11'."]}
# """
# root_task = """I want to see the spot China prices of all metals at 2012-12-12."""
# node_0_0 = "Based on the given information, the task requires joining three tables ('23_golden', '24_silver', '25_platinum') on the 'time' column. Since the tables have the same structure and only need to be joined on a single column, the complexity of this task is relatively low. There is no data filtering, grouping, or complex operations involved. Therefore, this task can be considered easy."
# node_0_1 = "Based on the given information, this task involves selecting specific columns from a joined table and filtering the data based on a specific date. The number of tables that need to be joined is not mentioned, so we cannot determine the complexity of the join operation. However, the task does not involve any complex operations like grouping or nested querying. It only requires selecting columns and applying a simple filter. Therefore, we can consider this task as easy."

# smaller_tasks = "1. " + node_0_0 + " 2. " + node_0_1
# x,y = Decomopose_checking(extracted_example, root_task, smaller_tasks)
# print(x)
# print(y)