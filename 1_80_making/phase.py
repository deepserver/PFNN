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
    global handle_t, channel_num,offset,level,level_list,frames,frame_time,motion
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
            frame_time = int(float(tem[2])*500)
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

def findvertex():
    global min_y,frames,leftlist,rightlist
    leftbefore = np.array([0.,0.,0.,0.])
    rightbefore = np.array([0.,0.,0.,0.])
    for m in range(frames):
        left = np.array([[1.,0.,0.,0.],[0.,1.,0.,0.],[0.,0.,1.,0.],[0.,0.,0.,1.]])
        right = np.array([[1.,0.,0.,0.],[0.,1.,0.,0.],[0.,0.,1.,0.],[0.,0.,0.,1.]])

        left = trans(0.,-min_y,0.,left)
        right = trans(0.,-min_y,0.,right)

        left = trans(-motion[0][0]/30,-motion[0][1]/30,-motion[0][2]/30,left)
        right = trans(-motion[0][0]/30,-motion[0][1]/30,-motion[0][2]/30,right)

        left = trans(motion[m][0]/30,motion[m][1]/30,motion[m][2]/30,left)
        right = trans(motion[m][0]/30,motion[m][1]/30,motion[m][2]/30,right)

        left = trans(-offset[0][0],-offset[0][1],-offset[0][2],left)
        left = temtemtem(m,0,0,left)
        right = trans(-offset[0][0],-offset[0][1],-offset[0][2],right)
        right = temtemtem(m,0,0,right)

        right = temtemtem(m,47,35,right)
        right = temtemtem(m,48,36,right)
        right = temtemtem(m,49,37,right)
        right = temtemtem(m,50,38,right)
        right_end = trans(offset[51][0],offset[51][1],offset[51][2],right)
        left = temtemtem(m,52,39,left)
        left = temtemtem(m,53,40,left)
        left = temtemtem(m,54,41,left)
        left = temtemtem(m,55,42,left)
        left_end = trans(offset[56][0],offset[56][1],offset[56][2],left)

        right = right@np.array([0.,0.,0.,1.])
        left = left@np.array([0.,0.,0.,1.])
        a = getV(left,leftbefore)
        b = getV(right,rightbefore)
        leftbefore = left
        rightbefore = right
        #print([right,right_end,left,left_end])
        if(a <= 2. and b <= 2.):
            if(a > b):
                leftlist.append(m)
            else:
                rightlist.append(m)
        elif (a <= 1.8):
            leftlist.append(m)
        elif (b <= 1.8):
            rightlist.append(m)

def opens(inp):
    global handle_t, channel_num, offset,level, level_list, frames, motion, min_y, X,Y,Z,leftlist,rightlist
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

    output = inp[:-4] + '_phase.txt'
    with open(inp,'r') as fi:
        openfile = fi.read().split('\n')
    with open(output,'w') as fi:
        fi.write('')
    i = 0
    while(i < len(openfile)):
        handle(openfile[i],output)
        i = i + 1
    findmin_y()

def phase(inp):
    global leftlist, rightlist
    output = inp[:-4] + '_phase.txt'
    a = 0
    b = 0
    mode = 0
    phase = []
    if(len(leftlist) == 0 and len(rightlist) == 0):
        phase.append([-1, "No phase, Please Check by hand"])
    elif(len(leftlist) == 0):
        phase.append([rightlist[0],"right"])
    elif(len(rightlist) == 0):
        phase.append([leftlist[0],"left"])
    else:
        if(leftlist[a] < rightlist[b]):
            phase.append([leftlist[a],"left"])
        else:
            phase.append([rightlist[b],"right"])
            mode = 1
        while(mode != 2):
            if (mode == 0):
                while(leftlist[a] < rightlist[b]):
                    a += 1
                    if(a == len(leftlist)):
                        phase.append([rightlist[b],"right"])
                        mode = 2
                        break
                if(mode != 2):
                    phase.append([rightlist[b],"right"])
                    mode = 1
            else:
                while(leftlist[a] > rightlist[b]):
                    b += 1
                    if(b == len(rightlist)):
                        phase.append([leftlist[a],"left"])
                        mode = 2
                        break
                if(mode != 2):
                    phase.append([leftlist[a],"left"])
                    mode = 0
    for data in phase:
        write_data(str(data), output)



def write_data(data, out):
    data += '\n'
    with open(out, 'a') as f:
        f.write(data)

def search():
    filepath = "C:\\Users\\chang\\Desktop\\1_80_making"
    for (path, dir, files) in os.walk(filepath):
        for filename in files:
            ext = os.path.splitext(filename)[-1]
            if ext == '.bvh':
                stri = path + "\\" + filename
                print("Opening : " + stri)
                opens(stri)
                findvertex()
                phase(stri)

search()                
