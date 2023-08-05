import timeit, n3, sys

times = 4
reps = 4

timeit.n3 = n3
timeit.data = file(sys.argv[1]).read()

nc = min(timeit.Timer(stmt='n3.parse(data)').repeat(reps, times))
print nc
