# project.py

# Portions of this code were inspired by the implementation at https://kienyew.github.io/CDCL-SAT-Solver-from-Scratch/The-Implementation.html

import random
from ast import literal_eval
from typing import List, Iterator, Set, Optional, Tuple
from structures import Literal, Clause, Formula, Assignment, Assignments




def satSolve(formula, M):
    assignments = M

    reason, clause = propagate(formula, assignments)
    if (reason == 'conflict'):
        return False, []
    
    while not (allVarsAssigned(formula, assignments)):
        var, val = decide(formula, assignments)
        assignments.dl = assignments.dl + 1
        assignments.assign(var, val, antecedent=None)
        while True:
            reason, clause = propagate(formula, assignments)
            if (reason != 'conflict'):
                break
            else:
                b, learnedClause = conflictAnalysis(clause, assignments)
                if (b < 0):
                    return False, []
                learn(formula, learnedClause)
                backjump(b, assignments)
                assignments.dl = b

    return True, assignments




def getStatus(clause, assignments):
    
    values = []
    for literal in clause:
        if literal.variable not in assignments:
            values.append(None)
        else:
            values.append(assignments.value(literal))

    if True in values:                              # All literals are True
        return 'satisfied'
    elif values.count(False) == len(values):        # All literals are False
        return 'unsatisfied'
    elif values.count(False) == len(values) - 1:    # All except one literal are False
        return 'unit'
    else:                                           # None of the above
        return 'unresolved'


def propagate(formula, assignments):
    done = False
    while not done:
        done = True
        for clause in formula:
            status = getStatus(clause, assignments)
            if status == 'unresolved' or status == 'satisfied':
                continue
            elif status == 'unit':
                # select literal to propagate
                literal = next(literal for literal in clause if literal.variable not in assignments)
                var = literal.variable
                val = not literal.negation

                # assign variable according to unit rule
                assignments.assign(var, val, antecedent=clause)
                done = False
            else:
                # conflict
                return ('conflict', clause)

    return ('unresolved', None)

# our pure function gets all pure literals at once
def pure(numVar, clauses, M):
    pure_literals = set()
    for i in range(1, numVar+1):
        if (i in (item for sublist in clauses for item in sublist) and -i not in (item for sublist in clauses for item in sublist)):
            pure_literals.add(i)
        elif (-i in (item for sublist in clauses for item in sublist) and i not in (item for sublist in clauses for item in sublist)):
            pure_literals.add(-i)
            
    for literal in pure_literals:
        M[abs(literal) - 1] = literal
    return M


def decide(formula, assignments):
    unassigned_vars = [var for var in formula.variables() if var not in assignments]
    var = random.choice(unassigned_vars)
    val = random.choice([True, False])
    return (var, val)


def conflict(clauses, M, C):
    # check if C is not empty first
    if C:
        return C
    for clause in clauses:
        unsatisfiable = all(M[abs(lit) - 1] == -lit for lit in clause)
        if unsatisfiable:
            return clause
    return None


def backjump(b, assignments):
    removing = []
    for var, assignment in assignments.items():
        if assignment.dl > b:
            removing.append(var)
            
    for var in removing:
        assignments.pop(var)


def explain(C, M):
    explanation = []
    for lit in C:
        if M[abs(lit) - 1] == -lit:
            explanation.append(lit)
    return explanation

# Example usage:
    # Assume C is the conflict clause [1, -2, 3] and M is the current assignment.
    # Explanation: [1, -2, 3] caused the conflict, so the explanation is [1, -2, 3].
    # Backjump: The highest decision level in C is 3 (from literal 3), so backjump to level 3.
    # Fail: If the solver reaches this point, it means the instance is unsatisfiable.

def fail():
    print("s UNSATISFIABLE\n")
    exit()

def learn(formula, clause):
    formula.clauses.append(clause)


def allVarsAssigned(formula, assignments):
    return len(formula.variables()) == len(assignments)


def conflictAnalysis(clause, assignments) -> Tuple[int, Clause]:
    if assignments.dl == 0:
        return (-1, None)
 
    # current decision level
    literals = [literal for literal in clause if assignments[literal.variable].dl == assignments.dl]
    while len(literals) != 1:

        literals = filter(lambda lit: assignments[lit.variable].antecedent != None, literals)

        literal = next(literals)
        antecedent = assignments[literal.variable].antecedent
        clause = resolve(clause, antecedent, literal.variable)

        literals = [literal for literal in clause if assignments[literal.variable].dl == assignments.dl]

    # new learnt clause
    # compute the backtrack level b (second largest decision level)
    decision_levels = sorted(set(assignments[literal.variable].dl for literal in clause))
    if len(decision_levels) <= 1:
        return 0, clause
    else:
        return decision_levels[-2], clause
    

def resolve(clauseA, clauseB, x):
    result = set(clauseA.literals + clauseB.literals) - {Literal(x, True), Literal(x, False)}
    result = list(result)
    return Clause(result)

def forget(formula, learned_clauses, threshold):
    """
    This function removes learned clauses that are not frequently used.
    """
    for clause in learned_clauses:
        if clause.usage < threshold:
            formula.remove(clause)
            learned_clauses.remove(clause)

def restart(assignments, threshold):
    """
    This function restarts the search process when a certain threshold is reached.
    """
    if assignments.num_assignments > threshold:
        assignments.clear()
        assignments.dl = 0

if __name__ == "__main__":

    inFile = open(input("Enter input file: "))
    # When prompted to give a file name in the console, type the response in the following format:
    # ./project1-revised-tests/{sat or unsat}/{filename}

    content = inFile.read()
    l = content.split('\n')
    clist = []
    
    numVars = 0
    numClauses = 0
    
    for i in l:
        if(i):
            if (i[0] == 'p'):
                line = i.split(' ')
                numVars = int(line[2])
                numClauses = int(line[3])

            elif (i[0] != 'c'):
                line = i.split(' ')
                s = ""
                for j in line:
                    if (j != '0'):
                        s = s + " " + j

                clist.append(s)

    clauses = []
    for i in clist:
        cl = []
        for j in (i.split(' ')):
            if (j != ''):
                l = Literal(abs(int(j)), int(j)<0)
                cl.append(l)
        c = Clause(cl)
        clauses.append(c)
    formula = Formula(clauses)
        
    M = [0]*numVars
    M = pure(numVars, clauses, M)   # all pure literals are first obtained
    #C = []
    
    #C = conflict(clauses, M, C)
    #M = propagate(clauses, M)

    a = Assignments()
    for i in range (0, len(M)):
        if  (M[i] != 0):
            a.assign(i+1, M[i]<0, antecedent=None)


    sat, lits = satSolve(formula, a)


    if(sat):
        print("s SATISFIABLE")
        s = "v "
        for t in lits:
            if(lits.get(t).value):
                s = s + "-" + str(t) + " "
            else:
                s = s + str(t) + " "
        print(s)
    else:
        fail()