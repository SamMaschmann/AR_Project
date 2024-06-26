# project.py

# Portions of this code were inspired by the implementation at https://kienyew.github.io/CDCL-SAT-Solver-from-Scratch/The-Implementation.html

import random, threading, time
from ast import literal_eval
from typing import List, Iterator, Set, Optional, Tuple
from structures import Literal, Clause, Formula, Assignment, Assignments
from collections import defaultdict



def satSolve(formula, M):
    # Initialize the activity scores and other parameters
    activity_scores = initialize_activity_scores(formula)
    increment = 1  # The value by which activity scores are incremented during conflict analysis
    decay_factor = 0.95  # The decay factor for activity scores

    assignments = M
    lit2clauses, clause2lits = init_watches(formula)

    unit_clauses = [clause for clause in formula if len(clause) == 1]
    to_propagate = []
    for clause in unit_clauses:
        lit = clause.literals[0]
        var = lit.variable
        val = not lit.negation
        if var not in assignments:
            assignments.assign(var, val, clause)
            to_propagate.append(lit)

    reason, clause = propagate(assignments, lit2clauses, clause2lits, to_propagate)
    if (reason == 'conflict'):
        return False, []
    
    while not (allVarsAssigned(formula, assignments)):
        var, val = decide(formula, assignments, activity_scores)
        assignments.dl = assignments.dl + 1
        assignments.assign(var, val, antecedent=None)
        to_propagate = [Literal(var, not val)]
        while True:
            reason, clause = propagate(assignments, lit2clauses, clause2lits, to_propagate)
            if (reason != 'conflict'):
                break
            else:
                b, learnedClause = conflictAnalysis(clause, assignments, activity_scores, increment, decay_factor)
                if (b < 0):
                    return False, []
                learn(formula, learnedClause, activity_scores, increment, assignments, lit2clauses, clause2lits)
                backjump(b, assignments)
                assignments.dl = b

                # The learned clause must be a unit clause, so the next step must again be unit progagation
                literal = next(literal for literal in learnedClause if literal.variable not in assignments)
                var = literal.variable
                val = not literal.negation
                assignments.assign(var, val, antecedent=learnedClause)
                to_propagate = [Literal(var, not val)]


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


def propagate(assignments, lit2clauses, clause2lits, to_propagate):
    while len(to_propagate) > 0:
        watching_lit = to_propagate.pop().neg()

        watching_clauses = list(lit2clauses[watching_lit])
        for watching_clause in watching_clauses:
            for lit in watching_clause:
                if lit in clause2lits[watching_clause]:
                    continue                                                                        # lit is another watching literal of watching_clause
                elif lit.variable in assignments and assignments.value(lit) == False:
                    continue                                                                        # lit is a assigned False
                else:                                                                               # lit is not another watching literal of watching_clause and is non-False literal, so we rewatch it
                    clause2lits[watching_clause].remove(watching_lit)
                    clause2lits[watching_clause].append(lit)
                    lit2clauses[watching_lit].remove(watching_clause)
                    lit2clauses[lit].append(watching_clause)
                    break
            else:                                                                                   # Can't find another literal to rewatch
                watching_lits = clause2lits[watching_clause]
                if len(watching_lits) == 1:                                                         # watching_clause is unit, and the literal is False, so there's a conflict
                    return ('conflict', watching_clause)
                other = watching_lits[0] if watching_lits[1] == watching_lit else watching_lits[1]
                if other.variable not in assignments:                                               # the other watching literal is unassigned
                    assignments.assign(other.variable, not other.negation, watching_clause)
                    to_propagate.insert(0, other)
                elif assignments.value(other) == True:                                              # the other watching literal is assigned True
                    continue
                else:                                                                               # the other watching literal is assigned False
                    return ('conflict', watching_clause)
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


def decide(formula, assignments, activity_scores):
    unassigned_vars = [var for var in formula.variables() if var not in assignments]
    var = max(unassigned_vars, key=lambda v: activity_scores.get(v, 0))
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

def learn(formula, learned_clause, activity_scores, increment, assignments, lit2clauses, clause2lits):
    # Add the learned clause to the formula
    formula.clauses.append(learned_clause)

    for lit in sorted(learned_clause, key=lambda lit: -assignments[lit.variable].dl):
        if len(clause2lits[learned_clause]) < 2:
            clause2lits[learned_clause].append(lit)
            lit2clauses[lit].append(learned_clause)
        else:
            break

    for lit in learned_clause:
        activity_scores[lit.variable] += increment

    if hasattr(learned_clause, 'usage'):
        learned_clause.usage += 1



def allVarsAssigned(formula, assignments):
    return len(formula.variables()) == len(assignments)


def conflictAnalysis(clause, assignments, activity_scores, increment, decay_factor):
    if assignments.dl == 0:
        return (-1, None)
 
    # current decision level
    literals = [literal for literal in clause if assignments[literal.variable].dl == assignments.dl]
    while len(literals) != 1:
        literals = filter(lambda lit: assignments[lit.variable].antecedent != None, literals)
        literal = next(literals)
        antecedent = assignments[literal.variable].antecedent
        clause = resolve(clause, antecedent, literal.variable)

        # Update activity scores for each variable in the antecedent clause
        for lit in antecedent:
            activity_scores[lit.variable] += increment

        literals = [literal for literal in clause if assignments[literal.variable].dl == assignments.dl]

    # Decay the activity scores
    for var in activity_scores:
        activity_scores[var] *= decay_factor

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

def initialize_activity_scores(formula):
    activity_scores = {var: 0 for var in formula.variables()}
    return activity_scores

def decay_activity_scores(activity_scores, decay_factor):
    for var in activity_scores:
        activity_scores[var] *= decay_factor

# Define the handler for the alarm signal
def handler(signum, frame):
    print("Timeout! The program took too long to execute.")
    exit(1)

# Define a function to raise a TimeoutError after a delay
def raise_timeout(delay, error_message="Timeout!"):
    def timeout():
        raise TimeoutError(error_message)
    timer = threading.Timer(delay, timeout)
    timer.start()
    return timer


def init_watches(formula: Formula):
    lit2clauses = defaultdict(list)
    clause2lits = defaultdict(list)
    
    for clause in formula:
        if len(clause) == 1:
            # Unit clause means only one literal to watch
            lit2clauses[clause.literals[0]].append(clause)
            clause2lits[clause].append(clause.literals[0])
        else:
            # Otherwise choose any 2 literals to watch
            lit2clauses[clause.literals[0]].append(clause)
            lit2clauses[clause.literals[1]].append(clause)
            clause2lits[clause].append(clause.literals[0])
            clause2lits[clause].append(clause.literals[1])
            
    return lit2clauses, clause2lits








if __name__ == "__main__":
    # Set the timeout duration (in seconds)
    timeout_duration = 300  # 1 minute timeout

    try:
        inFile = open(input("Enter input file: "))
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

        a = Assignments()
        for i in range (0, len(M)):
            if  (M[i] != 0):
                a.assign(i+1, M[i]<0, antecedent=None)

        # Start the timeout timer
        timer = raise_timeout(timeout_duration)
        # Check the current time to record runtime.
        start_time = time.time_ns() / (10 ** 9)
        # Call the satSolve function to solve the formula and determine satisfiability.
        sat, lits = satSolve(formula, a)
        # Check the end time to determine runtime.
        end_time = time.time_ns() / (10 ** 9)
        # Calculation for the total runtime.
        runtime = end_time - start_time


        if(sat):
            print("s SATISFIABLE")
            s = "v "
            for t in lits:
                if(lits.get(t).value):
                    s = s + "-" + str(t) + " "
                else:
                    s = s + str(t) + " "
            print(s)
            print(f"Runtime of the function: {runtime:.4f} seconds.")
            exit()
        else:
            print(f"Runtime of the function: {runtime:.4f} seconds.")
            fail()


    except TimeoutError as e:
        print(e)
        exit()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Cancel the timer if the function completes before the timeout
        timer.cancel()
