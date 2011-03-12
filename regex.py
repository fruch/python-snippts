import re
import mmap
import os
import time
'''Trying out regex on mmap files'''
FILE_NAME = 'C:\django\sub\sub.log'

def mapcount(filename,  end):
    f = open(filename, "r+")
    buf = mmap.mmap(f.fileno(),length=end, offset=0)
    lines = 0
    readline = buf.readline
    while readline():
        lines += 1
    return lines

f = open(FILE_NAME)
m = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
file_size = os.path.getsize(FILE_NAME)



regex = re.compile('\[(?P<date>.*?[^\]])\]ERROR.*?\n')

print file_size
start_time = time.time()
for match in regex.finditer(m):
    start = match.start()
    linenum = mapcount(FILE_NAME, start) + 1
    percentage = (start * 100 )/ file_size
    print linenum
    print percentage
    #print match.group('date')
print time.time() - start_time

start_time = time.time()
linenum = mapcount(FILE_NAME, file_size)
for num, line in enumerate(f):
    match = regex.match(line)
    if match:
        start = match.start()
        print (num *100) / linenum, match
print time.time() - start_time