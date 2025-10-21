#import libraries - you may need to install these first
import matplotlib.pyplot as plt
import scipy.signal as sig
import numpy as np
import pandas as pd
from IPython.display import display
from datetime import datetime, date, timedelta, time
import matplotlib.dates as mdates
import statistics

#set parameters and directories
win=30 #size of rolling median window
loadpath="/home/maheshkarnani/Documents/Code/Mazerex2/mazerex2/fem2_RIctrl/" #set this to your data folder!
start_date=date(2025,3,30) 
last_date=date(2025,5,5)
marker_times=[datetime(2025,4,3,12,0,0), datetime(2025,4,8,12,0,0), datetime(2025,4,12,12,0,0), datetime(2025,4,17,12,0,0)]#add important dates here to add vertical lines on last plot
datetag=str(last_date)
known_tags=[19644207130,19645782,19647186244,19644194143,19647181251]
filtermin=13 #lower limit in g -helps code ignore unrealistic values
filtermax=21 #upper limit in g -helps code ignore unrealistic values
d=last_date-start_date
days_to_plot=d.days
b=len(known_tags)

#concatenate data across days to a long pandas dataframe
datetag=str(last_date)
d=last_date-start_date
days_to_plot=d.days
data_coll_weight = pd.read_csv(loadpath + str(start_date) + "_events.csv")
for j in range(days_to_plot):
    day=start_date+timedelta(days = j+1) 
    data = pd.read_csv(loadpath + str(day) + "_events.csv") 
    frames=[data_coll_weight,data]
    data_coll_weight=pd.concat(frames)
df=data_coll_weight
df['Start_Time']=pd.to_datetime(df['Start_Time'])
df['Animal']=df['Animal'].astype(int)
print(df)

#start creating a figure
fig1 = plt.figure(figsize=(16, 8))
ax1 = fig1.add_subplot(221)
ax1.set_title(f"Rex1 fem3", fontsize =14)
# create a rolling median filter, roll through each animal's data, and plot
list_x=[]
list_weights=[]
list_weightmeds=[]
an=-1 #plotting index
for rfid in known_tags: #for loop across animals
    an=an+1
    print(rfid)
    animal_weights=df[df['Animal']==rfid]['Weight'].values
    animal_times=df[df['Animal']==rfid]['Start_Time'].values
    print(animal_times)
    init_prctile=np.percentile(animal_weights[0:win-1],80)
    keep_i=[]
    rolling_i=[]
    for i in range(win-1): #for loop to exclude outliers in first window
        weight=animal_weights[i]
        if weight<1.1*init_prctile and weight>0.9*init_prctile:
            keep_i.append(i)
            rolling_i.append(i)
    rolling_median=np.median(animal_weights[rolling_i])
    print(keep_i)
    rolling_medians=[]
    for i in range(len(keep_i)):
        rolling_medians.append(rolling_median) 
    for j in range(len(animal_weights[win:])): #for loop rolling through data
        weight=animal_weights[j+win]
        if weight<1.2*rolling_median and weight>0.8*rolling_median:
            keep_i.append(j+win)
            rolling_i.pop(0)
            rolling_i.append(j+win)
            rolling_median = np.median(animal_weights[rolling_i])
            rolling_medians.append(rolling_median) 
    print(keep_i)
    x = animal_times[keep_i]
    y = animal_weights[keep_i]
    ax1.plot(x, rolling_medians, label=str(rfid), marker='', linestyle = '-', color=[an/b, 1-an/b, 1-an/b, .5])    
    ax1.plot(x, y, label=str(rfid), marker='o', linestyle = '', color=[an/b, 1-an/b, 1-an/b, .1])    
    list_x.append(x)
    list_weightmeds.append(rolling_medians)
    list_weights.append(y)
    animal_weights5=df[(df['Animal']==rfid) & (df['Unit'] == 5)]['Weight'].values
    animal_times5=df[(df['Animal']==rfid) & (df['Unit'] == 5)]['Start_Time'].values
    ax1.plot(animal_times5, animal_weights5, label=str(rfid), marker='o', linestyle = '-', color=[an/b, 1-an/b, 1-an/b, .9])  
print(x)
print(list_x)
plt.ylabel("Weight (g)")
plt.xlabel("Time")
plt.xticks(rotation=30, ha='right')
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M:%S'))
plt.grid(True)


#start creating another figure
ax2 = fig1.add_subplot(222)
list_daily_w=[]
an=-1
for rfid in known_tags: #for loop across animals
    an=an+1
    data={
        "Date":list_x[an],
        "Weight":list_weights[an]
        }
    print(data)
    filtered_df=pd.DataFrame(data)
    print(filtered_df)
    daily_avg=filtered_df.groupby(pd.Grouper(key='Date', freq='12h', origin='2025-3-30')).median().reset_index()
    print(daily_avg)
    x=daily_avg['Date']
    y=daily_avg['Weight']
    print(x)
    print(y)
    ax2.plot(x,y, marker='o', linestyle = '-', color=[an/b, 1-an/b, 1-an/b, .5])
    list_daily_w.append(daily_avg['Weight'].values)
grand_avg=np.mean(list_daily_w, axis=0)
print(grand_avg)
print(x)
ax2.plot(x,grand_avg, marker='s', linestyle = '-', alpha=0.8, color='black', linewidth=2)
plt.ylabel("Weight (g)")
plt.xlabel("Time")
plt.xticks(rotation=30, ha='right')
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M:%S'))
plt.grid(True)
#add markers to all plots and plot!
for marker_time in marker_times:
    ax1.axvline(marker_time, color='black', linestyle='dashed')
    ax2.axvline(marker_time, color='black', linestyle='dashed')
plt.show()