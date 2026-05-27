import matplotlib.pyplot as plt
import scipy.signal as sig
import numpy as np
import pandas as pd
# from IPython.display import display
from datetime import datetime, date, timedelta, time
import matplotlib.dates as mdates
import statistics
from collections import Counter
plt.close('all')

start_date=date(2026,2,1) #
# last_date=date.today() #OR TYPE DESIRED DATE ON NEXT LINE AND UNCOMMENT IT
last_date=date(2026,3,5) #
datetag=str(last_date)
d=last_date-start_date
days_to_plot=d.days

loadpath="/home/maheshkarnani/Documents/Code/Mazerex2/mazerex2/cohort2/fem7_c_VRF_rex4/"
#concatenate
datetag=str(last_date)
d=last_date-start_date
days_to_plot=d.days
data_coll = pd.read_csv(loadpath + str(start_date) + "_autolindz.csv")

for j in range(days_to_plot):
    day=start_date+timedelta(days = j+1) 
    print(day)
    data = pd.read_csv(loadpath + str(day) + "_autolindz.csv") 
    frames=[data_coll,data]
    data_coll=pd.concat(frames)

df=data_coll.reset_index()
df['Start_Time']=pd.to_datetime(df['Start_Time'])
df['Animal']=df['Animal'].astype(int)
# df['Unit']=df['Unit'].astype(int)
# print(df)

#find assay starts
starts=df[df['Mode']=='start Lindzey']
ends=df[df['Mode']=='End Lindzey']
# print(ends.index)

#select assays with:
# 1) two diff animals entering within previous 60s at diff ports without visiting the other port
# 2) no other animals entering before assay ends

'''Mode,Start_Time,Animal,Unit'''
#an1=df.iloc[i-1]['Animal']
winners=list()
losers=list()
for i in starts.index:
    t=df.iloc[i]['Start_Time']
    t0=t-timedelta(seconds=60)
    animals_in_assay=df[(df['Start_Time']>t0) & (df['Start_Time']<t) & (df['Animal']>0)]['Animal'].reset_index()
    if len(animals_in_assay)>1: #1
        an1=list(animals_in_assay['Animal'])[0]
        other_animals=list(set(animals_in_assay['Animal'][(animals_in_assay['Animal']!=an1)]))
        if len(other_animals)==1: #only two entered for assay 
            an2=other_animals[0]
            pre_assay_data=df[(df['Start_Time']>t0) & (df['Start_Time']<t) & (df['Animal']>0)]
            an1_entries=list(set(pre_assay_data[(pre_assay_data['Animal']==an1)]['Unit']))
            an2_entries=list(set(pre_assay_data[(pre_assay_data['Animal']==an2)]['Unit']))
            if len(an1_entries)==1 and len(an2_entries)==1 and an1_entries!=an2_entries: #diff ports and not visiting others
                # print('assay start!')
                an1_entry=an1_entries[0]
                an2_entry=an2_entries[0]
                assay_end=ends.index[(ends.index>i)][0]
                assay_data=df.iloc[i:assay_end+1]
                # print(assay_data)
                animals_during_assay=list(set(assay_data[assay_data['Animal']>0]['Animal']))
                if len(animals_during_assay)==2 and (an1 in animals_during_assay) and (an2 in animals_during_assay): #2
                    # print(assay_data)
                    an1_exit=list(assay_data[(assay_data['Animal']==an1)]['Unit'])[-1]
                    # print(an1_exit)
                    an2_exit=list(assay_data[(assay_data['Animal']==an2)]['Unit'])[-1]
                    # print(an2_exit)
                    if an1_exit==an2_exit: #leave through same port
                        # print('assay completion!!')
                        # print(an1_entry, an2_entry, an1_exit, an2_exit)
                        if an1_exit==an1_entry:
                            winners.append(an2)
                            losers.append(an1)
                        if an2_exit==an2_entry:
                            winners.append(an1)
                            losers.append(an2)
print('wins')
print(Counter(winners))
print('losses')
print(Counter(losers))
# print(winners)
# print(losers)

# [x,winners.count(x)] 
i=list()
j=list()
Pij=list()
Pji=list()
interactions=list()
for x in set(winners+losers):
    print(x)
    for y in set(winners+losers):
        i.append(x)
        j.append(y)
        a=0
        n=0
        for f in range(len(winners)):
            if (winners[f]==x or winners[f]==y) and (losers[f]==x or losers[f]==y):
                n=n+1
                if winners[f]==x:
                    a=a+1
        if n==0:
            Pij.append(np.nan)
        else:
            Pij.append(a/n)
        Pji.append(1-Pij[-1])
        interactions.append(n)
league_table = pd.DataFrame({'i':i,
                             'j':j,
                             'Interactions':interactions,
                             'Pij':Pij,
                             'Pji':Pji}, 
                             columns=['i','j','Interactions','Pij','Pji'])
# print(league_table)

'''analyse league table to get David's Score'''
w=list()
w2=list()
l=list()
l2=list()
ints=list()
animals=list()
for x in set(i):
    animals.append(x)
    w.append(np.nansum(list(league_table[(league_table['i']==x)]['Pij'])))
    l.append(np.nansum(list(league_table[(league_table['i']==x)]['Pji'])))
    ints.append(np.nansum(list(league_table[(league_table['i']==x)]['Interactions'])))
#calc Wj
Wj=list()
Lj=list()
for x in range(len(j)):
    Wj.append(float(w[animals.index(j[x])]))
    Lj.append(float(l[animals.index(j[x])]))
df = pd.DataFrame({'Wj':Wj,
                   'Lj':Lj}, columns=['Wj','Lj'])
league_table = pd.concat([league_table, df], axis=1)
print(league_table)
#calc w2
for x in animals:
    array1=np.array(list(league_table[(league_table['i']==x)]['Pij']))
    array2=np.array(list(league_table[(league_table['i']==x)]['Wj']))
    # print(array1 * array2)
    w2.append(float(np.nansum(array1*array2)))
    array1=np.array(list(league_table[(league_table['i']==x)]['Pji']))
    array2=np.array(list(league_table[(league_table['i']==x)]['Lj']))
    # print(array1 * array2)
    l2.append(float(np.nansum(array1*array2)))
# print(w2)
# print(l2)

#calc DS
DaveScore=np.array(w)+np.array(w2)-np.array(l)-np.array(l2)
# print(DaveScore)

summary_table=pd.DataFrame({'Animal':animals,
                            'Rank': [0,0,0,0,0],
                            'Davids_Score':DaveScore,
                            'Interactions':ints,
                            'w':w}, 
                            columns=['Rank','Animal','Davids_Score','Interactions','w'])
summary_table=summary_table.sort_values('Davids_Score', ascending=False)
summary_table['Rank']=[1,2,3,4,5]
print(summary_table)