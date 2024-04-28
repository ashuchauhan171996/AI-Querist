from org_langchain import org_chain

question = "I am interested in organization that would expose me to indian culture. Suggest me some organization along with contact details"
           
output = org_chain.invoke(question)
print(output)