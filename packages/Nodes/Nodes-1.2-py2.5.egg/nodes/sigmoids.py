"""C functions."""
#from math import exp, fabs
from numpy import exp, fabs

def sigmoid(x):
	return 1/(1+exp(-x))

def msigmoid(x):
	return 1/(1+exp(-(2.5*x)**2))

def dsigmoid(x):
	return exp(-x)/(1+exp(-x))**2

def dmsigmoid(x):
	exponent=exp((2.5*x)**2)
	return (12.5*exponent*x)/((1+exponent)**2)

dblsigmoid=lambda x: (2*exp(x))/(1+exp(x))

# ok, less voodoo..
def mutability(x):
	return fabs(dmsigmoid(x))
def believing(x):
	return dsigmoid(x)*4
def keyness(x):
	return dblsigmoid(x)*dsigmoid(x)

