__author__ = 'Fruch'
import psyco

def test():
    "Stupid test function"
    psyco.full()
    L = [1]
    for i in range(100):
        L.append(i*L[-1]*L[-1])

def test2():
    L = [1]
    for i in range(100):
        L.append(i*L[-1]*L[-1])

if __name__=='__main__':
    from timeit import Timer
    t = Timer("test2()", "from __main__ import test2")
    print t.timeit(200)

    t = Timer("test()", "from __main__ import test")
    print t.timeit(200)
