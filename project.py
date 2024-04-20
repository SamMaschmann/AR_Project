#project.py

def satSolve(input):
    return input

if __name__ == "__main__":

    inFile = open(input("Enter input file: "))
    # When prompted to give a file name in the console, type "./project1-tests/{sat or unsat}/{filename}"

    content = inFile.read()
    l = content.split('\n')
    clist = []
    
    for i in l:
        if(i):
            if i[0] != 'c':
                clist.append(i)
        
    
    for i in clist:
        print(i)

    