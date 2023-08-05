from __future__ import with_statement
from test_temp01 import test_temp01
from sys import stdout

temp = test_temp01(stdout)
with temp:
    temp.NAME = 'foo'
    temp.item = 'product'
    for i in range(5):
	with temp.LOOP:
	    temp.cost = '$' + str(i)
	    temp.number = str(i)
	    pass
	pass
    pass
