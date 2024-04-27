#project.py

from ast import literal_eval
from typing import Literal


def satSolve(numVar, numClause, clauses, M):
    for c in clauses:
        if (len(c) == 1):
            if (M[abs(c[0])-1] == 0):
                M[abs(c[0])-1] = c[0]
            else:
                return False, []

    return True, M


def propagate(clauses, M):
    changed = True
    while changed:
        changed = False
        for clause in clauses:
            unassigned_literals = [lit for lit in clause if M[abs(lit) - 1] == 0]
            if len(unassigned_literals) == 1:
                lit = unassigned_literals[0]
                M[abs(lit) - 1] = lit
                changed = True
            elif len(unassigned_literals) == 0:
                # Found a conflict
                return M
    return M

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

# def decide

def conflict(clauses, M, C):
    # check if C is not empty first
    if C:
        return C
    for clause in clauses:
        unsatisfiable = all(M[abs(lit) - 1] == -lit for lit in clause)
        if unsatisfiable:
            return clause
    return None


# def explain
# def backjump
# def fail
# def learn
# def forget
# def restart


if __name__ == "__main__":

    inFile = open(input("Enter input file: "))
    # When prompted to give a file name in the console, type the response in the following format:
    # ./project1-tests/{sat or unsat}/{filename}

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
        c = []
        for j in (i.split(' ')):
            if (j != ''):
                c.append(int(j))
        clauses.append(c)
        
    M = [0]*numVars
    M = pure(numVars, clauses, M)   # all pure literals are first obtained
    
    C = []
    
    C = conflict(clauses, M, C)
    M = propagate(clauses, M)
    

    sat, lits = satSolve(numVars, numClauses, clauses, M)
    if(sat):
        print("SATISFIABLE")
        s = ""
        for i in lits:
            s = s + str(i) + " "
        print("v " + s)
    else:
        print("UNSATISFIABLE\n")
