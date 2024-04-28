from flask import Flask
import dotenv, os
from flask import request, jsonify
from org_langchain import org_chain
import requests
app = Flask(__name__)

message_log_dict = {}
dotenv.load_dotenv()
whatsapp_token = os.environ["WHATSAPP_TOKEN"]
verify_token = os.environ["VERIFY_TOKEN"]

@app.route("/", methods=["GET"])
def home():
    return "WhatsApp OpenAI Webhook is listening!"


# send LLM response to the user through whatsapp
def send_whatsapp_message(body, message):
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

# create a message log for each phone number and return the current message log
def update_message_log(message, phone_number, role):
    initial_log = {
        "role": "system",
        "content": "You are a helpful assistant named WhatsBot.",
    }
    if phone_number not in message_log_dict:
        message_log_dict[phone_number] = [initial_log]
    message_log = {"role": role, "content": message}
    message_log_dict[phone_number].append(message_log)
    return message_log_dict[phone_number]

# remove last message from log if OpenAI request fails
def remove_last_message_from_log(phone_number):
    message_log_dict[phone_number].pop()

def make_openai_request(message, from_number):
    try:
        message_log = update_message_log(message, from_number, "user")
        response_message = org_chain.invoke(message)
        print(f"openai response: {response_message}")
        # update_message_log(response_message, from_number, "assistant")
    except Exception as e:
        print(f"openai error: {e}")
        response_message = "Sorry, the OpenAI API is currently overloaded or offline. Please try again later."
        # remove_last_message_from_log(from_number)
    return response_message

# handle text WhatsApp messages
def handle_whatsapp_message(body):
    message = body["entry"][0]["changes"][0]["value"]["messages"][0]
    if message["type"] == "text":
        message_body = message["text"]["body"]
        print("message is:", message_body) 
    else:
        print("message is not text")
    response = make_openai_request(message_body, message["from"])
    send_whatsapp_message(body, response)

# handling messages received from whatsapp
def handle_message(request):
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
                handle_whatsapp_message(body)
            return jsonify({"status": "ok"}), 200
        else:
            # if the request is not a WhatsApp API event, return an error
            return (
                jsonify({"status": "error", "message": "Not a WhatsApp API event"}),
                404,
            )
            
    except Exception as e:
        print('error:', {e})
        return jsonify({"status": "error", "message": str(e)}), 500
    
    
# To verify and authenticate whatsapp and webapp webhook
def verify(request):
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode and token:
        # Check the mode and token sent are correct
        if mode == "subscribe" and token == verify_token:
            # Respond with 200 OK and challenge token from the request
            print("WEBHOOK_VERIFIED")
            return challenge, 200
        else:
            # Responds with '403 Forbidden' if verify tokens do not match
            print("VERIFICATION_FAILED")
            return jsonify({"status": "error", "message": "Verification failed"}), 403
    else:
        # Responds with '400 Bad Request' if verify tokens do not match
        print("MISSING_PARAMETER")
        return jsonify({"status": "error", "message": "Missing parameters"}), 400
    
# Accepting POST and GET requests at /webhook from whatsapp
@app.route("/webhook", methods=["POST", "GET"])
def webhook():
    # To verify and authenticate whatsapp and webapp webhook
    if request.method == "GET":
        return verify(request)
    # processing the received message from whatsapp
    elif request.method == "POST":
        return handle_message(request)

@app.route("/data_record", methods=["POST", "GET"])
def data_record():
    return message_log_dict

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)