#!/usr/bin/env python

"""
A simple example of parallel computation.
"""

import pprocess
import time

# Array size and a limit on the number of processes.

N = 100
limit = 10

def make_array(n):

    "Make an 'n' * 'n' array initialised with zeros."

    return [list(x) for x in [(0,) * n] * n]

def calculate(ch, i, j):

    """
    A time-consuming calculation, using 'ch' to communicate with the parent
    process, with 'i' and 'j' as operands.
    """

    time.sleep(1)
    ch.send((i, j, i * N + j))

class MyExchange(pprocess.Exchange):

    "Parallel convenience class containing the array assignment operation."

    def store_data(self, ch):
        i, j, result = ch.receive()
        self.D[i][j] = result

# Main program.

if __name__ == "__main__":

    # Initialise the communications exchange with a limit on the number of
    # channels/processes.

    exchange = MyExchange(limit=limit)

    # Initialise an array - it is stored in the exchange to permit automatic
    # assignment of values as the data arrives.

    exchange.D = make_array(N)

    # The parallel computation.

    print "Calculating..."
    for i in range(0, N):
        for j in range(0, N):
            ch = pprocess.start(calculate, i, j)
            exchange.add_wait(ch)

    print "Finishing..."
    exchange.finish()

    # Show the result.

    print
    for row in exchange.D:
        print row

# vim: tabstop=4 expandtab shiftwidth=4
