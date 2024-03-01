from pyomo.environ import *
import pyomo.opt as pyo

model = AbstractModel()

model.I = Set()
model.J = Set()

model.a = Param(model.I, model.J)
model.b = Param(model.I)
model.c = Param(model.J)

# the next line declares a variable indexed by the set J
model.x = Var(model.J, domain=NonNegativeReals)


def obj_expression(model):
    return summation(model.c, model.x)


model.OBJ = Objective(rule=obj_expression)


def ax_constraint_rule(model, i):
    # return the expression for the constraint for i
    return sum(model.a[i, j] * model.x[j] for j in model.J) >= model.b[i]


# the next line creates one constraint for each member of the set model.I
model.AxbConstraint = Constraint(model.I, rule=ax_constraint_rule)

# Initialize Model and load data
data = DataPortal()
data.load(filename='abstract1.dat', param=model.a, index=(model.I,model.J))
data.load(filename='abstract1.dat', param=model.b, index=model.I)
data.load(filename='abstract1.dat', param=model.c, index=model.J)


instance = model.create_instance(data)
opt = pyo.SolverFactory('cplex')
opt.solve(instance,tee=True)

instance.display()

