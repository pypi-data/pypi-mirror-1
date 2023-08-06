from scipy import interpolate

def linearInterp1D(x,y,x_new):
    """ Linear 1D interpolation."""

    f = interpolate.interp1d(x,y)
    y_new = f(x_new)
    return y_new


def splineInterp1D(x,y,x_new):
    """ Spline 1D interpolation."""

    tck = interpolate.splrep(x,y,s=0)
    y_new=interpolate.splev(x_new,tck,der=0)
    return y_new


if __name__ == '__main__': ## example to show
    #spline x_new can be wider than x, but should be increasing array.
    x = arange(0,-10,-1)
    y = exp(-x/3.0)
    x=x[::-1];y=y[::-1]
    x_new = arange(0,-12,-1)
    x_new = x_new[::-1]
    y_new = splineInterp1D(x,y,x_new)
#    plot (x,y,'ro',x_new,y_new,'b-')
#    show()