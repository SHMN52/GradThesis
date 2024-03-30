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
    

    def b_init(model, r, f):
        for i in range(2, acws.max_row+1):
            if acws[i][0].value == r :
                for j in range(len(stg_dat)):
                    if stg_dat[j].flight_id == f:
                        if acws[i][8].value == stg_dat[j].origin and acws[i][4].value >= stg_dat[j].planned_arrival - stg_dat[j].planned_departure :
                            return 1
        return 0
    model.b = Param(model.R, model.F, initialize=b_init)
    
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
    model.x = Var(model.R,model.F, domain=Binary)
    model.L = Var(model.F, domain=Binary)
    model.m = Var(model.F, domain=NonNegativeIntegers)
    model.n = Var(model.F, domain=NonNegativeIntegers)
    model.delt11 = Var(model.P,model.AP, domain=Binary)
    model.delt12 = Var(model.P,model.AP, domain=Binary)
    model.delt21 = Var(model.P,model.AP, domain=Binary)
    model.delt22 = Var(model.P,model.AP, domain=Binary)


    def obj_expression(model):
        return (sum( model.c[r, f] * model.x[r,f] for r in model.R for f in model.F ) 
            +sum(model.cd[f] * (model.m[f]-model.t[f]) for f in model.F)
            +sum(model.cc[f] * model.L[f] for f in model.F))

    model.obj = Objective(rule=obj_expression,sense = minimize)


    def C1(model, r, f):
        return model.x[r,f] <= model.b[r,f]

    def C2(model, r):
        return sum(model.x[r, f] for f in model.F) <= 1

    def C3(model, f):
        return sum(model.x[r, f] for r in model.R) == 1 - model.L[f]

    def C4(model,r, f):
        return model.m[f] >= model.x[r,f] * model.a[r,f]
    
    
    def C5(model, f):
        return model.n[f] == model.m[f] + model.T[f]

    def C6(model, f):
        return model.m[f] >= model.t[f]

    def C7(model, f, p, ap):
        for j in range(len(stg_dat)):
            if stg_dat[j].origin == ap and stg_dat[j].flight_id == f  :
                return model.delt11[p,ap] * 60*(p - 1) <= model.m[f]
        return model.delt11[p,ap] >= 0

    def C8(model, f, p, ap):
        for j in range(len(stg_dat)):
            if stg_dat[j].origin == ap and stg_dat[j].flight_id == f  :
                return model.delt11[p,ap] * 60 * p >= model.m[f]
        return model.delt11[p,ap] >= 0
        
    def C9(model, p, ap):
        fap=[]
        for fp in model.F:
            for j in range(len(stg_dat)):
                if stg_dat[j].origin == ap and stg_dat[j].flight_id == fp  :
                    fap.append(fp)
        return sum(model.x[r,f] for r in model.R for f in fap) <= model.depCap[p,ap] * model.delt12[p,ap]   
        
    def C10(model, f, p, ap):
        for j in range(len(stg_dat)):
            if stg_dat[j].dest == ap and stg_dat[j].flight_id == f  :
                return model.delt21[p,ap] * 60 *(p - 1) <= model.n[f]
        return model.delt21[p,ap] >= 0
    
    def C11(model, f, p, ap):
        for j in range(len(stg_dat)):
            if stg_dat[j].dest == ap and stg_dat[j].flight_id == f  :
                return model.delt21[p,ap] * 60 * p >= model.n[f]
        return model.delt21[p,ap] >= 0
        
    def C12(model, p, ap):
        fap=[]
        for fp in model.F:
            for j in range(len(stg_dat)):
                if stg_dat[j].dest == ap and stg_dat[j].flight_id == fp  :
                    fap.append(fp)
        return sum(model.x[r,f] for r in model.R for f in fap) <= model.arCap[p,ap] * model.delt22[p,ap]
    
    def C13(model, p, ap):
        return model.delt11[p,ap] <= model.delt12[p,ap]
    
    def C14(model, p, ap):
        return model.delt21[p,ap] <= model.delt21[p,ap]

    



    model.Co1 = Constraint(model.R,model.F, rule=C1)
    model.Co2 = Constraint(model.R, rule=C2)
    model.Co3 = Constraint(model.F, rule=C3)
    model.Co4 = Constraint(model.R,model.F, rule=C4)
    model.Co5 = Constraint(model.F, rule=C5)
    model.Co6 = Constraint(model.F, rule=C6)
    model.Co7 = Constraint(model.F,model.P,model.AP, rule=C7)
    model.Co8 = Constraint(model.F,model.P,model.AP, rule=C8)
    model.Co9 = Constraint(model.P,model.AP, rule=C9)
    model.Co10 = Constraint(model.F,model.P,model.AP, rule=C10)
    model.Co11 = Constraint(model.F,model.P,model.AP, rule=C11)
    model.Co12 = Constraint(model.P,model.AP, rule=C12)
    model.Co13 = Constraint(model.P,model.AP, rule=C13)
    model.Co14 = Constraint(model.P,model.AP, rule=C14)
    

    

    
    pyo.SolverFactory('cplex').solve(model,tee=True)
    return model
    
