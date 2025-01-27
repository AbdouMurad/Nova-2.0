import openai
from dotenv import load_dotenv, find_dotenv
import os
import time
import json
import Spotify
import Google
import datetime
from zoneinfo import ZoneInfo
import pyautogui
import base64

load_dotenv()
openai.api_key = os.environ.get("OpenAi_Api_Key")
#==================================FUNCTIONS================================
class Functions:
    def __init__(self):
        self.GoogleService = None
    def send_email(self,arguments):
        if not self.GoogleService:
            self.GoogleService = Google.authenticate_google_api()
        print(f"ARGUMENTS:{arguments}")
        if input(f"send email to {arguments["to"]}? (y/n)") == "y":
            Email_id = Google.send_email_gmail(self.GoogleService[0],arguments["to"],arguments["subject"],arguments["body"])
            return f"email sent. Email ID: {Email_id}"
        else:
            return "email canceled"
    def create_contact(self,argument):
        if not self.GoogleService:
            self.GoogleService = Google.authenticate_google_api()
        response = Google.add_contact(self.GoogleService[1],argument["name"],argument["email"])
        return response
    def get_contact_list(self,argument=None):
        if not self.GoogleService:
            self.GoogleService = Google.authenticate_google_api()
        response = Google.list_google_contacts(self.GoogleService[1])
        return response
    def create_event_calendar(self,argument):
        if not self.GoogleService:
            self.GoogleService = Google.authenticate_google_api()
        response = Google.create_event(self.GoogleService[2],argument)
        return response
    def get_timezone(self,argument=None):
        if not self.GoogleService:
            self.GoogleService = Google.authenticate_google_api()
        response = Google.get_timezone(self.GoogleService[2])
        return response
    def get_DateTime(self,arguement=None):
        time_zone = ZoneInfo(self.get_timezone(None))
        now = datetime.datetime.now(time_zone).isoformat(timespec="seconds")
        return f"current DateTime:{now}"
    def get_events(self,argument):
        if not self.GoogleService:
            self.GoogleService = Google.authenticate_google_api()
        events = []
        for event in Google.get_events(self.GoogleService[2],argument).get("items",[]):
            events.append([f"Date:{event["start"]["dateTime"]}",f"end:{event["end"]["dateTime"]}",f"summary:{event["summary"]}"])
        return f"Today's Date:{self.get_DateTime()}." + "upcoming events:"+str(events) 
    def get_track_spotify_uri(self,argument):
        response = Spotify.search_track(argument["song_name"],argument["artist_name"])
        return response
    def play_spotify_song(self,argument):
        response = Spotify.play_music(argument["track_uri"])
        return response
    def take_screenshot(self,argument=None):
        screenshot = pyautogui.screenshot()
        screenshot.save("screenshot.png")
        return "Screenshot saved"
    def get_screenshot(self,argument =None):
        with open("screenshot.png",'rb') as screenshot_file:
            screenshot_data = screenshot_file.read()
            encoded_image = base64.b64encode(screenshot_data).decode('utf-8')
        return encoded_image
#===================================Assistant================================
class Nova:
    thread_id = "thread_QS8gnvnXi1ODhLdFmlnMYB5o"
    Assistant_id = 'asst_iJEdZTYHW5RHES223KfY5ro0'

    def __init__(self, model = "gpt-4o-mini"):
        self.client = openai.OpenAI()
        self.model = model
        self.assistant = None
        self.Thread = None
        self.run = None
        self.summary = None

        self.FunctionsManager = Functions()

        if Nova.Assistant_id:
            self.assistant = self.client.beta.assistants.retrieve(
                assistant_id=Nova.Assistant_id
            )
        if Nova.thread_id:
            self.Thread = self.client.beta.threads.retrieve(
                thread_id=Nova.thread_id
            )
    def create_assistant(self,name,instructions,tools):
        if not self.assistant:
            assistant_obj = self.client.beta.assistants.create(
                name=name,
                instructions=instructions,
                tools=tools,
                model=self.model
            )
            Nova.Assistant_id = assistant_obj.id
            self.assistant = assistant_obj
            print(f"Assistant ID: {self.Assistant_id}")
    
    def create_thread(self):
        if not self.Thread:
            thread_obj = self.client.beta.threads.create()
            Nova.thread_id = thread_obj.id
            self.Thread = thread_obj
            print(f"Thread ID: {self.Thread.id}")

    def add_message_to_thread(self,role,content):
        if self.Thread:
            self.client.beta.threads.messages.create(
                thread_id=self.Thread.id,
                role=role,
                content=content
            )

    def run_assistant(self):
        if self.Thread and self.assistant:
            self.run = self.client.beta.threads.runs.create(
                thread_id=self.Thread.id,
                assistant_id=self.Assistant_id
            )
    def process_message(self):
        if self.Thread:
            messages = self.client.beta.threads.messages.list(
                thread_id=self.Thread.id
            )
            summary = []
            last_message = messages.data[0]
            role = last_message.role
            response = last_message.content[0].text.value
            summary.append(response)
            self.summary = "\n".join(summary)
            print(f"{role.capitalize()}:{response}")
            return response
    def call_required_functions(self,required_actions):
        if not self.run:
            return
        tools_output = [] #pulling required functions
        for action in required_actions["tool_calls"]:
            func_name = action["function"]["name"]
            arguments = json.loads(action["function"]["arguments"])

            if func_name == "send_email":
                output = self.FunctionsManager.send_email(arguments)
                print(output)
                tools_output.append({"tool_call_id":action["id"],"output":output})
            elif func_name == "create_contact":
                output = self.FunctionsManager.create_contact(arguments)
                print(output)
                tools_output.append({"tool_call_id":action["id"],"output":output})
            elif func_name == "get_contact_list":
                output = self.FunctionsManager.get_contact_list(arguments)
                print(output)
                tools_output.append({"tool_call_id":action["id"],"output":output})
            elif func_name == "get_track_spotify_uri":
                output = self.FunctionsManager.get_track_spotify_uri(arguments)
                print(output)
                tools_output.append({"tool_call_id":action["id"],"output":output})
            elif func_name  == "play_spotify_song":
                output = self.FunctionsManager.play_spotify_song(arguments)
                print(output)
                tools_output.append({"tool_call_id":action["id"],"output":output})
            elif func_name == "create_event_calendar":
                output = self.FunctionsManager.create_event_calendar(arguments)
                print(output)
                tools_output.append({"tool_call_id":action["id"],"output":output})
            elif func_name == "get_timezone":
                output = self.FunctionsManager.get_timezone(arguments)
                print(output)
                tools_output.append({"tool_call_id":action["id"],"output":output})
            elif func_name == "get_DateTime":
                output = self.FunctionsManager.get_DateTime(arguments)
                print(output)
                tools_output.append({"tool_call_id":action["id"],"output":output})
            elif func_name == "take_screenshot_image":
                output = self.FunctionsManager.take_screenshot(arguments)
                print(output)
                tools_output.append({"tool_call_id":action["id"],"output":output})
            elif func_name == "get_calendar_events":
                output = self.FunctionsManager.get_events(arguments)
                print(output)
                tools_output.append({"tool_call_id":action["id"],"output":output})
            elif func_name == "get_screenshot":
                output = self.FunctionsManager.get_screenshot(arguments)
                print(output)
                tools_output.append({"tool_call_id":action["id"],"output":output})
            else:
                raise ValueError(f"Unknown Function: {func_name}")
            print("Submiting outputs back to assistant")

            self.client.beta.threads.runs.submit_tool_outputs(
                thread_id=self.Thread.id,
                run_id=self.run.id,
                tool_outputs= tools_output
            )

    def wait_for_completed(self):
        if self.Thread and self.run:
            while True:
                time.sleep(1)
                run_status = self.client.beta.threads.runs.retrieve(
                    thread_id=self.Thread.id,
                    run_id=self.run.id
                )
                #print(f"RUN STATUS:{run_status.model_dump_json(indent=4)}")

                if run_status.status == "completed":
                    return self.process_message()
                elif run_status.status == "requires_action":
                    print("FUNCTION CALLING NOW...")
                    self.call_required_functions(
                        required_actions=run_status.required_action.submit_tool_outputs.model_dump()
                    )
    def run_steps(self):
        run_steps = self.client.beta.threads.runs.steps.list(
            thread_id=self.Thread.id,
            run_id=self.run.id
        )
        print(f"RUN STEPS:{run_steps}")



def TranscribeSpeech(FileName): #speech to text
    File = open(FileName, 'rb')
    Transcribtion = openai.audio.transcriptions.create(model = 'whisper-1', file=File)
    return Transcribtion.text
if __name__ == "__main__":
    Nova = Nova()
    Nova.add_message_to_thread(
        role="user",
        content="can you send an email to aymurad@ualberta.ca saying this is just a test"
    )
    Nova.run_assistant()
    Nova.wait_for_completed()

    

#thread_id = 'thread_kv32BoFXceyDi4ZRTZq5tN0D'
#Assistant_id = 'asst_iJEdZTYHW5RHES223KfY5ro0'
