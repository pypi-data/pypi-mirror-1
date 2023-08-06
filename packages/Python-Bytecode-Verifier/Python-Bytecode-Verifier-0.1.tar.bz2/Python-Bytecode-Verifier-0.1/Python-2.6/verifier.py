#
# Python 2.6 Bytecode Verifier
#
# Copyright (C) 2009 Kornél Pál <http://www.kornelpal.com/>
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

#
# Verificaion rules:
#
# Only opcodes and arguments can appear in the code string, even if unreachable.
# Only opcodes not preceded by an EXTENDED_ARG opcode are valid jump targets.
# Negative, overlong or multiple extended arguments are not allowed.
# Stack overflow (> co_stacksize) and underflow (< 0) is not allowed.
# Stack slots outside block boundaries cannot be accessed.
# If an opcode can be reached from different paths, stack must have the same depth and must be in the same block.
# SETUP_EXCEPT and SETUP_FINALLY handlers are pseudo-blocks.
# SETUP_EXCEPT handler pseudo-blocks are popped either by END_FINALLY or when the first of the three exception stack values is popped.
# SETUP_FINALLY blocks can only be popped by POP_BLOCK if immediately followed by LOAD_CONST None and the handler.
# SETUP_FINALLY handler pseudo-blocks can only be popped by END_FINALLY and cannot access the exception stack values.
# END_FINALLY can only appear when the original exception stack values are on the top of the stack.
# WITH_CLEANUP can only appear at the first opcode of a SETUP_FINALLY handler.
#

__all__ = ["VerificationError", "verify"]

CO_OPTIMIZED = 0x0001
CO_NEWLOCALS = 0x0002
CO_VARARGS = 0x0004
CO_VARKEYWORDS = 0x0008
CO_NESTED = 0x0010
CO_GENERATOR = 0x0020
CO_NOFREE = 0x0040

CO_MAXBLOCKS = 20

STOP_CODE = 0
POP_TOP = 1
ROT_TWO = 2
ROT_THREE = 3
DUP_TOP = 4
ROT_FOUR = 5
NOP = 9

UNARY_POSITIVE = 10
UNARY_NEGATIVE = 11
UNARY_NOT = 12
UNARY_CONVERT = 13

UNARY_INVERT = 15

LIST_APPEND = 18
BINARY_POWER = 19

BINARY_MULTIPLY = 20
BINARY_DIVIDE = 21
BINARY_MODULO = 22
BINARY_ADD = 23
BINARY_SUBTRACT = 24
BINARY_SUBSCR = 25
BINARY_FLOOR_DIVIDE = 26
BINARY_TRUE_DIVIDE = 27
INPLACE_FLOOR_DIVIDE = 28
INPLACE_TRUE_DIVIDE = 29

SLICE = 30
# Also uses 31-33

STORE_SLICE = 40
# Also uses 41-43

DELETE_SLICE = 50
# Also uses 51-53

STORE_MAP = 54
INPLACE_ADD = 55
INPLACE_SUBTRACT = 56
INPLACE_MULTIPLY = 57
INPLACE_DIVIDE = 58
INPLACE_MODULO = 59
STORE_SUBSCR = 60
DELETE_SUBSCR = 61

BINARY_LSHIFT = 62
BINARY_RSHIFT = 63
BINARY_AND = 64
BINARY_XOR = 65
BINARY_OR = 66
INPLACE_POWER = 67
GET_ITER = 68

PRINT_EXPR = 70
PRINT_ITEM = 71
PRINT_NEWLINE = 72
PRINT_ITEM_TO = 73
PRINT_NEWLINE_TO = 74
INPLACE_LSHIFT = 75
INPLACE_RSHIFT = 76
INPLACE_AND = 77
INPLACE_XOR = 78
INPLACE_OR = 79
BREAK_LOOP = 80
WITH_CLEANUP = 81
LOAD_LOCALS = 82
RETURN_VALUE = 83
IMPORT_STAR = 84
EXEC_STMT = 85
YIELD_VALUE = 86
POP_BLOCK = 87
END_FINALLY = 88
BUILD_CLASS = 89

HAVE_ARGUMENT = 90 # Opcodes from here have an argument:

STORE_NAME = 90 # Index in name list
DELETE_NAME = 91 # ""
UNPACK_SEQUENCE = 92 # Number of sequence items
FOR_ITER = 93

STORE_ATTR = 95 # Index in name list
DELETE_ATTR = 96 # ""
STORE_GLOBAL = 97 # ""
DELETE_GLOBAL = 98 # ""
DUP_TOPX = 99 # number of items to duplicate
LOAD_CONST = 100 # Index in const list
LOAD_NAME = 101 # Index in name list
BUILD_TUPLE = 102 # Number of tuple items
BUILD_LIST = 103 # Number of list items
BUILD_MAP = 104 # Always zero for now
LOAD_ATTR = 105 # Index in name list
COMPARE_OP = 106 # Comparison operator
IMPORT_NAME = 107 # Index in name list
IMPORT_FROM = 108 # Index in name list

JUMP_FORWARD = 110 # Number of bytes to skip
JUMP_IF_FALSE = 111 # ""
JUMP_IF_TRUE = 112 # ""
JUMP_ABSOLUTE = 113 # Target byte offset from beginning of code

LOAD_GLOBAL = 116 # Index in name list

CONTINUE_LOOP = 119 # Start of loop (absolute)
SETUP_LOOP = 120 # Target address (relative)
SETUP_EXCEPT = 121 # ""
SETUP_FINALLY = 122 # ""

LOAD_FAST = 124 # Local variable number
STORE_FAST = 125 # Local variable number
DELETE_FAST = 126 # Local variable number

RAISE_VARARGS = 130 # Number of raise arguments (1, 2 or 3)
# CALL_FUNCTION_XXX opcodes defined below depend on this definition
CALL_FUNCTION = 131 # #args + (#kwargs<<8)
MAKE_FUNCTION = 132 # #defaults
BUILD_SLICE = 133 # Number of items

MAKE_CLOSURE = 134 # #free vars
LOAD_CLOSURE = 135 # Load free variable from closure
LOAD_DEREF = 136 # Load and dereference from closure cell
STORE_DEREF = 137 # Store into cell

# The next 3 opcodes must be contiguous and satisfy
# (CALL_FUNCTION_VAR - CALL_FUNCTION) & 3 == 1
CALL_FUNCTION_VAR = 140 # #args + (#kwargs<<8)
CALL_FUNCTION_KW = 141 # #args + (#kwargs<<8)
CALL_FUNCTION_VAR_KW = 142 # #args + (#kwargs<<8)

# Support for opargs more than 16 bits long
EXTENDED_ARG = 143

PyCmp_LT = 0
PyCmp_LE = 1
PyCmp_EQ = 2
PyCmp_NE = 3
PyCmp_GT = 4
PyCmp_GE = 5
PyCmp_IN = 6
PyCmp_NOT_IN = 7
PyCmp_IS = 8
PyCmp_IS_NOT = 9
PyCmp_EXC_MATCH = 10

BLOCK_TYPE_NONE = 0
BLOCK_TYPE_EXCEPT_HANDLER = 1
BLOCK_TYPE_FINALLY_PROLOG = 2
BLOCK_TYPE_FINALLY_HANDLER = 3
BLOCK_TYPE_WITH_CLEANUP = 4
BLOCK_TYPE_WITH_BLOCK = 5

OPCODE_PROCESSED = 0x80000000
OPCODE_STACK_MASK = 0x7fffffff

class VerificationError(Exception):
	def __init__(self, message):
		return super(VerificationError, self).__init__("Unverifiable code: " + message)

class Block(object):
	def __init__(self, type, stack, parent):
		self.type = type
		self.stack = stack
		self.parent = parent
		if not parent is None:
			if self.type >= BLOCK_TYPE_WITH_BLOCK:
				self.level = parent.level + 1
			else:
				self.level = parent.level
		else:
			self.level = 0

ArgBlock = Block(BLOCK_TYPE_NONE, 0, None)
CodeBlock = Block(BLOCK_TYPE_NONE, 0, None)
MainBlock = Block(BLOCK_TYPE_NONE, 0, None)

class OpCode(object):
	def __init__(self):
		self.stack = 0
		self.block = None

class Verifier(object):
	def __init__(self, co):
		if co.co_flags & CO_NOFREE:
			if len(co.co_cellvars) != 0 or len(co.co_freevars) != 0:
				raise VerificationError("Invalid CO_NOFREE flag.")
		else:
			if len(co.co_cellvars) == 0 and len(co.co_freevars) == 0:
				raise VerificationError("Missing CO_NOFREE flag.")

		# Arguments other than code are assumend to be verified by PyCode_New.

		self.co = co
		self.stack = 0
		self.block = MainBlock
		self.opcodes = []
		self.prevoffset = 0
		self.offset = 0

		length = len(self.co.co_code)
		index = 0
		while index < length:
			self.opcodes.append(OpCode())
			index += 1

	def error(self, message):
		raise VerificationError(message + " Offset: " + str(self.offset))

	def targeterror(self, message, tooffset):
		raise VerificationError(message + " From offset: " + str(self.prevoffset if tooffset == self.offset else self.offset) + " To offset: " + str(tooffset))

	def stackdeptherror(self, message, tooffset, originstack, targetstack):
		raise VerificationError(message + " From offset: " + str(self.prevoffset if tooffset == self.offset else self.offset) + " To offset: " + str(tooffset) + " Origin stack: " + str(originstack) + " Target stack: " + str(targetstack))

	def stackboundaryerror(self, message, boundary, required):
		raise VerificationError(message + " Offset: " + str(self.offset) + " Stack: " + str(self.stack) + " Boundary: " + str(boundary) + " Required: " + str(required))

	# Use only when no values are modified
	def ensure(self, val):
		if val > 0x7fffffff or self.stack < val:
			self.stackboundaryerror("Stack underflow.", 0, val)

		newstack = self.stack - val
		block = self.block
		while block.stack > newstack and \
			  block.type == BLOCK_TYPE_EXCEPT_HANDLER:
			block = block.parent

		if block.stack > newstack:
			self.stackboundaryerror("Cannot access stack below block boundary.", block.stack, val)

	def pop(self, val):
		if val > 0x7fffffff or self.stack < val:
			self.stackboundaryerror("Stack underflow.", 0, val)

		newstack = self.stack - val
		while self.block.stack > newstack and \
			  self.block.type == BLOCK_TYPE_EXCEPT_HANDLER:
			# Pop the pseudo-block
			self.block = self.block.parent

		if self.block.stack > newstack:
			self.stackboundaryerror("Cannot access stack below block boundary.", self.block.stack, val)

		self.stack = newstack

	def push(self, val):
		if val > 0x7fffffff or self.stack > self.co.co_stacksize - val:
			self.stackboundaryerror("Stack overflow.", self.co.co_stacksize, val)
		self.stack += val

	def poppush(self, popval, pushval):
		self.pop(popval)
		self.push(pushval)

	def accessname(self, index):
		if index >= len(self.co.co_names):
			self.error("Invalid name index.")

	def accessconst(self, index):
		if index >= len(self.co.co_consts):
			self.error("Invalid constant index.")

	def accesslocal(self, index):
		if index >= self.co.co_nlocals:
			self.error("Invalid local variable index.")

	def accesscellorfree(self, index):
		if index >= len(self.co.co_cellvars) + len(self.co.co_freevars):
			self.error("Invalid cell or free variable index.")

	def target(self, index, stack, block):
		opcode = self.opcodes[index]
		if opcode.block is None or opcode.block is CodeBlock:
			opcode.stack = stack
			opcode.block = block
		elif opcode.block is ArgBlock:
			self.targeterror("Cannot jump to arguments.", index)
		elif (opcode.stack & OPCODE_STACK_MASK) != stack:
			self.stackdeptherror("Opcodes have to be reached with the same stack depth.", index, stack, opcode.stack & OPCODE_STACK_MASK)
		elif opcode.block is not block:
			if opcode.block.type == BLOCK_TYPE_FINALLY_PROLOG:
				self.targeterror("Cannot jump to LOAD_CONST None before SETUP_FINALLY handlers.", index)
			if opcode.block.type == BLOCK_TYPE_WITH_CLEANUP:
				self.targeterror("Cannot jump to WITH_CLEANUP.", index)
			self.targeterror("Opcodes can only be reached within the same block.", index)

	def code(self, index):
		opcode = self.opcodes[index]
		if opcode.block is None:
			opcode.block = CodeBlock
		elif opcode.block is ArgBlock:
			self.targeterror("Cannot jump to arguments.", index)

	def argument(self, index):
		opcode = self.opcodes[index]
		if opcode.block is None:
			opcode.stack = OPCODE_PROCESSED
			opcode.block = ArgBlock
		elif opcode.block is not ArgBlock:
			self.targeterror("Cannot jump to arguments.", index)

	def verify(self):
		jump = False
		jumpreturn = 0
		length = len(self.co.co_code)
		index = 0
		while index < length:
			self.code(index)

			if self.opcodes[index].stack & OPCODE_PROCESSED:
				jump = True
				if jumpreturn > index:
					index = jumpreturn
				else:
					index += 1

				while index < length and (self.opcodes[index].stack & OPCODE_PROCESSED):
					index += 1
				if index >= length:
					break
				self.code(index)

			opcode = ord(self.co.co_code[index])
			self.prevoffset = self.offset
			self.offset = index
			index += 1

			if opcode >= HAVE_ARGUMENT:
				if index > length - 2:
					self.error("Missing opcode argument.")

				self.argument(index)
				self.argument(index + 1)
				arg = ord(self.co.co_code[index]) | (ord(self.co.co_code[index + 1]) << 8)
				index += 2

				if opcode == EXTENDED_ARG:
					if arg == 0:
						self.error("Overlong extended arguments are not allowed.")
					elif arg > 0x7fff:
						self.error("Negative extended arguments are not allowed.")

					if index >= length:
						self.error("Missing opcode after extended argument.")

					self.argument(index)
					opcode = ord(self.co.co_code[index])
					index += 1

					if opcode < HAVE_ARGUMENT:
						self.error("Extended argument for opcode that takes no arguments.")
					if opcode == EXTENDED_ARG:
						self.error("Too many extended arguments.")

					if index > length - 2:
						self.error("Missing opcode argument.")

					self.argument(index)
					self.argument(index + 1)
					arg = ord(self.co.co_code[index]) | (ord(self.co.co_code[index + 1]) << 8) | (arg << 16)
					index += 2
			else:
				arg = 0

			if jump:
				if self.opcodes[self.offset].block is CodeBlock:
					continue
				jump = False
				self.stack = self.opcodes[self.offset].stack & OPCODE_STACK_MASK
				self.block = self.opcodes[self.offset].block
			else:
				self.target(self.offset, self.stack, self.block)

			self.opcodes[self.offset].stack |= OPCODE_PROCESSED

			# STOP_CODE is an invalid opcode
			if opcode == NOP:
				pass
			elif opcode == POP_TOP:
				self.pop(1)
			elif opcode == ROT_TWO:
				self.poppush(2, 2)
			elif opcode == ROT_THREE:
				self.poppush(3, 3)
			elif opcode == DUP_TOP:
				self.ensure(1)
				self.push(1)
			elif opcode == ROT_FOUR:
				self.poppush(4, 4)
			elif opcode == UNARY_POSITIVE or \
				 opcode == UNARY_NEGATIVE or \
				 opcode == UNARY_NOT or \
				 opcode == UNARY_CONVERT or \
				 opcode == UNARY_INVERT:
				self.poppush(1, 1)
			elif opcode == LIST_APPEND:
				self.pop(2)
			elif opcode == BINARY_POWER or \
				 opcode == BINARY_MULTIPLY or \
				 opcode == BINARY_DIVIDE or \
				 opcode == BINARY_TRUE_DIVIDE or \
				 opcode == BINARY_FLOOR_DIVIDE or \
				 opcode == BINARY_MODULO or \
				 opcode == BINARY_ADD or \
				 opcode == BINARY_SUBTRACT or \
				 opcode == BINARY_SUBSCR or \
				 opcode == BINARY_LSHIFT or \
				 opcode == BINARY_RSHIFT or \
				 opcode == BINARY_AND or \
				 opcode == BINARY_XOR or \
				 opcode == BINARY_OR or \
				 opcode == INPLACE_POWER or \
				 opcode == INPLACE_MULTIPLY or \
				 opcode == INPLACE_DIVIDE or \
				 opcode == INPLACE_TRUE_DIVIDE or \
				 opcode == INPLACE_FLOOR_DIVIDE or \
				 opcode == INPLACE_MODULO or \
				 opcode == INPLACE_ADD or \
				 opcode == INPLACE_SUBTRACT or \
				 opcode == INPLACE_LSHIFT or \
				 opcode == INPLACE_RSHIFT or \
				 opcode == INPLACE_AND or \
				 opcode == INPLACE_XOR or \
				 opcode == INPLACE_OR:
				self.poppush(2, 1)
			elif opcode == SLICE+0:
				self.poppush(1, 1)
			elif opcode == SLICE+1 or \
				 opcode == SLICE+2:
				self.poppush(2, 1)
			elif opcode == SLICE+3:
				self.poppush(3, 1)
			elif opcode == STORE_SLICE+0:
				self.pop(2)
			elif opcode == STORE_SLICE+1 or \
				 opcode == STORE_SLICE+2:
				self.pop(3)
			elif opcode == STORE_SLICE+3:
				self.pop(4)
			elif opcode == DELETE_SLICE+0:
				self.pop(1)
			elif opcode == DELETE_SLICE+1 or \
				 opcode == DELETE_SLICE+2:
				self.pop(2)
			elif opcode == DELETE_SLICE+3:
				self.pop(3)
			elif opcode == STORE_MAP:
				self.pop(2)
				self.ensure(1)
			elif opcode == STORE_SUBSCR:
				self.pop(3)
			elif opcode == DELETE_SUBSCR:
				self.pop(2)
			elif opcode == GET_ITER:
				self.poppush(1, 1)
			elif opcode == PRINT_EXPR or \
				 opcode == PRINT_ITEM:
				self.pop(1)
			elif opcode == PRINT_NEWLINE:
				pass
			elif opcode == PRINT_ITEM_TO:
				self.pop(2)
			elif opcode == PRINT_NEWLINE_TO:
				self.pop(1)
			elif opcode == BREAK_LOOP:
				while self.block.level > 0:
					if self.block.type == SETUP_LOOP:
						jump = True
						break
					self.block = self.block.parent

				if not jump:
					self.error("BREAK_LOOP without a loop.")
			elif opcode == WITH_CLEANUP:
				# In fact pops and pushes one of None, WHY_*, (WHY_RETURN or WHY_CONTINUE, retval), (type, value, traceback)
				# and pops __exit__ from the stack.
				if self.block.type != BLOCK_TYPE_WITH_CLEANUP:
					self.error("WITH_CLEANUP can only appear at the first opcode of a SETUP_FINALLY handler.")

				self.stack -= 1
				self.block = Block(BLOCK_TYPE_FINALLY_HANDLER, self.stack, self.block.parent)
			elif opcode == LOAD_LOCALS:
				self.push(1)
			elif opcode == RETURN_VALUE:
				self.pop(1)
				jump = True
			elif opcode == IMPORT_STAR:
				self.pop(1)
			elif opcode == EXEC_STMT:
				self.pop(3)
			elif opcode == POP_BLOCK:
				while True:
					if self.block.level <= 0:
						self.error("There are no blocks to pop.")
					if self.block.type < BLOCK_TYPE_WITH_BLOCK:
						self.block = self.block.parent
					elif self.block.type == BLOCK_TYPE_WITH_BLOCK or \
						 self.block.type == SETUP_FINALLY:
						if self.block.type == BLOCK_TYPE_WITH_BLOCK:
							type = BLOCK_TYPE_WITH_CLEANUP
						else:
							type = BLOCK_TYPE_FINALLY_HANDLER
						self.stack = self.block.stack
						self.block = Block(BLOCK_TYPE_FINALLY_PROLOG, self.stack, self.block.parent)

						if (index >= length - 4 or ord(self.co.co_code[index]) != LOAD_CONST or \
						   self.opcodes[index + 3].block.type != type) and \
						   (index >= length - 7 or ord(self.co.co_code[index]) == EXTENDED_ARG or \
						   ord(self.co.co_code[index + 3]) != LOAD_CONST or \
						   self.opcodes[index + 6].block.type != type):
							self.error("POP_BLOCK in a SETUP_FINALLY block has to be followed by LOAD_CONST None and the handler.")

						arg = ord(self.co.co_code[index + 1]) | (ord(self.co.co_code[index + 2]) << 8)
						if ord(self.co.co_code[index]) == EXTENDED_ARG:
							if arg > 0x7fff:
								self.error("POP_BLOCK in a SETUP_FINALLY block has to be followed by LOAD_CONST None and the handler.")
							arg = ord(self.co.co_code[index + 4]) | (ord(self.co.co_code[index + 5]) << 8) | (arg << 16)
						if arg >= len(self.co.co_consts) or self.co.co_consts[arg] is not None:
							self.error("POP_BLOCK in a SETUP_FINALLY block has to be followed by LOAD_CONST None and the handler.")

						break
					else:
						self.stack = self.block.stack
						self.block = self.block.parent
						break
			elif opcode == YIELD_VALUE:
				if not (self.co.co_flags & CO_GENERATOR):
					self.error("YIELD_VALUE only allowed in generators.")

				self.poppush(1, 1)
			elif opcode == END_FINALLY:
				# In fact pops one of None, WHY_*, (WHY_RETURN or WHY_CONTINUE, retval), (type, value, traceback)
				if self.block.type != BLOCK_TYPE_EXCEPT_HANDLER and self.block.type != BLOCK_TYPE_FINALLY_HANDLER:
					self.error("END_FINALLY can only appear in a SETUP_EXCEPT or a SETUP_FINALLY handler.")
				if self.stack != self.block.stack:
					self.error("END_FINALLY requires the original exception values on the top of the stack.")

				self.stack = self.block.stack - 3
				self.block = self.block.parent
			elif opcode == BUILD_CLASS:
				self.poppush(3, 1)

			# Opcodes from here have an argument:

			elif opcode == STORE_NAME:
				self.accessname(arg)

				self.pop(1)
			elif opcode == DELETE_NAME:
				self.accessname(arg)
			elif opcode == UNPACK_SEQUENCE:
				self.poppush(1, arg)
			elif opcode == FOR_ITER:
				if arg >= length - index:
					self.error("Jump outside of code.")

				self.pop(1)
				self.target(index + arg, self.stack, self.block)
				self.push(2)
			elif opcode == STORE_ATTR:
				self.accessname(arg)

				self.pop(2)
			elif opcode == DELETE_ATTR:
				self.accessname(arg)

				self.pop(1)
			elif opcode == STORE_GLOBAL:
				self.accessname(arg)

				self.pop(1)
			elif opcode == DELETE_GLOBAL:
				self.accessname(arg)
			elif opcode == DUP_TOPX:
				if arg != 2 and arg != 3:
					self.error("Invalid item count.")

				self.ensure(arg)
				self.push(arg)
			elif opcode == LOAD_CONST:
				self.accessconst(arg)

				if self.block.type == BLOCK_TYPE_FINALLY_PROLOG:
					self.stack += 3
					self.block = self.opcodes[index].block
				else:
					self.push(1)
			elif opcode == LOAD_NAME:
				self.accessname(arg)

				self.push(1)
			elif opcode == BUILD_TUPLE or \
				 opcode == BUILD_LIST:
				self.poppush(arg, 1)
			elif opcode == BUILD_MAP:
				self.push(1)
			elif opcode == LOAD_ATTR:
				self.poppush(1, 1)
			elif opcode == COMPARE_OP:
				if arg > PyCmp_EXC_MATCH:
					self.error("Invalid comparison identifier.")

				self.poppush(2, 1)
			elif opcode == IMPORT_NAME:
				self.accessname(arg)

				self.poppush(2, 1)
			elif opcode == IMPORT_FROM:
				self.accessname(arg)

				self.poppush(1, 2)
			elif opcode == JUMP_FORWARD:
				if arg >= length - index:
					self.error("Jump outside of code.")

				self.target(index + arg, self.stack, self.block)
				jump = True
			elif opcode == JUMP_IF_FALSE or \
				 opcode == JUMP_IF_TRUE:
				if arg >= length - index:
					self.error("Jump outside of code.")

				self.ensure(1)
				self.target(index + arg, self.stack, self.block)
			elif opcode == JUMP_ABSOLUTE:
				if arg >= length:
					self.error("Jump outside of code.")

				self.target(arg, self.stack, self.block)
				jump = True

				if arg < index and not (self.opcodes[arg].stack & OPCODE_PROCESSED):
					jumpreturn = index
					index = arg
			elif opcode == LOAD_GLOBAL:
				self.accessname(arg)

				self.push(1)
			elif opcode == CONTINUE_LOOP:
				if arg >= length:
					self.error("Jump outside of code.")

				while self.block.level > 0:
					if self.block.type == SETUP_LOOP:
						self.target(arg, self.stack, self.block)
						jump = True

						if arg < index and not (self.opcodes[arg].stack & OPCODE_PROCESSED):
							jumpreturn = index
							index = arg
						break
					elif self.block.type == BLOCK_TYPE_WITH_BLOCK:
						self.stack = self.block.stack - 1
					elif self.block.type > BLOCK_TYPE_WITH_BLOCK:
						self.stack = self.block.stack
					self.block = self.block.parent

				if not jump:
					self.error("CONTINUE_LOOP without a loop.")

				if arg < index and not (self.opcodes[arg].stack & OPCODE_PROCESSED):
					jumpreturn = index
					index = arg
			elif opcode == SETUP_LOOP or \
				 opcode == SETUP_EXCEPT or \
				 opcode == SETUP_FINALLY:
				if arg >= length - index:
					self.error("Jump outside of code.")

				if self.block.level >= CO_MAXBLOCKS:
					self.error("Too many nested blocks.")

				targetindex = index + arg
				if opcode == SETUP_LOOP:
					self.target(targetindex, self.stack, self.block)
				elif opcode == SETUP_FINALLY and ord(self.co.co_code[targetindex]) == WITH_CLEANUP:
					self.poppush(1, 4)
					self.target(targetindex, self.stack, Block(BLOCK_TYPE_WITH_CLEANUP, self.stack, self.block))
					self.stack -= 3
					opcode = BLOCK_TYPE_WITH_BLOCK
				else:
					self.push(3)
					self.target(targetindex, self.stack, Block(BLOCK_TYPE_EXCEPT_HANDLER if opcode == SETUP_EXCEPT else BLOCK_TYPE_FINALLY_HANDLER, self.stack, self.block))
					self.stack -= 3
				self.block = Block(opcode, self.stack, self.block)
			elif opcode == LOAD_FAST:
				self.accesslocal(arg)

				self.push(1)
			elif opcode == STORE_FAST:
				self.accesslocal(arg)

				self.pop(1)
			elif opcode == DELETE_FAST:
				self.accesslocal(arg)
			elif opcode == RAISE_VARARGS:
				if arg > 3:
					self.error("Invalid argument count.")

				self.pop(arg)
				jump = True
			elif opcode == CALL_FUNCTION:
				if arg > 0xffff:
					self.error("Too many call arguments.")

				self.poppush((arg & 0xff) + 2 * ((arg >> 8) & 0xff) + 1, 1)
			elif opcode == MAKE_FUNCTION:
				self.poppush(arg + 1, 1)
			elif opcode == BUILD_SLICE:
				if arg != 2 and arg != 3:
					self.error("Invalid argument count.")

				self.poppush(arg, 1)
			elif opcode == MAKE_CLOSURE:
				self.poppush(arg + 2, 1)
			elif opcode == LOAD_CLOSURE or \
				 opcode == LOAD_DEREF:
				self.accesscellorfree(arg)

				self.push(1)
			elif opcode == STORE_DEREF:
				self.accesscellorfree(arg)

				self.pop(1)
			elif opcode == CALL_FUNCTION_VAR or \
				 opcode == CALL_FUNCTION_KW:
				if arg > 0xffff:
					self.error("Too many call arguments.")

				self.poppush((arg & 0xff) + 2 * ((arg >> 8) & 0xff) + 2, 1)
			elif opcode == CALL_FUNCTION_VAR_KW:
				if arg > 0xffff:
					self.error("Too many call arguments.")

				self.poppush((arg & 0xff) + 2 * ((arg >> 8) & 0xff) + 3, 1)
			else:
				self.error("Invalid opcode.")

		index = 0
		while index < length:
			if not (self.opcodes[index].stack & OPCODE_PROCESSED) and \
			   not self.opcodes[index].block is CodeBlock:
				self.offset = index
				if self.opcodes[index].block is None:
					self.error("Internal error: Unseen opcode.")
				self.error("Internal error: Unprocessed opcode.")
			index += 1

def verify(co):
	Verifier(co).verify()
