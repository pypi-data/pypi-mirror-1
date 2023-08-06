import sys
import math

from test import pystone


def checkinterval():
    # Computes the optimal interpreter checkinterval
    # as advised on zope-dev: pystones / 50.

    tries = 3
    stones = []

    for i in range(tries):
        stones.append(pystone.pystones()[1])

    raw = reduce(lambda x,y: x+y, stones, 0.0) / (50.0*tries)
    return int(math.ceil(raw))


def main():
    print checkinterval()
    sys.exit(0)


if __name__ == '__main__':
    main()

