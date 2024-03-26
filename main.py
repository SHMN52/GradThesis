import openpyxl as x
from pyomo.environ import *
wb = x.load_workbook("flights.xlsx")
ws = wb.active
acwb = x.load_workbook("aircraft.xlsx")
acws = acwb.active
from Staging import staging
from Abdelghany import optimize


current_stage=1

while current_stage <= 48:
    
    
    print('current stage=',current_stage)
    st = staging(current_stage,ws)
    for i in range(len(st)):
            for row in range(2, ws.max_row+1):
                if (ws[row][0].value == st[i].flight_id):
                    ws[row][4].value = current_stage
    
    op=optimize(st,acws)
    for i in op.R:
        for j in op.F:
                if value(op.x[i,j])==1:
                    for row1 in range(2, ws.max_row+1):
                        if ws[row1][0].value==j:
                            for row2 in range(2, acws.max_row+1):
                                if acws[row2][0].value==i:
                                    acws[row2][7].value=value(op.n[j])
                                    acws[row2][8].value=ws[row1][6].value
                                    ws[row1][7].value=value(op.m[j])
                                    ws[row1][8].value=value(op.n[j])
    
    
    
    current_stage+=1
    
    wb.save("flights.xlsx")
    acwb.save("aircraft.xlsx")
    


