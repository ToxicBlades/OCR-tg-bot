# -*- coding: utf-8 -*-
from openai import OpenAI
import os
import time
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")

#Set your apikey for chat gpt
client = OpenAI(
    # defaults to os.environ.get("OPENAI_API_KEY")
    api_key=API_KEY,
)

def process_ai(text):
    """Function to perform AI processing on email data"""
    retries = 0
    while retries < 3:
      try:
        completion =  client.chat.completions.create(
        # gpt-4-0613
        # gpt-3.5-turbo
        messages = [{"role": "user", "content": f"I will provide you text from a business card pls provide me json which will follow this structure: name,email,phone_number,company_name,address,description,needs. If some fiels is missing just fill them with none: {text}."}],
        model="gpt-3.5-turbo")
        # Extract the required information from the completion
        response_data = completion.choices[0].message.content
        # time.sleep(20)
        if response_data:
            #leave while because we got data
            return response_data
      # Pause for 20 seconds (Api has limit for requsts in a minute,if we procces more then 3 mail it give us api error)
      except Exception as e:
        retries += 1
        time.sleep(20)



