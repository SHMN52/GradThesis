from tokenize import String
from pyomo.environ import *
import pyomo.opt as pyo
def optimize(stg_dat,acws,apws):
    
    model = ConcreteModel()
    
    # Sets rf import
    M = 999999999
    Eps = 0.0000001

    def R_init(model):
       return [acws[i][0].value for i in range(2, acws.max_row+1)]
    model.R = Set(initialize=R_init) # Resource set (aircraft)
    
    def F_init(model):
        return [stg_dat[i].flight_id for i in range(len(stg_dat))]
    model.F = Set(initialize=F_init) # Flight set

    def I_init(model):
        return [apws[i][0].value for i in range(2, apws.max_row+1)]
    model.I = Set(initialize=I_init) # Origin set

    
    # parameters


    def origin_init(model, f):
        for j in range(len(stg_dat)):
            if stg_dat[j].flight_id == f :
                return stg_dat[j].origin
    model.origin = Param(model.F, initialize = origin_init ) # Origin on flights

    def Destination_init(model, f):
        for j in range(len(stg_dat)):
            if stg_dat[j].flight_id == f :
                return stg_dat[j].dest
    model.dest = Param(model.F, initialize = Destination_init) # Destination on flights

    def airport_resource(model, i):
        for row in range(2, acws.max_row+1):
            k=0
            if acws[row][8].value == i:
                k+=1
        return int(k)
    model.ar = Param(model.I, initialize = airport_resource, within = NonNegativeIntegers)

    def T_init(model, f):
        for j in range(len(stg_dat)):
            if stg_dat[j].flight_id == f :
                return int(stg_dat[j].planned_arrival - stg_dat[j].planned_departure)
    model.T = Param(model.F, initialize=T_init, within = PositiveIntegers) # Time of flights (minites)
    
    def c_init(model, r, f):
        for i in range(2, acws.max_row+1):
            if acws[i][0].value == r:
                if acws[i][4].value >= model.T[f]:
                    return int(acws[i][5].value * model.T[f]/60)
        return M        
    model.c = Param(model.R, model.F, initialize = c_init, within = NonNegativeIntegers) # Cost of assigning resourse r to flight f (hourly operation cost of aircraft * time of flight)
    
    model.cd = Param(model.F, initialize = (0.75*120), within = PositiveIntegers) # Estimated cost of flights delay per minute
    
    def t_init(model, f):
        for i in range(len(stg_dat)):
            if stg_dat[i].flight_id == f :
                return int(stg_dat[i].planned_departure + stg_dat[i].delay)
    model.t = Param(model.F, initialize=t_init, within = NonNegativeIntegers) # Scheduled departure time of flights (plus initial delay)

    
    model.cc = Param(model.F, initialize = 50000, within = PositiveIntegers) # Estimated cost of flight cancellation
    
    # def a_init(model, r):
    #     for i in range(2, acws.max_row+1):
    #         if acws[i][0].value == r:
    #             return acws[i][7].value + acws[i][6].value
    # model.a = Param(model.R, initialize=a_init) # Ready time of aircraft r (time of previus flight landing plus the turn-around time)
    
    

    def b_init(model, f, i, j):
        if model.origin[f]==i and model.dest[f]==j :
            return 1
        return 0
    model.b = Param(model.F,model.I,model.I, initialize=b_init, within = Binary) # determines whether aircraft r can service flight f in current stage (same location and enought range of fly)
    
    
    

    
    
    # Variables
    model.x = Var(model.R,model.F,model.I,model.I, domain=Binary) #Assignment variable
    model.L = Var(model.F, domain=Binary) # cancellation variable
    model.m = Var(model.F, domain=NonNegativeIntegers) # Departure time variable for flight f
    model.n = Var(model.F, domain=NonNegativeIntegers) # Arrival variable for flight f
    
    
    
    def obj_expression(model):
        return ( sum( model.c[r, f] * model.x[r,f,i,j] for r in model.R for f in model.F for i in model.I for j in model.I) 
                +sum(model.cd[f] * (model.m[f]-model.t[f]) for f in model.F)
                +sum(model.cc[f] * model.L[f] for f in model.F))

    model.obj = Objective(rule=obj_expression,sense = minimize)


    def C1(model, f, i, j ):
        return sum(model.x[r,f,i,j] for r in model.R) <= model.b[f,i,j] 

    # C1 Checks assignability 

    # def C2(model, r):
    #     return sum(model.x[r,f,i,j] for f in model.F) <= 1

    # C2 states that in a single stage, an aircraft can only accompany 

    def C3(model, f):
        return sum(model.x[r,f,i,j] for r in model.R for i in model.I for j in model.I) == 1 - model.L[f]
    
    # C3: A flight must be either assigned to an aircraft or be cancceled

    # def C4(model,r, f):
    #     return model.m[f] >= model.x[r,f,i,j] * model.a[r]
    
    # C4: if flight f is assined to aircraft r, it can depart only after its ready time

    def C5(model, f):
        return model.n[f] == model.m[f] + model.T[f]

    # C5: a flights arrival is its departure plus the time of the flight

    def C6(model, f):
        return model.m[f] >= model.t[f]
    
    # C6: a flight can only depart after it initial schedualed takeoff

    def C7(model, r, f, fp):
        return sum(model.x[r,f,i,j] for i in model.I for j in model.I) + sum(model.x[r,fp,i,j] for i in model.I for j in model.I) <= 2 + Eps*(model.m[fp] - model.n[f])
        

    def C8(model, j):
        return sum(model.x[r,f,i,j] for r in model.R for f in model.F for i in model.I) + model.ar[j]  >= sum(model.x[r,f,j,h] for r in model.R for f in model.F for h in model.I)


    model.Co1  = Constraint(model.F,model.I,model.I, rule=C1)
    #model.Co2  = Constraint(model.R, rule=C2)
    model.Co3  = Constraint(model.F, rule=C3)
    #model.Co4  = Constraint(model.R,model.F, rule=C4)
    model.Co5  = Constraint(model.F, rule=C5)
    model.Co6  = Constraint(model.F, rule=C6)
    model.Co7  = Constraint(model.R,model.F,model.F, rule=C7)
    model.Co8  = Constraint(model.I, rule=C8)
    
    
   

    
    pyo.SolverFactory('cplex').solve(model,tee=True)
    return model
    
