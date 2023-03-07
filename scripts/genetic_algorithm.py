
from shift import ShiftModel
import orders
import numpy as np
import matplotlib.pyplot as plt
from genetic_helperfunctions import makespan, average_lateness
from simpy_simulation import main
import pandas as pd

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
jobs_from_db = True
#y=np.array(id_init)


class MyProblem(ElementwiseProblem):

    def __init__(self, input_jobs, n_var):
        super().__init__(
                         n_obj=2,
                         n_ieq_constr=0, # constrains auf zero if we dont need them 
                         )
        self.input_jobs = input_jobs
        self.n_var = n_var

    def _evaluate(self, x, out, *args, **kwargs):
        o1, o2 = main(ids=x, input_jobs=self.input_jobs)
        f1 = abs(o1[0])
        f2 = abs(o2[0])

        out["F"] = [f1, f2]

def main_algorithm(gen_amount = 5, input_jobs = None):
    
    print("Start")
    
    if not jobs_from_db:
        id_init = list(orders.get_westaflex_orders().index)
        input_jobs = orders.get_westaflex_orders()
    else:
        id_init = np.linspace(0, len(input_jobs)-1, num=len(input_jobs)).tolist()
    print("id_init: ",id_init)
    amount_of_var = len(id_init)

    problem = MyProblem(input_jobs=input_jobs, n_var=amount_of_var)
    algorithm = NSGA2(
                        pop_size=1,
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
                save_history=True
                )
    
    n_evals = np.array([e.evaluator.n_eval for e in res.history])
    X_opt = np.array([e.opt[0].X for e in res.history])
    opt = np.array([e.opt[0].F for e in res.history])
    plt.title("GA_Convergence")
    plt.plot(n_evals, opt, "--")
    plt.yscale("log")
    plt.show()

    data = np.column_stack((X_opt, opt))
    header = 'X,F'
    # np.savetxt('GA_Convergence.csv', data, delimiter=',', header=header, fmt='%f', comments='')

    X = res.X
    F = res.F
    output = [X,F]

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
    