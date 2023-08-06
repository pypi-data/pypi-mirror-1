from simplex import noise3
from random import uniform

while 1:
	x = uniform(-10000, 10000)
	y = uniform(-10000, 10000)
	z = uniform(-10000, 10000)
	n = noise3(x,y,z)
	print x, y, z, noise3(x,y,z)
	assert -1.0 <= n <= 1.0
	
