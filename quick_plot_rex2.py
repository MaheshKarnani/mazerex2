import matplotlib.pyplot as plt
import scipy.signal as sig
import numpy as np
import pandas as pd
from IPython.display import display
from datetime import datetime, date, timedelta, time
import matplotlib.dates as mdates
import statistics
plt.close('all')

start_date=date(2025,1,29) 
marker_times=[datetime(2025,2,1,12,0,0),datetime(2025,2,4,12,0,0) ,datetime(2025,2,7,12,0,0)] #add important dates here to add vertical lines on last plot
last_date=date.today() #OR TYPE DESIRED DATE ON NEXT LINE AND UNCOMMENT IT
# last_date=date(2025,2,3)
datetag=str(last_date)
known_tags=[196447011,19645674,19645246186,19644148217,19647144222]
filtermin=13 #lower limit in g
filtermax=23 #upper limit in g 
d=last_date-start_date
days_to_plot=d.days
         
loadpath="/home/maheshkarnani/Documents/Code/Mazerex2/mazerex2/"
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
matrix=[]
x=[]
for j in range(days_to_plot):
    day=date.today()-timedelta(days = j) 
    data = pd.read_csv(loadpath + str(day) + "_events.csv") #filter time to 12h bin
    # plot filtered weights of known animals and gather averages
    bin1_offset=time(18,0)
    bin1_centre=datetime.combine(day,bin1_offset)
    bin1_start_offset=time(12,0)
    bin1_start=datetime.combine(day,bin1_start_offset)
    x.append(bin1_centre)
    bin2_offset=time(6,0)
    bin2_centre=datetime.combine(day,bin2_offset)
    x.append(bin2_centre)
    averages1=[]
    averages2=[]
    for i in range(len(known_tags)):
        filtered_an = data.loc[data['Animal'] == known_tags[i]] 
        filtered_min = filtered_an.loc[filtered_an['Weight'] > filtermin]
        filtered_minmax =  filtered_min.loc[filtered_min['Weight'] < filtermax]
        filtered_time = filtered_minmax.loc[pd.to_datetime(filtered_minmax['Start_Time'], format='%Y-%m-%d %H:%M:%S.%f') > bin1_start]
        averages1.append(statistics.mean(filtered_time['Weight']))
        filtered_time = filtered_minmax.loc[pd.to_datetime(filtered_minmax['Start_Time'], format='%Y-%m-%d %H:%M:%S.%f') < bin1_start]
        averages2.append(statistics.mean(filtered_time['Weight']))
    matrix.append(averages1)
    matrix.append(averages2)
print(x)
matrix1=list(map(list, zip(*matrix)))
# print(matrix1)
ax4=fig1.add_subplot(224)
ax4.set_title(f"daily mean of {len(known_tags)} known tags")
print(len(known_tags))
for i in range(len(known_tags)):
    print(i)
    print(matrix1[i])
    ax4.plot(x , matrix1[i], alpha=.5)
for i in range(len(marker_times)):
    ax4.plot([marker_times[i],marker_times[i]],[filtermin, filtermax])
ax4.set_ylabel("weight, g")
ax4.set_xticks(x)
ax4.set_xticklabels(x,rotation=30,ha='right')
fmt=mdates.DateFormatter('%m-%d')
ax4.xaxis.set_major_formatter(fmt)
plt.subplots_adjust(bottom=0.15)
plt.show()
