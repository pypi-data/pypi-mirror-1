
"""
NUMDIFFTOOLS
===========
 Suite of tools to solve automatic numerical differentiation
 problems in one or more variables. All of these methods also 
 produce error estimates on the result.
 A pdf file is also provided to explain the theory behind these tools.
 
 To test if the toolbox is working paste the following in an interactive python session: 
    import numdifftools as nd
    nd.test(coverage=True)

 Derivative:
 -----------
 A flexible tool for the computation of derivatives of order 1 through 4
 on any scalar function. Finite differences are used in an adaptive manner,
 coupled with a Romberg extrapolation methodology to provide a maximally
 accurate result. The user can configure many of the options, changing
 the order of the method or the extrapolation, even allowing the user to
 specify whether central, forward or backward differences are used.

 Gradient
 --------
 Computes the gradient vector of a scalar function of one or more variables
 at any location.

 Jacobian
 --------
 Computes the Jacobian matrix of a vector (or array) valued function of
 one or more variables.

 Hessian
 -------
 Computes the Hessian matrix of all 2nd partial derivatives of a scalar
 function of one or more variables.

 Hessdiag
 --------
 The diagonal elements of the Hessian matrix are the pure second order
 partial derivatives. 
 
 See also
 --------
 scipy.misc.derivative

"""