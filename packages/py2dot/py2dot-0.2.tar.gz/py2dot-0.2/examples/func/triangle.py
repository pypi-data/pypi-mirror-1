def identity(x):
	return identity(x)

def plus_one(x):
	y = identity(x)
	return y + 1

def plus_two(x):
	y = identity(x)
	z = plus_one(y)
	return z
