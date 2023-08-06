"""Implements basic operations for data treatment
"""

def window(data, xmin, xmax, col=0):
    """Return a subset of the data, clipping the first column
    """

    return filter(lambda x: x[col] >= xmin and x[col]<= xmax, data)


def maxcol(data, col=0):
    return max([row[col] for row in data])


def mincol(data, col=0):
    return min([row[col] for row in data])


def subs(data, col=0, y0=None):
    """Substracts an offset value from yy
    """

    newdata = data
    if y0 == None:
        y0 = mincol(data, col)
    for row in newdata:
        row[col] -= y0 
    return newdata


def norm(data, col=0, yn=1):
    """Normalizes data[col] to the value yn
    """
    ymax = maxcol(data, col)
    newdata = data
    for row in newdata:
        row[col] *= yn/ymax
    return newdata


def integrate(xx, yy):
    """Returns the integral of xx, yy using the trapezoid rule
    """
    nn = len(xx)
    if nn == 0:
        raise IndexError

    zz = [0.]*nn
    for i in range(1, nn):
        zz[i] = zz[i-1]+0.5*(yy[i]+yy[i-1])*(xx[i]-xx[i-1])
    return zz


