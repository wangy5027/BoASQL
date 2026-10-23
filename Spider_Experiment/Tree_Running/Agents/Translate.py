from Tree_Running.Agents.agents_init import *
from Tree_Running.Agents.Tools.zhengze import *

# from Agents.agents_init import *
# from Agents.Tools.zhengze import *

Translate_prompt="""
You are a professional translator, I'm going to give you a [other language sentence], please help me translate it into English.Your one action should follow the framework below:

input:
[other language sentence]: sentence that should be translated, given externally.

output:
[translated sentence]:sentence that you translated.

warn: 
1. Reply in strict accordance with format requirements.
2. The [translated sentence] you output must end with ".".
"""

def Translate(goal):
    messages = [{"role":"system","content":"You are a precise, efficient and concise translator."}]
    CodeChecking_agent = LlmAgent(messages=messages)
    CodeChecking_agent.environmental_feedback(Translate_prompt)
    response = CodeChecking_agent.continue_conversation(user_input = goal)
    print(response)
    
    if  "translated sentence" in response:
        translated = get_translation(response)
        return translated
    else:
        return response