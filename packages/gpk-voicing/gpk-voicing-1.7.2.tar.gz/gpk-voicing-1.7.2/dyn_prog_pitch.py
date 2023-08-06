"""Viterbi search."""

from gmisclib import Num


HUGE = 1e30


# The internal representation of a path is a linked list of tuples: state: (state_id, prev_state)

def path(nodecost, linkcost, extra_info, N, T):
	"""This function returns a tuple of the cost of the best path
	and the best path, shown as an array: (cost, [j])

	nodecost(t, extra_info) -> ([j-j0], j0, jn)  at time t, pitch=j
	All nodes with j<j0 or j>=jn have infinite cost.
	linkcost(t, extra_info) -> ([j1, j2-j0], j0, jn)  this is the
	cost to go from (t,j1) to (t+1,j2),
	where j=pitch.  Note the first index spans from 0 to N.
	All links that have either j1 or j1 outside of [j0,jn) have infinite cost.
	The extra_info argument isn't used by this function;
	it is simply passed down to the nodecost() and linkcost
	functions.
	T=number of time steps
	N = Largest possible pitch
	"""

	bestpathto = []
	tmp, j0, jn = nodecost(0, extra_info)
	assert j0>=0 and j0<=jn and jn<=N
	cost = Num.zeros((N,), Num.Float) + HUGE
	cost[j0:jn] = tmp
	bestpathto = [ (j, None) for j in range(N) ]

	for t in range(1,T):
		nbp = []
		ncost = Num.zeros((N,), Num.Float)
		nbp = Num.zeros((N,), Num.PyObject)
		nodecost_t, j0, jn = nodecost(t, extra_info)
		assert j0>=0 and j0<=jn and jn<=N
		linkcost_t, jj0, jjn = linkcost(t, extra_info)
		jjj0 = max(j0, jj0)
		jjjn = min(jn, jjn)
		for j in range(0, jjj0):
			ncost[j] = HUGE
			nbp[j] = None
		for j in range(jjj0, jjjn):
			cc = cost + linkcost_t[:,j-jj0]
			o = Num.argmin(cc)
			ncost[j] = cc[o] + nodecost_t[j-j0]
			nbp[j] = (j, bestpathto[o])
		for j in range(jjjn, N):
			ncost[j] = HUGE
			nbp[j] = None
		bestpathto = nbp
		cost = ncost

	jj = Num.argmin(cost)

	return (cost[jj], _unwind(bestpathto[jj]))


def _unwind(path):
	"""Converts the intermediate nested tuple representation to a linear list."""
	o = []
	while 1:
		id, prev = path
		o.append(id)
		if prev is None:
			o.reverse()
			return o
		path = prev



def _test_nodecost(t, xtra):
	return (xtra[0][t,:], 0, len(xtra[0][t,:]))

def _test_linkcost(t, xtra):
	return (xtra[1], 0, len(xtra[1][0,:]))

def _test1():
	T = 10
	N = 7
	noc = Num.zeros((T,N), Num.Float) + 5
	noc[:,3] = 1
	linkc = Num.zeros((N,N), Num.Float) + 2

	c, p = path(_test_nodecost, _test_linkcost, (noc, linkc), N, T)
	assert abs(c - (10*1 + 9*2)) < 0.0001
	assert p == [3]*T

def _test2():
	T = 10
	N = 7
	noc = Num.zeros((T,N), Num.Float) + 5
	for i in range(T):
		noc[i,i%N] = 1
	linkc = Num.zeros((N,N), Num.Float) + 2

	c, p = path(_test_nodecost, _test_linkcost, (noc, linkc), N, T)
	assert abs(c - (10*1 + 9*2)) < 0.0001
	assert p == [0,1,2,3,4,5,6,0,1,2]


def _test3():
	T = 10
	N = 7
	noc = Num.zeros((T,N), Num.Float) + 1
	noc[0,0] = 0
	linkc = Num.zeros((N,N), Num.Float) + 2
	for i in range(N):
		linkc[i,(i+1)%N] = 1

	c, p = path(_test_nodecost, _test_linkcost, (noc, linkc), N, T)
	assert abs(c - (0+9*1 + 9*1)) < 0.0001
	assert p == [0,1,2,3,4,5,6,0,1,2]

def _test_nodecost3(t, xtra):
	a, j0, jn = _test_nodecost(t, xtra)
	return (a[2:-1], 2, len(a)-1)

def _test4():
	T = 10
	N = 7
	noc = Num.zeros((T,N), Num.Float) + 5
	noc[:,3] = 1
	linkc = Num.zeros((N,N), Num.Float) + 2

	c, p = path(_test_nodecost3, _test_linkcost, (noc, linkc), N, T)
	assert abs(c - (10*1 + 9*2)) < 0.0001
	assert p == [3]*T

def _test_linkcost3(t, xtra):
	a, j0, jn = _test_linkcost(t, xtra)
	return (a[:,2:-1], 2, a.shape[1]-1)

def _test5():
	T = 10
	N = 7
	noc = Num.zeros((T,N), Num.Float) + 5
	noc[:,3] = 1
	linkc = Num.zeros((N,N), Num.Float) + 2
	linkc[3,3] = 1

	c, p = path(_test_nodecost3, _test_linkcost3, (noc, linkc), N, T)
	assert abs(c - (10*1 + 9*2 - (T-1)*1)) < 0.0001
	assert p == [3]*T


if __name__ == '__main__':
	_test1()
	_test2()
	_test3()
	_test4()
	_test5()
