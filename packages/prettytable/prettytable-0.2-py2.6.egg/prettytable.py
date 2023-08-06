# PrettyTable 0.2
# Copyright (c) 2009, Luke Maurits <luke@maurits.id.au>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice,
#   this list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
# * The name of the author may not be used to endorse or promote products
#   derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import copy

class PrettyTable:

	def __init__(self, fields=None, caching=True):
		
		"""Return a new PrettyTable instance

		Arguments:
			
		fields - list or tuple of field names
		caching - boolean value to turn string caching on/off"""

		# Data
		if fields:
			self.set_field_names(fields)
		else:
			self.fields = []
			self.widths = []
			self.aligns = []
		self.rows = []
		self.cache = {}

		# Options
		self.hrules = False
		self.caching = caching

	def __getslice__(self, i, j):

		"""Return a new PrettyTable whose data rows are a slice of this one's

		Arguments:
			
		i - beginning slice index
		j - ending slice index"""
		
		newtable = copy.deepcopy(self)
		newtable.rows = self.rows[i:j]
		return newtable

	def __str__(self):

		return self.get_string()
	
	def set_field_names(self, fields):

		"""Set the alignment of a field by its fieldname

		Arguments:
			
		fields - list or tuple of field names"""

		self.fields = fields
		self.widths = [len(field) for field in fields]
		self.aligns = len(fields)*["c"]
		self.cache = {}

	def set_field_align(self, fieldname, align):

		"""Set the alignment of a field by its fieldname

		Arguments:
			
		fieldname - name of the field whose alignment is to be changed
		align - desired alignment - "l" for left, "c" for centre and "r" for right"""

		if fieldname not in self.fields:
			raise Exception("No field %s exists!" % fieldname)
		if align not in ["l","c","r"]:
			raise Exception("Alignment %s is invalid, use l, c or r!" % align)
		self.aligns[self.fields.index(fieldname)] = align
		self.cache = {}

	def add_row(self, row):

		"""Add a row to the table

		Arguments:
			
		row - row of data, should be a list with as many elements as the table
		has fields"""
		
		if len(row) != len(self.fields):
			raise Exception("Row has incorrect number of values")
		self.rows.append(row)
		for i in range(0,len(row)):
			if len(str(row[i])) > self.widths[i]:
				self.widths[i] = len(str(row[i]))
		self.cache = {}

	def get_string(self, start=0, end=None, fields=None, hrules=None):

		"""Return string representation of table in current state.
		
		Arguments:
			
		start - index of first data row to include in output
		end - index of last data row to include in output PLUS ONE (list slice style)"""

		if self.caching:
			key = (start, end, fields, hrules)
			if key in self.cache:
				print "Using cache!"
				return self.cache[key]

		bits = []
		if not self.fields:
			return ""
		bits.append(self._stringify_header(fields))
		hrule = hrules or self.hrules
		for row in self.rows[start:end]:
			bits.append(self._stringify_row(row, fields, hrule))
		if not hrule:
			bits.append(self._stringify_hrule())
		string = "\n".join(bits)
		
		if self.caching:
			self.cache[key] = string

		return string

	def printt(self, start=0, end=None, fields=None, hrules=None):

		"""Print table in current state to stdout.
		
		Arguments:
			
		start - index of first data row to include in output
		end - index of last data row to include in output PLUS ONE (list slice style)"""

		print self.get_string(start, end, fields, hrules)

	def _stringify_hrule(self, fields=None):
		bits = ["+"]
		for field, width in zip(self.fields, self.widths):
			if fields and field not in fields:
				continue
			bits.append((width+2)*"-")
			bits.append("+")
		return "".join(bits)

	def _stringify_header(self, fields=None):

		bits = [self._stringify_hrule()]
		bits.append("\n")
		bits.append("|")
		for field, width in zip(self.fields, self.widths):
			if fields and field not in fields:
				continue
			bits.append(field.center(width+2))
			bits.append("|")
		bits.append("\n")
		bits.append(self._stringify_hrule())
		return "".join(bits)

	def _stringify_row(self, row, fields, hrule):
		bits = ["|"]
		for field, value, width, align in zip(self.fields, row, self.widths, self.aligns):
			if fields and field not in fields:
				continue
			if align == "l":
				bits.append(str(value).ljust(width).center(width+2))
			elif align == "r":
				bits.append(str(value).rjust(width).center(width+2))
			else:
				bits.append(str(value).center(width+2))
			bits.append("|")
		if hrule:
			bits.append(self._stringify_hrule())
		return "".join(bits)

def main():

	x = PrettyTable(["City name", "Area", "Population", "Annual Rainfall"])
	x.set_field_align("City name", "l") # Left align city names
	x.add_row(["Adelaide",1295, 1158259, 600.5])
	x.add_row(["Brisbane",5905, 1857594, 1146.4])
	x.add_row(["Darwin", 112, 120900, 1714.7])
	x.add_row(["Hobart", 1357, 205556, 619.5])
	x.add_row(["Sydney", 2058, 4336374, 1214.8])
	x.add_row(["Melbourne", 1566, 3806092, 646.9])
	x.add_row(["Perth", 5386, 1554769, 869.4])
	print x

if __name__ == "__main__":
	main()
