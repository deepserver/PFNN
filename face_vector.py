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

def handle(open,out):
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
    global min_y,frames
    output = inp[:-4] + '_face.txt'
    for m in range(frames):
        lsdr = np.array([[1.,0.,0.,0.],[0.,1.,0.,0.],[0.,0.,1.,0.],[0.,0.,0.,1.]])
        rsdr = np.array([[1.,0.,0.,0.],[0.,1.,0.,0.],[0.,0.,1.,0.],[0.,0.,0.,1.]])
        lhip = np.array([[1.,0.,0.,0.],[0.,1.,0.,0.],[0.,0.,1.,0.],[0.,0.,0.,1.]])
        rhip = np.array([[1.,0.,0.,0.],[0.,1.,0.,0.],[0.,0.,1.,0.],[0.,0.,0.,1.]])

        lsdr = trans(0.,-min_y,0.,lsdr)
        rsdr = trans(0.,-min_y,0.,rsdr)
        lhip = trans(0.,-min_y,0.,lhip)
        rhip = trans(0.,-min_y,0.,rhip)

        lsdr = trans(-motion[0][0]/30,-motion[0][1]/30,-motion[0][2]/30,lsdr)
        rsdr = trans(-motion[0][0]/30,-motion[0][1]/30,-motion[0][2]/30,rsdr)
        lhip = trans(-motion[0][0]/30,-motion[0][1]/30,-motion[0][2]/30,lhip)
        rhip = trans(-motion[0][0]/30,-motion[0][1]/30,-motion[0][2]/30,rhip)

        lsdr = trans(motion[m][0]/30,motion[m][1]/30,motion[m][2]/30,lsdr)
        rsdr = trans(motion[m][0]/30,motion[m][1]/30,motion[m][2]/30,rsdr)
        lhip = trans(motion[m][0]/30,motion[m][1]/30,motion[m][2]/30,lhip)
        rhip = trans(motion[m][0]/30,motion[m][1]/30,motion[m][2]/30,rhip)

        lsdr = trans(-offset[0][0],-offset[0][1],-offset[0][2],lsdr)
        lsdr = temtemtem(m,0,0,lsdr)
        rsdr = trans(-offset[0][0],-offset[0][1],-offset[0][2],rsdr)
        rsdr = temtemtem(m,0,0,rsdr)
        lhip = trans(-offset[0][0],-offset[0][1],-offset[0][2],lhip)
        lhip = temtemtem(m,0,0,lhip)
        rhip = trans(-offset[0][0],-offset[0][1],-offset[0][2],rhip)
        rhip = temtemtem(m,0,0,rhip)

        rsdr = temtemtem(m,1,1,rsdr)
        rsdr = temtemtem(m,2,2,rsdr)
        rsdr = temtemtem(m,9,7,rsdr)
        rsdr = temtemtem(m,10,8,rsdr)
        lsdr = temtemtem(m,1,1,lsdr)
        lsdr = temtemtem(m,2,2,rsdr)
        lsdr = temtemtem(m,28,21,lsdr)
        lsdr = temtemtem(m,29,22,lsdr)
        rhip = temtemtem(m,47,35,rhip)
        lhip = temtemtem(m,52,39,lhip)

        rsdr = rsdr@np.array([0.,0.,0.,1.])
        lsdr = lsdr@np.array([0.,0.,0.,1.])
        rhip = rhip@np.array([0.,0.,0.,1.])
        lhip = lhip@np.array([0.,0.,0.,1.])


        tem = lsdr - rsdr
        tem2 = lhip - rhip
        temp = (tem+tem2)/2.

        ret = np.cross(temp[:-1],np.array([0.,1.,0.]))

        string = str(ret[0]) +'\t'+str(ret[2])
        write_data(string,output)

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

    output = inp[:-4] + '_face.txt'
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
                findvertex(stri)

search()                
