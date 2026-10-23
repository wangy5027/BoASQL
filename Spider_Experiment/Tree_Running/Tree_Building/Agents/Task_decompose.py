from Tree_Running.Tree_Building.Agents.agents_init import *
from Tree_Running.Tree_Building.Agents.Tools.zhengze import *

# from Tree_Building.Agents.agents_init import *
# from Tree_Building.Agents.Tools.zhengze import *

Decompose_or_not_prompt = """
Now you are a professional SQL engineer, I'm going to give you a data selection goal, and tables related to it, please tell me the complexity of the task based on the difficulty of sql code generation.If you cannot make sure that a language model like you can generate the sql code correctly in one round, you should consider this task as "complicate". your one action should follow the framework below:

input:
[goal]: data selection goal, given externally.
[related tables]: related data table information, given externally.

output:
[thinking]: Fully based on the given [goal] and [related tables], think step by step, figure out if this sql task is easy or complicate.
[easy_or_complicate]:Your judgment, just return "easy" or "complicate" in this field, no syntax needed.

warn: 
1.Reply in strict accordance with format requirements.
2.Just use the given [related tables], you don't have to figure out the database information by yourself.
3.You don't have to consider the table size, just consider the difficulty of correct sql code generation.
4.When asking for a highest or lowest value of something, instead of using the MAX or MIN, use the DESC LIMIT 1 or ASC LIMIT 1, this can make the task much easier.

example:
Input:
[goal]:Select the open price of stock 000001 from the joined table.
[related tables]: 
{'open_price': {'have_column': {'time': {'time': {'data_type': {'datetime': {}, 'date': {}}}}, 'stock_id': {'stock_id': {'data_type': {'string': {}}}}, 'open_price': {'open_price': {'data_type': {'double': {}}}}}}}
{'close_price': {'have_column': {'time': {'time': {'data_type': {'datetime': {}, 'date': {}}}}, 'stock_id': {'stock_id': {'data_type': {'string': {}}}}, 'close_price': {'close_price': {'data_type': {'double': {}}}}}}}

Output:
[thinking]: Based on the given information, the [goal] described the table as "from the joined table", so I know that the table has already been joined. Therefore, in this round, this task can be easily finished, because it only requires one step(smaller than 3, if more than 3, this should be complicate): simple data filter. So it is easy.
[easy_or_complicate]: easy

example:
Input:
[goal]:I want to see the open price and close price of stock 000002 in 20210101.
[related tables]: 
{'open_price': {'have_column': {'time': {'time': {'data_type': {'datetime': {}, 'date': {}}}}, 'stock_id': {'stock_id': {'data_type': {'string': {}}}}, 'open_price': {'open_price': {'data_type': {'double': {}}}}}}}
{'close_price': {'have_column': {'time': {'time': {'data_type': {'datetime': {}, 'date': {}}}}, 'stock_id': {'stock_id': {'data_type': {'string': {}}}}, 'close_price': {'close_price': {'data_type': {'double': {}}}}}}}

Output:
[thinking]: Based on the given information, this task can be easily finished, because it only requires two steps(smaller than 3, if more than 3, this should be complicate): tables joinning and simple data filter, and the number of tables that need to be joined is very small(smaller than 3), and it does not involves many complex operations like: "tables joining","data filtering","grouping",and "average calculating", "nested queying", etc, so it is easy.
[easy_or_complicate]: easy
"""

def Decompose_or_not(goal,Database_discription):
    messages = [{"role":"system","content":"You are a precise, efficient and concise SQL engineer."}]
    Decompose_or_not_agent = LlmAgent(messages=messages)
    Decompose_or_not_agent.environmental_feedback(Decompose_or_not_prompt)
    
    response = Decompose_or_not_agent.continue_conversation(user_input = "let us begin:" + "[goal]:" + goal + "[database description]:" + str(Database_discription))
    print(response)

    e_c_signal, easy_or_complicate = get_easy_or_complicate(response)
    thinking_signal, thinking = get_thinking_from_Decompose_or_not(response)
    if e_c_signal == "Success" and thinking_signal == "Success":
        return e_c_signal, easy_or_complicate, thinking
    else:
        return "Fail", "", ""

# Database_discription = {'4_consumerpriceindex': {'have_column': {'time': {'data_type': {'datetime': {}, 'date': {}}}, 'china': {'data_type': {'double': {}}}}}, '8_interestrate': {'have_column': {'china': {'data_type': {'double': {}}}}}, '3_unemploymentrate': {'have_column': {'china': {'data_type': {'double': {}}}}}}

# # goal = "What were China's interest rate and consumer price index when China's unemployment rate peaked?"
# goal = "4. Select the interest rate and consumer price index columns from the joined table where the time matches the time when the unemployment rate peaked."
# x, y = Decompose_or_not(goal,Database_discription)
# print(y)

Decompose_PlanMaking_prompt = """
Now you are a professional SQL engineer, I'm going to give you a [goal], a [database description]. Please generate a plan to accomplish the goal. Don't think too much, all the necessary information are given in [database information], NEVER try to modify the table or columns information! Your one action should follow the framework below:

Use the following instructions for PLAN MAKING: 
1.If the [goal] does not ask for the count data, All the aggregation like COUNT, AVE, MAX, MIN can be used only in HAVING, ORDER BY, GROUP BY part and should never exists in the SELECT part.
2.Reply in strict accordance with the format requirements.
3.Select ONLY the columns that are DIRECTLY asked by the [goal], never select the extra columns. for example, if asking "who is the tallest boy", just "select the name column of the tallest boy", do not select the height column.
4.The columns exist in ORDER BY or HAVING should not be selected if the [goal] does not exactly asked to show it.
5.Use the value that directly given by the [goal]. For example, if asking "what's volvo's phone number", just "Filter the results to include only rows where `name` is 'volvo'.", do not change 'volvo' into 'Volvo' or 'VOLVO' or anything else.If no value is provided, use the lowercase values.
6.DESC LIMIT 1 is preferred than SELECT MAX().
7.If not exactly asked, do not use GROUP BY.

input:
[goal]: data selection goal, given externally by me.
[database description]: database description, given externally by me.

output:
[thinking]: Based on the given [goal] and [database descriprtion], think step by step, Break down the current target into n SQL statements to generate small targets.
[steps]:Steps of sql code generating to accomplish the goal. Each step is related to its forward and afterward steps.

example:
input:
[goal]: I want to see the stock 000002's factor_1 data and stock open price data at 2012-01-12, where the company name is volvo.
[database description]: 
{'stock_open_price': {'have_column': {'time': {'time': {'data_type': {'datetime': {}}}}, 'stock_000001': {'stock_000001': {'data_type': {'double': {}}}}, 'stock_000002': {'stock_000002': {'data_type': {'double': {}}}}}}}
{'factor_1': {'have_column': {'time': {'time': {'data_type': {'datetime': {}}}}, 'company_name': {'company_name': {'data_type': {'TEXT': {}}}}, 'stock_000001': {'stock_000001': {'data_type': {'double': {}}}}, 'stock_000002': {'stock_000002': {'data_type': {'double': {}}}}}}}
{'factor_2': {'have_column': {'time': {'time': {'data_type': {'datetime': {}}}}, 'stock_000001': {'stock_000001': {'data_type': {'double': {}}}}}}}

output:
[thinking]: Based on the given [goal] and [database description], we need to select stock 000002's factor_1, factor_2 and open price data. According to the given [database description], factor_2 table doesn't have a column that relevant to stock 000002. As I only generate contents based on the given information, and I always try to make sure each step I generated are operable, so here I decide to ignore the table factor_2.
[steps]:
1. Join the table stock_open_price and factor_1 on column 'stock_000001'.
2. Filter the results to include only rows where `time` is '2012-01-12' and `company_name` is 'volvo'.
"""

def Decompose_PlanMaking(goal,Database_discription):
    messages = [{"role":"system","content":"You are a precise, efficient and concise SQL engineer."}]
    Decompose_PlanMaking_agent = LlmAgent(messages=messages)
    Decompose_PlanMaking_agent.environmental_feedback(Decompose_PlanMaking_prompt)
    
    response = Decompose_PlanMaking_agent.continue_conversation(user_input = "let us begin:" + "[goal]:" + goal + "[database description]:" + str(Database_discription))
    print(response)

    pattern = r'\[steps\]:\s*(.*?)\n\n'
    matches = re.search(pattern, response, re.DOTALL)

    if matches:
        steps_text = matches.group(1)
        steps_list = steps_text.split('\n')
    else:
        steps_list = []
    
    if len(steps_list) == 0:
        pattern = r'\[steps\]:\s+(.+)'
        matches = re.search(pattern, response, re.DOTALL)

        if matches:
            steps_text = matches.group(1)
            steps_list = steps_text.split('\n')
        else:
            steps_list = []
    
    if len(steps_list) == 0:
        steps_match = re.search(r'\[?s(?:te)?ps\]?:(.+)', response, re.DOTALL | re.IGNORECASE)
        if steps_match:
            steps_list = steps_match.group(1).split('\n')
        else:
            steps_list = []
    
    for i in steps_list:
        if "missing information" in i:
            signal = "missing information"
            return signal, response

    signal = "Sucess"
    return signal,steps_list



Decompose_PlanMaking_with_fail_cases_prompt = """
Now you are a professional SQL engineer, I'm going to give you a data selection goal, a detailed description of database, a wrong steps and its corresponding wrong reason. Please modify the [wrong steps] according to the [wrong reason]. Don't think too much, just use the given [database information], NEVER try to modify the table or columns information! Your one action should follow the framework below:

input:
[goal]: data selection goal, given externally by me.
[database description]: database description, given externally by me.
[wrong steps]: wrong steps, given externally by me.
[wrong reason]: the error message got when executing the [wrong steps], given externally by me.

output:
[thinking]: Based on the given [goal], [database descriprtion], [wrong steps] and [wrong reason], think step by step, figure out how to modify the [wrong steps] according to the [wrong reason].
[New steps]: New steps of sql code generating to accomplish the goal. Each step is related to its forward and afterward steps, and is got from modifying the [wrong steps]. 

warn: 
1.Reply in strict accordance with format requirements.
2.If the given [database information] is not enough for you to generate the plan, return "missing information".
3.Never return a direct sql code to me.
4.Never create a table name or column name by yourself when there is no related column or table.
5.Don't think too much, just use the given [database information], NEVER try to modify the table or columns information!
6.You don't have to use all the tables provided.

example:
input:
[goal]: I want to see the stock 000002's factor_1 data, factor_2 data and stock open price data at 2012-01-01.
[database description]: 
{'stock_open_price': {'have_column': {'time': {'time': {'data_type': {'datetime': {}, 'date': {}}}}, 'stock_000001': {'stock_000001': {'data_type': {'double': {}}}}, 'stock_000002': {'stock_000002': {'data_type': {'double': {}}}}}}}
{'factor_1': {'have_column': {'time': {'time': {'data_type': {'datetime': {}, 'date': {}}}}, 'stock_000001': {'stock_000001': {'data_type': {'double': {}}}}, 'stock_000002': {'stock_000002': {'data_type': {'double': {}}}}}}}
[wrong steps]:
["1. Join the table stock_open_price, factor_1, factor_2 on column 'stock_000001'.",
"2. Select the stock_000001 and time columns from the joined table where time = '2012-01-01'."]
[wrong reason]:
pymysql.err.ProgrammingError: (1146, "Table 'factor_2' doesn't exist")

output:
[thinking]: Based on the given [goal] and [database description], we need to select stock 000002's factor_1 and open price data. According to the given [database description], there are two tables: 'stock_open_price' and 'factor_1' tables. The [wrong steps] try to use the table factor_2, but it does not exist in the database according to the [wrong reason]. So here I would modify the [wrong plan] to make it without table 'factor_2'.
[New steps]:
1. Join the table stock_open_price and factor_1 on column 'stock_000001'.
2. Select the stock_000001 and time columns from the joined table where time = '2012-01-01'.
"""

def Decompose_PlanMaking_with_fail_cases(goal, wrong_steps, wrong_reason, Database_discription):
    messages = [{"role":"system","content":"You are a precise, efficient and concise SQL engineer."}]
    Decompose_PlanMaking_with_fail_cases_agent = LlmAgent(messages=messages)
    Decompose_PlanMaking_with_fail_cases_agent.environmental_feedback(Decompose_PlanMaking_with_fail_cases_prompt)
    
    response = Decompose_PlanMaking_with_fail_cases_agent.continue_conversation(user_input = "let us begin:" + "[goal]: " + str(goal) + "[database description]: " + str(Database_discription) + "[wrong steps]:" + str(wrong_steps) + "[wrong reason]:" + str(wrong_reason))
    print(response)

    pattern = r'\[New steps\]:\s*(.*?)\n\n'
    matches = re.search(pattern, response, re.DOTALL)

    if matches:
        steps_text = matches.group(1)
        steps_list = steps_text.split('\n')
    else:
        steps_list = []
    
    if len(steps_list) == 0:
        pattern = r'\[New steps\]:\s+(.+)'
        matches = re.search(pattern, response, re.DOTALL)

        if matches:
            steps_text = matches.group(1)
            steps_list = steps_text.split('\n')
        else:
            steps_list = []
    
    for i in steps_list:
        if "missing information" in i:
            signal = "missing information"
            return signal, response

    signal = "Sucess"
    return signal,steps_list

# related_tables = """{'101_gdpinchina_namegdp': {'have_column': {'time': {'time': {'data_type': {'datetime': {}, 'date': {}}}}, 'china': {'china': {'data_type': {'double': {}}}}, 'usa': {'usa': {'data_type': {'double': {}}}}, 'japan': {'japan': {'data_type': {'double': {}}}}, 'germany': {'germany': {'data_type': {'double': {}}}}, 'u.k.': {}, 'switzerland': {'switzerland': {'data_type': {'double': {}}}}}}}
# """
# goal = "I'd like to see the years when China's actual gdp was higher than its name gdp."

# kg = """{'23_golden': {'have_column': {'time': {'time': {'data_type': {'datetime': {}, 'date': {}}}}, 'spot_china_gold': {'spot_china_gold': {'data_type': {'double': {}}}}, 'spot_london_gold': {'spot_london_gold': {'data_type': {'double': {}}}}, 'futures_china_gold': {'futures_china_gold': {'data_type': {'double': {}}}}, 'futures_comex_gold': {'futures_comex_gold': {'data_type': {'double': {}}}}}}}
# {'24_silver': {'have_column': {'time': {'time': {'data_type': {'datetime': {}, 'date': {}}}}, 'spot_china_silver': {'spot_china_silver': {'data_type': {'double': {}}}}, 'spot_london_silver': {'spot_london_silver': {'data_type': {'double': {}}}}, 'futures_china_gold': {'futures_china_gold': {'data_type': {'double': {}}}}, 'futures_comex_silver': {'futures_comex_silver': {'data_type': {'double': {}}}}}}}
# {'25_platinum': {'have_column': {'time': {'time': {'data_type': {'datetime': {}, 'date': {}}}}, 'spot_china_platinum': {'spot_china_platinum': {'data_type': {'double': {}}}}, 'spot_london_platinum': {'spot_london_platinum': {'data_type': {'double': {}}}}, 'futures_comex_platinum': {'futures_comex_platinum': {'data_type': {'double': {}}}}, 'usa': {'usa': {'data_type': {'double': {}}}}}}}
# """
# goal = "I want to see the spot London prices of all metals at 2012-12-12."
# wrong_steps = ["1.Join the tables '23_golden', '24_silver', '26_copper', '27_aluminum', '28_zinc', '29_lead', and '30_nickel' on the 'time' column.",
#               "2.Select the spot London prices from the joined table where the time is '2012-12-12'."]
# signal,steps_list = Decompose_PlanMaking_with_fail_cases(goal, wrong_steps, kg)
# print(steps_list)  



# related_tables = """{'14_stockmarketindex': {'have_column': {'time': {'time': {'data_type': {'datetime': {}, 'date': {}}}}, 'china': {'china': {'data_type': {'double': {}}}}, 'usa': {'usa': {'data_type': {'double': {}}}}, 'japan': {'japan': {'data_type': {'double': {}}}}, 'germany': {'germany': {'data_type': {'double': {}}}}, 'u.k.': {}, 'switzerland': {'switzerland': {'data_type': {'double': {}}}}}}}
# {'15_housepriceindex': {'have_column': {'time': {'time': {'data_type': {'datetime': {}, 'date': {}}}}, 'china': {'china': {'data_type': {'double': {}}}}, 'usa': {'usa': {'data_type': {'double': {}}}}, 'japan': {'japan': {'data_type': {'double': {}}}}, 'germany': {'germany': {'data_type': {'double': {}}}}, 'u.k.': {}, 'switzerland': {'switzerland': {'data_type': {'double': {}}}}}}}
# """
# goal = "I want to know the China's stock market index at the time China’s house price index reached its highest pitch."

# signal, tasks_list = Decompose(goal, related_tables)

# print("tasks:", tasks_list)