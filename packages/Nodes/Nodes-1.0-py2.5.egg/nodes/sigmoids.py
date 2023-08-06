"""C functions."""
#from math import exp, fabs
from numpy import exp, fabs
sigmoid=lambda x: 1/(1+exp(-x))

msigmoid=lambda x: 1/(1+exp(-(2.5*x)**2))

dsigmoid=lambda x: exp(-x)/(1+exp(-x))**2

def dmsigmoid(x):
	exponent=exp((2.5*x)**2)
	return (12.5*exponent*x)/((1+exponent)**2)

dblsigmoid=lambda x: (2*exp(x))/(1+exp(x))

# ok, less voodoo..
mutability=lambda x: abs(dmsigmoid(x))
believing=lambda x: dsigmoid(x)*4
keyness=lambda x: dblsigmoid(x)*dsigmoid(x)/2

