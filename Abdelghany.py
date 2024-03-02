from pyomo.environ import *
import pyomo.opt as pyo

model = AbstractModel()

# Sets
model.R = Set()
model.F = Set()

# Parameters
model.c = Param(model.R, model.F)
model.cd = Param(model.F)
model.t = Param(model.F)
model.cc = Param(model.F)
model.b = Param(model.R, model.F)
model.a = Param(model.R, model.F)
model.v = Param(model.R)
model.UBn = Param(model.F)
model.T = Param(model.F)

# Variables
model.x = Var((model.R,model.F), domain=Binary)
model.L = Var(model.F, domain=Binary)
model.m = Var(model.F, domain=NonNegativeIntegers)
model.n = Var(model.F, domain=NonNegativeIntegers)


def obj_expression(model):
    return (sum( model.c[r, f] * model.x[r,f] for r in model.R for f in model.F ) 
           +sum(model.cd[f] * (model.m[f]-model.t[f]) for f in model.F)
           +sum(model.cc[f] * model.L[f] for f in model.F))

model.obj = Objective(rule=obj_expression,sense = minimize)


def C1(model, f, r):
    return model.x[r,f] <= model.b[r,f]

def C2(model, r):
    return sum(model.x[r, f] for f in model.F) <= 1

def C3(model, f):
    return sum(model.x[r, f] for r in model.R) == 1 - model.L[f]

def C4(model,f, r):
    return model.m[f] >= model.x[r,f] * model.a[r,f]

def C5(model,f, r):
    return model.n[f] <= model.x[r,f] * model.v[r] + (1 - model.x[r,f]) * model.UBn[f]

def C6(model, f):
    return model.n[f] == model.m[f] + model.T[f]

def C7(model, f):
    return model.m[f] >= model.t[f]



model.Co1 = Constraint((model.F,model.R), rule=C1)
model.Co2 = Constraint(model.R, rule=C2)
model.Co3 = Constraint(model.F, rule=C3)
model.Co4 = Constraint((model.F,model.R), rule=C4)
model.Co5 = Constraint((model.F,model.R), rule=C5)
model.Co6 = Constraint(model.F, rule=C6)
model.Co7 = Constraint(model.F, rule=C7)


# data import needs to be tuned
data = DataPortal()
data.load(filename='abstract1.dat', param=model.a, index=(model.I,model.J))
data.load(filename='abstract1.dat', param=model.b, index=model.I)
data.load(filename='abstract1.dat', param=model.c, index=model.J)


instance = model.create_instance(data)
opt = pyo.SolverFactory('cplex')
opt.solve(instance,tee=True)

instance.display()