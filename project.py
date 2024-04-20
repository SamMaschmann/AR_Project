#project.py

def satSolve(numVar, numClause, clauses, M):
    for c in clauses:
        if (len(c) == 1):
            if (M[abs(c[0])-1] == 0):
                M[abs(c[0])-1] = c[0]
            else:
                return False, []


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
                line = i.split(' ')
                s = ""
                for j in line:
                    if (j != '0'):
                        s = s + " " + j

                clist.append(s)
    
    M = [0]*vars

    cl = []
    for i in clist:
        e = i.split(' ')
        c = []
        for j in e:
            if (j != ''):
                c.append(int(j))
        cl.append(c)

    sat, lits = satSolve(vars, clauses, cl, M)
    if(sat):
        print("SATISFIABLE")
        s = ""
        for i in lits:
            s = s + str(i) + " "
        print("v " + s)
    else:
        print("UNSATISFIABLE\n")

    