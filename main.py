from __future__ import print_function
import datetime
import os
import time
import pyttsx3
import speech_recognition as sr
import pytz
import subprocess 
from cal_setup import authenticate_google_calendar, convert_to_RFC_datetime


# If modifying these scopes, delete the file token.pickle.

MONTHS = ["january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december"]
DAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
DAY_EXTENSIONS = ["rd", "th", "st", "nd"]
NOTE_STRS2 = ['i have a ', 'i have an ', 'i got a ', 'i got an ']
split_word1 = ['at ']
split_word2 = ['on ']
am_or_pm = [' a.m.', ' p.m.']
calendar_id = "zhengc84@gmail.com"

def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def get_audio():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        audio = r.listen(source)
        said = ""

        try:
            said = r.recognize_google(audio)
            print(said)
        except Exception as e:
            print("Exception" + str(e))

    return said.lower()

def get_events(day, service):
    # Call the Calendar API
    date = datetime.datetime.combine(day, datetime.datetime.min.time())
    end_date = datetime.datetime.combine(day, datetime.datetime.max.time())
    utc = pytz.UTC
    date = date.astimezone(utc)
    end_date = end_date.astimezone(utc)

    events_result = service.events().list(calendarId='primary', timeMin=date.isoformat(), timeMax=end_date.isoformat(),
                                        singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        speak('No upcoming events found.')
    else:
        speak(f"you have {len(events)} on  this day")
        
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(start, event['summary'])
            start_time = str(start.split("T")[1].split("-")[0])
            if int(start_time.split(":")[0]) < 12:
                start_time = start_time + "am"
            else:
                start_time = str(int(start_time.split(":")[0])-12) +  start_time.split(":")[1]
                start_time = start_time + "pm"
            
            speak(event["summary"] + " at " + start_time)

def get_date(text):
    text = text.lower()
    today = datetime.date.today()

    if text.count("today") > 0:
        return today

    day = -1
    day_of_week = -1
    month = -1
    year = today.year

    for word in text.split():
        if word in MONTHS:
            month = MONTHS.index(word) + 1
        elif word in DAYS:
            day_of_week = DAYS.index(word)
        elif word.isdigit():
            day = int(word)
        else:
            for ext in DAY_EXTENSIONS:
                found = word.find(ext)
                if found > 0:
                    try:
                        day = int(word[:found])
                    except:
                        pass
    if month < today.month and month != -1:
        year = year + 1
    
    if day < today.day and month == -1 and day != -1:
        month = month + 1 

    if month == -1 and day == -1 and day_of_week != -1:
        current_day_of_week = today.weekday() 
        dif = day_of_week - current_day_of_week

        if dif < 0:
            dif += 7
            if text.count("next") >= 1:
                dif += 7
        
        return today + datetime.timedelta(dif)
    
    print(day)
    print(month)
    print(year)

    if month == -1 or day == -1:
        return None

    return datetime.date(month=month, day=day, year=year)


    text = text.lower()
    today = datetime.date.today()

    if text.count("today") > 0:
        return today

    day = -1
    day_of_week = -1
    month = -1
    year = today.year

    for word in text.split():
        if word in MONTHS:
            month = MONTHS.index(word) + 1
        elif word in DAYS:
            day_of_week = DAYS.index(word)
        elif word.isdigit():
            day = int(word)
        else:
            for ext in DAY_EXTENSIONS:
                found = word.find(ext)
                if found > 0:
                    try:
                        day = int(word[:found])
                    except:
                        pass
    if month < today.month and month != -1:
        year = year + 1
    
    if day < today.day and month == -1 and day != -1:
        month = month + 1 

    if month == -1 and day == -1 and day_of_week != -1:
        current_day_of_week = today.weekday() 
        dif = day_of_week - current_day_of_week

        if dif < 0:
            dif += 7
            if text.count("next") >= 1:
                dif += 7
        
        return today + datetime.timedelta(dif)
    
    print(day)
    print(month)
    print(year)

    if month == -1 or day == -1:
        return None

    return datetime.date(month=month, day=day, year=year)

def note(text, service):

    for word in split_word2:
        if word in text:
            frag1 = text.split(split_word2[0])
            date_and_time = frag1[1]
            event = frag1[0]

            for phrase in NOTE_STRS2:
                if phrase in event:
                    new_event = event.replace(phrase, '')
                else:
                    new_event = event

            # if the word "at" is in the sentence
            for phrase in split_word1:
                if phrase in date_and_time:                               
                    date_split = date_and_time.split(split_word1[0])      # splitting the word at the word "at" to distinguish between the day and the time
                    day_of_month = date_split[0]                          # storing the day of date
                    time = date_split[1]                                  # storing the time of date

                    # checking if there is an am or pm
                    for word in am_or_pm:                                 
                        if word in time:                                    
                            time_in_number = time.replace(word, '')
                            if word == ' a.m.': 
                                if ':' in time_in_number:
                                    temp_time = time_in_number.split(":")
                                    hours = int(temp_time[0])
                                    minutes = int(temp_time[1])
                                else:
                                    hours = time_in_number
                                    minutes = '00'
                            elif word == " p.m.":
                                if ':' in time_in_number:
                                    temp_time = time_in_number.split(":")
                                    hours = int(temp_time[0]) + 12
                                    minutes = int(temp_time[1])
                                else:
                                    hours = int(time_in_number) + 12
                                    minutes = '00'

                # if the time is not specified
                elif phrase not in date_and_time:
                        day_of_month = date_and_time                          
                        hours = '00'
                        minutes = '00'
                date = get_date(day_of_month)

        else:
            print("sorry, I didn't get that")

    event_request_body = {
        'start' : {
            'timeZone' : 'America/Toronto',
            'dateTime' : f'{date}T{hours}:{minutes}:00',
            
        },
        'end' : {
            'timeZone' : 'America/Toronto',
            'dateTime': f'{date}T{hours}:{minutes}:00',
        },
        'summary' : new_event,
        'status': 'confirmed',
        'transparency':'opaque', 
        'visibility':'private',
    }


    service.events().insert(
        calendarId=calendar_id, 
        body=event_request_body,
    ).execute()


WAKE = "hey tim"
SERVICE = authenticate_google_calendar()
print("speak")

while True:
    print("Listening...")
    text = get_audio()

    if text.count(WAKE) > 0:
        speak("what's up?")
        text = get_audio()

        CALENDAR_STRS = ["what do i have", "do i have", "am i busy"]
        for phrase in CALENDAR_STRS:
            if phrase in text.lower():
                date = get_date(text)
                if date:
                    get_events(date, SERVICE)
                else:
                    speak("I didn't get that")


        NOTE_STRS = ["make a note", "mark this down", "remember this", "set a reminder"]
        for phrase in NOTE_STRS:
            if phrase in text:
                speak("What would you like me to write down?")
                note_text = get_audio()
                note(note_text, SERVICE)
                speak("I've made a note about that.")