#
# Python Bytecode Verifier Tests
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

import sys
import os
import dis
import verifier

count = 0

def verifyrecursive(co):
	try:
		verifier.verify(co)
	except KeyboardInterrupt:
		raise
	except:
		dis.dis(co)
		raise

	for const in co.co_consts:
		if hasattr(const, "co_code"):
			verifyrecursive(const)

def verifydir(dir):
	global count
	names = os.listdir(dir)
	for name in names:
		fullname = os.path.join(dir, name)
		if os.path.isfile(fullname):
			if name[-3:] == ".py":
				f = open(fullname, "r")
				try:
					codestring = f.read()
				except UnicodeDecodeError:
					continue
				finally:
					f.close()
				try:
					co = compile(codestring, fullname, "exec", 0, 1)
				except SyntaxError:
					continue
				try:
					verifyrecursive(co)
					count += 1
				except KeyboardInterrupt:
					pass
				except:
					print("Failed to verify: " + fullname)
					raise
		elif os.path.isdir(fullname) and \
			 not os.path.islink(fullname):
			verifydir(fullname)

verifydir(os.curdir)
print("Files verified: " + str(count))
