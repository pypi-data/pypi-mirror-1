from sexp import parse
from sys import stdin
from datetime import datetime

data = stdin.read()

start_time = datetime.now()

for i in range(1000):
    parse(data)

end_time = datetime.now()

print end_time - start_time
