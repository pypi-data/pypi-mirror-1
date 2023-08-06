import numpy
import tools
import pickle

class ProblemDefinition:
    """
    defines a boundary value problem.
    properties:
    num_ODE - the number of first order ordinary differential equations in the problem
    num_parameters - the number of unknown parameters in the problem
    num_left_boundary_conditions - the number of boundary conditions enforced on the left boundary
    boundary_points - array that defines the two boundary points on the x axis
    function - function which evaluates the ODEs that make up the boundary value problem
    boundary_conditions - function which evaluates the difference between the boundary conditions and the values of the variables at the boundary points
    function_derivative - evaluates the derivatives of function
    boundary_conditions_derivative - evaluates the derivatives of bounday_conditions
    """
    def __init__(self,
                 num_ODE,
                 num_parameters,
                 num_left_boundary_conditions,
                 boundary_points,
                 function,
                 boundary_conditions,
                 function_derivative = None,
                 boundary_conditions_derivative = None):
        """
        num_ODE - the number of first order ordinary differential equations in the problem
        num_parameters - the number of unknown parameters in the problem
        num_left_boundary_conditions - the number of boundary conditions enforced on the left boundary
        boundary_points - array that defines the two boundary points on the x axis

        function - a function which calculates the value of the ODE equations
            arguments:
                X - scalar value of x at which
                Y - (array) current value of all variables
                [P - (array) value of all unknown parameters]: this is only included if num_parameters > 0
            returns:
                array of all ODEs

        boundary_conditions - a function which calculates the difference between the boundary conditions and the actual variables currently calculated
            arguments:
                YA - (array) value of all variables at the left boundary
                YB - (array) value of all variables at the right boundary
                [P - (array) value of all unknown parameters]: this is only included if num_parameters > 0
            returns:
                BCA - array of the difference between the boundary condition and variables at the left boundary
                BCB - array of the difference between the boundary condition and variables at the right boundary

        function_derivative - a function which returns the partial derivatives of the function argument
            arguments (same as function):
                X - scalar value of x at which
                Y - (array) current value of all variables
                [P - (array) value of all unknown parameters]: this is only included if num_parameters > 0
            returns:
                - array of partial derivative of all ODEs with respect to all variables; index of ODEs is first, index of variables is second
                - [array of partial derivative of all ODEs with respect to all unknown parameters; index of ODEs is first, index of parameters is second]
                    must not be returned if the problem does not include unknown parameters

        boundary_conditions_drivative - a function which returns the partial derivatives of the boundary_conditions argument
            arguments (same as boundary_conditions):
                YA - (array) value of all variables at the left boundary
                YB - (array) value of all variables at the right boundary
                [P - (array) value of all unknown parameters]: this is only included if num_parameters > 0
            returns:
                BCA - array of the partial derivatives of the difference between the left boundary condition and the actual variables at the left boundary
                    (boundary condition index is first and variable index is second)
                BCB - array of the partial derivatives of the difference between the right boundary condition and the actual variables at the right boundary
                    (boundary condition index is first and variable index is second)
                BCPA - array of the partial derivatives of the difference between the left boundary condition and the unknown parameters
                    (boundary condition index is first and parameter index is second)
                BCPB - array of the partial derivatives of the difference between the right boundary condition and the unknown parameters
                    (boundary condition index is first and parameter index is second)

        """

        self.num_ODE = num_ODE
        self.num_parameters = num_parameters
        self.num_left_boundary_conditions = num_left_boundary_conditions
        self.boundary_points = tools.preparg(boundary_points)
        self.function = function
        self.boundary_conditions =boundary_conditions
        self.function_derivative = function_derivative
        self.boundary_conditions_derivative = boundary_conditions_derivative


        #figure out whether the user has supplied derivatives for the function and boundary conditions
        self.has_function_derivative = not self.function_derivative is None
        self.has_boundary_conditions_derivative = not self.boundary_conditions_derivative is None

        if self.num_parameters == 0:

            # if don't have unknown parameters then give all the arguments for callbacks with parameter arguments dummy functions
            self.functionp = fp_dummy
            self.boundary_conditionsp = bcp_dummy
            self.function_derivativep = fderivep_dummy
            self.boundary_conditions_derivativep = bcderivep_dummy

            # also assign dummy arguments to optional derivatives if they were not supplied
            if self.function_derivative is None:
                self.function_derivative = f_dummy

            if self.boundary_conditions_derivative is None:
                self.boundary_conditions_derivative = bcderive_dummy
        else:

            #also assign all the supplied arguments to the callback arguments with parameter arguments in them
            self.functionp = function
            self.boundary_conditionsp = self.boundary_conditions
            self.function_derivativep = self.function_derivative
            self.boundary_conditions_derivativep = self.boundary_conditions_derivative

            # if have unknown parameters then give all the arguments for callbacks without parameter arguments dummy functions
            self.function = f_dummy
            self.boundary_conditions = bc_dummy
            self.function_derivative = fderive_dummy
            self.boundary_conditions_derivative = bcderive_dummy

            # give dummy arguments in those cases when no derivative arugment is supplied
            if self.function_derivativep is None:
                self.function_derivativep = fp_dummy

            if self.boundary_conditions_derivativep is None:
                self.boundary_conditions_derivativep = bcderivep_dummy

    def test(self, test_solution):
        """
        Test that the boundary value problem definition is self consistent, and
        tests whether test_solution is consistent with the bvp definition.
        This requires some legal values for the parameters and thus requires a test solution.
        """

        if self.num_parameters > 0:

            if test_solution.parameters is None:
                raise ValueError ("parameter guess required, but not given")

            tools.argShapeTest(test_solution.parameters, (self.num_parameters,),
                               "parameter array",
                               "Should be (num_parameters,)")

        tools.argShapeTest(test_solution.solution, (self.num_ODE,len(test_solution.mesh)),
                               "solution array",
                               "Should be (num_ODE,length(mesh))")

        if not (self.boundary_points.shape == (2,)):
            raise ValueError("This boundary value problem definition must be given exactly two boundary points, but got: "
                              + self.boundary_points +" as the boundary values")

        #at this point we want to check the call backs to make sure they take the right arguments and return the right things
        if self.num_parameters ==0:
            f = self.function(test_solution.mesh[0],
                         test_solution.solution[:,0])

            tools.argShapeTest(f, (self.num_ODE,),
                               "function callback return",
                               "Should be (num_ODE,)")

            bca,bcb = self.boundary_conditions(test_solution.solution[:,0],
                                     test_solution.solution[:,-1])

            tools.argShapeTest(bca, (self.num_left_boundary_conditions,),
                               "Boundary conditions callback first return",
                               "Should be (num_left_boundary_conditions,)")

            tools.argShapeTest(bcb, (self.num_ODE + self.num_parameters - self.num_left_boundary_conditions,),
                               "Boundary conditions callback second return",
                               "Should be (num_ODE + num_parameters - num_left_boundary_conditions,)")

            if self.has_function_derivative:
                df = self.function_derivative(test_solution.mesh[0],
                                         test_solution.solution[:,0])

                tools.argShapeTest(df, (self.num_ODE, self.num_ODE),
                                   "function derivative callback first return",
                                   "Should be (num_ODE, num_ODE)")

            if self.has_boundary_conditions_derivative:
                dbca, dbcb = self.boundary_conditions_derivative(test_solution.solution[:,0],
                                                            test_solution.solution[:,0])

                tools.argShapeTest(dbca, (self.num_left_boundary_conditions, self.num_ODE),
                                   "Boundary conditions derivative callback first return",
                                   "Should be (num_left_boundary_conditions, num_ODE)")

                tools.argShapeTest(dbcb, (self.num_ODE + self.num_parameters - self.num_left_boundary_conditions, self.num_ODE),
                                   "Boundary conditions derivative callback second return",
                                   "Should be (num_ODE + num_parameters - num_left_boundary_conditions, num_ODE)")

        else: ## if unknown parameters are used, things should be a little different
            f = self.functionp(test_solution.mesh[0],
                         test_solution.solution[:,0],
                         test_solution.parameters)

            tools.argShapeTest(f, (self.num_ODE,),
                               "function callback return",
                               "Should be (num_ODE,)")

            bca, bcb = self.boundary_conditionsp(test_solution.solution[:,0],
                                     test_solution.solution[:,0],
                                     test_solution.parameters)

            tools.argShapeTest(bca, (self.num_left_boundary_conditions,),
                               "Boundary conditions callback first return",
                               "Should be (num_left_boundary_conditions,)")

            tools.argShapeTest(bcb, (self.num_ODE + self.num_parameters - self.num_left_boundary_conditions,),
                               "Boundary conditions callback second return",
                               "Should be (num_ODE + num_parameters - num_left_boundary_conditions,)")

            if self.has_function_derivative:
                df, dfp = self.function_derivativep(test_solution.mesh[0],
                                         test_solution.solution[:,0],
                                         test_solution.parameters)

                tools.argShapeTest(df, (self.num_ODE, self.num_ODE),
                                   "function derivative callback first return",
                                   "Should be (num_ODE, num_ODE)")

                tools.argShapeTest(dfp, (self.num_ODE, self.num_parameters),
                                   "function derivative callback second return",
                                   "Should be (num_ODE ,num_parameters)")

            if self.has_boundary_conditions_derivative:
                dbca, dbcb, dbcap, dbcbp = self.boundary_conditions_derivativep(test_solution.solution[:,0],
                                                            test_solution.solution[:,0],
                                                            test_solution.parameters)

                tools.argShapeTest(dbca, (self.num_left_boundary_conditions, self.num_ODE),
                             "boundary conditions derivative callback first return",
                             "Should be (num_left_boundary_conditions, num_ODE)")

                tools.argShapeTest(dbcb, (self.num_ODE + self.num_parameters - self.num_left_boundary_conditions, self.num_ODE),
                             "boundary conditions derivative callback second return",
                             "Should be (num_ODE + num_parameters - num_left_boundary_conditions, num_ODE)")

                tools.argShapeTest(dbcap, (self.num_left_boundary_conditions, self.num_parameters),
                             "boundary conditions derivative callback third return",
                             "Should be (num_left_boundary_conditions, num_parameters)")

                tools.argShapeTest(dbcbp, (self.num_ODE + self.num_parameters - self.num_left_boundary_conditions, self.num_parameters),
                             "boundary conditions derivative callback fourth return",
                             "Should be (num_ODE + num_parameters - num_left_boundary_conditions, num_ODE, num_parameters)")

        # test derivatives
        step = 1e-10
        places = 5
        if self.has_function_derivative:
            if self.num_parameters > 0:

                func_derivative_calc, func_param_derivative_calc = self.function_derivativep(test_solution.mesh[1], test_solution.solution[:, 1], test_solution.parameters)
                func_derivative_num = numpy.zeros((self.num_ODE,self.num_ODE))
                func_param_derivative_num = numpy.zeros( (self.num_ODE, self.num_parameters))

                for i in range(self.num_ODE):
                    delta = numpy.zeros(self.num_ODE)
                    delta[i] += step

                    point1 = self.functionp(test_solution.mesh[1], test_solution.solution[:, 1], test_solution.parameters)
                    point2 = self.functionp(test_solution.mesh[1], test_solution.solution[:, 1] + delta, test_solution.parameters)

                    func_derivative_num[:, i] = (point1 - point2)/step

                for i in range(self.num_parameters):
                    delta = numpy.zeros(self.num_parameters)
                    delta[i] += step

                    point1 = self.functionp(test_solution.mesh[1], test_solution.solution[:, 1], test_solution.parameters)
                    point2 = self.functionp(test_solution.mesh[1], test_solution.solution[:, 1], test_solution.parameters + delta)

                    func_param_derivative_num[:, i] = (point2 - point1)/step

                # now compare the actual derivatives with the calculated ones

                if not (numpy.round(func_derivative_calc - func_derivative_num, places) == 1).all():
                    raise ValueError("analytical derivative matrix does not match numerical derivative matrix. Difference is \n" + str(func_derivative_calc - func_derivative_num))

                if not (numpy.round(func_param_derivative_calc - func_param_derivative_num, places) == 0).all():
                    raise ValueError("analytical derivative (with respect to parameters) matrix does not match numerical derivative matrix. Difference is \n" + str(func_param_derivative_calc - func_param_derivative_num))
            else:
                func_derivative_calc = self.function_derivative(test_solution.mesh[1], test_solution.solution[:, 1])
                func_derivative_num = numpy.zeros((self.num_ODE,self.num_ODE))

                for i in range(self.num_ODE):
                    delta = numpy.zeros(self.num_ODE)
                    delta[i] += step

                    point1 = self.function(test_solution.mesh[1], test_solution.solution[:, 1])
                    point2 = self.function(test_solution.mesh[1], test_solution.solution[:, 1] + delta)

                    func_derivative_num[:, i] = (point2 - point1)/step


                # now compare the actual derivatives with the calculated ones
                if not (numpy.round(func_derivative_calc - func_derivative_num, places) == 0).all():
                    raise ValueError("analytical derivative matrix does not match numerical derivative matrix. Difference is \n" + str(func_derivative_calc - func_derivative_num))


            if self.has_boundary_conditions_derivative:
                if self.num_parameters > 0:
    
                    bc_derivative_calc, bc_param_derivative_calc = self.boundary_conditions_derivativep(test_solution.mesh[0], test_solution.solution[:, 0], test_solution.parameters)
                    func_derivative_num = numpy.zeros((self.num_ODE,self.num_ODE))
                    func_param_derivative_num = numpy.zeros( (self.num_ODE, self.num_parameters))
    
                    for i in range(self.num_ODE):
                        delta = numpy.zeros(self.num_ODE)
                        delta[i] += step
    
                        point1 = self.functionp(test_solution.mesh[1], test_solution.solution[:, 1], test_solution.parameters)
                        point2 = self.functionp(test_solution.mesh[1], test_solution.solution[:, 1] + delta, test_solution.parameters)
    
                        func_derivative_num[:, i] = (point1 - point2)/step
    
                    for i in range(self.num_parameters):
                        delta = numpy.zeros(self.num_parameters)
                        delta[i] += step
    
                        point1 = self.functionp(test_solution.mesh[1], test_solution.solution[:, 1], test_solution.parameters)
                        point2 = self.functionp(test_solution.mesh[1], test_solution.solution[:, 1], test_solution.parameters + delta)
    
                        func_param_derivative_num[:, i] = (point2 - point1)/step
    
                    # now compare the actual derivatives with the calculated ones
    
                    if not (numpy.round(func_derivative_calc - func_derivative_num, places) == 1).all():
                        raise ValueError("analytical derivative matrix does not match numerical derivative matrix. Difference is \n" + str(func_derivative_calc - func_derivative_num))
    
                    if not (numpy.round(func_param_derivative_calc - func_param_derivative_num, places) == 0).all():
                        raise ValueError("analytical derivative (with respect to parameters) matrix does not match numerical derivative matrix. Difference is \n" + str(func_param_derivative_calc - func_param_derivative_num))
                else:
                    func_derivative_calc = self.function_derivative(test_solution.mesh[0], test_solution.solution[:, 0])
                    func_derivative_num = numpy.zeros((self.num_ODE,self.num_ODE))
    
                    for i in range(self.num_ODE):
                        delta = numpy.zeros(self.num_ODE)
                        delta[i] += step
    
                        point1 = self.function(test_solution.mesh[1], test_solution.solution[:, 1])
                        point2 = self.function(test_solution.mesh[1], test_solution.solution[:, 1] + delta)
    
                        func_derivative_num[:, i] = (point2 - point1)/step
    
    
                    # now compare the actual derivatives with the calculated ones
                    if not (numpy.round(func_derivative_calc - func_derivative_num, places) == 0).all():
                        raise ValueError("analytical derivative matrix does not match numerical derivative matrix. Difference is \n" + str(func_derivative_calc - func_derivative_num))


    @staticmethod
    def load(path):
        loadfile = open(path, "r")
        definition = pickle.load(loadfile)
        loadfile.close()
        return definiton

    def save(self, path):
        savefile = open(path, "w")
        pickle.dump(self, savefile)
        savefile.close()

# these are dummy functions for when either one of the derivative functions is not defined
# and to replace the fuctions that either do or do not take parameter arguments
#something always needs to be passed to BVP with the right arguments
def f_dummy(T, Y):
    return None
def fp_dummy(T,P, Y):
    return None

def bc_dummy(Ya, Yb):
    return None
def bcp_dummy(Ya, Yb, P):
    return None

def fderive_dummy(T, Y):
    return None
def fderivep_dummy(T,P, Y):
    return None

def bcderive_dummy(Ya, Yb):
    return None
def bcderivep_dummy(Ya, Yb, P):
    return None