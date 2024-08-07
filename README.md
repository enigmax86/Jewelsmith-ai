# Jewelsmith-ai

This is a Streamlit-based web application for generating jewelry design recommendations and images based on user input using Amazon Bedrock Foundation models like Claude and StabilityAi for LLM and Image generation tasks. 

## Setup

1. Clone the repository:
    ```bash
    git clone https://github.com/enigmax86/Jewelsmith-ai.git
    cd jewelsmith-ai
    ```

2. Install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Run the Streamlit app:
    ```bash
    streamlit run app.py
    ```

## Usage

1. Enter your basic information and upload an image of your outfit (optional).
2. Follow the chatbot's questions to refine your jewelry design preferences.
3. Generate and view the jewelry design images based on your inputs.
4. Save the conversation and images for future reference.

## Project Structure

```
jewelry_design_app/
│
├── app.py
├── requirements.txt
├── README.md
├── config.py
├── utils/
│   ├── __init__.py
│   ├── api_calls.py
│   ├── image_processing.py
│   ├── conversation.py
└── assets/
    └── outfit_images/

```

