    
    #Lindzey tube:
    if detect3.value == 0:
        tag3=int(scan_tag3(mux[0]["instance"],7))
        print(tag3)
        lindz_action_time=datetime.now()
        if tag3 in known_tags:
            ser.write(str.encode('b'))
            print("entry3")
            print(known_tags.index(tag3))
            event_list3.update({'Start_Time': [datetime.now()]})
            event_list3.update({'Animal': [tag3]})
            event_list3.update({'Mode': [state3]})
            event_list4.update({'Mode': [state4]})
            state3=state3+1
            save.append_lindzey(event_list3)#for this animal
            start_time=datetime.now()
    if detect4.value == 0:
        tag4=int(scan_tag4(mux[0]["instance"],6))
        lindz_action_time=datetime.now()
        if tag4 in known_tags:
            ser.write(str.encode('c'))
            print("entry4")
            print(known_tags.index(tag4))
            event_list4.update({'Start_Time': [datetime.now()]})
            event_list4.update({'Animal': [tag4]})
            event_list3.update({'Mode': [state3]})
            event_list4.update({'Mode': [state4]})
            state4=state4+1
            save.append_lindzey(event_list4)#for this animal
            start_time=datetime.now()
    if state3>0 and state4>0 and not test_started:
        if tag3==tag4:#animal passed through
            print('solo traversal')
            tag3=0
            tag4=1
            state3=0
            state4=0
            ser.write(str.encode('a'))
            status_list.update({'Start_Time': [datetime.now()]})
            status_list.update({'Mode': ["solo"]})
            save.append_lindzey(status_list)
            
        else:#dominance test in progress
            print('dominance test in progress')
            start_time=datetime.now()
            test_started=True
            status_list.update({'Start_Time': [datetime.now()]})
            status_list.update({'Mode': ["start Lindzey"]})
            save.append_lindzey(status_list)
    if test_started and start_time+interval<datetime.now():
        if beam1_detect.value==1:#unobstructed
            print('test has finished and tube empty')
            state3=0
            state4=0
            test_started=False
            ser.write(str.encode('a'))
            status_list.update({'Start_Time': [datetime.now()]})
            status_list.update({'Mode': ["End Lindzey"]})
            save.append_lindzey(status_list)
        else:     
            print('dominance test still in progress')
            start_time=datetime.now()
    if lindz_action_time+interval<datetime.now():# and (state3>0 or state4>0):
        if beam1_detect.value==1:#unobstructed
#             print('tube empty --- resetting')
            tag3=0
            tag4=1
            state3=0
            state4=0
            test_started=False
            ser.write(str.encode('a'))
#             status_list.update({'Start_Time': [datetime.now()]})
#             status_list.update({'Mode': ["reset"]})
#             save.append_lindzey(status_list)
            lindz_action_time=datetime.now()
