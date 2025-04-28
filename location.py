import sys
import numpy as np 
import os


handle_t = 0
channel_num = 0
offset = []
level = -1
level_list = []
frames = 1
motion = []
min_y = 0.
X = []
Y = []
Z = []

leftlist = []
rightlist = []
lis_i = []
lis_n = []

def rotate_handle(ch):
    global X,Y,Z
    if (ch == 'X' or ch == 'x'):
        X.append(1)
        Y.append(0)
        Z.append(0)
    elif (ch == 'Y' or ch == 'y'):
        X.append(0)
        Y.append(1)
        Z.append(0)
    elif (ch == 'Z' or ch == 'z'):
        X.append(0)
        Y.append(0)
        Z.append(1)

def findmin_y():
    global min_y,offset,level_list
    min_y_list = [0]
    i = 1
    while(len(offset) > i):
        tem = offset[i][1]
        if(level_list[i-1] <= level_list[i]):
            min_y_list.append(min_y_list[-1]+tem)
            if(min_y_list[-1] < min_y):
                min_y = min_y_list[-1]
        else:
            ii = level_list[i-1]-level_list[i]
            for t in range(ii+1):
                min_y_list = min_y_list[:-1]
            min_y_list.append(min_y_list[-1]+tem)
            if(min_y_list[-1] < min_y):
                min_y = min_y_list[-1]
        i = i+1

def handle(open,out): #out 불필요
    global handle_t, channel_num,offset,level,level_list,frames,motion
    tem = open.split()
    if(len(tem) != 0 and handle_t == 0):
        if(tem[0] == '{'):
            level = level + 1
        elif(tem[0] == 'OFFSET'):
            offset.append([float(tem[1])/30,float(tem[2])/30,float(tem[3])/30])
            level_list.append(level)
        elif(tem[0] == 'CHANNELS'):
            channel_num = channel_num + int(tem[1])
            if(int(tem[1]) == 6):
                rotate_handle(tem[5][0])
                rotate_handle(tem[6][0])
                rotate_handle(tem[7][0])
            else:
                rotate_handle(tem[2][0])
                rotate_handle(tem[3][0])
                rotate_handle(tem[4][0])
        elif(tem[0] == '}'):
            level = level - 1
        elif(tem[0] == 'Frames:'):
            frames = int(tem[1])
        elif(tem[0] == 'Frame' and tem[1] == 'Time:'):
            handle_t = 1
    elif(len(tem) != 0):
        list_tem = []
        i = 0
        while(i < channel_num):
            list_tem.append(float(tem[i]))
            i = i + 1
        motion.append(list_tem)


def is_end_site(num):
    global level_list
    if(len(level_list) > num+1):
        if(level_list[num] < level_list[num+1]):
            return False
    return True

def list_append(list, data):
    tem = []
    for i in range(len(data)):
        tem.append(data[i])
    list.append(tem) 

def drawmodel():
    global level_list, lis_n, lis_i,offset
    i = 1
    n = 0
    lis_n = []
    lis_i = []
    data_n = []
    data_i = []
    while(len(level_list)>i):
        if(level_list[i-1] < level_list[i]):
            data_i.append(i)
            if(not(is_end_site(i))):
                data_n.append(n)
                n = n + 1
        else:
            ii = level_list[i-1]-level_list[i]
            for t in range(ii):
                data_i = data_i[:-1]
                data_n = data_n[:-1]
            data_i = data_i[:-1]
            data_i.append(i)
            if(not(is_end_site(i))):
                data_n.append(n)
                n = n + 1

        list_append(lis_n,data_n)
        list_append(lis_i,data_i)
        i = i+1

def findRotationMatrix(m,x,y,z):
    if (x == 1):
        return np.array([[1.,0.,0.,0.],[0.,np.cos(m),(-1.)*np.sin(m),0.],[0.,np.sin(m),np.cos(m),0.],[0.,0.,0.,1.]])
    elif(y == 1):
        return np.array([[np.cos(m),0.,np.sin(m),0.],[0.,1.,0.,0.],[(-1.)*np.sin(m),0.,np.cos(m),0.],[0.,0.,0.,1.]])
    else:
        return np.array([[np.cos(m),(-1.)*np.sin(m),0.,0.],[np.sin(m),np.cos(m),0.,0.],[0.,0.,1.,0.],[0.,0.,0.,1.]])

def temtemtem(m,i,n,arr):
    global offset, motion, X, Y, Z
    arr = trans(offset[i][0],offset[i][1],offset[i][2],arr)
    arr = arr@findRotationMatrix(motion[m][3*n+3]*np.pi/180,X[3*n],Y[3*n],Z[3*n])
    arr = arr@findRotationMatrix(motion[m][3*n+4]*np.pi/180,X[3*n+1],Y[3*n+1],Z[3*n+1]) 
    arr = arr@findRotationMatrix(motion[m][3*n+5]*np.pi/180,X[3*n+2],Y[3*n+2],Z[3*n+2])

    return arr

def trans(x,y,z,arr):
    tem = np.array([[1.,0.,0.,x],[0.,1.,0.,y],[0.,0.,1.,z],[0.,0.,0.,1.]])
    return arr@tem

def getV(a, b):
    tem = ((a[0]-b[0])**2 + (a[1]-b[1])**2 + (a[2]-b[2])**2)**0.5
    return tem*120.

def findvertex(inp):
    global min_y,frames,offset,lis_n,lis_i
    output = inp[:-4] + '_location.txt'
    string = ""
    for m in range(frames):
        for i in range(len(offset)-1):
            data = np.array([[1.,0.,0.,0.],[0.,1.,0.,0.],[0.,0.,1.,0.],[0.,0.,0.,1.]])

            data = trans(0.,-min_y,0.,data)

            data = trans(-motion[0][0]/30,-motion[0][1]/30,-motion[0][2]/30,data)

            data = trans(motion[m][0]/30,motion[m][1]/30,motion[m][2]/30,data)

            data = trans(-offset[0][0],-offset[0][1],-offset[0][2],data)
            data = temtemtem(m,0,0,data)

            for nu in range(len(lis_n[i])):
                data = temtemtem(m,lis_i[i][nu],lis_n[i][nu],data)
            if(is_end_site(i)):
                data = trans(-offset[lis_i[i][-1]][0],-offset[lis_i[i][-1]][1],-offset[lis_i[i][-1]][2],data)

            data = data@np.array([0.,0.,0.,1.])

            string += str(data[0]) + '\t' +str(data[1]) + '\t' +str(data[2]) + '\t'
        write_data(string[:-1],output)
        string = ""

def opens(inp):
    global handle_t, channel_num, offset, level, level_list, frames, motion, min_y, X,Y,Z,leftlist,rightlist
    handle_t = 0
    channel_num = 0
    offset = []
    level = -1
    level_list = []
    frames = 1
    motion = []
    min_y = 0.
    X = []
    Y = []
    Z = []

    leftlist = []
    rightlist = []

    output = inp[:-4] + '_location.txt'
    with open(inp,'r') as fi:
        openfile = fi.read().split('\n')
    with open(output,'w') as fi:
        fi.write('')
    i = 0
    while(i < len(openfile)):
        handle(openfile[i],output)
        i = i + 1
    findmin_y()


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
                stri = path + "\\" + filename
                opens(stri)
                drawmodel()
                findvertex(stri)

search()                
