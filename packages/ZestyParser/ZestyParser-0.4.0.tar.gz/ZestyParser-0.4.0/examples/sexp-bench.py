from sexp import SexpParser
from sys import stdin
from datetime import datetime

parser = SexpParser()
data = stdin.read()

start_time = datetime.now()

for i in range(1000):
	parser.parse(data)

end_time = datetime.now()

print end_time - start_time
