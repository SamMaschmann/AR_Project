#project.py

from ast import literal_eval
from typing import Literal


def satSolve(numVar, numClause, clauses, M):
    
    temp = []   # temp is a copy of clauses that doesn't get changed. It is used to handle some bugs that happen when removing elements from clauses
    for i in clauses:
        temp.append(i)

    for c in clauses:
        if (len(c) == 0):       # if there is an empty clause in our list, that means that it is unsatisfiable
            return False, []    
        
        if (len(c) == 1):                           # this chunk of code looks at every clause of length 1 and checks if we have a value for it already
            if (M[abs(c[0])-1] == 0):               # if M has a value and the value doesn't match, then there is a conflict, so it is unsatisfiable
                M[abs(c[0])-1] = c[0]               # ex: M = [1, 0, 3] and clauses contains [-1], then it is unsatisfiable
                for clause in temp:                 # if M doesn't have a value, it assigns one and removes clauses with that value and removes negations of that value
                    if c[0] in clause:              # ex: if we are adding [1] to M, then in clauses: [1, 2, 3] gets removed (since it is satisfied) and [-1, 4, 6] becomes [4, 6]
                        clauses.remove(clause)      # This works similarly to the Propagate rule
                    elif (c[0] * -1) in clause:
                        clause.remove(c[0] * -1)
                return satSolve(numVar, numClause, clauses, M)
            elif (M[abs(c[0])-1] != c[0]):
                return False, []
            

    if (len(clauses) == 0):         # if there are no more clauses left to satisfy, then we have reached an assignment that satisfies the clause set
        return True, M
    else:               # otherwise, we have to decide
        if (0 in M):
            z = M.index(0)
            m1 = []         # m1 and m2 are the two assignemnts we try with each decision. m1 tries with a positive value, and m2 with a negative value (ie 3 and -3)
            m2 = []
            for i in range(0, len(M)):
                if(i == z):
                    m1.append(i+1)
                    m2.append(-1*(i+1))
                else:
                    m1.append(M[i])
                    m2.append(M[i])
            c1 = []         # c1 and c2 are the clause sets left over after we assign values to m1 and m2. (c1 for pos and c2 for neg)
            c2 = []         # the process for removing clauses is the same as above in the propagation chunk
            for clause in clauses:
                if (z+1) in clause: 
                    clause.remove(z+1)
                    c2.append(clause)
                elif ((z+1) * -1) in clause:
                    clause.remove((z+1) * -1)
                    c1.append(clause)
                else:
                    c1.append(clause)
                    c2.append(clause)

            x, a1 = satSolve(numVar, numClause, c1, m1)         # first we check if the assignment will work if the value is positive...
            if(x):
                return True, a1
            else:
                y, a2 = satSolve(numVar, numClause, c2, m2)     # ...and if not we try with negative
                if(y):
                    return True, a2
                else:
                    return False, []                # if neither work, then it fails
        else:
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

def decide(M):
    for i, value in enumerate(M):
        if value == 0:
            # Assign positive or negative value to unassigned variable
            M[i] = i + 1  # Positive assignment
            # M[i] = -(i + 1)  # Negative assignment
            return M
    return M  # No unassigned variables left

# Example usage:
# Assume M is the current assignment with some variables assigned and others unassigned.
# Call decide(M) to make a decision and update M.


def conflict(clauses, M, C):
    # check if C is not empty first
    if C:
        return C
    for clause in clauses:
        unsatisfiable = all(M[abs(lit) - 1] == -lit for lit in clause)
        if unsatisfiable:
            return clause
    return None

def backjump(C, M):
    highest_level = 0
    for lit in C:
        level = abs(M[abs(lit) - 1])
        if level > highest_level:
            highest_level = level
    return highest_level

def explain(C, M):
    explanation = []
    for lit in C:
        if M[abs(lit) - 1] == -lit:
            explanation.append(lit)
    return explanation

def fail():
    print("s UNSATISFIABLE\n")
    exit()
    
    # Example usage:
    # Assume C is the conflict clause [1, -2, 3] and M is the current assignment.
    # Explanation: [1, -2, 3] caused the conflict, so the explanation is [1, -2, 3].
    # Backjump: The highest decision level in C is 3 (from literal 3), so backjump to level 3.
    # Fail: If the solver reaches this point, it means the instance is unsatisfiable.

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
    #M = propagate(clauses, M)
    

    sat, lits = satSolve(numVars, numClauses, clauses, M)
    if(sat):
        #for i in range(0, len(lits)):
        #    if lits[i] == 0:
        #        lits[i] = i+1
        print("s SATISFIABLE")
        s = ""
        for i in lits:
            s = s + str(i) + " "
        print("v " + s)
    else:
        print("s UNSATISFIABLE\n")