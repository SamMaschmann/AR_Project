#project.py

def satSolve(numVar, numClause, clauses):
    M = [1,2,3,-4, -69]
    return True, M

if __name__ == "__main__":

    inFile = open(input("Enter input file: "))
    # When prompted to give a file name in the console, type the response in the following format:
    # ./project1-tests/{sat or unsat}/{filename}

    content = inFile.read()
    l = content.split('\n')
    clist = []
    
    vars = 0
    clauses = 0
    
    for i in l:
        if(i):
            if (i[0] == 'p'):
                line = i.split(' ')
                vars = int(line[2])
                clauses = int(line[3])

            elif (i[0] != 'c'):
                clist.append(i)
        
    sat, lits = satSolve(vars, clauses, clist)
    if(sat):
        print("SATISFIABLE")
        s = ""
        for i in lits:
            s = s + str(i) + " "
        print("v " + s)
    else:
        print("UNSATISFIABLE\n")

    