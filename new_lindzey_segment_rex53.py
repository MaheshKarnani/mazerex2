    '''add these to init routine:
    
    timeout_flag=True
    timeout_start=datetime.now()
    timeout_dur=timedelta(seconds=30)
    doorA_open=DigitalInputDevice(14)
    doorB_open=DigitalInputDevice(15)
    tube_active=True
    object_start=datetime.now()
    close_time=datetime.now()
    '''
  
    #Lindzey tube:
    if timeout_flag:
        if detect3.value == 0 or detect4.value == 0:
            print('unusual RFID detected during Lindzey timeout')
            tag3=int(scan_tag3(mux[0]["instance"],7))
            print(tag3)
            tag4=int(scan_tag4(mux[0]["instance"],6))
            print(tag4)
        if object_start+interval<datetime.now() and beam1_detect.value==0:
            print('unusual object detected during Lindzey timeout')
            object_start=datetime.now()
        if timeout_start+timeout_dur<datetime.now():
            timeout_flag=False
            tube_active=False
            ser.write(str.encode('a'))
            print('TUBE OPEN')
            status_list.update({'Start_Time': [datetime.now()]})
            status_list.update({'Mode': ["OPEN"]})
            save.append_lindzey(status_list)
            detect_list_A=list()
            detect_list_B=list()
                
    if not timeout_flag:
        if detect3.value == 0:
            tag3=int(scan_tag3(mux[0]["instance"],7))
            print(tag3)
            # lindz_action_time=datetime.now()
            if tag3 in known_tags:
                ser.write(str.encode('b'))
                close_time=datetime.now()
#                 print("entry A")
                print(known_tags.index(tag3))
                event_list3.update({'Start_Time': [datetime.now()]})
                event_list3.update({'Animal': [tag3]})
                event_list3.update({'Mode': [state3]})
                event_list4.update({'Mode': [state4]})
                save.append_lindzey(event_list3)#for this animal
                state3=state3+1
                if doorA_open.value == 1 and detect_list_A and (tag3 not in detect_list_A):
                    ser.write(str.encode('c'))
                    close_time=datetime.now()
                    print("followerA")
                    status_list.update({'Start_Time': [datetime.now()]})
                    status_list.update({'Mode': ["followerA"]})
                    save.append_lindzey(status_list)
                detect_list_A.append(tag3)
                start_time=datetime.now()
        if detect4.value == 0:
            tag4=int(scan_tag4(mux[0]["instance"],6))
            lindz_action_time=datetime.now()
            if tag4 in known_tags:
                ser.write(str.encode('c'))
                close_time=datetime.now()
#                 print("entry B")
                print(known_tags.index(tag4))
                event_list4.update({'Start_Time': [datetime.now()]})
                event_list4.update({'Animal': [tag4]})
                event_list3.update({'Mode': [state3]})
                event_list4.update({'Mode': [state4]})
                save.append_lindzey(event_list4)#for this animal
                state4=state4+1
                if doorB_open.value == 1 and detect_list_B and (tag4 not in detect_list_B):
                    ser.write(str.encode('b'))
                    close_time=datetime.now()
                    print("followerB")
                    status_list.update({'Start_Time': [datetime.now()]})
                    status_list.update({'Mode': ["followerB"]})
                    save.append_lindzey(status_list)
                detect_list_B.append(tag4)
                start_time=datetime.now()
        if (doorA_open.value == 0 or doorB_open.value == 0) and not tube_active and close_time+interval<datetime.now() and beam1_detect.value==1:#unobstructed, a mouse likely triggered and retreated.
            ser.write(str.encode('b'))
            print('a door has closed and tube empty -- timeout and reset')
            ser.write(str.encode('c'))
            state3=0
            state4=0
            tube_active=False
            timeout_start=datetime.now()
            timeout_flag=True #breaks to timeout state, so no more saved data, only printouts
        if not tube_active and (state3>0 or state4>0) and doorA_open.value == 0 and doorB_open.value == 0:
            print('tube closed')
            start_time=datetime.now()
            tube_active=True
            status_list.update({'Start_Time': [datetime.now()]})
            animalsA=set(detect_list_A)
#             print(animalsA)
            animalsB=set(detect_list_B)
            if len(animalsA)==1 and len(animalsB)==1:
                if animalsA==animalsB:
                    print('solo traversal')
                    status_list.update({'Mode': ["solo"]})
                else:#dominance test in progress
                    print('dominance test in progress')
                    status_list.update({'Mode': ["start Lindzey"]})
                    test_started=True
            else:#following in progress
                print('sequence in tube')
                status_list.update({'Mode': ["sequence"]})
            save.append_lindzey(status_list)
        if tube_active and start_time+interval<datetime.now():
            if beam1_detect.value==1:#unobstructed
                print('event finished and tube empty')
                state3=0
                state4=0
                tube_active=False
                timeout_start=datetime.now()
                timeout_flag=True #breaks to timeout state, so no more saved data, only printouts
                if test_started:
                    status_list.update({'Start_Time': [datetime.now()]})
                    status_list.update({'Mode': ["End Lindzey"]})
                    save.append_lindzey(status_list)
                    test_started=False
            else:     
                print('tube still active')
                start_time=datetime.now()
            
