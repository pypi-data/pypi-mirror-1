"""Window means"""

try:
    import numpy as N
except:
    try:
        import numarray as N
    except:
        import Numeric as N

#Probalblly not the best place to put it, but to temporally resolve my problem!


def window_mean(y,x=None,x_out=None,method="rectangular",boxsize=None):
    """Windowed means along 1-D array
    
    Input:
        - x [0,1,2,3,...] =>
        - x_out [x] =>
        - method [rectangular]:
            + rectangular => All data in window have same weight
        - boxsize [mean space] =>
    Output:

    Apply windowed means on a 1-D data array. Selecting adequate x_out
    and boxsize could define boxmeans or smooth filters. Method defines
    the weight method.

    An important point of this function is the ability to work with 
    unhomogenious spaced samples. Data ([1,2,3]) colected at [1,2,4] 
    times would be different if was collected at [1,2,3].
    """
    if(x==None):
        x=N.arange(N.size(y))

    if(x_out==None):
        x_out=x

    y_out = N.zeros(N.size(x_out),N.Float)

    if(boxsize==None):
        # !!! Improve it! A better way than *1. ?!
        boxsize =(max(x)-min(x))/(N.size(x_out)*1.)

    half_boxsize = boxsize/2.

    #for x_i in x_out:
    for i in range(N.size(x_out)):
        x_i = x_out[i]

        
        # Higher window limit
        hi_limit = x_i+half_boxsize
        # Lower window limit
        lo_limit = x_i-half_boxsize
        # index of values inside window
        index = N.less_equal(x,hi_limit)*N.greater_equal(x,lo_limit)

        # !!! INSERT some type of check for minimum number of samples to be considered
        
        # x values on window around x_i
        x_tmp = N.compress(index,x)-x_i
        # y values on window
        y_tmp = N.compress(index,y)

        # weights in window according to x position
        weight = window_weight(x_tmp,boxsize,method)

        y_out[i] = N.sum(y_tmp*weight)
    
    return y_out

def window_weight(x,boxsize=None,method="rectangular"):
    """Window weights
    """

#    # Size of the window
#    n=N.size(x)
#    print
    
    if(method=="rectangular"):
        # Weight of window points
        weight = N.ones(N.shape(x),N.Float)

    # Need to develop this triangular form!
    elif(method=="triangular"):
        half_size = boxsize/2.

        # Resolving left side of triangle
        left = N.less_equal(x,0)*(x+half_size)
        # Resolving right side of triangle
        right = N.greater(x,0)*(half_size-x)
        weight = left + right
        
    else:
        return

    # Normalized weight
    weight = weight/N.sum(weight)

    return weight
