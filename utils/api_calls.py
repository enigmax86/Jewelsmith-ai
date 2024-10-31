import requests
import streamlit as st
from config import *
import uuid
import io 
import base64
import json
from config import similarimagesfetcher

def call_endpoint(endpoint , json_data):
    try:
        response = requests.post(endpoint, json=json_data)
        print(response.json())
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        st.error(f'HTTP error occurred: {http_err}')
    except requests.exceptions.RequestException as req_err:
        st.error(f'Request error occurred: {req_err}')
    except requests.exceptions.JSONDecodeError as json_err:
        st.error(f'JSON decode error occurred: {json_err}')
        st.error(f"Response text: {response.text}")


def store_in_mongodb(s3_conv_url, s3_image_urls):
    chat_id = str(uuid.uuid4())
    mongodb_data = {
        "username": st.session_state.basic_info['username'],
        "chat_id": chat_id,
        "conversation_link": s3_conv_url,
        "image_link": s3_image_urls
    }
    mongodb_response = call_endpoint(store_data_endpoint, mongodb_data)
    st.success(mongodb_response['body'])


def fetch_similar_images(prompt, jtype):
    # payload = {
    #     "body": "{\"prompt\": \"" +prompt + ", \"jtype\": \"" + jtype +"\"}"
    # }
    body_content = {"prompt" : prompt , "jtype" : jtype} 
    body_content_str = json.dumps(body_content)

    payload = {
        
    "body": body_content_str

    }
    response = call_endpoint(similarimagesfetcher, payload)  # Modify to match your API call function
    body_str = response['body']
    parsed_json = json.loads(body_str)
    urllist = parsed_json['urls']
    return urllist