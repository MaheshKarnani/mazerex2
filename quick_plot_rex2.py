import matplotlib.pyplot as plt
import scipy.signal as sig
import numpy as np
import pandas as pd
from IPython.display import display
from datetime import datetime, date, timedelta
import matplotlib.dates as mdates
import statistics
plt.close('all')

datetag=str(date.today()) #OR TYPE DESIRED DATE ON NEXT LINE AND UNCOMMENT IT
# datetag="2025-01-28"
known_tags=[196447011,19645674,19645246186,19644148217,19647144222]
filtermin=13 #lower limit in g
filtermax=23 #upper limit in g            
loadpath="/home/maheshkarnani/Documents/Data/rex2/"
data = pd.read_csv(loadpath + datetag + "_events.csv")
display(data.head(5))
tags=data['Animal']
unique_tags=list(set(tags))
print(unique_tags)
#diagnosing unique tags per unit
data_unit1=data.loc[data['Unit'] == 1] 
tags_unit1=list(set(data_unit1['Animal']))
print("UNIT1:")
print(tags_unit1)
data_unit2=data.loc[data['Unit'] == 2] 
tags_unit2=list(set(data_unit2['Animal']))
print("UNIT2:")
print(tags_unit2)
data_unit3=data.loc[data['Unit'] == 3] 
tags_unit3=list(set(data_unit3['Animal']))
print("UNIT3:")
print(tags_unit3)
data_unit4=data.loc[data['Unit'] == 4] 
tags_unit4=list(set(data_unit4['Animal']))
print("UNIT4:")
print(tags_unit4)

hits=[]
fig1 = plt.figure(figsize=(80, 50))
# plot filtered weights
ax1 = fig1.add_subplot(221)
ax1.set_title(f"all {len(unique_tags)} unique tags ")
for i in range(len(unique_tags)):
    filtered_an = data.loc[data['Animal'] == unique_tags[i]] 
    filtered_min = filtered_an.loc[filtered_an['Weight'] > filtermin]
    filtered_minmax =  filtered_min.loc[filtered_min['Weight'] < filtermax]
    display(filtered_minmax.head(20))
    x=mdates.datestr2num(filtered_minmax['Start_Time']) 
    ax1.plot(x , filtered_minmax['Weight'], alpha=.5)
    # ax1.set_xticks(x)
    hits.append(len(x))
ax1.set_ylabel("weight, g")
ax1.set_xticklabels(x,rotation=30,ha='right')
fmt=mdates.DateFormatter('%m-%d %H:%M:%S')
ax1.xaxis.set_major_formatter(fmt)
print("tag hits")
print(hits)
print('and tags')
print(unique_tags)

# plot filtered weights of known animals and gather averages
averages=[]
ax2 = fig1.add_subplot(223)
ax2.set_title(f"all {len(known_tags)} known tags ")
for i in range(len(known_tags)):
    filtered_an = data.loc[data['Animal'] == known_tags[i]] 
    filtered_min = filtered_an.loc[filtered_an['Weight'] > filtermin]
    filtered_minmax =  filtered_min.loc[filtered_min['Weight'] < filtermax]
    display(filtered_minmax.head(20))
    x=mdates.datestr2num(filtered_minmax['Start_Time']) 
    ax2.plot(x , filtered_minmax['Weight'], alpha=.5)
    # ax1.set_xticks(x)
    averages.append(statistics.mean(filtered_minmax['Weight']))
ax2.set_ylabel("weight, g")
ax2.set_xticklabels(x,rotation=30,ha='right')
fmt=mdates.DateFormatter('%m-%d %H:%M:%S')
ax2.xaxis.set_major_formatter(fmt)

# plot average filtered weights of known animals
ax3 = fig1.add_subplot(222)
ax3.set_title(f"mean of {len(known_tags)} known tags")
x=list(map(str, known_tags))
ax3.bar(x,averages)
ax3.set_ylabel("mean weight, g")
ax3.set_xticklabels(x)
ax3.set_xticklabels(x,rotation=30,ha='right')
ax3.set_ylim([12, 20])

# gather and plot daily averages of known animals
matrix=[averages]
x=[date.today()]
for j in range(4):
    day=date.today()-timedelta(days = j+1)
    x.append(day)
    loadpath="/home/maheshkarnani/Documents/Data/rex2/"
    data = pd.read_csv(loadpath + str(day) + "_events.csv")
    # plot filtered weights of known animals and gather averages
    averages=[]
    for i in range(len(known_tags)):
        filtered_an = data.loc[data['Animal'] == known_tags[i]] 
        filtered_min = filtered_an.loc[filtered_an['Weight'] > filtermin]
        filtered_minmax =  filtered_min.loc[filtered_min['Weight'] < filtermax]
        averages.append(statistics.mean(filtered_minmax['Weight']))
    matrix.append(averages)
print(x)
matrix1=list(map(list, zip(*matrix)))
print(matrix1)
ax4=fig1.add_subplot(224)
ax4.set_title(f"daily mean of {len(known_tags)} known tags")
print(len(known_tags))
for i in range(len(known_tags)):
    print(i)
    print(matrix1[i])
    ax4.plot(x , matrix1[i], alpha=.5)
ax4.set_ylabel("weight, g")
ax4.set_xticks(x)
ax4.set_xticklabels(x,rotation=30,ha='right')
fmt=mdates.DateFormatter('%m-%d')
ax4.xaxis.set_major_formatter(fmt)
plt.subplots_adjust(bottom=0.15)
plt.show()


# ax1.set_title("animals 1-2")
# ax1.plot(filtered_minmax['Start_Time'] , filtered_minmax['Weight'])
# # plot the DAC (clamp current)
# ax2 = fig3.add_subplot(223, sharex=ax1)  # <-- this argument is new
# ax2.set_title("DAC (stimulus waveform)")
# ax2.plot(abf.sweepX, abf.sweepC, color='r')
# # decorate the plots

# ax2.set_xlabel(abf.sweepLabelX)
# ax2.set_ylabel(abf.sweepLabelC)
