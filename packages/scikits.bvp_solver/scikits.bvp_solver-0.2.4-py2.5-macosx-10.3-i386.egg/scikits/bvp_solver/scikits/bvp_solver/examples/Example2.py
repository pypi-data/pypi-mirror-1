#based off of this fortran example
# use of function derivative callback
# function callback for a guess
# a singular term

import scikits.bvp_solver
import numpy
import pylab
print ("test #1")


def function1(X , Y):
    return numpy.array([Y[1], -(X*Y[0] - 1.0)*Y[0]])

def dfunction1(X,Y):
    PD = numpy.zeros((2,2))
    PD[0,1] = 1.0
    PD[1,0] = 1.0 - 2*X*Y[0]
    return PD

def boundary_conditions1(YA,YB):
    BCA= numpy.zeros(1)
    BCB= numpy.zeros(1)

    BCA[0] = YA[1]
    BCB[0] = YB[0] + YB[1]

    return BCA, BCB

def guess_y1(X):
    Y = numpy.zeros(2)

    if X <= 1.5:
      Y[0] = 2
      Y[1] = 0
    else:
      Y[0] = 2.0*numpy.exp(1.5 - X)
      Y[1] = - Y[0]

    return Y

singular_term = numpy.zeros((2,2))
singular_term[1,1] = -4.0

problem1 = scikits.bvp_solver.ProblemDefinition(num_ODE = 2,
                                  num_parameters = 0,
                                  num_left_boundary_conditions = 1,
                                  boundary_points = (0, 10.0),
                                  function = function1,
                                 boundary_conditions = boundary_conditions1,
                                 function_derivative = dfunction1)

solution = scikits.bvp_solver.solve(problem1,
                                 solution_guess = guess_y1,
                                 singular_term = singular_term,
                                 max_subintervals = 300)
x = numpy.linspace(problem1.boundary_points[0],problem1.boundary_points[1], 45)
y = solution(x)

solution2 = solution.extend(0, 11, order = 1)



pylab.subplot(211)
pylab.plot(x, y[0,:],'-')
pylab.plot(x, y[1,:],'-')

pylab.subplot(212)
pylab.plot(solution2.mesh, solution2.solution[0,:],'-')
pylab.plot(solution2.mesh, solution2.solution[1,:],'-')
pylab.show()

