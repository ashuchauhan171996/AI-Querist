from langchain.prompts import (
    PromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    ChatPromptTemplate,
)

org_template_str = """Your job is to use organization data
of all the organization at Texas A&M University to answer questions and 
queries of students about various organizations. Use the following context to answer questions.
Be as consise as possible, but don't make up any information
that's not from the context. If you don't know an answer, say
you don't know.

{context}
"""

org_system_prompt = SystemMessagePromptTemplate(
    prompt=PromptTemplate(
        input_variables=["context"],
        template=org_template_str,
    )
)

org_human_prompt = HumanMessagePromptTemplate(
    prompt=PromptTemplate(
        input_variables=["question"],
        template="{question}",
    )
)
messages = [org_system_prompt, org_human_prompt]
org_prompt_template = ChatPromptTemplate(
    input_variables=["context", "question"],
    messages=messages,
)