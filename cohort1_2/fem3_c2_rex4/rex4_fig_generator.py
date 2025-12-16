import matplotlib.pyplot as plt
import scipy.signal as sig
import numpy as np
import pandas as pd
from IPython.display import display
from datetime import datetime, date, timedelta, time
import matplotlib.dates as mdates
import statistics
import json
savepath="/home/rex4/Documents/Data/"

time_line = np.array(pd.read_csv(savepath+"TimeLine.csv", header=None)).astype(np.datetime64).reshape(-1,1)
# print(time_line)
start_date=time_line[0]
# print(start_date)
marker_times=time_line#add important dates here to add vertical lines on last plot
last_date=np.datetime64(datetime.today()) #OR TYPE DESIRED DATE ON NEXT LINE AND UNCOMMENT IT
# last_date=np.datetime64(date(2025,11,26))
datetag=str(pd.to_datetime(last_date).to_pydatetime().date())
# print(datetag)
known_tags=np.array(pd.read_csv(savepath + "AnimalTags.csv", header=None)).ravel().tolist()
# print(known_tags)

filtermin=12 #lower limit in g
filtermax=24 #upper limit in g 
d=(last_date-start_date)/np.timedelta64(1,'D')
# print(round(float(d[0])))
days_to_plot=round(float(d[0]))

data = pd.read_csv(savepath + datetag + "_events.csv")
tags=data['Animal']
unique_tags=list(set(tags))
fig1 = plt.figure(figsize=(16, 8))
# plot filtered weights
ax1 = fig1.add_subplot(221)
ax1.set_title(f"all {len(unique_tags)} unique tags ")
hits=[]
for i in range(len(unique_tags)):
    filtered_an = data.loc[data['Animal'] == unique_tags[i]] 
    filtered_min = filtered_an.loc[filtered_an['Weight'] > filtermin]
    filtered_minmax =  filtered_min.loc[filtered_min['Weight'] < filtermax]
#     display(filtered_minmax.head(20))
    x=mdates.datestr2num(filtered_minmax['Start_Time']) 
    ax1.plot(x , filtered_minmax['Weight'], linestyle='-', marker='o', color=[1/len(unique_tags)*i, 1-1/len(unique_tags)*i, 1-1/len(unique_tags)*i, .5])
    # ax1.set_xticks(x)
    hits.append(len(x))
# ax1.set_ylabel("weight, g")
ax1.set_xticklabels(x,rotation=30,ha='right')
fmt=mdates.DateFormatter('%m-%d %H:%M:%S')
ax1.xaxis.set_major_formatter(fmt)

# plot filtered weights of known animals and gather averages
averages=[]
ax2 = fig1.add_subplot(223)
ax2.set_title(f"all {len(known_tags)} known tags ")

# gather and plot daily averages of known animals
bw_matrix=[]
data_unit5_coll=pd.DataFrame(
    {
        "Mode": [],
        "Start_Time": [],
        "Animal": [],
        "Weight": [],
        "Unit": [],
        "Pellets": [],
    }
)
pel_matrix=[]
x=[]
for j in range(days_to_plot):
    day=pd.to_datetime(last_date).to_pydatetime().date()-timedelta(days = j) 
    data = pd.read_csv(savepath + str(day) + "_events.csv") #filter time to 12h bin
    # plot filtered weights of known animals and gather averages
    bin1_offset=time(18,0)
    bin1_centre=datetime.combine(day,bin1_offset)
    bin1_start_offset=time(12,0)
    bin1_start=datetime.combine(day,bin1_start_offset)
    x.append(bin1_centre)
    bin2_offset=time(6,0)
    bin2_centre=datetime.combine(day,bin2_offset)
    x.append(bin2_centre)
    bw_averages1=[]
    bw_averages2=[]
    pel_sums1=[]
    pel_sums2=[]
    for i in range(len(known_tags)):
        filtered_an = data.loc[data['Animal'] == known_tags[i]] 
        filtered_min = filtered_an.loc[filtered_an['Weight'] > filtermin]
        filtered_minmax =  filtered_min.loc[filtered_min['Weight'] < filtermax]
        filtered_time = filtered_minmax.loc[pd.to_datetime(filtered_minmax['Start_Time'], format='%Y-%m-%d %H:%M:%S.%f') > bin1_start]
        if filtered_time.empty:
            # print('empty bin')
            bw_averages1.append(np.nan)
        else:
            bw_averages1.append(statistics.median(filtered_time['Weight']))
        filtered_time = filtered_minmax.loc[pd.to_datetime(filtered_minmax['Start_Time'], format='%Y-%m-%d %H:%M:%S.%f') < bin1_start]
        if filtered_time.empty:
            # print('empty bin')
            bw_averages2.append(np.nan)
        else:
            bw_averages2.append(statistics.median(filtered_time['Weight']))
    bw_matrix.append(bw_averages1)
    bw_matrix.append(bw_averages2)
    #pellets next
    for i in range(len(known_tags)):
        filtered_an = data.loc[data['Animal'] == known_tags[i]] 
        filtered_time = filtered_an.loc[pd.to_datetime(filtered_an['Start_Time'], format='%Y-%m-%d %H:%M:%S.%f') > bin1_start]
        if filtered_time.empty:
            # print('empty bin')
            pel_sums1.append(np.nan)
        else:
            pel_sums1.append(sum(filtered_time['Pellets']))
        filtered_time = filtered_an.loc[pd.to_datetime(filtered_an['Start_Time'], format='%Y-%m-%d %H:%M:%S.%f') < bin1_start]
        if filtered_time.empty:
            # print('empty bin')
            pel_sums2.append(np.nan)
        else:
            pel_sums2.append(sum(filtered_time['Pellets']))
    pel_matrix.append(pel_sums1)
    pel_matrix.append(pel_sums2)
    #next manual measurements
    data_unit5=data.loc[data['Unit'] == 5] 
    if data_unit5.empty:
        donothing=1
#         print('no manual')
    else:
        frames=[data_unit5_coll,data_unit5.iloc[::-1]]
        data_unit5_coll=pd.concat(frames)
        # print(data_unit5_coll)
bw_matrix1=list(map(list, zip(*bw_matrix)))
pel_matrix1=list(map(list, zip(*pel_matrix)))
# print(matrix1)
ax4=fig1.add_subplot(224)
ax4.set_title(f"B {len(known_tags)}")
b=1/len(known_tags)

for i in range(len(known_tags)):
    ax4.plot(x , bw_matrix1[i], linestyle='-', marker='o', color=[b*i, 1-b*i, 1-b*i, .5], linewidth=5,label="automated")
for i in range(len(known_tags)):
    an_data=[]
    an_data=data_unit5_coll.loc[data_unit5_coll['Animal'] == known_tags[i]] 
    an_data.Start_Time=pd.to_datetime(an_data.Start_Time)
    ax4.plot(an_data.Start_Time, an_data['Weight'] , linestyle='-', marker='o', color=[b*i, 1-b*i, 1-b*i, .9],label="manual")
for marker_time in marker_times:
    ax4.axvline(marker_time, color='black', linestyle='dashed')
# ax4.set_ylabel("weight, g")
ax4.set_xticks(x)
ax4.set_xticklabels(x,rotation=30,ha='right')
fmt=mdates.DateFormatter('%m-%d')
ax4.xaxis.set_major_formatter(fmt)
# plt.legend(loc="upper right")
plt.grid()

ax3=fig1.add_subplot(222)
ax3.set_title(f"PEL")
# print(len(known_tags))
for i in range(len(known_tags)):
    # print(i)
    # print(pel_matrix1[i])
    ax3.plot(x , pel_matrix1[i], linestyle='-', marker='o', color=[b*i, 1-b*i, 1-b*i, .5])
for marker_time in marker_times:
    ax3.axvline(marker_time, color='black', linestyle='dashed')
# ax3.set_ylabel("pel")
ax3.set_xticks(x)
ax3.set_xticklabels(x,rotation=30,ha='right')
fmt=mdates.DateFormatter('%m-%d')
ax3.xaxis.set_major_formatter(fmt)
ax3.set_ylim([0, 180])
plt.grid()
plt.subplots_adjust(bottom=0.15)
# plt.show()
# plt.close()
plt.savefig(savepath + "rig4output.svg", bbox_inches='tight', pad_inches=0)
