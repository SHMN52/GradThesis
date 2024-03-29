import openpyxl as x
from pyomo.environ import *
wb = x.load_workbook("flights.xlsx")
ws = wb.active
acwb = x.load_workbook("aircraft.xlsx")
acws = acwb.active
from Staging import staging
from Abdelghany import optimize


current_stage=17


while current_stage <= 48:
    
    
    print('current stage=',current_stage)
    st = staging(current_stage,ws)
    for i in range(len(st)):
            for row in range(2, ws.max_row+1):
                if (int(ws[row][0].value) == int(st[i].flight_id)):
                    ws[row][4].value = current_stage
    
    op=optimize(st,acws)

    
    for j in op.F:
        k = 0
        for i in op.R:
            tmp = int(value(op.x[i,j]) + 0.5)
            k += tmp
            if tmp:
                for row1 in range(2, ws.max_row+1):
                    if  ws[row1][0].value == j:
                        ws[row1][7].value = value(op.m[j])
                        ws[row1][8].value = value(op.n[j])
                        for row2 in range(2, acws.max_row+1):
                            if  acws[row2][0].value == i:
                                acws[row2][7].value = value(op.n[j])
                                acws[row2][8].value = ws[row1][6].value
            
                                
                                
        for row in range(2, ws.max_row+1):
            if  int(ws[row][0].value) == j:
                ws[row][9].value = k
                L = int(value(op.L[j]))
                ws[row][10].value = L
                if k + L != 1:
                    print(f'Error, Flight {j} has the problem!')
                    input('Continue?')                    
                                     
    
    current_stage+=1
    
    wb.save("flights.xlsx")
    acwb.save("aircraft.xlsx")
    



