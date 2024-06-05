
def staging(curr_stg,ws):
    
    


    class flight:
        def __init__(self,flight_id,planned_departure,planned_arrival,delay,origin,dest):
            self.flight_id=flight_id
            self.planned_departure=planned_departure
            self.planned_arrival=planned_arrival
            self.delay=delay
            self.origin=origin
            self.dest=dest
    f_list=[]
    for row in range(2, ws.max_row+1):
        if ws[row][4].value == 0:
            f=flight(ws[row][0].value,ws[row][1].value,ws[row][2].value,ws[row][3].value,ws[row][5].value,ws[row][6].value)
            f_list.append(f)
            


    # step 1 : sorting flights chronologicaly (based on departure times)
    f_sorted=sorted(f_list,key=lambda x: x.planned_departure)



    # step 2 : finding the critical flights (disrupted and not in previous stages)
    current_stage_flights=[]
    # for i in range(len(f_sorted)-1):
    #     if(f_sorted[i].delay > 0 and f_sorted[i].included_in_stage==0 ):
    #         current_stage_flights.append(f_sorted[i])
    #         break
    # if len(current_stage_flights) ==0:
    #     return print('sike')
    # step 3 : listing current stage flights (not in prevoius stages and depart before the arrival of critical flight)
    
    for i in range(len(f_sorted)):
        if(f_sorted[i].planned_departure <= curr_stg*60):
            current_stage_flights.append(f_sorted[i])
            
    
    
    return current_stage_flights
   

