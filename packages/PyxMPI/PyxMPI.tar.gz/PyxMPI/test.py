#!/usr/bin/env python
# mpirun -np 2 test.py

import numpy.oldnumeric as Numeric, numpy.random as RandomArray
import mpi

def complex_random(*args):
    return RandomArray.uniform(*args) + RandomArray.uniform(*args)*1.0j

SHAPE = (13, 17, 5)
TYPECODES = [
    (RandomArray.random_integers, "i"),
    (RandomArray.random_integers, "l"),
    (RandomArray.uniform, "f"),
    (RandomArray.uniform, "d"),
    (complex_random, "D"),]

world = mpi.world

myid = world.rank
numproc = world.size
left = (myid + numproc - 1) % numproc
right = (myid + 1) % numproc
node = mpi.get_processor_name()

print "I am processor %d of %d on node %s" %(myid, numproc, node)

if myid == 0:
    print 'Modes: ', ', '.join([repr(m) for m in
        [mpi.SYNC, mpi.STANDARD, mpi.READY, mpi.BUFFERED]])

world.barrier()

if numproc < 2:
    raise RuntimeError("Not enough cpus for tests")

# send / receive
def testPointToPoint(shape, typecode, mode, random_source, msg):
    # Pass an array around the ring, from 0 and back to 0
    if myid == 0:
        A = random_source(0,10,shape).astype(typecode)
        B = Numeric.zeros(shape, typecode)
        world.send(A, 1, mode=mode)
        world.receive(B, numproc-1)
        assert (A == B).all()
        print msg
    else:
        X = Numeric.zeros(shape, typecode)
        world.receive(X, myid-1)
        world.send(X, (myid+1)%numproc, mode=mode)


for (random_source, typecode) in TYPECODES:
    msg = "numpy '%s' array send / receive OK" % typecode
    testPointToPoint(SHAPE, typecode, None, random_source, msg)

for mode in [mpi.SYNC, mpi.STANDARD]:
    msg = "Mode '%s' send / receive OK" % mode
    testPointToPoint(SHAPE, typecode, mode, random_source, msg)

# send_obj / receive_obj
A = ['ABC', (1,2,3.14), {8: 'Monty'}, Numeric.array([13.45, 1.2])]
if myid == 0:
    world.send_obj(A,1)
    B, status = world.receive_obj(numproc-1, return_status=True)
    assert (A[-1] == B[-1]).all()
    assert A[:-1] == B[:-1]
    print "Object send / receive OK"
else:
    X = world.receive_obj(myid-1)
    world.send_obj(X, (myid+1)%numproc)

# communicators
subcom = world.split(myid % 2) # 2 groups
if subcom.rank == 0:
    print subcom.size, 'nodes in sub-communicator', myid % 2

# broadcast_obj
for cpu in range(world.size):
    cpu2 = world.broadcast_obj(myid, cpu)
    assert cpu2 == cpu
for cpu in range(world.size):
    cpu2 = world.broadcast_obj([myid], cpu)
    assert cpu2 == [cpu]
for cpu in range(world.size):
    cpu2 = world.broadcast_obj(Numeric.array([myid]), cpu)
    assert cpu2 == Numeric.array([cpu])

# broadcast array
for cpu in range(world.size):
    x = Numeric.array([12, myid])
    world.broadcast(x, cpu)
    assert (x == Numeric.array([12, cpu])).all()
if myid == 0:
    print "Broadcast OK"

# gather
x = world.gather(myid)
y = Numeric.array(range(world.size))
assert (x == y).all(), (myid, x, y)
if myid == 0:
    print "Gather OK"

# scatter
orig = Numeric.array(range(myid, myid+world.size))
assert world.scatter(orig, 1) == myid + 1

orig = Numeric.array([[x,x+myid] for x in range(world.size)])
assert list(world.scatter(orig, 1)) == [myid, myid+1]

if myid == 0:
    print "Scatter OK"

# reduce
assert world.sum(myid) == sum(range(world.size))
assert world.min(myid) == 0
assert world.max(myid) == world.size - 1
if myid == 0:
    print "Reduce OK"

# all to all (transpose)
x = Numeric.arange(world.size)
y = world.transpose(x)
assert list(y) == [world.rank] * world.size, (x, y, world.rank)
if myid == 0:
    print "Transpose OK"

# immediate send
x = Numeric.array([myid])
req = world.immediate_send(x, right)
y = Numeric.zeros([1])
world.receive(y, left)
assert y[0] == left
if myid == 0:
    print "Immediate send OK"

# immediate recv
y = Numeric.zeros([1])
req = world.immediate_receive(y, left)
x = Numeric.array([myid])
world.send(x, right)
req.wait()
assert y[0] == left
if myid == 0:
    print "Immediate receive OK"
    
