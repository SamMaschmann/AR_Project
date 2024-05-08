# structures.py

# content in this file was taken from https://kienyew.github.io/CDCL-SAT-Solver-from-Scratch/The-Implementation.html

from ast import literal_eval
from typing import List, Iterator, Set, Optional
from dataclasses import dataclass


@dataclass(frozen=True)
class Literal:
    variable: int
    negation: bool

    def __repr__(self):
        if self.negation:
            return '-' + str(self.variable)
        else:
            return str(self.variable)

    def neg(self) -> 'Literal':
        return Literal(self.variable, not self.negation)

@dataclass
class Clause:
    literals: List[Literal]

    def __repr__(self):
        return ' '.join(map(str, self.literals))

    def __iter__(self) -> Iterator[Literal]:
        return iter(self.literals)

    def __len__(self):
        return len(self.literals)
    
    def __hash__(self):
        x = 0 
        for lit in self.literals:
            x ^= hash(lit)
        return x

@dataclass
class Formula:
    clauses: List[Clause]
    __variables: Set[int]

    def __init__(self, clauses: List[Clause]):
        self.clauses = []
        self.__variables = set()
        for clause in clauses:
            self.clauses.append(Clause(list(set(clause))))
            for lit in clause:
                var = lit.variable
                self.__variables.add(var)

    def variables(self) -> Set[int]:
        return self.__variables

    def __iter__(self) -> Iterator[Clause]:
        return iter(self.clauses)

    def __len__(self):
        return len(self.clauses)

@dataclass
class Assignment:
    value: bool
    antecedent: Optional[Clause]
    dl: int

class Assignments(dict):

    def __init__(self):
        super().__init__()
        self.dl = 0

    def value(self, literal: Literal) -> bool:
        if literal.negation:
            return not self[literal.variable].value
        else:
            return self[literal.variable].value

    def assign(self, variable: int, value: bool, antecedent: Optional[Clause]):
        self[variable] = Assignment(value, antecedent, self.dl)

    def unassign(self, variable: int):
        self.pop(variable)

    def satisfy(self, formula: Formula) -> bool:
        for clause in formula:
            if True not in [self.value(lit) for lit in clause]:
                return False
        return True