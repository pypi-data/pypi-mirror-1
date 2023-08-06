## Copyright(c) 2009 William Waites <wwaites_at_gmail.com>
## 
## Permission is hereby granted, free of charge, to any person 
## obtaining a copy of this software and associated documentation 
## files (the "Software"), to deal in the Software without restriction, 
## including without limitation the rights to use, copy, modify, merge, 
## publish, distribute, sublicense, and/or sell copies of the Software, 
## and to permit persons to whom the Software is furnished to do so, 
## subject to the following conditions:
## 
## The above copyright notice and this permission notice shall be included 
## in all copies or substantial portions of the Software.
## 
## THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, 
## EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES 
## OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. 
## IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, 
## DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, 
## ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR 
## OTHER DEALINGS IN THE SOFTWARE.

from bm_ext import *

__all__ = ["BitVector", "strat"]

class BitVector(object):
	def __init__(self, v = None):
		if v is None:
			v = bvector()
			v.set_new_blocks_strat(strat.GAP)
		self.__vector__ = v

		self.count = v.count
		self.resize = v.resize
		self.capacity = v.capacity

		self.set = v.set
		self.any = v.any
		self.none = v.none

		self.calc_stat = v.calc_stat
		self.optimize = v.optimize
		self.serialize = v.serialize
		self.deserialize = v.deserialize
		self.set_new_blocks_strat = v.set_new_blocks_strat

	def __len__(self):
		return len(self.__vector__)
	def __setitem__(self, k, v):
		self.__vector__[k] = v
	def __getitem__(self, k):
		return self.__vector__[k]
	def __and__(self, other):
		if isinstance(other, BitVector):
			other = other.__vector__
		return BitVector(self.__vector__ & other)
	def __or__(self, other):
		if isinstance(other, BitVector):
			other = other.__vector__
		return BitVector(self.__vector__ | other)
	def __invert__(self):
		return BitVector(~self.__vector__)
	def __eq__(self, other):
		if isinstance(other, BitVector):
			other = other.__vector__
		return self.__vector__ == other

	def __iter__(self):
		e = enumerator(self.__vector__, 0)
		end = enumerator(self.__vector__, 1)
		while True:
			if e < end:
				yield e.value()
			else:
				break
			e.next()
	def clear(self, free=False):
		self.__vector__.clear(free)

	def print_stats(self):
		st = statistics()
		self.calc_stat(st)
		print "Size:".rjust(25), len(self)
		print "Bits count:".rjust(25), self.count()
		print "Bit blocks:".rjust(25), st.bit_blocks
		print "GAP blocks:".rjust(25), st.gap_blocks
		print "Memory used:".rjust(25), "%.02fMB" % (float(st.memory_used) / 1024 / 1024)
