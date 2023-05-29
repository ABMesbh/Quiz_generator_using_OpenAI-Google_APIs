from __future__ import print_function
import openai
import re
import os
import numpy as np
import streamlit as st
from io import BytesIO
import streamlit.components.v1 as components


# from st_custom_components import st_audiorec

# wav_audio_data = st_audiorec()

# if wav_audio_data is not None:
#     # display audio data as received on the backend
#     st.audio(wav_audio_data, format='audio/wav')
    
# INFO: by calling the function an instance of the audio recorder is created
# INFO: once a recording is completed, audio data will be saved to wav_audio_data
import whisper
import time


from apiclient import discovery
from httplib2 import Http
from oauth2client import client, file, tools


model = whisper.load_model("base")


while not os.path.exists("audio.wav"):
    # print("Waiting for the file to be created...")
    time.sleep(30)
result = model.transcribe("audio.wav")
# print(result["text"])


openai.api_key = "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"
content = result["text"] + """ create the quiz with 10 questions with multiple choice answers in the same format as following and in the end say finished : 
    Title of quiz : "quiz on ..." 
Question 1 : ....
    a.  
    b.  
    c.
    d.
Question 2 : ....
    a. 
    b. 
    c. 
    d. 
"""

completion = openai.ChatCompletion.create(model = "gpt-3.5-turbo-0301", messages = [{"role": "user", "content": content }])
requests = completion.choices[0].message.content

# Parsing the result

Title = re.findall(r'Quiz on (.*?)\n' , requests)
questions = re.findall(r'Question \d+: (.*?)\n', requests)

a_answers = re.findall(r'a\.(.*?)\n' ,requests)
b_answers = re.findall(r'b\.(.*?)\n' ,requests)
c_answers = re.findall(r'c\.(.*?)\n' ,requests)
d_answers = re.findall(r'd\.(.*?)\n' ,requests)


q = []

for i in range(len(questions)):
  q.append({
        "createItem": {
            "item": {
                "title": questions[i],
                "questionItem": {
                    "question": {
                        "required": True,
                        "choiceQuestion": {
                            "type": "RADIO",
                            "options": [
                                {"value": a_answers[i]},
                                {"value": b_answers[i]},
                                {"value": c_answers[i]},
                                {"value": d_answers[i]}
                            ],
                            "shuffle": True
                        }
                    }
                },
            },
            "location": {
                "index": i
            }
        }
    })


SCOPES = "https://www.googleapis.com/auth/forms.body"
DISCOVERY_DOC = "https://forms.googleapis.com/$discovery/rest?version=v1"

store = file.Storage('token.json')
creds = None
if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets('key.json', SCOPES)
    creds = tools.run_flow(flow, store)

form_service = discovery.build('forms', 'v1', http=creds.authorize(
    Http()), discoveryServiceUrl=DISCOVERY_DOC, static_discovery=False)

# Request body for creating a form
NEW_FORM = {
    "info": {
        "title": Title[0],
    }
}

# Request body to add a multiple-choice question
NEW_QUESTION = {
    "requests": q}

# Creates the initial form
result = form_service.forms().create(body=NEW_FORM).execute()

# Adds the question to the form
question_setting = form_service.forms().batchUpdate(formId=result["formId"], body=NEW_QUESTION).execute()

# Prints the result to show the question has been added
get_result = form_service.forms().get(formId=result["formId"]).execute()
print(get_result['responderUri'])
