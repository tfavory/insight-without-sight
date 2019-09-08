# -*- coding: utf-8 -*-

'''
Workflow:
    A - Wait for the user to pick a dataset
        a) If no dataset chosen, wait more
        b) If a dataset is chosen:
            1 - The user picks a command with voice
            2 - the algorithm returns an answer
                If the command was 'quit', go back to A)
                Otherwise, go back to 1 -
'''


import pandas as pd
from mutagen import mp3
import time
import json
import urllib
from gtts import gTTS  # Text to voice
import os
import speech_recognition as sr


BASE_URL = 'https://www.data.qld.gov.au/api/3/action/'
r = sr.Recognizer()


def search_dataset():
    '''
    Asks the user what to search
    Finds relevant dataset from Queensland OpenAPI
    Tells the user the datasets names
    Returns names and resource_ids
    
    /!\ Gives only the first 5 datasets. Otherwise, that would be a lot for someone to remember.
    '''
    
    # Ask the user what to search
    print('What do you want to search in one word?')
    tts = gTTS(text='What do you want to search in one word?', lang="en")
    tts.save("search.mp3")
    os.startfile("search.mp3")
    time.sleep(mp3.MP3('search.mp3').info.length)
    
    # Listen to the user's answer
    with sr.Microphone() as source:
        audio = r.listen(source)
    text = r.recognize_google(audio, language="en")
    print('You have searched {}'.format(text))
    
    # Request search results from the API
    url = BASE_URL + 'package_search?q={}'.format(text)
    fileobj = urllib.request.urlopen(url)
    datasets = json.loads(fileobj.read())
    
    
    if datasets['result']['count'] == 0:
        return '', []
    else:
        # Find the relevant datasets
        datasets = datasets['result']['results']
        
        # Get the names of 
        to_say = 'There are {} datasets.'.format(len(datasets))
        to_add = ['Dataset number {}. name: {}'.format(i + 1, datasets[i]['resources'][0]['name']) 
                                                                    for i in range(len(datasets))]
        to_add = '. '.join(to_add[:5])  # Take 5 datasets maximum, otherwise it's a lot to remember
        to_say += to_add
        
        # Say the datasets name
        tts = gTTS(text=to_say, lang="en")
        tts.save("datasets.mp3")
        os.startfile("datasets.mp3")
        time.sleep(mp3.MP3('datasets.mp3').info.length)
        
        # Get the names and resource_ids to return
        names = ['{}'.format(datasets[i]['resources'][0]['name']) for i in range(len(datasets))]
        ids = [datasets[i]['resources'][0]['id'] for i in range(len(datasets))]
        return names, ids
    
    
def get_dataset(i, ids):
    '''
    Finds the dataset the user asked for
    '''
    url = BASE_URL + 'datastore_search?resource_id={}'.format(ids[i - 1])
    print(url)
    fileobj = urllib.request.urlopen(url)
    return json.loads(fileobj.read())


def say_headers(headers):
    '''
    Tells the users the headers of the dataset
    '''
    to_say = ['row {}: {}'.format(i + 1, headers[i]) for i in range(len(headers))]
    to_say = ', '.join(to_say)
    print(to_say)
    tts = gTTS(text=to_say, lang="en")
    tts.save("header.mp3")
    os.startfile("header.mp3")
    time.sleep(mp3.MP3('header.mp3').info.length)
    
    
def say_table_name(name):
    '''
    Gives back the dataset's name
    Info: harder than it looks through the API.
          Insight Without Sight makes it easier even if you're not blind.
    '''
    tts = gTTS(text=name, lang="en")
    tts.save("row.mp3")
    os.startfile("row.mp3")
    time.sleep(mp3.MP3('row.mp3').info.length)


def say_stats_qualitative(table):
    '''
    Asks which column
    Performs a simple categorial statistic (ex: column takes female/male. Returns 60% female)
    Tells the user the result.
    
    Ex: Column takes only for values 'Female' or 'Male'.
        Counts the number of 'Female' and the number of 'Male'
        Return the proportion of 'Female' and the proportion of 'Male'
    '''
    # Ask the user which column to study
    tts = gTTS(text='Which column do you need stats on?', lang="en")
    tts.save("ask_col.mp3")
    os.startfile("ask_col.mp3")
    time.sleep(mp3.MP3('row.mp3').info.length)
    
    # Get the user's answer
    with sr.Microphone() as source:
        audio = r.listen(source)
    text = r.recognize_google(audio, language="en")
    print('You chose column number {}'.format(text))
    # Extract the column and get the category's statistics
    data = [table.iloc[i][int(text) - 1] for i in range(len(table))]
    unique = list(set(data))
    percentages = [data.count(i) / len(data) for i in unique]
    
    # Tell the user the category's statistics
    to_say = ['{}: {}'.format(unique[i], percentages[i]) for i in range(len(unique))]
    to_say = ', '.join(to_say)
    to_say = 'Proportions for columns {}: '.format(headers[int(text) - 1]) + to_say
    tts = gTTS(text=to_say, lang="en")
    tts.save("to_say.mp3")
    os.startfile("to_say.mp3")
    time.sleep(mp3.MP3('to_say.mp3').info.length)
    return to_say


def data_exloration_loop(name, table, headers):
    # Tell the user which commands are available
    tts = gTTS(text='choose a command: columns, qualitative, name, quit.', lang="en")
    tts.save("commands.mp3")
    os.startfile("commands.mp3")
    time.sleep(mp3.MP3('number.mp3').info.length)
    
    # Wait for the command (only the last word counts)
    r = sr.Recognizer()
    with sr.Microphone() as source:
        audio = r.listen(source)
    
    try:
        text = r.recognize_google(audio, language="en")
        print("You said: " + text)
        res = True
        
        if text[-7:] == 'columns':
            say_headers(headers)
        if text[-11:] == 'qualitative':
            say_stats_qualitative(table)
        if text[-4:] == 'name':
            say_table_name(name)
        if text[-4:] == 'quit':
            res = False
        return res
    
    except sr.UnknownValueError:
        error = "Gov Hack did not understand."
        tts = gTTS(text=error, lang="en")
        tts.save("error_unknown_value.mp3")
        os.startfile("error_unknown_value.mp3")
        print(error)
        return True
    
    except sr.RequestError as e:
        error = "Request error. Check internet connection."
        tts = gTTS(text=error, lang="en")
        tts.save("error_request.mp3")
        os.startfile("error_request.mp3")
        print(error + " ".format(e))
        return True
        

# Main loop
while True:
    # Dataset search
    names, ids = search_dataset()
    
    # Ask which dataset to explore
    print('Which dataset do you want to explore? For dataset number one, say one. For dataset number two say to and so on.')
    tts = gTTS(text='Which dataset do you want to explore? For dataset number one, say one. For dataset number two say to and so on.', lang="en")
    tts.save("number.mp3")
    os.startfile("number.mp3")
    time.sleep(mp3.MP3('number.mp3').info.length)
    
    # Get the user's answer
    with sr.Microphone() as source:
        audio = r.listen(source)
    text = r.recognize_google(audio, language="en")
    print(text)
    
    # Get the table, headers, and name
    table = get_dataset(int(text), ids)
    print(table['result']['records'])
    headers_fields = table['result']['fields']
    headers = [field['id'] for field in headers_fields]
    dataframe = pd.DataFrame(table['result']['records'], columns=headers)
    name = names[int(text) - 1]
    
    # get in a subloop if the user found a dataset to explore
    b = False
    if name != '':
        b = True
    while b == True:
        # Continue with data exploration as long as the user doesn't quit.
        b = data_exloration_loop(name, dataframe, headers)
    time.sleep(3)