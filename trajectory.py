import sys
import os


def work(inp,out):
    database = ""
    inp1 = inp + "_location.txt"
    inp2 = inp + "_velocity.txt"
    with open(inp1,'r') as fi:
        openfile1 = fi.read().split('\n')
    with open(inp2,'r') as fi:
        openfile2 = fi.read().split('\n')
    with open(out,'w') as fi:
        fi.write('')
    i = 0
    if(os.path.isfile(inp1) and os.path.isfile(inp2)):
        while((i < len(openfile1)) and (i < len(openfile2))):
            if((len(openfile1[i]) != 0) and (len(openfile2[i]) != 0)):
                database = openfile1[i] +'\t'+ openfile2[i]
                write_data(database,out)
            i += 1

def write_data(data, out):
    data += '\n'
    with open(out, 'a') as f:
        f.write(data)

def search():
    filepath = "C:\\Users\\chang\\Desktop\\PFNN_chang"
    for (path, dir, files) in os.walk(filepath):
        for filename in files:
            ext = os.path.splitext(filename)[-1]
            if ext == '.bvh':
                stri = path + "\\" + filename[:-4] 
                out =  path + "\\" + filename[:-4] + ".database"
                work(stri,out)

search()                