import sys
import numpy as np 
import os

lis = []

def isNumber(s):
  try:
    float(s)
    return True
  except ValueError:
    return False

def handle(open):
    global lis
    i = 0
    mode = 0
    tem = 0
    ret = 0
    while(i < len(open) and mode != 3):
        if(mode == 0):
            if(isNumber(open[i])):
                tem = int(open[i])
                mode = 1
        elif(mode == 1):
            if(isNumber(open[i])):
                tem = tem*10 + int(open[i])
            else:
                mode = 2
        elif(mode == 2):
            if(open[i] == 'r'):
                ret = 1
                mode = 3
            elif(open[i] == 'l'):
                ret = 2
                mode = 3
            elif(open[i] == 'e'):
                ret = 3
                mode = 3
        i += 1
    lis.append([tem,ret])

def opens(inp):
    global lis
    output = inp[:-10] + '.phase'
    with open(inp,'r') as fi:
        openfile = fi.read().split('\n')
    with open(output,'w') as fi:
        fi.write('')
    i = 0
    while(i < len(openfile)):
        handle(openfile[i])
        i = i + 1
    for i in range(lis.count([0,0])):
        lis.remove([0,0])

def interpolate(inp):
    global lis
    output = inp[:-10] + '.phase'
    phase = 0.
    i = 1
    add = 0.
    n = 0
    end = 0
    if (lis[0][1] == 2):
        phase = 1.
    while(i <= lis[-1][0]):
        if(i == lis[n][0]):
            if(end == 0):
                if(lis[n+1][1] == 2):
                    phase = 0.
                    add = 1./(lis[n+1][0] - lis[n][0])
                    n += 1
                elif(lis[n+1][1] == 1):
                    phase = 1.
                    add = 1./(lis[n+1][0] - lis[n][0])
                    n += 1
                else:
                    if(lis[n][1] == 1):
                        phase = 0.
                        add = 0.
                    else:
                        phase = 1.
                        add = 0.
                    end = 1
        else:
            phase += add
        write_data(phase,output)
        i += 1

def write_data(data, out):
    data = data%2.
    ret = str(data) + '\n'
    with open(out, 'a') as f:
        f.write(ret)

def search():
    filepath = "C:\\Users\\chang\\Desktop\\1_80_making"
    for (path, dir, files) in os.walk(filepath):
        for filename in files:
            ext = os.path.splitext(filename)[-1]
            if ext == '.txt':
                stri = path + "\\" + filename
                print("Opening : " + stri)
                opens(stri)
                interpolate(stri)

search()