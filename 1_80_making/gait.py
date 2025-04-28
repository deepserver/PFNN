import sys
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
    while i < len(open):
        if mode == 0:
            if isNumber(open[i]):
                tem = int(open[i])
                mode = 1
        elif mode == 1:
            if isNumber(open[i]):
                tem = tem*10 + int(open[i])
            else:
                mode = 2
        elif mode == 2:
            if open[i] == 's':
                if open[i+2] == 'a':
                    ret = 0
                elif open[i+2] == 'o':
                    ret = 7
                break
            elif open[i] == 'w':
                ret = 1
                break
            elif open[i] == 'j':
                if open[i] == 'o':
                    ret = 2
                elif open[i] == 'u':
                    ret = 5
                break
            elif open[i] == 'r':
                ret = 3
                break
            elif open[i] == 'c':
                if open[i+2] == 'o':
                    ret = 4
                elif open[i+2] == 'a':
                    ret = 6
                break
            elif open[i] == 'j':
                ret = 5
                break
            elif open[i] == 'e':
                ret = 7
                break
            else:
                print("file read error")
                break
        i += 1
    lis.append([tem,ret])

def gait(inp):
    global lis
    Frames = lis[-1][0]
    gait = [[0.]*8 for _ in range(Frames+1)]
    output = inp[:-8] + '.gait'
    num = 0
    add = 0.
    old_ret = -1
    i = 1
    while i <= Frames:
        ret = lis[num][1]
        if lis[num][0] == i:
            old_ret = lis[num][1]
            gait[i][old_ret] = 1.
            if num < (len(lis)-1):
                new_ret = lis[num+1][1]
                if old_ret != new_ret:
                    add = 1./(lis[num+1][0]-lis[num][0])
                else:
                    add = 0
                num += 1
        if i != Frames:
            gait[i+1][old_ret] = gait[i][old_ret] - add
            gait[i+1][new_ret] = gait[i][new_ret] + add
        for j in range (8):
            write_data(gait[i][j], output)
            write_data(' ', output)
        write_data('\n', output)       
        i += 1
    
def write_data(data, out):
    ret = str(data)
    with open(out, 'a') as f:
        f.write(ret)

def opens(inp):
    global lis
    lis = []
    output = inp[:-8] + '.gait'
    with open(inp,'r') as fi:
        openfile = fi.read().split('\n')
    with open(output,'w') as fi:
        fi.write('')
    i = 0
    while(i < len(openfile)):
        handle(openfile[i])
        i = i + 1
    print(lis)

def search():
    filepath = "C:\\Users\\chang\\Desktop\\1_80_making"
    for (path, dir, files) in os.walk(filepath):
        for filename in files:
            ext = os.path.splitext(filename)[-1]
            if filename.endswith("gait.txt"):
                stri = path + "\\" + filename
                print("Opening : " + stri)
                opens(stri)
                gait(stri)
                                
search()
