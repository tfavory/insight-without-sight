# -*- coding: utf-8 -*-

'''
Converts a graph into a sounds

Future developments:
    Say 'up' and 'down' on top of the beeps to give a better experience
    Use moving averages instead of raw data for clarity
'''

import json
import urllib
import pandas as pd
import matplotlib.pyplot as plt
import winsound


MIN_FREQUENCY = 500
MAX_FREQUENCY = 5000


# Get data
url = 'https://www.data.qld.gov.au/api/3/action/datastore_search?resource_id=2017-indicator-4-1-0-6-1'
table = urllib.request.urlopen(url)
table = json.loads(table.read())
headers = [field['id'] for field in table['result']['fields']]
dataframe = pd.DataFrame(table['result']['records'], columns=headers)
del dataframe['_id']
del dataframe['Name']
del dataframe['Measure']

# get the array of 
to_listen_to = dataframe.loc[[7]]
for (index_label, row_series) in to_listen_to.iterrows():
    array = row_series.values
new_array = []
for value in array:
    if value != ' ':
        new_array += [float(value)]

# Map data point into frequencies
def frequency(x, maxi, mini):
    return (MAX_FREQUENCY - MIN_FREQUENCY) * ((x - mini) /(maxi - mini) + MIN_FREQUENCY / (MAX_FREQUENCY - MIN_FREQUENCY))

# Create an array of frequencies
mini = min(new_array)
maxi = max(new_array)
frequency_array = [frequency(x, maxi, mini) for x in new_array]

# Deliver the sound version of the graph
duration = 0.5
for frequency in frequency_array:
    winsound.Beep(int(frequency), 150)

# for reference: plot the graph
fig, ax = plt.subplots(figsize=[8, 5])
ax.plot(range(len(new_array)), new_array, color='black')
plt.plot()

