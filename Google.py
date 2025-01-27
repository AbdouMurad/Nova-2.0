import os
import pickle #a file that stores authentication - once authenticated once user wont have to again
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from google.auth.transport.requests import Request
import base64
from email.mime.text import MIMEText
import datetime


#These scopes are full access to gmail, contacts and calendar
SCOPES = [
    'https://www.googleapis.com/auth/gmail.modify',        # Full Gmail access (read and write)
    'https://www.googleapis.com/auth/contacts',            # Full access to Contacts (read and write)
    'https://www.googleapis.com/auth/calendar',            # Full access to Calendar (read and write)
]

def authenticate_google_api():
    creds = None
    if os.path.exists("Credentials/google_pickle.token"):
        with open("Credentials/google_pickle.token","rb") as token: #if the file exists load it as creds
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token: #check if creds exists but is expired
            creds.refresh(Request())
        else:
            # Set up the OAuth 2.0 flow (opens a browser window for user authentication)
            flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                'Credentials/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)  # Launches the authentication flow

        #save creds
        with open("Credentials/google_pickle.token","wb") as token:
            pickle.dump(creds,token)
    serviceGmail = googleapiclient.discovery.build('gmail', 'v1', credentials=creds)
    serviceContacts = googleapiclient.discovery.build('people','v1',credentials=creds)
    serviceCalander = googleapiclient.discovery.build('calendar','v3',credentials=creds)
    return [serviceGmail,serviceContacts,serviceCalander]

def get_timezone(service): #Written by chatgpt
    #now = datetime.datetime.utcnow().isoformat() + 'Z'
        # Get timezone information from Calendar API
    calendar_list = service.calendarList().list().execute()
    primary_calendar = next(
        (cal for cal in calendar_list['items'] if cal.get('primary', False)), None
    )
    
    if primary_calendar:
        timezone = primary_calendar.get('timeZone', 'UTC')
        return timezone
    else:
        return "error occured - no time zone found"



def send_email_gmail(service, to_email, subject, text):
    #Create mime email address
    message = MIMEText(text)
    message['to'] = to_email
    message['subject'] = subject
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    #send the email
    try:
        send_message = (service.users().messages().send(userId="me", body={"raw": raw_message}).execute())
        return send_message["id"]
    except Exception as E:
        print(E)

def list_google_contacts(service):
    try:
        results = service.people().connections().list(
            resourceName='people/me',
            pageSize=1000,  # Number of contacts to fetch - 1000 is max
            personFields='names,emailAddresses'  # Specify fields you want
        ).execute()
        connections = results.get('connections',[])
        contacts = dict()
        for person in connections:
            names = person.get('names', [])
            emails = person.get('emailAddresses',[])

            contacts[names[0].get("displayName")] = emails[0].get("value")
        return str(contacts)
    except Exception as e:
        print(e)
        return "error occured"
    
def add_contact(service, name, email):
    try:
        contact = {
            "names":[{"givenName":name}],
            "emailAddresses":[{"value":email}]
        }
        service.people().createContact(body  = contact).execute()
        return "Contact Created"
    except:
        return "Contact not created - error occured"

def create_event(service,data):
    print(data)
    data2 = {}
    data2["summary"] = data["title"]
    data2["location"] = data["location"]
    data2["start"] = {}
    data2["start"]["dateTime"] = data["start_date_time"]
    data2["start"]["timeZone"] = data["time_zone"]
    data2["end"] = {}
    data2["end"]["dateTime"] = data["end_date_time"]
    data2["end"]["timeZone"] = data["time_zone"]
    data2["reminders"] = {}
    data2["reminders"]["useDefault"] = True
    
    event = service.events().insert(calendarId="primary", body=data2).execute()
    print(event)
    return "Event Schedueled"
    #print(event.get('htmlLink'))

def get_events(service,data):
    event_result = (
        service.events().list(
            calendarId="primary",
            timeMin = data['datetime'],
            maxResults = 10,
            singleEvents = True,
            orderBy = "startTime"
        ).execute())
    if event_result:
        return event_result
    else:
        return "no events found"
        
    
