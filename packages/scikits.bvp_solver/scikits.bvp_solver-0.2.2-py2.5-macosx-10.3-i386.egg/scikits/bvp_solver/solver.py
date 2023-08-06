import bvp_solverf
import numpy
from Solution import Solution
import tools

#TODO: add derivative checker


def solve(bvp_problem,
               solution_guess, # this provides the initial solution as well as several other parameters
               initial_mesh = None,
               parameter_guess = None,
               max_subintervals = 300,
               singular_term = None,
               tolerence = 1e-6,
               method = 4,
               trace = 0,
               stop_on_fail = False):
    """
    Attempts to solve the supplied boundary value problem starting from the user-supplied guess for the solution using BVP_SOLVER.

    bvp_problem - (required) a ProblemDefinition object which defines the boundary value problem to be solved.
    solution_guess - (required) a guess for the solution, can either be a Solution object, a constant or an array of values or a function.
    initial_mesh - an array (or castable) of points on the x-axis to use, default is 10 evenly spaced points.
                    Must not be supplied if solution_guess is a Solution object.
    parameter_guess - an array (or castable) of guesses for the unknown parameters.
                    Must not be supplied if solution_guess is a Solution object.
    max_subintervals - maximum number of points on the mesh before an error is returned. Default is 300
    singular_term - array (or castable) that defines the singular term for the problem if one exist.
    tolerence - Default is 1e-6
    method - order of Runge-Kutta to use. Must be either 2, 4 or 6. Default is 4.
    trace - indicates verbosity of output. 0 for no output, 1 for some output, 2 for full output. Default is 0.
    stop_on_fail - Default is false.
    """

    init_solution = 0

    if isinstance(solution_guess,Solution):
        if not (initial_mesh == None and
                parameter_guess == None):
            raise ValueError("values for initial mesh and parameter_guess must not be given if solution_guess is a Solution object")
        init_solution = solution_guess
    else:

        if initial_mesh == None:
            initial_mesh = numpy.linspace(bvp_problem.boundary_points[0],bvp_problem.boundary_points[1] , 10)

        # here we call one of the BVP_GUESS_i routines that make up BVP_INIT to set up the solution
        if ( not callable(solution_guess)):   # in this case the initial solution passed was not a function

            if ( solution_guess is not numpy.array):

                bvp_solverf.bvp.guess_1_wrap(bvp_problem.num_parameters,
                                           bvp_problem.num_left_boundary_conditions,
                                           tools.farg(initial_mesh),
                                           solution_guess,
                                           tools.farg(parameter_guess),
                                           max_subintervals,
                                           bvp_problem.num_ODE)

                init_solution = Solution.from_arg_list(bvp_solverf.bvp)

            else:

                bvp_solverf.bvp.guess_2_wrap(
                                             bvp_problem.num_parameters,
                                             bvp_problem.num_left_boundary_conditions,
                                             tools.farg(initial_mesh),
                                             tools.farg(solution_guess),
                                             tools.farg(parameter_guess),
                                             max_subintervals,
                                             bvp_problem.num_ODE)
                init_solution = Solution.from_arg_list(bvp_solverf.bvp)

        else:
            # initialization function for
            bvp_solverf.bvp.guess_3_wrap(node_in = bvp_problem.num_ODE,
                                           nparam_in = bvp_problem.num_parameters,
                                           leftbc_in = bvp_problem.num_left_boundary_conditions,
                                           x_in= tools.farg(initial_mesh),
                                           fcn = solution_guess,
                                           parameters_in = tools.farg(parameter_guess),
                                           mxnsub_in = max_subintervals)

            init_solution = Solution.from_arg_list(bvp_solverf.bvp)


    if not (method == 2 or method == 4 or method == 6 ):
        raise ValueError ("method must be either 2, 4 or 6 but got " + method )

    if (tolerence < 0):
        raise ValueError("tolerance must be nonnegative")

    singular = not (singular_term is None)

    # check to see if the singular term is of the right size
    singular_term = tools.preparg(singular_term)
    if singular and not (singular_term.shape == (bvp_problem.num_ODE, bvp_problem.num_ODE)):
        raise ValueError("singular_term has the wrong shape/size. Expected: " +
                         (bvp_problem.num_ODE, bvp_problem.num_ODE)+
                         " but got :" +
                          singular_term.shape)

    bvp_problem.test(init_solution)

    bvp_solverf.bvp.bvp_solver_wrap(bvp_problem.num_ODE,
                                    bvp_problem.num_parameters,
                                    bvp_problem.num_left_boundary_conditions,
                                    len(init_solution.mesh),
                                    init_solution.successIndicator,
                                    max_subintervals,
                                    tools.farg(init_solution.mesh),
                                    tools.farg(init_solution.solution),
                                    tools.farg(init_solution.parameters),
                                    tools.farg(init_solution.work),
                                    tools.farg(init_solution.iwork),
                                    bvp_problem.function,
                                    bvp_problem.functionp,
                                    bvp_problem.boundary_conditions,
                                    bvp_problem.boundary_conditionsp,

                                    singular,

                                    bvp_problem.has_function_derivative,
                                    bvp_problem.function_derivative,
                                    bvp_problem.function_derivativep,

                                    bvp_problem.has_boundary_conditions_derivative,
                                    bvp_problem.boundary_conditions_derivative,
                                    bvp_problem.boundary_conditions_derivativep,
                                    #optional arguments
                                    method = method,
                                    tol = tolerence,

                                    trace = trace,
                                    stop_on_fail = stop_on_fail,

                                    singularterm = tools.farg(singular_term))

    calculatedSolution = Solution.from_arg_list(bvp_solverf.bvp)

    # check to see if there was a problem with the solution
    return calculatedSolution