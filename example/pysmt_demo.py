import pysmt
from pysmt import *

print("pysmt version:", pysmt.__version__)


# ================== Pysmt Solver Demo ==================
# This is a simple example of using Pysmt to create a solver and check satisfiability of a constraint.
# The example creates a solver, adds a simple constraint, and checks if the constraint is satisfiable.
# The example also demonstrates how to create variables and use them in constraints.
# Import necessary modules from Pysmt
from pysmt.typing import BOOL, INT, REAL
from pysmt.solvers.z3 import Z3Solver, Z3Converter, Z3Model
from pysmt.shortcuts import Symbol, And, Or, Not, Implies, Solver



def main_entry():
    # Initialize the solver
    from pysmt.environment import get_env
    from pysmt.logics import QF_LIA

    # Initialize the solver with environment and logic
    env = get_env()
    solver = Z3Solver(env, logic=QF_LIA)
    # solver = Solver(name="z3", logic=QF_LIA)
    # Create variables
    x = Symbol('x', INT)
    y = Symbol('y', INT)
    z = Symbol('z', INT)
    # Create constraints      
    constraint1 = And(x > 0, y > 0)
    constraint2 = Or(x < 5, y < 5)
    constraint3 = Implies(x + y > 10, z < 5)
    # Add constraints to the solver
    solver.add_assertion(constraint1)
    solver.add_assertion(constraint2)
    solver.add_assertion(constraint3)
    # Check satisfiability
    if solver.solve():
        print("The constraints are satisfiable.")
        # Get the model
        model = solver.get_model()
        print("Model:", model)
    else:
        print("The constraints are unsatisfiable.")
    # Cleanup
            
        
if __name__ == "__main__":
    main_entry()
