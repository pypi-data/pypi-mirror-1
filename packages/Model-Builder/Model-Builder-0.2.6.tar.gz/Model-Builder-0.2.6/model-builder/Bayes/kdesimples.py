from pylab import *
from RandomArray import *
import sys

def kde(x,h=None,positive=0,kernel=1):
    """
    """
    n = len(x)
    if not h:
        h = 1.06*std(x)*n**(-1/5.)
    if positive and any(x<0):
        sys.exit('there is a negative element in x')
    mn1 = min(x)
    mx1 = max(x)
    mn = mn1 - (mx1-mn1)/3.
    mx = mx1 + (mx1-mn1)/3.
    gridsize = 256
    xx = linspace(mn,mx,gridsize)
    d = xx[1] - xx[0]
    xh = zeros(size(xx))
    xa = (x-mn)/(mx-mn)*float(gridsize)
    for i in xrange(n):
        i1 = int(floor(xa[i]))
        a = xa[i]-i1
        xh[i1:i1+2]+=[1-a,a]
    xh = array(xh)
    print xh
    #compute
    
    xk = arange(-gridsize,gridsize-1)*d
    if kernel == 1:
        K= exp(-0.5*(xk/h)**2)
    
    
    K = K/(sum(K)*d*n)
    K = concatenate((K,zeros(1),K[gridsize-1:0:-1]),1)
    f = convolve(ravel(xh),K)
    print K.shape
    f=f[:gridsize]
    return f,xx

if __name__=='__main__':
    x = normal(.5,1,5000)
    f,xx = kde(x)
    #hist(x, normed=1)
    plot(xx,f,'r-o')
    show()