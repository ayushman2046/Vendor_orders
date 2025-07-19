import os

from langchain_core.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)

from langchain.chat_models import ChatOpenAI


def create_prompt_template(template_string, sys_prompt=None):
    #--------------Create a ChatPromptTemplate from the given template string, optionally including a system prompt.
    if sys_prompt is not None and len(sys_prompt) > 0:
        system_template = SystemMessagePromptTemplate.from_template(sys_prompt)
        user_template = HumanMessagePromptTemplate.from_template(template_string)
        template = ChatPromptTemplate.from_messages([system_template, user_template])
    else:
        template = ChatPromptTemplate.from_template(template_string)

    return template


def extract_input_variables(langchain_prompt_template):
    #----------------Extract all input variables from the given ChatPromptTemplate.

    prompt_variables = langchain_prompt_template.input_variables
    return prompt_variables


def all_reqd_variables_present(langchain_prompt_template, input_variables):
    #----Verify if all the dynamic keys in prompts are available.

    variables_list = extract_input_variables(langchain_prompt_template)
    print("REQD VARIABLES LIST: ")
    print(type(variables_list), variables_list)
    for variable in variables_list:
        if variable not in input_variables:  # reqd variable is not present in the input
            print("MISSING VARIABLE: ")
            print(type(variable), variable)
            return False
    return True  # all reqd variables are present


def gen_final_prompt(
    langchain_prompt_template,
    input_variables
):
    # Verify the dynamic variable availablity and fill the values in actual prompt.

    allPresent = all_reqd_variables_present(langchain_prompt_template, input_variables)
    if allPresent == False:
        return None
    print("All reqd variables are present")

    # Get required variables list from the langchain_template
    reqd_variables_list = extract_input_variables(langchain_prompt_template)

    # Create a dictionary of variables to be sent in the prompt
    prompt_variables_dict = {
        var: input_variables.get(var, "") for var in reqd_variables_list
    }

    # Format the prompt with the input variables
    final_prompt = langchain_prompt_template.format_messages(**prompt_variables_dict)
    return final_prompt


def invoke_langchain(prompt_langchain_template, input_variables):
    #-------------Invoke Langchain API with the given prompt and return the response.

    llm_model = "gpt-4o-mini" #------------as we have only one source openai so I am using gpt-4o-mini, we can use other models as well.
    input_temperature = input_variables.get("temperature", 0.7)
    
    chat = ChatOpenAI(
            temperature=input_temperature,
            model=llm_model,
    )
    # Build final prompt: fill dynamic keys in prompt
    final_prompt = gen_final_prompt(prompt_langchain_template, input_variables)
    if not final_prompt:
        return False
    
    print("****> final prompt before inference <**** : ", final_prompt)
    response = chat.invoke(final_prompt)
    print("response - ", response)
    return response