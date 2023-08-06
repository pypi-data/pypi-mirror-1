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
		self.clear = v.clear
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

	def print_stats(self):
		st = statistics()
		self.calc_stat(st)
		print "Size:".rjust(25), len(self)
		print "Bits count:".rjust(25), self.count()
		print "Bit blocks:".rjust(25), st.bit_blocks
		print "GAP blocks:".rjust(25), st.gap_blocks
		print "Memory used:".rjust(25), "%.02fMB" % (float(st.memory_used) / 1024 / 1024)
