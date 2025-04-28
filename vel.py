import sys
import os


def work(inp):
    output = inp[:-13] + '_velocity.txt'
    with open(inp,'r') as fi:
        openfile = fi.read().split('\n')
    with open(output,'w') as fi:
        fi.write('')
    i = 1
    vel = ""
    data = 0.
    while(i < len(openfile)):
        if(len(openfile[i]) != 0):
            vel = ""
            database = openfile[i].split('\t')
            for n in range(len(database)):
                data = (float(database[n]) - float(database[n-1]))*60.
                vel += str(data) + '\t'
            write_data(vel[:-1],output)
        i += 1

def write_data(data,out):
    data += '\n'
    with open(out, 'a') as f:
        f.write(data)

def search():
    filepath = "C:\\Users\\chang\\Desktop\\PFNN_chang"
    for (path, dir, files) in os.walk(filepath):
        for filename in files:
            if (filename.endswith("_location.txt")):
                stri = path + "\\" + filename
                work(stri)

search()                