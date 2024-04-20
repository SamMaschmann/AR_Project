#project.py

def satSolve(input):
    return input

if __name__ == "__main__":
    print("Works")

    inFile = open(input("Enter input file: "))
    # When prompted to give a file name in the console, type "./project1-tests/{sat or unsat}/{filename}"

    content = inFile.read()
    l = content.split('\n')

    print(l[1])
    