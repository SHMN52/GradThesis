from pyomo.environ import *
import pyomo.opt as pyo
def optimize(stg_dat,acws,apws):
    
    model = ConcreteModel()
    
    # Sets rf import
    M = 999999999

    def R_init(model):
       return [acws[i][0].value for i in range(2, acws.max_row+1)]
    model.R = Set(initialize=R_init)
    
    def F_init(model):
        return [stg_dat[i].flight_id for i in range(len(stg_dat))]
    model.F = Set(initialize=F_init)

    def Airport_init(model):
        return [apws[i][0].value for i in range(2, apws.max_row+1)]
    model.AP = Set(initialize=Airport_init)

    def Period_init(model):
        return [i for i in range(1,25)]
    model.P = Set(initialize=Period_init)

    model.RFPAP = Set(within= model.R * model.F * model.P * model.AP)
    
    # parameters

    def time_init(model, p):
        for i in model.P:
            if i == p:
                return i * 60
        
    model.S = Param(model.P, initialize = time_init)

    def origin_init(model, f):
        for j in range(len(stg_dat)):
            if stg_dat[j].flight_id == f :
                return stg_dat[j].origin
    model.origin = Param(model.F, initialize = origin_init)

    def dest_init(model, f):
        for j in range(len(stg_dat)):
            if stg_dat[j].flight_id == f :
                return stg_dat[j].dest
    model.dest = Param(model.F, initialize = dest_init)
    
    def c_init(model, r, f):
        for i in range(2, acws.max_row+1):
            if acws[i][0].value == r :
                for j in range(len(stg_dat)):
                    if stg_dat[j].flight_id == f :
                        return acws[i][5].value * (stg_dat[j].planned_arrival - stg_dat[j].planned_departure)/60
        return M        
    model.c = Param(model.R, model.F, initialize = c_init)
    
    model.cd = Param(model.F, initialize = (0.75*120))
    
    def t_init(model, f):
        for i in range(len(stg_dat)):
            if stg_dat[i].flight_id == f :
                return stg_dat[i].planned_departure + stg_dat[i].delay
    model.t = Param(model.F, initialize=t_init)

    
    model.cc = Param(model.F, initialize = 50000)
    
    def a_init(model, r, f):
        for i in range(2, acws.max_row+1):
            if acws[i][0].value == r :
                for j in range(len(stg_dat)):
                    if stg_dat[j].flight_id == f :
                        return acws[i][7].value + acws[i][6].value
        return M
    
    model.a = Param(model.R, model.F, initialize=a_init)
    
    def T_init(model, f):
        for j in range(len(stg_dat)):
            if stg_dat[j].flight_id == f :
                return (stg_dat[j].planned_arrival - stg_dat[j].planned_departure)
    model.T = Param(model.F, initialize=T_init)

    def b_init(model, r, f, ap):
        for i in range(2, acws.max_row+1):
            if acws[i][0].value == r :
                if acws[i][8].value == model.origin[f] and acws[i][4].value >= model.T[f] and model.origin[f] == ap:
                    return 1
        return 0
    model.b = Param(model.R, model.F, model.AP, initialize=b_init)
    
    
    def depCap_init(model,p, ap):
        for i in range(2, apws.max_row+1):
            if apws[i][0].value == ap :
                for j in range(1,int(apws.max_column/4 +1)):
                    if p*60 <= apws[i][4*j].value and apws[i][4*j-1].value <= (p - 1) * 60:
                        return apws[i][4*j-3].value
        return 0
    model.depCap = Param(model.P,model.AP, initialize=depCap_init)

    def arCap_init(model,p, ap):
        for i in range(2, apws.max_row+1):
            if apws[i][0].value == ap :
                for j in range(1,int(apws.max_column/4 +1)):
                    if p*60 <= apws[i][4*j].value and apws[i][4*j-1].value <= (p - 1) * 60:
                        return apws[i][4*j-2].value
        return 0
    model.arCap = Param(model.P,model.AP, initialize=arCap_init)

    
    
    # Variables
    model.x = Var(model.RFPAP, domain=Binary)
    model.L = Var(model.F, domain=Binary)
    model.m = Var(model.F, domain=NonNegativeIntegers)
    model.n = Var(model.F, domain=NonNegativeIntegers)
    model.delt1 = Var(model.F, model.P, domain=Binary)
    model.delt2 = Var(model.F, model.P, domain=Binary)
    
    
    def obj_expression(model):
        return (sum( model.c[r, f] * model.x[r,f,p,ap] for r in model.R for f in model.F for p in model.P for ap in model.AP) 
            +sum(model.cd[f] * (model.m[f]-model.t[f]) for f in model.F)
            +sum(model.cc[f] * model.L[f] for f in model.F))

    model.obj = Objective(rule=obj_expression,sense = minimize)


    def C1(model, r, f , ap):
        return sum(model.x[r,f,p,ap] for p in model.P) <= model.b[r,f,ap]

    def C2(model, r, p, ap):
        return sum(model.x[r, f, p, ap] for f in model.F) <= 1

    def C3(model, f):
        return sum(model.x[r, f, p, ap] for r in model.R for p in model.P for ap in model.AP) == 1 - model.L[f]

    def C4(model,r, f):
        return model.m[f] >= sum(model.x[r,f,p,ap] for p in model.P for ap in model.AP) * model.a[r,f]
    
    
    def C5(model, f):
        return model.n[f] == model.m[f] + model.T[f]

    def C6(model, f):
        return model.m[f] >= model.t[f]

    def C7(model, f, p):
        return model.m[f] <= model.S[p] + (1-model.delt1[f,p]) * M

    def C8(model, f, p):
        if p < 2 :
            return -M * (1-model.delt1[f,p]) <= model.m[f]
        return  -M * (1-model.delt1[f,p]) + model.S[p-1] <= model.m[f]
        
    def C9(model, p,ap):
        return  sum(model.delt1[f,p] for f in model.F) >= sum(model.x[r,f,p,ap] for f in model.F for r in model.R) 
        
    def C10(model, p, ap):
        return  sum(model.delt1[f,p] for f in model.F) <= model.depCap[p,ap]
    
    def C11(model, f, p):
        return model.n[f] <= model.S[p] + (1-model.delt2[f,p]) * M
        
    def C12(model, f, p):
        if p < 2 :
            return -M * (1-model.delt2[f,p]) <= model.n[f]
        return -M * (1-model.delt2[f,p]) +  model.S[p-1] <= model.n[f]
    
    def C13(model, p ,ap):
        return sum(model.delt2[f,p] for f in model.F) >= sum(model.x[r,f,p,ap] for f in model.F for r in model.R)
    
    def C14(model, p, ap):
        return sum(model.delt2[f,p] for f in model.F) <= model.arCap[p,ap]

    



    model.Co1  = Constraint(model.R,model.F,model.AP, rule=C1)
    model.Co2  = Constraint(model.R,model.P,model.AP, rule=C2)
    model.Co3  = Constraint(model.F, rule=C3)
    model.Co4  = Constraint(model.R,model.F, rule=C4)
    model.Co5  = Constraint(model.F, rule=C5)
    model.Co6  = Constraint(model.F, rule=C6)
    model.Co7  = Constraint(model.F,model.P, rule=C7)
    model.Co8  = Constraint(model.F,model.P, rule=C8)
    model.Co9  = Constraint(model.P,model.AP, rule=C9)
    model.Co10 = Constraint(model.P,model.AP, rule=C10)
    model.Co11 = Constraint(model.F,model.P, rule=C11)
    model.Co12 = Constraint(model.F,model.P, rule=C12)
    model.Co13 = Constraint(model.P,model.AP, rule=C13)
    model.Co14 = Constraint(model.P,model.AP, rule=C14)
    

    
    # model.Co1.deactivate()
    # model.Co7.deactivate()
    # model.Co8.deactivate()
    # model.Co9.deactivate()
    # model.Co11.deactivate()
    # model.Co12.deactivate() 
    # model.Co13.deactivate() 
    # model.Co14.deactivate()
    

    
    pyo.SolverFactory('cplex').solve(model,tee=True)
    return model
    
