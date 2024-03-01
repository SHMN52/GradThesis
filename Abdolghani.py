from nt import environ
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
model.m = Var(model.F, domain=NonNegativeReals)
model.n = Var(model.F, domain=NonNegativeReals)


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


model.Co1 = Constraint((model.F,model.R), rule=C1)
model.Co2 = Constraint(model.R, rule=C2)
model.Co3 = Constraint(model.F, rule=C3)