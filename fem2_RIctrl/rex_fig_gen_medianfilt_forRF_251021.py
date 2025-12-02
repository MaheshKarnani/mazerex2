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

#annotating the plot with induction 1 and 2;
ax2.annotate('Baseline', xy=(510, 390), xycoords='figure points', fontsize=7, color='orange')
ax2.annotate('Induction 1', xy=(558.5, 390), xycoords='figure points', fontsize=7, color='red')
ax2.annotate('Induction 2', xy=(632.5, 390), xycoords='figure points', fontsize=7, color='blue')
plt.show()

###This is all a bit messy - Couldn't figure out a way to tie the text to the marker times themselves in
###graphs, possibly a better way to do it.

#%Change from baseline to last day of induction 1;

##Making the dataframe readable (other approaches did not work, kept getting errors), so used approach
#from line 25 to make it readable for the commands, except now just taking data from 04/03 and 
#not all of the .csv files
baselinedata_coll_weight = pd.read_csv(loadpath + "2025-04-03_events.csv")
for j in range(days_to_plot):
    day=start_date+timedelta(days = j+1) 
    baselinedata = pd.read_csv(loadpath + "2025-04-03_events.csv") 
    baselineframes=[baselinedata_coll_weight,baselinedata]
    baselinedata_coll_weight=pd.concat(baselineframes)
baselinedf=baselinedata_coll_weight
baselinedf['Start_Time']=pd.to_datetime(baselinedf['Start_Time'])
baselinedf['Animal']=baselinedf['Animal'].astype(int)
print(baselinedf)

#Separating this df by animal (Otherwise returns "Too many indexers" error)
BaselineAnimal1 = baselinedf.loc[baselinedf['Animal'] == 19645782]
BaselineAnimal2 = baselinedf.loc[baselinedf['Animal'] == 19647186244]
BaselineAnimal3 = baselinedf.loc[baselinedf['Animal'] == 19644194143]
BaselineAnimal4 = baselinedf.loc[baselinedf['Animal'] == 19647181251]

#Computing a mean for each animal for baseline (04/07)
animal1baseline = statistics.mean(BaselineAnimal1['Weight'])
animal2baseline = statistics.mean(BaselineAnimal2['Weight'])
animal3baseline = statistics.mean(BaselineAnimal3['Weight'])
animal4baseline = statistics.mean(BaselineAnimal4['Weight'])

#Same approach as before for making the dataframe "readable", just with 04/07 instead of 04/03
induct1data_coll_weight = pd.read_csv(loadpath + "2025-04-07_events.csv")
for j in range(days_to_plot):
    day=start_date+timedelta(days = j+1) 
    induct1data = pd.read_csv(loadpath + "2025-04-07_events.csv") 
    induct1frames=[induct1data_coll_weight,induct1data]
    induct1data_coll_weight=pd.concat(induct1frames)
induct1df=induct1data_coll_weight
induct1df['Start_Time']=pd.to_datetime(induct1df['Start_Time'])
induct1df['Animal']=induct1df['Animal'].astype(int)

#Induction1 weights for each animal
Induct1Weight1 = induct1df.loc[induct1df['Animal'] == 19645782]
Induct1Weight2 = induct1df.loc[induct1df['Animal'] == 19647186244]
Induct1Weight3 = induct1df.loc[induct1df['Animal'] == 19644194143]
Induct1Weight4 = induct1df.loc[induct1df['Animal'] == 19647181251]

#Computing mean for each animal
Induct1animal1 = statistics.mean(Induct1Weight1['Weight'])
Induct1animal2 = statistics.mean(Induct1Weight2['Weight'])
Induct1animal3 = statistics.mean(Induct1Weight3['Weight'])
Induct1animal4 = statistics.mean(Induct1Weight4['Weight'])

#Computing percentage change for each animal (% change = change/original x 100)
percentchange1 = ((animal1baseline - Induct1animal1)/animal1baseline*100)
print(percentchange1)
percentchange2 = ((animal2baseline - Induct1animal2)/(animal2baseline)*100)
print(percentchange2)
percentchange3 = ((animal3baseline - Induct1animal3)/(animal3baseline)*100)
print(percentchange3)
percentchange4 = ((animal4baseline - Induct1animal4)/(animal4baseline)*100)
print(percentchange4)

#Making boxplot for panel A (I.e., completing the original coding task assigned)
Animals = ['1', '2', '3', '4']
Percent = [percentchange1, percentchange2, percentchange3, percentchange4]
plt.bar(Animals, Percent)
plt.xlabel('Animal')
plt.ylabel('Percentage Change (%)')
plt.title('VRF - Baseline Weight vs. Induction1')
plt.show()

#This should compute the average weight across *all* animals for the end of induction 1
grandaverageinduct1 = statistics.mean(induct1df['Weight'])

grandpercentchange1 = ((animal1baseline - grandaverageinduct1)/animal1baseline*100)
print(grandpercentchange1)
grandpercentchange2 = ((animal2baseline - grandaverageinduct1)/(animal2baseline)*100)
print(grandpercentchange2)
grandpercentchange3 = ((animal3baseline - grandaverageinduct1)/(animal3baseline)*100)
print(grandpercentchange3)
grandpercentchange4 = ((animal4baseline - grandaverageinduct1)/(animal4baseline)*100)
print(grandpercentchange4)

Animals = ['1', '2', '3', '4']
Percent = [grandpercentchange1, grandpercentchange2, grandpercentchange3, grandpercentchange4]
plt.bar(Animals, Percent)
plt.xlabel('Animal')
plt.ylabel('Percentage Change (%)')
plt.title('VRF - Baseline Weight vs. Grand Average Induction 1')
plt.show()

#To calculate z-score, calculating the average % change for the population (I.e., the 4 animals)
averagepercentchange = (statistics.mean([percentchange1, percentchange2, percentchange3, percentchange4]))

#Computing z-score as (population average - individual/standard deviation of the population)
zscore1 = ((averagepercentchange - percentchange1)/statistics.stdev([percentchange1, percentchange2, percentchange3, percentchange4]))
zscore2 = ((averagepercentchange - percentchange2)/statistics.stdev([percentchange1, percentchange2, percentchange3, percentchange4]))
zscore3 = ((averagepercentchange - percentchange3)/statistics.stdev([percentchange1, percentchange2, percentchange3, percentchange4]))
zscore4 = ((averagepercentchange - percentchange4)/statistics.stdev([percentchange1, percentchange2, percentchange3, percentchange4]))

#Plotting
Animals = ['1', '2', '3', '4']
Percent = [zscore2, zscore2, zscore3, zscore4]
plt.bar(Animals, Percent)
plt.xlabel('Animal')
plt.ylabel('Z-Score')
plt.title('VRF - Z-Score')
plt.show()
