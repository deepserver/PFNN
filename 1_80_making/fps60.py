import sys
import os.path

handle_t = 0
count = 0

def handle(open,out):
    global handle_t, count
    tem = open.split()
    if(len(tem) != 0 and handle_t == 0):
        if(tem[0] == 'Frame' and tem[1] == 'Time:'):
            write_data("Frame Time:	0.06666666",out)
            handle_t = 1
        elif(tem[0] == 'Frames:'):
            temp = ''
            temp += tem[0]
            temp += ' '
            temp += str(int((int(tem[1])+1)/2))
            write_data(temp, out)
        else:
            write_data(open,out)
    elif(len(tem) != 0):
        if(count == 0):
            write_data(open,out)
            count += 1
        else:
            count += 1
            if(count == 2):
                count = 0

def handle2(open, out):
    global count
    tem = open.split()
    if(len(tem) != 0):
        if(count == 0):
            write_data(open,out)
            count += 1
        else:
            count += 1
            if(count == 2):
                count = 0

def opens():
    global handle_t
    handle_t = 0
    inp = sys.argv[1]
    output = sys.argv[1][:-4] + '_60fps.bvh'
    with open(inp,'r') as fi:
        openfile = fi.read().split('\n')
    with open(output,'w') as fi:
        fi.write('')
    i = 0
    while(i < len(openfile)):
        handle(openfile[i],output)
        i = i + 1

def opens_phase():
    global count
    count = 0
    inp = sys.argv[1][:-4] + '.phase'
    if(os.path.isfile(inp)):
        output = sys.argv[1][:-4] + '_60fps.phase'
        with open(inp,'r') as fi:
            openfile = fi.read().split('\n')
        with open(output,'w') as fi:
            fi.write('')
        i = 0
        while(i < len(openfile)):
            handle2(openfile[i],output)
            i = i + 1

def opens_face():
    global count
    count = 0
    inp = sys.argv[1][:-4] + '_face.txt'
    if(os.path.isfile(inp)):
        output = sys.argv[1][:-4] + '_face_60fps.txt'
        with open(inp,'r') as fi:
            openfile = fi.read().split('\n')
        with open(output,'w') as fi:
            fi.write('')
        i = 0
        while(i < len(openfile)):
            handle2(openfile[i],output)
            i = i + 1

def write_data(data, out):
    data += '\n'
    with open(out, 'a') as f:
        f.write(data)
 

opens()
opens_phase()
opens_face()