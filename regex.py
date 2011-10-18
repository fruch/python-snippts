import re
import mmap
import os
import time

'''Trying out regex on mmap files'''
FILE_NAME = 'C:\Users\Fruch\Dropbox\Python\sub\sub.log'
lines = 0
def mapcount(filename,  end):
    global lines
    readline = m.readline
    lines += 1
    while readline():
        if m.tell() > end: break
        lines += 1
    return lines

f = open(FILE_NAME)
m = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
file_size = os.path.getsize(FILE_NAME)


regex = re.compile('\[(?P<date>.*?[^\]])\]DEBUG(?P<line>.*?)\n')

print file_size
start_time = time.time()
for match in regex.finditer(m):
    start = match.start()
    linenum = mapcount(FILE_NAME, start)
    
    #print percentage
    #print match.group('date')
print time.time() - start_time

start_time = time.time()
linenum = mapcount(FILE_NAME, file_size)
for num, line in enumerate(f):
    match = regex.match(line)
    if match:
        start = match.start()
        #print  num, match
print time.time() - start_time

