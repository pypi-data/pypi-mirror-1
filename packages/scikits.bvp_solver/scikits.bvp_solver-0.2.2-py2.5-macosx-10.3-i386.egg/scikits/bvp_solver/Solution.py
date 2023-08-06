import numpy
import tools
import bvp_solverf
import pickle

class Solution:
    """

    """
    def __init__(self,
                 mesh,   #the current mesh
                 solution,   #the current solution
                 parameters = None,
                 work = None,
                 iwork = None,
                 yerror = None,
                 successIndicator = None,
                 extended = False):
        """
        """
        self.mesh = tools.preparg(mesh)
        self.solution = tools.preparg(solution)
        self.parameters = tools.preparg(parameters)
        self.work = tools.preparg(work)
        self.iwork = tools.preparg(iwork)
        self.yerror = yerror
        self.successIndicator = successIndicator
        self.extended = extended

    def __call__(self, points, eval_derivative = False):
        """
        Calculates the approximate solution and optionally the first derivative at a vector of points.
            arguments:
                points - vector of points where the solution and derivative should be calculated
                [eval_derivative - (logical) determines whether the first derivative should be returned]
            returns
                approximateSolution - vector of the approximate solution. Variable index is first, point index is second.
                [derivative - vector of the first derivative to the approximate solution. Variable index is first, point index is second.]
        """
        if self.successIndicator == -1:
            raise ValueError("Solution is the result of computation error, cannot evaluate")

        if self.extended == True:
            raise ValueError("""this solution is the result of extending a previous solution and cannot be evaluated.
             If you really want to know what the solution looks like, look at .mesh and .solution""")

        # if any of the points are more than a certain tolerance outside of the bounds, something has gone wrong
        tol = 1e-12
        dist = tol * (self.mesh[-1] - self.mesh[0])
        if (points < self.mesh[0] - dist).any() or (points > self.mesh[-1] + dist).any():
            raise ValueError("some points are outside the bounds of the solution")

        npar = 0
        if not (self.parameters is None):
            npar = len(self.parameters)

        bvp_solverf.bvp.bvp_eval_wrap(eval_derivative = eval_derivative,
                        points = tools.farg(points),
                        node_in = self.solution.shape[0],
                        npar_in = npar,
                        leftbc_in = 1, # this value doesn't matter
                        npts_in = len(self.mesh),
                        info_in = self.successIndicator,
                        mxnsub_in = 300, # nor does this
                        x_in = tools.farg(self.mesh),
                        y_in = tools.farg(self.solution),
                        parameters_in = tools.farg(self.parameters),
                        work_in = tools.farg(self.work),
                        iwork_in = tools.farg(self.iwork))

        #would prefer not to copy arrays here
        # but the results end up getting screwed up when this function is called again for some other purpose
        # this is probably because the old arrays "deallocated" by Fortran

        if eval_derivative:
            return bvp_solverf.bvp.evaluated.copy(), bvp_solverf.bvp.evaluated_d.copy()
        else:
            return bvp_solverf.bvp.evaluated.copy()


    def extend(self, new_left, new_right, order = 0, new_parameters = None):
        """
        """
        new_parameters = tools.preparg(new_parameters)
        if new_parameters is None:
            new_parameters = self.parameters

        npar = 0
        if not (self.parameters is None):
            npar = len(self.parameters)

        bvp_solverf.bvp.bvp_extend_wrap(node_in = self.solution.shape[0],
                                        npar_in = npar,
                                        leftbc_in = 1, # this value doesn't matter
                                        npts_in = len(self.mesh),
                                        info_in = self.successIndicator,
                                        mxnsub_in = 300, # nor does this
                                        x_in = tools.farg(self.mesh),
                                        y_in = tools.farg(self.solution),
                                        parameters_in = tools.farg(self.parameters),
                                        work_in = tools.farg(self.work),
                                        iwork_in = tools.farg(self.iwork),
                                        anew = new_left,
                                        bnew = new_right,
                                        order = order,
                                        p = tools.farg(new_parameters),
                                        max_num_subintervals = 300  # nor does this
                                        )

        result = self.from_arg_list(bvp_solverf.bvp)
        result.extended = True
        return result

    @staticmethod
    def from_arg_list( bvp_object):
        """
        Gets the results of the fortran code from the fortran object, and returns a Soltuion object created from them.
        This is necessary because 2d arrays cannot be passed back to Python so the fortran code must
        store the results in a temporary area where we can get them later.
        """

        #would prefer not to copy arrays here
        # but the results end up getting screwed up when this function is called again for some other purpose
        # this is probably because the old arrays "deallocated" by Fortran

        new = Solution(mesh = tools.fromf(bvp_object.x),
                      solution = tools.fromf(bvp_object.y),
                      parameters = tools.fromf(bvp_object.parameters),
                      work = tools.fromf(bvp_object.work),
                      iwork = tools.fromf(bvp_object.iwork),
                      yerror = bvp_object.yerror,
                      successIndicator = bvp_object.info)
        return new

    @staticmethod
    def load(path):
        """
        Loads a Solution object from the file at the given path.
        """
        loadfile = open(path, "r")
        solution = pickle.load(loadfile)
        loadfile.close()
        return solution

    def save(self, path):
        """
        Saves the Solution object to a file given by the path.
        """
        savefile = open(path, "w")
        pickle.dump(self, savefile)
        savefile.close()