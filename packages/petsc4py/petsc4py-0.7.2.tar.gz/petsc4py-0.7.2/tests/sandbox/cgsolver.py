from petsc.PETSc import *

class CG:
    """Conjugate Gradient Solver.
    
    creation:  solver = CG(A,b,x)
    
    solution:  solver.solve()   -> automatic
               solver.step(n=1) -> interactive

    options:   maxit
               tol
               rescalc
               monitor

    functions: converged()
               view()
               reset()
               clean()"""
    
    # constructor
    def __init__(self, matrix, rhs, solution = None):

        # check matrix an rhs
        m,n = matrix.GetSize()
        if m != n : raise ValueError, 'Matrix is not square'

        n = rhs.GetSize()
        if m != n : raise ValueError, 'Matrix and RHS have incompatible sizes.'
        
        self.matrix = matrix
        self.rhs    = rhs
        self.size   = n;
        
        if solution == None :
            self.solution = self.rhs.Duplicate();
            self.solution.Set(0)
        else:
            try:
                assert(solution.GetSize()==self.size)
                self.solution = solution;
            except AssertionError:
                self.solution = self.rhs.Duplicate()
                self.solution.Set(0)
                print 'Warning: Solution has incompatible size. Discarded'

        self.default()
        self.reset()
        self.clean()

        
    # default options
    def default(self):
        "Set CG Solver default options."
        
        # convergence control
        self.maxit  = min(100,self.rhs.GetSize()) # max iteration
        self.tol    = 1e-6     # relative residual norm tolerance
    
        # options
        self.rescalc = False  # residual calculation
        self.monitor = False  # print convergence


    # init/reset data members
    def reset(self):
        "Initialize (or Reset) CG Solver data."
        
        # convergence info
        self.iter    = 0     # iteration count
        self.relres  = 0     # relative residual norm
        self.rhsnorm = 0     # right hand side norm
        self.resnorm = []    # residual norms

        # scalars
        self.alpha = 0
        self.beta  = 0
        self.delta = 0

        # flags
        self.__setup_called = False
        self.__converged    = False

    def clean(self):
        "Clean CG Solver work data."
        # work data
        self.residual  = None  # residual           
        self.searchdir = None  # search direction   
        self.projdir   = None  # projected direction

    def __makeworkvecs(self):
        if self.residual == None :
            self.residual = self.rhs.Duplicate();
        if self.searchdir == None :
            self.searchdir = self.rhs.Duplicate();
        if self.projdir == None :
            self.projdir = self.rhs.Duplicate();

    def __chkconv(self):
        if self.relres < self.tol :
            self.__converged = True
        else:
            self.__converged = False

    def __monitor(self):
        if self.monitor : self.view()


    def view(self):
        print '[CG Solver]  iter: %3d, relres: %9.3e, converged: %s' %\
              (self.iter, self.relres, self.converged())

    def converged(self):
        return self.__converged


    def solve(self):
        "Solve linear system (AUTO mode)."
        
        self.reset()
        self.__makeworkvecs()
        
        # A*x = b          # work vectors    
        A = self.matrix;    r = self.residual;
        b = self.rhs;       d = self.searchdir;
        x = self.solution;  q = self.projdir;
        
        # if b == 0, then x = 0
        b_norm = b.Norm()
        if b_norm == 0 :
            x.Set(0)
            self.rhsnorm = 0
            self.relres  = 0
            self.resnorm = [ 0 ]
            self.__converged = True
            self.__monitor()
            return
           
        # initial residual
        A.Mult(x,r) 
        r.AYPX(-1,b)     
        r_norm = r.Norm()

        self.rhsnorm = b_norm
        self.relres  = r_norm / b_norm
        self.resnorm = [ r_norm ]
    
        # check if initial guess
        #is good enough solution
        self.__chkconv()
        self.__monitor()        
        if self.converged() : return
            
        self.delta = r_norm**2

        # initial search direction
        r.Copy(d) 

        # loop over maxit iterations
        # unless convergence o failure
        for self.iter in range(1,self.maxit+1):

            self.__pre_step()

            self.__chkconv()
            self.__monitor()
            if self.converged() : break

            self.__post_step()



    def step(self,iters=1):
        "CG Solver in STEP mode."
        
        if self.__setup_called == False :
            self.__setup()
            if iters == 0 :
                return

        if iters == 0 :
            self.__monitor()
            return
        
        self.iter += 1
        
        for self.iter in range(self.iter,self.iter+iters):
            self.__pre_step()
            self.__chkconv()
            self.__monitor()
            self.__post_step()


    def __setup(self):

        self.reset()
        self.__makeworkvecs()
 
        A = self.matrix
        b = self.rhs
        x = self.solution
        r = self.residual
        d = self.searchdir
        
        A.Mult(x,r) 
        r.AYPX(-1,b)     
        r.Copy(d)

        r_norm = r.Norm()
        b_norm = b.Norm()
        
        self.rhsnorm = b_norm
        self.relres  = r_norm / b_norm
        self.resnorm.append(r_norm)
    
        self.delta = r_norm**2

        self.__setup_called =  True
        self.__chkconv()
        self.__monitor()


    def __pre_step(self):
        A = self.matrix;    r = self.residual;  
        b = self.rhs;       d = self.searchdir; 
        x = self.solution;  q = self.projdir;

        # update projdir
        A.Mult(d,q)  # q <= A*d

        # update solution
        self.alpha = self.delta / d.Dot(q)
        x.AXPY(self.alpha,d)  # x <= alpha*d + x

        # update residual
        if self.rescalc:
            r.AXPY(-self.alpha,q)  # r <= -alpha*q + r
        else:
            A.Mult(x,r)
            r.AYPX(-1,b)  # r <= b - A*x
        r_norm = r.Norm()
        self.relres = r_norm / self.rhsnorm
        self.resnorm.append(r_norm)
        

    def __post_step(self):
        r = self.residual
        d = self.searchdir

        # update searchdir
        delta_old = self.delta
        self.delta = self.resnorm[self.iter]**2
        self.beta = self.delta/delta_old
        d.AYPX(self.beta,r)  # d = beta*d + r
