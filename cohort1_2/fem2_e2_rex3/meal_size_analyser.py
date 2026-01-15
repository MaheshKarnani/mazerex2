import matplotlib.pyplot as plt
import scipy.signal as sig
import numpy as np
import pandas as pd
from datetime import datetime, date, timedelta, time
import matplotlib.dates as mdates
import statistics
import json
savepath="/home/maheshkarnani/Documents/Code/Mazerex2/mazerex2/cohort1_2/fem2_e2_rex3/"
win=30 #size of rolling median window

time_line = np.array(pd.read_csv(savepath+"TimeLine.csv", header=None)).astype(np.datetime64).reshape(-1,1)
# print(time_line)
start_date=time_line[0]
print(start_date)
marker_times=time_line#add important dates here to add vertical lines on last plot
# last_date=np.datetime64(datetime.today()) #OR TYPE DESIRED DATE ON NEXT LINE AND UNCOMMENT IT
last_date=np.datetime64(date(2025,12,21))
datetag=str(pd.to_datetime(last_date).to_pydatetime().date())
# print(datetag)
known_tags=np.array(pd.read_csv(savepath + "AnimalTags.csv", header=None)).ravel().tolist()
b=len(known_tags)
# print(known_tags)

filtermin=14 #lower limit in g
filtermax=24 #upper limit in g 
d=(last_date-start_date)/np.timedelta64(1,'D')
# print(round(float(d[0])))
days_to_plot=round(float(d[0]))

#concatenate data across days to a long pandas dataframe
data_coll_weight = pd.read_csv(savepath + str(start_date)[2:12] + "_events.csv")
for j in range(days_to_plot):
    day=start_date+np.timedelta64(j+1,'D') 
    data = pd.read_csv(savepath + str(day)[2:12] + "_events.csv") 
    frames=[data_coll_weight,data]
    data_coll_weight=pd.concat(frames)
df=data_coll_weight
df['Start_Time']=pd.to_datetime(df['Start_Time'])
df['Animal']=df['Animal'].astype(int)
sorted_df = df.sort_values(by=['Start_Time'], ascending=True)
del df

#still unable to convert start_date to npdatetime64
# print(pd.to_datetime(start_date))
# print(np.datetime64(date(2025,12,1)))
# print(sorted_df[sorted_df['Start_Time']<np.datetime64(date(2025,12,1))]['Start_Time'])


sorted_df.reset_index(drop=True, inplace=True)
df=sorted_df.drop([0,1]) #workaround!
# df=np.delete(sorted_df, sorted_df[sorted_df['Start_Time']<np.datetime64(date(2025,12,1))])
print(df)

#start creating a figure
fig1 = plt.figure(figsize=(16, 8))
ax1 = fig1.add_subplot(221)
ax1.set_title(f"Rex1 fem1", fontsize =14)
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
    # print(data)
    filtered_df=pd.DataFrame(data)
    # print(filtered_df)
    daily_avg=filtered_df.groupby(pd.Grouper(key='Date', freq='12h', origin=str(start_date)[2:12])).median().reset_index()
    print(daily_avg)
    x=daily_avg['Date']
    y=daily_avg['Weight']
    print(x)
    print(y)
    ax2.plot(x,y, marker='o', linestyle = '-', color=[an/b, 1-an/b, 1-an/b, .5])
    print(daily_avg['Weight'].values)
    list_daily_w.append(daily_avg['Weight'].values[:19])
grand_avg=np.nanmean(list_daily_w, axis=0)
print(grand_avg)
print(x)
ax2.plot(x[:19],grand_avg, marker='s', linestyle = '-', alpha=0.8, color='black', linewidth=2)
plt.ylabel("Weight (g)")
plt.xlabel("Time")
plt.xticks(rotation=30, ha='right')
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M:%S'))
plt.grid(True)


#annotating the plot with induction 1 and 2;
# ax2.annotate('Baseline', xy=(510, 390), xycoords='figure points', fontsize=7, color='orange')
# ax2.annotate('Induction 1', xy=(558.5, 390), xycoords='figure points', fontsize=7, color='red')
# ax2.annotate('Induction 2', xy=(632.5, 390), xycoords='figure points', fontsize=7, color='blue')
# plt.show()

#plot histogram of meal lengths
ax3 = fig1.add_subplot(223)
ax4 = fig1.add_subplot(224)
an=-1
df1=df[df['Pellets'] != 0]
# print(df1)
list_daily_m=[]
for rfid in known_tags: #for loop across animals
    an=an+1
    print(rfid)
    p=df1[df1['Animal']==rfid]['Pellets'].values
    t=df1[df1['Animal']==rfid]['Start_Time'].values
    u=df1[df1['Animal']==rfid]['Unit'].values
    # print(t)
    intervals=np.diff(t)/1000000000
    # print(intervals)
    y, x = np.histogram(intervals, bins=np.arange(0,120,2))
    ax3.plot(x[:-1],y, linestyle = '-', color=[an/b, 1-an/b, 1-an/b, .5])

    meal_threshold=30 #define duration (s) of meal based on histograms 
    rows=len(p)-1
    for i in range(rows):
        row=rows-i
        interval=intervals[row-1]
        if u[row]==u[row-1]: #same unit
            if interval<meal_threshold:
                p[row-1]=p[row-1]+p[row]
                p=np.delete(p, row)
                t=np.delete(t, row)
                u=np.delete(u, row)
    
    # ax4.plot(t,p, marker='o', linestyle = '-', color=[an/b, 1-an/b, 1-an/b, .5])

    data={
        "Date":t,
        "Meal_size":p
        }
    # print(data)
    filtered_df=pd.DataFrame(data)
    # print(filtered_df)
    daily_avg=filtered_df.groupby(pd.Grouper(key='Date', freq='12h', origin=str(start_date)[2:12])).median().reset_index()
    print(daily_avg)
    x=daily_avg['Date']
    y=daily_avg['Meal_size']
    print(x)
    print(y)
    ax4.plot(x,y, marker='o', linestyle = '-', color=[an/b, 1-an/b, 1-an/b, .5])
    print(daily_avg['Meal_size'].values)
    list_daily_m.append(daily_avg['Meal_size'].values[:19])
grand_avg=np.nanmean(list_daily_m, axis=0)
print(grand_avg)
print(x)
ax4.plot(x[:19],grand_avg, marker='s', linestyle = '-', alpha=0.8, color='black', linewidth=2)
plt.ylabel("Meal size (pellets)")
plt.xlabel("Time")
plt.xticks(rotation=30, ha='right')
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M:%S'))
plt.grid(True)
#add markers to all plots and plot!
for marker_time in marker_times:
    ax1.axvline(marker_time, color='black', linestyle='dashed')
    ax2.axvline(marker_time, color='black', linestyle='dashed')
    ax4.axvline(marker_time, color='black', linestyle='dashed')
# plt.show()
plt.savefig(savepath + "output.svg", bbox_inches='tight', pad_inches=0)