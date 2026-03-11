import matplotlib.pyplot as plt
import scipy.signal as sig
import numpy as np
import pandas as pd
from datetime import datetime, date, timedelta, time
import matplotlib.dates as mdates
import statistics
import json

#"fem7_c_VRF_rex4"
#"fem4_e_PFChm4di_rex1"
#"fem6_e_IChm4di_rex3"
#"fem5_c_rex2"

savepath="C:\\Users\\robbi\\Documents\\GitHub\mazerex2\\cohort2\\fem4_e_PFChm4di_rex1\\"
win=30 #size of rolling median window
bins=58
time_line = np.array(pd.read_csv(savepath+"TimeLine.csv", header=None)).astype(np.datetime64).reshape(-1,1)
start_date=time_line[0]

marker_times=time_line#add important dates here to add vertical lines on last plot
#last_date=np.datetime64(datetime.today()) #OR TYPE DESIRED DATE ON NEXT LINE AND UNCOMMENT IT

last_date=np.datetime64(date(2026,3,2))
datetag=str(pd.to_datetime(last_date).to_pydatetime().date())

known_tags=np.array(pd.read_csv(savepath + "AnimalTags.csv", header=None)).ravel().tolist()
b=len(known_tags)

filtermin=14 #lower limit in g
filtermax=24 #upper limit in g 
d=(last_date-start_date)/np.timedelta64(1,'D')
days_to_plot=round(float(d[0]))

#Class for getting rolling_medians
def Rolling_Medians(X, Y): #X defines the rig, Y defines the animal (I.e., Rolling_Medians("fem4_e_PFChm4di_rex1", "1")) is PFC cohort, first animal
    savepath="C:\\Users\\robbi\\Documents\\GitHub\mazerex2\\cohort2\\" + X + "\\"
    time_line = np.array(pd.read_csv(savepath+"TimeLine.csv", header=None)).astype(np.datetime64).reshape(-1,1)
    known_tags = np.array(pd.read_csv(savepath + "AnimalTags.csv", header=None)).ravel().tolist()
    
    known_tags = [known_tags[Y]]

    print(known_tags)

    filtermin=14 #lower limit in g
    filtermax=24 #upper limit in g 
    d=(last_date-start_date)/np.timedelta64(1,'D')
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
    df['Animal']=df['Animal']
    sorted_df = df.sort_values(by=['Start_Time'], ascending=True)
    del df
    
    sorted_df.reset_index(drop=True, inplace=True)
    df=sorted_df.drop([0,1])
    # create a rolling median filter, roll through each animal's data, and plot
    list_x=[]
    list_weights=[]
    list_weightmeds=[]
    an=-1 #plotting index
    for rfid in known_tags: #for loop across animals
        an=an+1
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
    x = animal_times[keep_i]
    y = animal_weights[keep_i]
    list_x.append(x)
    list_weightmeds.append(rolling_medians)
    list_weights.append(y)

    plt.ylabel("Weight (g)")
    plt.xlabel("Time")
    plt.xticks(rotation=30, ha='right')
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M:%S'))
    plt.grid(True)
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
    daily_avg=pd.DataFrame(daily_avg)
    return(daily_avg)


#Grabbing PFC data for one animal
PFCdaily_avg = Rolling_Medians("fem4_e_PFChm4di_rex1", 1)
print(PFCdaily_avg)

#These make it so you can splice arrays using single words as the dates (Doesn't work otherwise!)
#time0:
for date0 in time_line[0]: #Habituation starts
    if date0 != 2026:
        break
print(date0)

#time1:
for date1 in time_line[1]: #Baseline starts
    if date1 != 2026:
        break
print(date1)

#time2:
for date2 in time_line[2]: #Induction 1 starts
    if date2 != 2026:
        break
print(date2)

#time3:
for date3 in time_line[3]: #Induction 1 ends
    if date3 != 2026:
        break
print(date3)

#time4:
for date4 in time_line[4]: #Induction 2 starts
    if date4 != 2026:
        break
print(date4)

#time5:
for date5 in time_line[5]: #Induction 2 ends
    if date5 != 2026:
        break
print(date5)

#time6:
for date6 in time_line[6]: #Recovery 2 ends
    if date6 != 2026:
        break
print(date6)

#Getting baseline weight
BL = PFCdaily_avg.loc[PFCdaily_avg['Date'] >= date1]
BL = BL.loc[BL['Date'] <= date2]
baselineweight = BL['Weight'].mean()

#Setting x-axis
x = PFCdaily_avg.loc[PFCdaily_avg['Date'] <= date6]
x = x.loc[x['Date'] >= date1]

#Showing baseline and beyond up to the end of recovery 2
normalised = ((x['Weight'] / baselineweight))*100
PFCx = x['Date']
PFCy = normalised

#Plotting
fig1, ax1 = plt.subplots(figsize=(16, 10))

ax1.plot(PFCx, PFCy, marker='s', linestyle = '-', alpha=0.8, color='black', linewidth=2, label = "PFC, animal 1")

ax1.axvline(date1, color='black', linestyle='dashed', label = "Baseline")
ax1.axvline(date2, color='blue', linestyle='dashed', label = "Induction 1")
ax1.axvline(date3, color='blue', linestyle='dashed')
ax1.axvline(date4, color='red', linestyle='dashed', label = "Induction 2")
ax1.axvline(date5, color='red', linestyle='dashed')
ax1.axvline(date6, color='gray', linestyle='dashed', label = "Recovery 2 ends")
ax1.legend()

ax1.set_title("% Body Weight")
ax1.set_ylabel("% Body Weight")
ax1.set_xlabel("Time")
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M:%S'))
ax1.set_xticks(ax1.get_xticks(), ax1.get_xticklabels(), rotation=45, ha='right')
ax1.grid(True)
plt.show()