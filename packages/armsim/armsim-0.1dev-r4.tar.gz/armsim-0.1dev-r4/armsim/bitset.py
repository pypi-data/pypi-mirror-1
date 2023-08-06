"""
bitset.py

Written by Geremy Condra

Licensed under GPLv3

Released 3 May 2009

This module provides a simple bitset implementation
for Python.

Modified by Eduardo Diaz
Mayo 8 2009

"""
#Copyright 2009 armsim authors.
#
#This file is part of armsim.
#
#armsim is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#armsim is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with armsim.  If not, see <http://www.gnu.org/licenses/>

from collections import Sequence
import math

class Bitset(Sequence):
	"""A very simple bitset implementation for Python.

	Note that the rightmost
	index is the LSB, and that
	is 0.

	Usage:
		>>> b = Bitset(5)
		>>> b
		Bitset(101)
		>>> b[:]
		[True, False, True]
		>>> b[0] = False
		>>> b
		Bitset(001)
		>>> b << 1
		Bitset(010)
		>>> b >> 1
		Bitset(000)
		>>> b & 1
		Bitset(001)
		>>> b | 2
		Bitset(011)
		>>> b ^ 6
		Bitset(111)
		>>> ~b
		Bitset(110)
	"""

	value = 0
	length = 0

	@classmethod
	def from_sequence(cls, seq):
		"""Iterates over the sequence to produce a new Bitset.

		As in integers, the 0 position represents the LSB.
		"""
		n = 0
		for index, value in enumerate(reversed(seq)):
			n += 2**index * bool(int(value))
		b = Bitset(n)
		return b

	def __init__(self, value=0, length=0):
		"""Creates a Bitset with the given integer value."""
		self.value = value
		try: self.length = length or math.floor(math.log(value, 2)) + 1
		except Exception: self.length = 0

	def __and__(self, other):
		b = Bitset(self.value & int(other))
		b.length = max((self.length, b.length))
		return b

	def __or__(self, other):
		b = Bitset(self.value | int(other))
		b.length = max((self.length, b.length))
		return b

	def __invert__(self):
		#b = Bitset(~self.value)
		#b.length = max((self.length, b.length))
		b = Bitset(self.value, self.length)
		i = 0
		while i < self.length:
			b[i] = not b[i]
			i += 1
		return b

	def __xor__(self, value):
		b = Bitset(self.value ^ int(value))
		b.length = max((self.length, b.length))
		return b

	def __lshift__(self, value):
		b = Bitset(self.value << int(value))
		b.length = max((self.length, b.length))
		return b

	def __rshift__(self, value):
		b = Bitset(self.value >> int(value))
		b.length = max((self.length, b.length))
		return b

	def __eq__(self, other):
		try:
			return self.value == other.value
		except Exception:
			return self.value == other

	def __int__(self):
		return self.value

	def __str__(self):
		s = ""
		for i in self[::-1]:
			s += "1" if i else "0"
		return s

	def __repr__(self):
		return "Bitset(%s)" % str(self)

	def __getitem__(self, s):
		"""Gets the specified position.

		0 represents the LSB.
		"""
		try:
			start, stop, step = s.indices(len(self))
			results = []
			for position in range(start, stop, step):
				#pos = len(self) - position - 1
                                pos = position
				results.append(bool(self.value & (1 << pos)))
			return results
		except:
			#pos = len(self) - s - 1
                        pos = s
			return bool(self.value & (1 << pos))
 
	def __setitem__(self, s, value):
		"""Sets the specified position/s to value.

		0 represents the LSB.
		"""
		try:
			start, stop, step = s.indices(len(self))
			for position in range(start, stop, step):
				#pos = len(self) - position - 1
                                pos = position
				if value: self.value |= (1 << pos)
				else: self.value &= ~(1 << pos)
			maximum_position = max((start + 1, stop, len(self)))
			self.length = maximum_position
		except:
			#pos = len(self) - s - 1
                        pos = s
			if value: self.value |= (1 << pos)
			else: self.value &= ~(1 << pos)
			if len(self) < pos: self.length = pos
		return self

	def __add__(self, other):
		carry  = 0
                size   = int(max((other.length, self.length)))
                result = Bitset(0, size)
                for i in range(size):
			num = int(other[i]) + int(self[i]) + carry
			if num >= 2:
				carry = 1
				num -= 2
			else:
				carry = 0
			result[i] = num
			
		return (result, carry)
 
	def __sub__(self, other):
		carry  = 0
                size   = int(max((other.length, self.length)))
                result = Bitset(0, size)
                for i in range(size):
                        substract = int(other[i]) + carry
			num = int(self[i]) - substract
			if num == -2:
				carry = 1
				num = 0
			elif num == -1:
				carry = 1
				num = 1
			else:
				carry = 0
				
			result[i] = num
			
		return (result, carry)

	def __iter__(self):
		"""Iterates over the values in the bitset."""
		for i in self[:]:
			yield i

	def __len__(self):
		"""Returns the length of the bitset."""
		return self.length
