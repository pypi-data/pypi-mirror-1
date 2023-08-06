"""
Contain utilities for reading numerical data from file
"""

def parserow(row):
    """return the numerical values from a string
    """

    if row[0] == '#':
        return None
    else:
        return [float(w) for w in row.split()]


def parsecolstring(cols):
    """given a string in the format "c1:c2:..." return an index
    list [c1-1, c2-1...]
    """

    return [int(c)-1 for c in cols.split(':')]


def parselist(mylist, cols):
    """return the elements given in the string cols (c1:c2:c3...)
    """

    cols = parsecolstring(cols)
    return [mylist[c] for c in cols]


def extractcols(data, cols):
    """return selected columns from a list of rows
    """
    
    return [parselist(row, cols) for row in data]
    

def readcols(input, cols=None):
    """return numerical columns from an inputsource
    """

    data = []
# Note to self: the whole file is read at the beginning of the loop
    for row in input:
        p = parserow(row)
        if p is not None and p != []:
            if cols == None:
                data.append(p)
            else:
                data.append(parselist(p, cols))
    return data


def writecols(output, data):
    """Write a list of rows to output
    """

    for row in data:
        st = ""
        for cell in row:
            st += "%e " % cell
        output.write(st[:-1]+'\n')



