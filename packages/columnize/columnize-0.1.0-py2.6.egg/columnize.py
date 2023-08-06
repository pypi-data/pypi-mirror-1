# -*- coding: utf-8 -*-
"""Return compact set of columns as a string with newlines for an
array of strings.

Adapted from the routine of the same name inside cmd.py"""
import types

def columnize(array, displaywidth=80, colsep = '  '):
    """Return a list of strings as a compact set of columns.

    For example, for a line width of 4 characters:
        ['1', '2,', '3', '4'] => '1  3\n2  4\n'
    
    Each column is only as wide as necessary.  By default, columns are
    separated by two spaces - one was not legible enough. Set `colsep' to 
    adjust the string separate columns. Set `displaywidth' to set the
    line width.
    """
    if not isinstance(array, list) and not isinstance(array, tuple): 
        raise TypeError, (
            'array needs to be an instance of a list or a tuple')

    nonstrings = [i for i in range(len(array))
                    if not isinstance(array[i], str)]
    if nonstrings:
        raise TypeError, ("array[i] not a string for i in %s" %
                          ", ".join(map(str, nonstrings)))

    # Some degenerate cases
    size = len(array)
    if 0 == size: 
        return "<empty>\n"
    elif size == 1:
        return '%s\n' % str(array[0])

    # Try every row count from 1 upwards
    for nrows in range(1, len(array)):
        ncols = (size+nrows-1) // nrows
        colwidths = []
        totwidth = -len(colsep)
        for col in range(ncols):
            # get max column width for this column
            colwidth = 0
            for row in range(nrows):
                i = row + nrows*col # [rows, cols]
                if i >= size:
                    break
                x = array[i]
                colwidth = max(colwidth, len(x))
            colwidths.append(colwidth)
            totwidth += colwidth + len(colsep)
            if totwidth > displaywidth:
                break
            pass
        if totwidth <= displaywidth:
            break
        pass
    else:
        nrows = len(array)
        ncols = 1
        colwidths = [0]
        pass

    # The smallest number of rows computed and the
    # max widths for each column has been obtained.
    # Now we just have to format each of the
    # rows.
    s = ''
    for row in range(nrows):
        texts = []
        for col in range(ncols):
            i = row + nrows*col
            if i >= size:
                x = ""
            else:
                x = array[i]
            texts.append(x)
        while texts and not texts[-1]:
            del texts[-1]
        for col in range(len(texts)):
            texts[col] = texts[col].ljust(colwidths[col])
            pass
        s += "%s\n" % str(colsep.join(texts))
        pass
    return s

# Demo it
if __name__=='__main__':
  #
  print columnize([])
  print columnize(['1', '2', '3', '4'], 4)
  print columnize(["a", '2', "c"], 10, ', ')
  print columnize(["oneitem"])
  print columnize(("one", "two", "three",))
  print columnize([
                  "one", "two", "three",
                  "4ne", "5wo", "6hree",
                  "7ne", "8wo", "9hree",
                  "10e", "11o", "12ree",
                  "13e", "14o", "15ree",
                  "16e", "17o", "18ree",
                  "19e", "20o", "21ree",
                  "22e", "23o", "24ree",
                  "25e", "26o", "27ree",
                  "28e", "29o", "30ree",
                  "31e", "32o", "33ree",
                  "34e", "35o", "36ree",
                  "37e", "38o", "39ree",
                  "40e", "41o", "42ree",
                  "43e", "44o", "45ree",
                  "46e", "47o", "48ree",
                  "one", "two", "three"])

  try:
      print columnize(5)
  except TypeError, e:
      print e

  try:
      # We don't str the array, probably in the future we should
      print columnize(range(4))
  except TypeError, e:
      print e
