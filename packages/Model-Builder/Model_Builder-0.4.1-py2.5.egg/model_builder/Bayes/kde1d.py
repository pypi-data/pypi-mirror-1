# -*- coding:iso8859-1 -*-
#-----------------------------------------------------------------------------
# Name:        kde1d.py
# Purpose:     Univariate Kernel density estimator
#
# Author:      Flávio Codeço Coelho
#
# Created:     2003/22/12
# RCS-ID:      $Id: kde1d.py $
# Copyright:   (c) 2003
# Licence:     GPL
# New field:   Whatever
#-----------------------------------------------------------------------------
#from FFT import *
#from MLab import *
#from cmath import *
#from crat import *

from RandomArray import *



def KDE(x, A, k='knorm', h=0):
    """
    performs the kernel density estimation and returns (y,h) where y 
    is the KDE for each point of x
    x is a vector containing the points at which the estimates are to be calculated
    A contains the data
    h is window width will be optimal if not specified. 
    k is the kernel for the estimation: 
    'KNORM' Univariate Normal
    'KEPAN' epanechnikov kernel 
    'KBIWE' Bi-weight kernel 
    'KTRIA' triangular kernel 
    'KRECT' Rectangular Kernel
    """
    n = len(A)
    
    if h == 0:
        h= hste(A,k) #calculate optimal window size
    if k == 'knorm':
        soma = knorm((x-A*ones(len(x), Float))/h)
    
        for i in xrange(2,n): #Sum Over all data points
            soma += knorm((x-A[i]*ones(len(x), Float))/h)
        
        y = soma/(n*h)
    
    return [y,h]

def hste(A,k):
    """
    Solve the equation Estimate of h
    A is data 
    k is kernel type 
    returns h 
    """
    
    n = len(A)
    inc = 512.
    if k == 'knorm':
        R = 1/(2*sqrt(pi))
        mu2 = 1
        r = 4
    
    P = inc*2
    
    xmin = min(A)
    xmax = max(A)
    rangex = xmax-xmin
    
    if siqr(A) > 0:
        s = min([std(A), siqr(A)/1.34])
    else:
        s = std(A)
    
    ax = xmin-rangex/8.
    bx = xmax+rangex/8.
    
    xa = linspace(ax,bx,inc) #x axis vector, i.e. where the kernel density function will be evaluated
    
    c = zeros(int(inc), Float)
    deltax = (bx-ax)/float((inc-1))
    binx = (floor((A-ax)/deltax)+1).astype(Int)
    
    #obtain the grid counts
    
    for i in xrange(n):
        c[binx[i]] = c[binx[i]]+(xa[binx[i]+1]-A[i])/deltax
        c[binx[i]+1] = c[binx[i]+1]+(A[i]-xa[binx[i]])/deltax
        
    psi6 = -15/(16*sqrt(pi)*s**7)
    psi8 = 105/(32*sqrt(pi)*s**9)
    
    k40 = deriv(0,k)[0]
    
    g1 = (-2*k40/(mu2*psi6*n))**(1./7.)
    
    [k40,k60] = deriv(0,k)[:2]
    
    g2 = (-2*k60/(mu2*psi8*n))**(1./9)
    
    #estimate psi6
    
    #obtain the kernel weights
    
    [kw4,kw6] = deriv((bx-ax)*arange(inc)/((inc-1)*g2),k)[:2]
    
    #apply 'fftshift' to kw
    
    
    kw= concatenate((kw6,zeros(1),kw6[int(inc-1):0:-1]),1)
    
    #perform the convolution
  
    #z = inverse_real_fft(fft(c,P)*fft(kw))
    z = convolve(ravel(c),kw)
    
    psi6 = sum(c*z[:int(inc)])/(n*(n-1)*g2*7)
    psi6 = sum(psi6)
    
    #Now estimate psi4
    
    #obtain the kernel weights
    
    kw4 = deriv((bx-ax)*arange(inc)/((inc-1)*g1),k)[0]
    
    #apply 'fftshift' to kw
    
    kw = concatenate((kw4,zeros(1),kw4[int(inc)-1:0:-1]),1)
    
    #perform the convolution
    
    #z = inverse_real_fft(fft(c,P)*fft(kw))
    z = convolve(ravel(c),kw)

    psi4 = sum(c*z[:int(inc)])/(n*(n-1)*g1**5)
    psi4 = sum(psi4)
    
    ho = 0.
    
    h=hns(A,k)
    
    k40 = deriv(0,k)[0]
    
    while abs(ho-h)/abs(h) > 0.01:
        temp = h
        gamma = ((2*k40*mu2*psi4*h**5)/(-psi6*R))**(1/7.)
        
        #now estimate psi4
        #Obtain the kernel weights
        t = (bx-ax)*arange(inc)/((inc-1)*gamma)
        kw4 = deriv(t,k)[0]
        #Apply 'fftshift' to kw
        kw = concatenate((kw4,zeros(1),kw4[int(inc)-1:0:-1]),1)
        #perform the convolution
        #z = inverse_real_fft(fft(c,P)*fft(kw))
        z = convolve(ravel(c),kw)
        #print c.shape,kw.shape
        num = c*z[:int(inc)]
        p4 = sum(num)/(n*(n-1)*gamma**5)
        
        h = mu2**(-2/5.)*R**(1/5.)*(p4*n)**(-1/5.)
        #print abs(ho-h)/abs(h)
        ho = temp
        
    return h
        
    

def hns(A,k):
    """
    Basic Normal Scale estimate of Smoothing Parameter.
    A is the data, k is the kernel type. 
    
    This function evaluates an 'optimal' value of h for use with univariate data A and kernel k. 
    'KNORM' Univariate Normal; 
    'KEPAN' epanechnikov kernel; 
    'KBIWE' Bi-weight kernel; 
    'KTRIW' is the tri-weight kernel; 
    'KTRIA' triangular kernel; 
    'KRECT' Rectangular Kernel; 
    'KLAPL' Laplace kernel; 
    'KLOGI' Logistic kernel. 
    """
    n = len(A)
    if k == 'knorm':
        a = 1.0592
    elif k == 'kepan':
        a = 2.34
    elif k =='kbiwe':
        a = 2.7779
    elif k == 'ktria':
        a = 2.5760
    elif k == 'krect':
        a = 1.8431
    elif k == 'klapl':
        a = 0.7836
    elif k == 'ktriw':
        a = 3.1545
    elif k == 'klogi':
        a = 0.5921
    
    if siqr(A) > 0:
        s = min((std(A), siqr(A)/1.34))
    else:
        s = std(A)
    
    h = a*s*n**(-1/5.)
    
    return h

def siqr(x):
    """
    Calculates the sample interquartile range of x
    """
    n = len(x)
    
    order = sort(x)
    
    mlo = int(ceil(n/4.))
    mhi = int(ceil(3*n/4.))
    
    if mlo > 0 & mlo < n:
        zlo = (order[mlo]+order[mlo+1])/2.
    
    if mhi > 0 & mhi < n:
        zhi = (order[mhi]+order[mhi+1])/2.
    
    y = zhi-zlo
    
    return y
    
    
def deriv(t,k):
    """
    4th, 6th, 8th and 10th derivative of the Normal kernel
    
    This function finds the derivatives kernel k at point t.
    (only normal kernel )
    """
    if k == 'knorm':
        
        y4 = (t**4-6*t**2+3)*exp(-0.5*t**2)/sqrt(2*pi)
        y6 = (t**6-15*t**4+45*t**2-15)*exp(-0.5*t**2)/sqrt(2*pi)
        y8 = (t**8-28*t**6+210*t**4-420*t**2+105)*exp(-0.5*t**2)/sqrt(2*pi)
        y10 = (t**10-45*t**8+630*t**6-3150*t**4+4725*t**2-945)*exp(-0.5*t**2)/sqrt(2*pi)
        
    return (y4,y6,y8,y10)

def knorm(x,y=None,z=None):
    """
    Uni-, Bi- or Tri-variate Normal density function
    """
    if z != None:
        s = x*x+y*y+z*z
        d = 3
    elif y != None:
        s = x*x+y*y
        d = 2
    else:
        s = x*x
        d = 1
    
    
    k = (2*pi)**(-d/2.)*exp(-0.5*s)
    
    return k
    
    

if __name__ == '__main__':
    import matplotlib
    matplotlib.use('WX')
    from pylab import *
    
    A = normal(.5,1,5000)
    x = arange(-5,5,0.002)
    [y,h] = KDE(x,A)
    nb, bins, patches = hist(A, bins=20, normed=1)
    plot(x,y,'r-o')
    
    show()
