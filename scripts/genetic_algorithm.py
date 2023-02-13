
from shift import ShiftModel
import orders
import numpy as np
from genetic_helperfunctions import makespan, average_lateness


import time


from pymoo.operators.crossover.pntx import TwoPointCrossover
from pymoo.operators.sampling.rnd import PermutationRandomSampling
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.operators.mutation.inversion import InversionMutation
from pymoo.operators.crossover.ox import OrderCrossover
from pymoo.core.problem import ElementwiseProblem
from pymoo.operators.crossover.sbx import SBX
from pymoo.termination import get_termination
from pymoo.optimize import minimize


#z=1



id_init = list(orders.get_westaflex_orders().index)
amount_of_var = len(id_init)
#y=np.array(id_init)


class MyProblem(ElementwiseProblem):

    def __init__(self):
        super().__init__(
                         n_var=amount_of_var,
                         n_obj=2,
                         n_ieq_constr=0, # constrains auf zero if we dont need them 
                         )

    def _evaluate(self, x, out, *args, **kwargs):
        f1 = -abs(makespan(ids=x, decider="genetic"))
        f2 = average_lateness(ids=x, decider="genetic")


        out["F"] = [f1, f2]

def main_algorithm(gen_amount = 5):
    
    print("Start")
    problem = MyProblem()
    algorithm = NSGA2(
                        pop_size=30,
                        pop=id_init,
                        mutation=InversionMutation(),
                        #crossover=SBX(prob=0.9, eta=15),
                        crossover=OrderCrossover(),
                        sampling=PermutationRandomSampling(),
                        
                    )


    termination = get_termination("n_gen", gen_amount)

    

    res = minimize(problem,
                algorithm,
                termination,
                seed=1,
                display=None,
                )

    X = res.X
    F = res.F
    output = [X,F]
    print("end")
    return output, 
    



'''if __name__ == "__main__":
    problem = MyProblem()

    starttime = time.time()
    print("Start")
    algorithm = NSGA2(
                    pop_size=190,
                    pop=id_init,
                    mutation=InversionMutation(),
                    #crossover=SBX(prob=0.9, eta=15),
                    crossover=OrderCrossover(),
                    sampling=PermutationRandomSampling(),
                   )
    termination = get_termination("n_gen", 1)
    res = minimize(problem,
               algorithm,
               termination,
               seed=1,
               display=None,
              )

    X = res.X
    F = res.F
'''
    