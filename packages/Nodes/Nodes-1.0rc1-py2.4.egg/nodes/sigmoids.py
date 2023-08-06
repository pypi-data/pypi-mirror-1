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

def dblsigmoid(x):
	return (2*exp(x))/(1+exp(x))

	
