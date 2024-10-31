import os
from PIL import Image
from config import upload_image_endpoint, image_caption_endpoint , image_generator_endpoint
from utils.api_calls import call_endpoint
import streamlit as st
import requests
import io 
import base64
from io import BytesIO

# Function to return base64_encoded_string 
# Input : takes the outfit_image object recieved from st.file_uploader in the basic info form
def get_outfit_base64(uploaded_file):
    bytes_data = uploaded_file.getvalue()
    base64_encoded_string = base64.b64encode(bytes_data).decode('utf-8')
    return base64_encoded_string
    
# Function to save the image locally 
# Input : takes the outfit_image object recieved from st.file_uploader in the basic info form
# NOT BEING USED IN THE CODE CURRENTLY
def save_image(outfit_image):
    outfit_image_path = os.path.join("assets/outfit_images", outfit_image.name)
    with open(outfit_image_path, "wb") as f:
        f.write(outfit_image.getbuffer())
    return outfit_image_path

# Function to generate captions (for outfit images) 
# Input : takes the outfit_image object recieved from st.file_uploader in the basic info form
def generate_image_captions(outfit_image):
    img_b64_encoded_string = get_outfit_base64(outfit_image)
    outfit_caption = call_endpoint(image_caption_endpoint, {'image_base64' : img_b64_encoded_string})['body']
    st.success(f"Outfit caption generated: {outfit_caption}")
    return outfit_caption

def generate_image_captions_froms3(image_url, image_caption_endpoint = image_caption_endpoint):
    # Step 1: Download the image from the S3 URL
    response = requests.get(image_url)
    
    if response.status_code == 200:
        # Step 2: Open the image and convert it to base64
        image = Image.open(BytesIO(response.content))
        buffered = BytesIO()
        image.save(buffered, format="JPEG")
        img_b64_encoded_string = base64.b64encode(buffered.getvalue()).decode("utf-8")
        
        # Step 3: Call the API endpoint to get the image caption
        caption_response = call_endpoint(image_caption_endpoint, {'image_base64': img_b64_encoded_string})
        
        if 'body' in caption_response:
            return caption_response['body']  # Return the caption from the API response
        else:
            return "Caption not found in response"
    else:
        return f"Failed to retrieve image from URL. Status code: {response.status_code}"


# Function to generate final image based on the final prompt 
# json_data = {'prompt' : final_prompt}
def get_image_response(json_data):
    return call_endpoint(image_generator_endpoint , json_data)

# Function to upload image to s3 bucket and return the link of the image
def upload_image_to_s3(img):
    image_buffer = io.BytesIO()
    img.save(image_buffer, format="PNG")
    image_base64 = base64.b64encode(image_buffer.getvalue()).decode()
    s3_response = call_endpoint(upload_image_endpoint,{'image_data': image_base64})
    try :
        response_body = s3_response['body']
        s3_image_url = response_body.strip('"')
    except Exception as e:
        print(e)
        s3_image_url = "Sorry, could not get the url. Please try again "
    return s3_image_url    
    