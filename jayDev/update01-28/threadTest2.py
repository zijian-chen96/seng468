import threading
import sys

class Inputs(threading.Thread):

    def __init__(self, q, ins):
        threading.Thread.__init__(self)
        self.q = q
        self.ins = ins

    def run(self):
        q.append(ins)
        print(q)

class Outputs(threading.Thread):

    def __init__(self, q):
        threading.Thread.__init__(self)
        self.q = q

    def run(self):
        while True:
            if len(q) != 0:
                print("pop out: " + q.pop(0)+"now q is: "+str(q))

if __name__ == '__main__':
    q = []
    o = Outputs(q)
    o.start()

    while True:
        print("enter massages")
        fromUser = sys.stdin.readline()
        q.append(fromUser)
        print(q)
