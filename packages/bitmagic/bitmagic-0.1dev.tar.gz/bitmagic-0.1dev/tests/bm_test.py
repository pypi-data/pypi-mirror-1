from bm import *
from random import random, seed
from time import time
from datetime import datetime

seed(time())

def fill_vector(v, size=1000, chance=0.5):
	for i in range(size):
		if random() < chance:
			v[i] = 1

def random_vector(v, size=1000000, chance=0.10):
	for i in range(int(size * chance)):
		j = int(size * random())
		if j >= size:
			continue
		v[j] = 1

def alloc_vector(size=1000000):
	v = BitVector()
	def f():
		v.resize(size)
		random_vector(v)
		v.optimize()
		v.print_stats()
	print "="*50
	time(f, "Allocated Vector")
	return v

def time(f, desc, iterations=1):
	start = datetime.now()
	for i in range(iterations):
		f()
	end = datetime.now()
	delta = end - start
	s = desc.rjust(25)
	s = s + " %s" % (delta,)
	if iterations > 1:
		s = s + " (%s/iteration)" % (delta/iterations)
	print s


v = alloc_vector()
u = alloc_vector()
print

print "=" * 50
print "Binary operations:".rjust(25), "AND/OR"
time(lambda: u&v, "AND", 1000)
time(lambda: u.__vector__&v.__vector__, "AND[R]", 1000)
time(lambda: u|v, "OR", 1000)
time(lambda: u.__vector__|v.__vector__, "OR[R]", 1000)

print "=" * 50
i = 0
for k in v:
	i = i + 1
print "V:".rjust(25), i
i = 0
for k in u:
	i = i + 1
print "U:".rjust(25), i

from sys import exit
exit(0)

v = BitVector()
v.resize(10000000)
v[1000000] = True
v[1000002] = True
v[1000004] = True
v[1000006] = True
v[1000008] = True
v.optimize()
v.print_stats()
for k in v:
	print k
print
u = ~v
u.print_stats()
u.optimize()
#for k in u:
#	print k
