from fastapi import FastAPI, Request
import dotenv, os
from flask import request, jsonify
from openai import OpenAI
import requests
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

app = FastAPI()

#dictionary to store chat history for every user
message_history_dic = {}

#loading the tokens and keys
dotenv.load_dotenv()
openai_token = os.environ["OPENAI_API_KEY"]
whatsapp_token = os.environ["WHATSAPP_TOKEN"]
verify_token = os.environ["VERIFY_TOKEN"]

#create chroma database to store vector embeedings of all the documents
ORGS_CHROMA_PATH = "chroma_data/"
orgs_vector_db = Chroma(
    persist_directory=ORGS_CHROMA_PATH,
    embedding_function=OpenAIEmbeddings(),
)

# creating LLM model
client = OpenAI(api_key=openai_token)
  
# To verify and authenticate whatsapp and webapp webhook
def verify_and_authen(request):
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode and token:
        # Check the mode and token sent are correct
        if mode == "subscribe" and token == verify_token:
            print("WEBHOOK_VERIFIED")
            return challenge, 200
        else:
            print("VERIFICATION_FAILED - verify tokens did not match")
            return jsonify({"status": "error", "message": "Verification failed"}), 403
    else:
        print("MISSING_PARAMETER")
        return jsonify({"status": "error", "message": "Missing parameters"}), 400
    
# handling messages received from whatsapp
def process_message(request):
    body = request.get_json()
    # print(f"request body: {body}")
    try:
        if body.get("object"):
            if (
                body.get("entry")
                and body["entry"][0].get("changes")
                and body["entry"][0]["changes"][0].get("value")
                and body["entry"][0]["changes"][0]["value"].get("messages")
                and body["entry"][0]["changes"][0]["value"]["messages"][0]
            ):
                message = body["entry"][0]["changes"][0]["value"]["messages"][0]
                if message["type"] == "text":
                    print("message is:", message["text"]["body"]) 
                    response = request_llm_model(message["text"]["body"], message["from"])
                    reply_to_whatsapp(body, response)
                else:
                    print("message is not text")
                    reply_to_whatsapp(body, 'send message in text form')
                
            return jsonify({"status": "ok"}), 200
        else:
            # if the request is not a WhatsApp API event, return an error
            return (jsonify({"status": "error", "message": "Not a WhatsApp API event"}), 404,)
            
    except Exception as e:
        print('error:', {e})
        return jsonify({"status": "error", "message": str(e)}), 500
    
# create a message log for each phone number and return the current message log
def add_message_in_log(message, phone_number, role):
    initial_log = {
        "role": "system",
        "content": """Your job is to use organization data
of all the organization at Texas A&M University to answer questions and 
queries of students about various organizations. Use the following context to answer questions.
Be as consise as possible, try to limit response to max tokens of 100, but don't make up any information
that's not from the context. If you don't know an answer, say
you don't know.""",
    }
    if phone_number not in message_history_dic:
        message_history_dic[phone_number] = [initial_log]
        relevant_docs = orgs_vector_db.similarity_search(message, k=4)
        message_log_context = {
        "role":"system", "content": relevant_docs[0].page_content + relevant_docs[1].page_content + relevant_docs[2].page_content + relevant_docs[3].page_content,
        }
        message_history_dic[phone_number].append(message_log_context)
    
    message_log_role = {
        "role": role, "content": message
    }
    message_history_dic[phone_number].append(message_log_role)
    return message_history_dic[phone_number]

#requesting llm model and receiving the response
def request_llm_model(message, from_number):
    try:
        message_log = add_message_in_log(message, from_number, "user")
        print('sending following messgae to model: ', message_log)
        response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages= message_log,
        temperature=0.0,
        max_tokens=100,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
        )
        response_message = response.choices[0].message.content
        print(f"openai response: {response_message}")
        
        message_log = {"role": "assistant", "content": response_message}
        message_history_dic[from_number].append(message_log)
        
    except Exception as e:
        print(f"openai error: {e}")
        response_message = "Sorry, the OpenAI API is currently overloaded or offline. Please try again later."
        message_history_dic[from_number].pop()
    return response_message


# send LLM response to the user through whatsapp
def reply_to_whatsapp(body, message):
    value = body["entry"][0]["changes"][0]["value"]
    phone_number_id = value["metadata"]["phone_number_id"]
    from_number = value["messages"][0]["from"]
    headers = {
        "Authorization": f"Bearer {whatsapp_token}",
        "Content-Type": "application/json",
    }
    url = "https://graph.facebook.com/v18.0/" + phone_number_id + "/messages"
    data = {
        "messaging_product": "whatsapp",
        "to": from_number,
        "type": "text",
        "text": {"body": message},
    }
    response = requests.post(url, json=data, headers=headers)
    print(f"whatsapp message response: {response.json()}")
    response.raise_for_status()



################
#### ROUTES ####
################

@app.get("/")
async def home():
    return "WhatsApp OpenAI Webhook is listening!"

   
# Accepting POST and GET requests at /webhook from whatsapp
@app.get("/webhook")
@app.post("/webhook")
async def webhook(request: Request):
    # To verify and authenticate WhatsApp and web app webhook
    if request.method == "GET":
        return verify_and_authen(request)
    # Processing the received message from WhatsApp
    elif request.method == "POST":
        return process_message(request)

@app.get("/data_record")
async def data_record():
    return message_history_dic

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, debug=True)