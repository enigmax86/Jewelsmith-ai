import json
import uuid
import streamlit as st
from utils.api_calls import call_endpoint, store_in_mongodb
from config import upload_conversation_endpoint , chatbot_response_endpoint


# The system prompt being sent to get follow up questions giving all the previous chat as the context
temp_sys_prompt_1 = """
You are a friendly and engaging chatbot for a jewelry company. Based on the information provided below, please ask one follow-up question to the customer to understand their needs better. Follow these guidelines:

1. Question Specificity: Ask one short, one-liner question containing only one key entity to understand the customer's needs better.
2. Inclusion of Options: Yes : Frame every question to include options in the framed sentence itself related to the question providing the user a choice.
3. Explanation : Explain the options if using some complex terms in options like 'filigree' or 'embellishments'.
4. Entity Specification: Clearly mention the key entity in the question. Do not include entities such as metal or size.
5. Context Awareness: Do not repeat key entities already covered in the basic information provided below.
6. Conciseness: Print only the follow-up question and nothing extra, such as explanations or additional comments.
7. Tone: Use a warm and friendly tone to make the user feel welcomed and valued.
8. Relevance to Outfit : If outfit description is provided also consider the details of the outfit to ask the follow up question.

Make sure to include options for every question and explain complex terms if used in the question or options.



"""

# Function to convert the basic info json data and outfit_caption data into a string to be passed to the llm for further response
def basic_info_to_string(basic_info, outfit_caption):
    info_str = ( 
        f"Occasion: {basic_info['occasion']}, \n"
        f"Gift or Personal Purchase: {basic_info['purchase_type']} , \n"
        f"Gender: {basic_info['gender']} , \n"
        f"Age Group: {basic_info['age_group']} , \n"
        f"Religion: {basic_info.get('religion', 'Not specified')} , \n"
        f"Type of Jewelry: {basic_info['jewelry_type']} , \n"
        f"Budget: {basic_info['budget']} , \n"
        f"Outfit Image Provided: {'Yes' if basic_info['outfit_image'] else 'No'} , "
        f"Outfit Description : {outfit_caption if basic_info['outfit_image'] else 'No'} "
    )
    return info_str

# Function to call the chatbot_response_endpoint 
# Input : json_data = {'system_prompt' : system_prompt , 'user_prompt' : user_prompt}
def get_chatbot_response(json_data):
    return call_endpoint(chatbot_response_endpoint, json_data)['body']
    
# Function to properly format the conversation from st.session_state.messages and upload the conversation to the s3_bucket
# returns the link to the file stored in s3_bucket
def format_and_upload_conversation():
    conversation_dict = {}
    for idx, message in enumerate(st.session_state.messages):
        key = f"{message['role']}_{idx}"
        conversation_dict[key] = message['content']
    
    json_conversation = json.dumps(conversation_dict)
    
    event_payload = {
        "body": json_conversation
    }
    
    response = call_endpoint(upload_conversation_endpoint, event_payload)
    response_body = response['body']
    s3_conv_url = response_body.strip('"')
    st.success(f"Conversation saved and successfully uploaded ! Access it [here]({s3_conv_url}).")
    return s3_conv_url
