
# Fibonacci

def fib(max):
	n, a, b = 0, 0, 1
	while n < max:
		yield b
		a, b = b, a + b
		n = n + 1
	return 'done'


def triangles():
    n, a = 1, 1
    l = list()
    while True:
        ll = l
        if n % 2 != 0:
            if n == 1:
                l.append(a)
            else:
                # return
                m = n / 2 + 1
                l = l [:m]
                for i in range(1, m):
                    l[i] = ll[i-1] + ll[i]
                ll = l[:-1]
                ll.reverse()
                l.extend(ll)
        else:
            m = n / 2
            if m == 1:
                l.append(a)
            else:
                # return
                l = l [:m]
                for i in range(1, m):
                    l[i] = ll[i-1] + ll[i]
                ll = l[:]
                ll.reverse()
                l.extend(ll)
        n = n + 1
        yield l
        # print l
        # if n == 11:
        #     break
