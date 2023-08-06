
from processing import Pool
def f(x): return x*x
p = Pool(4)
result = p.mapAsync(f, range(10))
print result.get(timeout=1)

