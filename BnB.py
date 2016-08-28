try:
    from coinor.blimpy import PriorityQueue as pQueue
except ImportError:
    print "Module not installed. Use easy_install coinor.grumpy in cmd or terminal."
import math
import time

#============================================
#build gurobi model

from gurobipy import *
model = Model("test")



x = []
for i in range(3):
    x.append(model.addVar(vtype=GRB.INTEGER, name="x%d" %(i+1)))

model.update() # add variables first so that constrants can be added.


model.addConstr(x[0] + 2 * x[1] + 3 * x[2] >= 8, name = 'const1')
model.addConstr(3 * x[0] + x[1] + x[2] >= 5, name = 'const2')


model.setObjective(-7 * x[0] - 3 * x[1] - 4 * x[2], GRB.MAXIMIZE)
model.update()



#=============================================

#initial setup
root_model = model.relax().copy()
root_model.optimize()

#modelsense = +1 if minimization; -1 if maximization
model_sense = root_model.modelsense
priority = model_sense * root_model.ObjVal

Q = pQueue()
Q.push(root_model, priority)

if model_sense < 0:
    LB = -float('inf')
    UB = root_model.ObjVal
    #best_obj = -float('inf')
else:
    LB = root_model.ObjVal
    UB = float('inf')
    #best_obj =

optSol = {}

#=============================================

def frac(x):
    return min(x - math.floor(x), math.ceil(x) - x)

def branchVar(grbm, branch_strategy = "MOST_FRACTIONAL"):
    """input: solved gurobi model; output: variable whose fractional part closest to 0.5"""
    if branch_strategy == "MOST_FRACTIONAL":
        cur_frac = 0
        for var in grbm.getVars():
            if frac(var.X) > cur_frac:
                cur_frac = frac(var.X)
                mfv = var
        return mfv
    else:
        print "Unknown branching strategy %s" %branch_strategy

def allInt(vs):
    for v in vs:
        if v.X - math.floor(v.X) > 1e-3:
            return False
    return True

def prune(m):
    if m.status == 2: # optimal
        if model_sense < 0:
            if m.ObjVal <= LB:
                print "==========pruned by bound==========="
            else:
                priority = model_sense * m.ObjVal
                Q.push(m, priority)
        else:
            if m.ObjVal >= UB:
                print "==========pruned by bound==========="
            else:
                priority = model_sense * m.ObjVal
                Q.push(m, priority)
    elif m.status == 3 or m.status == 4: # infeasible
        print "==========pruned by infeasibility==========="
    else:
        print "check optimization status! status code is %d" %m.status

#=============================================


nodes = 1

start_time = time.time()

while (not Q.isEmpty()) and time.time()-start_time <60:
    print Q.size
    parent_model = Q.pop()
    nodes += 1
    if allInt(parent_model.getVars()):
        if model_sense < 0:
            if parent_model.ObjVal > LB:
                LB = parent_model.ObjVal
                for v in parent_model.getVars():
                    optSol[v.VarName] = v.X
                print "==========pruned by integrality==========="
            else:
                print "==========pruned by bound==========="
        else:
            if parent_model.Objval < UB:
                UB = parent_model.ObjVal
                for v in parent_model.getVars():
                    optSol[v.VarName] = v.X
                print "==========pruned by integrality==========="
            else:
                print "==========pruned by bound==========="
    else:
        bvar = branchVar(parent_model)
        bvar_name = bvar.VarName
        bvar_val = bvar.X
        child_model_l = parent_model.copy()
        bvar_child_l = child_model_l.getVarByName(bvar_name)
        child_model_l.addConstr(bvar_child_l, GRB.LESS_EQUAL, math.floor(bvar_val))
        child_model_l.update()
        child_model_r = parent_model.copy()
        bvar_child_r = child_model_r.getVarByName(bvar_name)
        child_model_r.addConstr(bvar_child_r, GRB.GREATER_EQUAL, math.ceil(bvar_val))
        child_model_r.update()
        child_model_l.optimize()
        prune(child_model_l)
        child_model_r.optimize()
        prune(child_model_r)

end_time = time.time()

bnb_time = end_time - start_time

print "Branch and bound completed in %s s" %bnb_time

for (k,v) in optSol.items():
    print k +": %f" %v