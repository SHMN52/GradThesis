import openpyxl as x
wb = x.load_workbook("flights.xlsx")
ws = wb.active
acwb = x.load_workbook("aircraft.xlsx")
acws = acwb.active
from pyomo.environ import *
from Staging import staging
from Abdelghany import optimize

current_stage=1

while current_stage <20:
    st = staging()
    for row in range(2, ws.max_row):
        for i in range(len(st)):
            if (ws[row][0].value == st[i].flight_id):
                ws[row][4].value = current_stage
    op=optimize(st)
    for i in op.F:
        for row1 in range(2, ws.max_row):
            if ws[row1][0].value==i:
                for j in op.R:
                    if value(op.x[j,i])==1:
                        for row2 in range(2, acws.max_row):
                            if acws[row2][0].value==j:
                                acws[row2][7].value=value(op.n[i])
                                acws[row2][8].value=ws[row1][6].value
                                ws[row1][7].value=value(op.m[i])
                                ws[row1][8].value=value(op.n[i])

    loop_kpi=1
    for row in range(2, ws.max_row):
        loop_kpi*=ws[row][4].value
    if loop_kpi!=0:
        break

    
             
    current_stage+=1
    wb.save("flights.xlsx")
    acwb.save("aircraft.xlsx")


