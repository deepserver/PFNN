import wx
from wx import *
from OpenGL.GL import *
import numpy as np 
from OpenGL.GLU import *
from wx.glcanvas import *

import sys
import os
import torch
import torch.nn as nn
import torch.nn.functional as F

mode = 0
r = 8
angleXZ = np.radians(45)
angleY = np.radians(0)
trX = 0
trY = 0
trZ = 0
temX = 0
temY = 0
rx = 4.*np.sqrt(2)
ry = 0.
rz = 4.*np.sqrt(2)
handle_t = 0
channel_num = 0
offset = []
level = -1
level_list = []
frames = 1
frame_time = 1
motion = []
min_y = 0.
animate = -1
X = []
Y = []
Z = []
start = 0
frame_num = 0
posi = np.array([0.,0.,0.])
face = 0.

pastTraV = []
pastTraP = []
for i in range(61):
    pastTraV.append([0.,0.])
    pastTraP.append([0.,0.])
pridicTraV = []
pridicTraP = []
for i in range(5):
    pridicTraV.append([0.,0.])
    pridicTraP.append([0.,0.])
keyboard = [0,0,0,0]

inp = 432
outp = 521
hid1 = 256
hid2 = 256

class Net(nn.Module):

    def __init__(self):
        super(Net, self).__init__()
        self.fc01 = nn.Linear(inp, hid1)
        self.fc02 = nn.Linear(hid1, hid2)
        self.fc03 = nn.Linear(hid2, outp)
        self.fc11 = nn.Linear(inp, hid1)
        self.fc12 = nn.Linear(hid1, hid2)
        self.fc13 = nn.Linear(hid2, outp)
        self.fc21 = nn.Linear(inp, hid1)
        self.fc22 = nn.Linear(hid1, hid2)
        self.fc23 = nn.Linear(hid2, outp)
        self.fc31 = nn.Linear(inp, hid1)
        self.fc32 = nn.Linear(hid1, hid2)
        self.fc33 = nn.Linear(hid2, outp)

    def forward(self, x, phase):
        w = (phase*2.)%1
        k = -(int(phase*-2.))
        li = [[self.fc01,self.fc02,self.fc03],[self.fc11,self.fc12,self.fc13],[self.fc21,self.fc22,self.fc23],[self.fc31,self.fc32,self.fc33]]
        a1 = li[k%4]
        a2 = li[(k+1)%4]
        a3 = li[(k+2)%4]
        a4 = li[(k+3)%4]
        hid_lay1 = F.elu(a1[0](x) + w*(a2[0](x)/2. - a4[0](x)/2.) + (w**2.)*(a4[0](x)-a1[0](x)*5./2. + 2.*a2[0](x) - a3[0](x)/2.) + (w**3.)*(a1[0](x)*3./2. - a2[0](x)*3./2. + a3[0](x)/2. - a4[0](x)/2.))
        hid_lay2 = F.elu(a1[1](hid_lay1) + w*(a2[1](hid_lay1)/2. - a4[1](hid_lay1)/2.) + (w**2.)*(a4[1](hid_lay1)-a1[1](hid_lay1)*5./2. + 2.*a2[1](hid_lay1) - a3[1](hid_lay1)/2.) + (w**3.)*(a1[1](hid_lay1)*3./2. - a2[1](hid_lay1)*3./2. + a3[1](hid_lay1)/2. - a4[1](hid_lay1)/2.))
        out =  (a1[2](hid_lay2) + w*(a2[2](hid_lay2)/2. - a4[2](hid_lay2)/2.) + (w**2.)*(a4[2](hid_lay2)-a1[2](hid_lay2)*5./2. + 2.*a2[2](hid_lay2) - a3[2](hid_lay2)/2.) + (w**3.)*(a1[2](hid_lay2)*3./2. - a2[2](hid_lay2)*3./2. + a3[2](hid_lay2)/2. - a4[2](hid_lay2)/2.))
        return out


net = Net().to("cpu")
net.load_state_dict(torch.load("tensor.pt", map_location = torch.device('cpu')))
input_data = []
output_data = []
phase = 0.

def blendT(a,b):
    ret = []
    for i in range(len(a)):
        t = ((i+1)/6)**2
        ret.append([(1-t)*a[i][0] + t*b[i][0],(1-t)*a[i][1] + t*b[i][1]])
    return ret

def blendV(a,b):
    ret = []
    for i in range(len(a)):
        t = ((i+1)/6)**(0.5)
        ret.append([(1-t)*a[i][0] + t*b[i][0],(1-t)*a[i][1] + t*b[i][1]])
    return ret

def target_vel(keyborad):
    ret = [0.,0.]
    if(keyboard[0] == 1):
        ret[0] -= 1.
    if(keyboard[1] == 1):
        ret[0] += 1.
    if(keyboard[2] == 1):
        ret[1] -= 1.
    if(keyboard[3] == 1):
        ret[1] += 1.
    if(ret[0] != 0. or ret[1] != 0.):
        tem = (ret[0]**2.+ret[1]**2.)**(0.5)
        ret[0] = (ret[0]/tem)*5
        ret[1] = (ret[1]/tem)*5
    return ret

def pridictPosition(tv):
    ret = []
    for i in range(5):
        ret.append(list(map(lambda x : x*(i+1)*10., tv)))
    return ret

def IsInt(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False

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

def handle(open):
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

def openBVH(file):
    global handle_t,channel_num,offset,level,level_list,frames,frame_time,motion,min_y,animate,X,Y,Z
    handle_t = 0
    channel_num = 0
    offset = []
    level = -1
    level_list = []
    frames = 1
    frame_time = 1
    motion = []
    min_y = 0.
    animate = 0
    X = []
    Y = []
    Z = []
    with open(file[0],'r') as fi:
        openfile = fi.read().split('\n')
    i = 0
    while(i < len(openfile)):
        handle(openfile[i])
        i = i + 1
    findmin_y()

def openNN(inpu,p):
    global input_data, net, output_data,phase
    input_data = []
    output_data = []
    phase = 0.
    with open(inpu,'r') as fi:
        tem = fi.read().split('\n')
        for i in range(1):
            if(len(tem[i]) != 0):
                for data in tem[i].split('\t'):
                    input_data.append(float(data))

    with open(p,'r') as fi:
        tem = fi.read().split('\n')
        phase = float(tem[61])

    outp = net(torch.tensor(input_data),phase)
    output_data = outp.detach().numpy()


def temopen(outpu):
    global input_data, output_data
    input_data = []
    output_data = []
    with open(outpu,'r') as fi:
        tem = fi.read().split('\n')
        for i in range(len(tem)):
            if(len(tem[i]) != 0):
                output_data.append([])
                for data in tem[i].split('\t'):
                    output_data[i].append(float(data))

def upvect(angle):
    if np.cos(angle)>0:
        return 1
    else:
        return -1

def drawline():
    glBegin(GL_LINES)
    glColor3ub(255,255,255)
    for i in range(11):
        if i != 5:
            glVertex3fv(np.array([i-5,0,-5]))
            glVertex3fv(np.array([i-5,0,5]))
            glVertex3fv(np.array([-5,0,i-5]))
            glVertex3fv(np.array([5,0,i-5]))
    glEnd()

def is_end_site(num):
    global level_list
    if(len(level_list) > num+1):
        if(level_list[num] < level_list[num+1]):
            return False
    return True

def draw(tem1,tem2):
    tem = tem1-tem2
    if(np.dot(tem,tem) != 0):
        glColor3ub(255, 255, 255) 
        glBegin(GL_LINES)
        glVertex3fv(tem1)
        glVertex3fv(tem2)
        glEnd()


def drawmodelPos():
    global offset,level_list,motion,min_y,frame,frame_time,animate,frames,X,Y,Z, frame_num,output_data
    i = 1
    #n = 0
    last = 0
    m = 0
    trans = []
    tem = np.array([])
    #glPushMatrix()
    #glTranslatef(0.,-min_y,0.)
    #if(animate != -1):
    #    glTranslatef(-motion[0][0]/30,-motion[0][1]/30,-motion[0][2]/30)
    #glPushMatrix()
    if(animate != -1):
        m = frame_num
        trans.append(np.array([output_data[m][48],output_data[m][49],output_data[m][50]]))
        glTranslatef(trans[-1][0],trans[-1][1],trans[-1][2])
        #glRotatef(motion[m][3], X[0], Y[0], Z[0]) 
        #glRotatef(motion[m][4], X[1], Y[1], Z[1]) 
        #glRotatef(motion[m][5], X[2], Y[2], Z[2]) 
    while(len(offset)>i+1):
        #tem = np.array(offset[i])
        if(level_list[i-1] <= level_list[i]):
            tem = np.array([output_data[m][3*i+48],output_data[m][3*i+49],output_data[m][3*i+50]])
            draw(trans[-1],tem)
            if(not(is_end_site(i))):
               # glPushMatrix()
                trans.append(tem)
                #glTranslatef(tem2[0],tem2[1],tem2[2])
                #if(animate != -1):
                #    glRotatef(motion[m][3*n+3], X[3*n], Y[3*n], Z[3*n]) 
                #    glRotatef(motion[m][3*n+4], X[3*n+1], Y[3*n+1], Z[3*n+1]) 
                #    glRotatef(motion[m][3*n+5], X[3*n+2], Y[3*n+2], Z[3*n+2]) 
                #    n = n + 1
        else:
            ii = level_list[i-1]-level_list[i]
            for t in range(ii):
                #glPopMatrix()
                trans = trans[:-1]
            tem = np.array([output_data[m][3*i+48],output_data[m][3*i+49],output_data[m][3*i+50]])
            draw(trans[-1],tem)
            if(not(is_end_site(i))):
                #glPushMatrix()
                trans.append(tem)
                #glTranslatef(tem2[0],tem2[1],tem2[2])
                #if(animate != -1):
                #    glRotatef(motion[m][3*n+3], X[3*n], Y[3*n], Z[3*n]) 
                #    glRotatef(motion[m][3*n+4], X[3*n+1], Y[3*n+1], Z[3*n+1]) 
                #    glRotatef(motion[m][3*n+5], X[3*n+2], Y[3*n+2], Z[3*n+2]) 
                #    n = n + 1
        #last = level_list[i]
        i = i+1
    #for tt in range(last-1):
    #    glPopMatrix()
    #glPopMatrix()
    #glPopMatrix()

def draw2(tem):
    if(np.dot(tem,tem) != 0):
        glColor3ub(0, 255, 255) 
        glBegin(GL_LINES)
        glVertex3fv(np.array([0.,0.,0.]))
        glVertex3fv(tem)
        glEnd()

def drawtrajectory():
    global pastTraP,pastTraV,pridicTraP,pridicTraV,animate,posi
    if(animate != -1):
        for i in range(7):
            glPushMatrix()
            glTranslatef(posi[0],posi[1],posi[2])
            #glRotatef(-face,0.,1.,0.)
            glTranslatef(pastTraP[10*i][0]/30.,0.,pastTraP[10*i][1]/30.)
            ang = np.arctan2(pastTraV[10*i][1],pastTraV[10*i][0])/np.pi*180
            glRotatef(-ang,0.,1.,0.)
            glColor3ub(255,255,0)
            glBegin(GL_LINES)
            glVertex3fv(np.array([0.5,0.,0.]))
            glVertex3fv(np.array([0.,0.,0.]))
            glVertex3fv(np.array([0.5,0.,0.]))
            glVertex3fv(np.array([0.35,0.,0.15]))
            glVertex3fv(np.array([0.5,0.,0.]))
            glVertex3fv(np.array([0.35,0.,-0.15]))
            glEnd()
            glPopMatrix()
        for i in range(5):
            glPushMatrix()
            glTranslatef(posi[0],posi[1],posi[2])
            glTranslatef(pridicTraP[i][0]/30.,0.,pridicTraP[i][1]/30.)
            ang = np.arctan2(pridicTraV[i][1],pridicTraV[i][0])/np.pi*180
            glRotatef(-ang,0.,1.,0.)
            glColor3ub(255,255,0)
            glBegin(GL_LINES)
            glVertex3fv(np.array([0.5,0.,0.]))
            glVertex3fv(np.array([0.,0.,0.]))
            glVertex3fv(np.array([0.5,0.,0.]))
            glVertex3fv(np.array([0.35,0.,0.15]))
            glVertex3fv(np.array([0.5,0.,0.]))
            glVertex3fv(np.array([0.35,0.,-0.15]))
            glEnd()
            glPopMatrix()

def tem_drawtrajectory():
    global output_data,animate
    if(animate != -1):
        for i in range(12):
            glPushMatrix()
            glTranslatef(posi[0],posi[1],posi[2])
            glRotatef(-face,0.,1.,0.)
            glTranslatef(output_data[2*i]/30.,0.,output_data[2*i+1]/30.)
            ang = np.arctan2(output_data[2*i+25],output_data[2*i+24])
            glRotatef(-ang,0.,1.,0.)
            glColor3ub(255,255,0)
            glBegin(GL_LINES)
            glVertex3fv(np.array([0.5,0.,0.]))
            glVertex3fv(np.array([0.,0.,0.]))
            glVertex3fv(np.array([0.5,0.,0.]))
            glVertex3fv(np.array([0.35,0.,0.15]))
            glVertex3fv(np.array([0.5,0.,0.]))
            glVertex3fv(np.array([0.35,0.,-0.15]))
            glEnd()

            glPopMatrix()


def drawmodelAng():
    global offset,level_list,motion,min_y,frame,frame_time,animate,frames,X,Y,Z, frame_num,output_data,posi,face
    i = 1
    n = 1
    last = 0
    m = 0
    trans = []
    tem = np.array([])
    #glPushMatrix()
    #glTranslatef(0.,-min_y,0.)
    #if(animate != -1):
       # glTranslatef(-motion[0][0]/30,-motion[0][1]/30,-motion[0][2]/30)
    glPushMatrix()
    if(animate != -1):
        m = frame_num
        glTranslatef(output_data[48]/30.,output_data[49]/30.,output_data[50]/30.)
        glTranslatef(posi[0],posi[1],posi[2])
        glRotatef(-face,0.,1.,0.)
        glRotatef(output_data[384], X[0], Y[0], Z[0]) 
        glRotatef(output_data[385], X[1], Y[1], Z[1]) 
        glRotatef(output_data[386], X[2], Y[2], Z[2]) 
    while(len(offset)>i):
        tem = np.array(offset[i])
        if(level_list[i-1] <= level_list[i]):
            draw2(tem)
            if(not(is_end_site(i))):
                glPushMatrix()
                glTranslatef(tem[0],tem[1],tem[2])
                if(animate != -1):
                    glRotatef(output_data[3*n + 384], X[3*n], Y[3*n], Z[3*n]) 
                    glRotatef(output_data[3*n + 385], X[3*n+1], Y[3*n+1], Z[3*n+1]) 
                    glRotatef(output_data[3*n + 386], X[3*n+2], Y[3*n+2], Z[3*n+2]) 
                    n = n + 1
        else:
            ii = level_list[i-1]-level_list[i]
            for t in range(ii):
                glPopMatrix()
            draw2(tem)
            if(not(is_end_site(i))):
                glPushMatrix()
                glTranslatef(tem[0],tem[1],tem[2])
                if(animate != -1):
                    glRotatef(output_data[3*n + 384], X[3*n], Y[3*n], Z[3*n]) 
                    glRotatef(output_data[3*n + 385], X[3*n+1], Y[3*n+1], Z[3*n+1]) 
                    glRotatef(output_data[3*n + 386], X[3*n+2], Y[3*n+2], Z[3*n+2]) 
                    n = n + 1
        last = level_list[i]
        i = i+1
    for tt in range(last-1):
        glPopMatrix()
    glPopMatrix()
    #glPopMatrix()

def render():
    global r,angleXZ,angleY,trX,trY,trZ,filled,l0,l1,rx,ry,rz
    glClear(GL_COLOR_BUFFER_BIT) 
    glEnable(GL_DEPTH_TEST) 
    glLoadIdentity()
    gluPerspective(45, 1, 1, 50)

    gluLookAt(rx,ry,rz, trX,trY,trZ, 0,upvect(angleY),0)
    # draw cooridnate
    glBegin(GL_LINES)
    glColor3ub(255, 0, 0)
    glVertex3fv(np.array([-5.,0.,0.]))
    glVertex3fv(np.array([8.,0.,0.]))
    glColor3ub(0, 255, 0)
    glVertex3fv(np.array([0., 0., -5.]))
    glVertex3fv(np.array([0., 0., 8.]))
    glEnd()
    drawline()
    #drawmodelPos()
    drawmodelAng()
    drawtrajectory()

def output_to_input(output):
    out = []
    for i in range(48):
        out.append(output[i])
    for i in range(12):
        out.append(0.)
        out.append(1.)
        out.append(0.)
        out.append(0.)
    for i in range(48,384):
        out.append(output[i])

    return torch.tensor(out)

def phase_update(output):
    global phase
    phase += output[516]
    #phase += 0.031
    while (phase >= 2.):
        phase -= 2.
    #print(phase, output[516])
    
class BVH(wx.Frame):
    def __init__(self):
        global frame_time, start
        wx.Frame.__init__(self, None, size = (600,700))
        self.canvas = GLCanvas(self, size = (600,600),attribList=[wx.glcanvas.WX_GL_DOUBLEBUFFER])
        self.button1 = wx.Button(self, size = (80,50), label = "<<", pos = (15,605))
        self.button2 = wx.Button(self, size = (80,50), label = "Start", pos = (115,605))
        self.button3 = wx.Button(self, size = (80,50), label = ">>", pos = (225,605))
        self.button4 = wx.Button(self, size = (80,50), label = "Jump", pos = (445,605))
        self.button1.Bind(wx.EVT_BUTTON, self.button1_event)
        self.button2.Bind(wx.EVT_BUTTON, self.button2_event)
        self.button3.Bind(wx.EVT_BUTTON, self.button3_event)
        self.button4.Bind(wx.EVT_BUTTON, self.button4_event)
        self.canvas.Bind(wx.EVT_PAINT, self.OnDraw)
        self.canvas.Bind(wx.EVT_MOTION, self.MouseMotion)

        wx.Window.DragAcceptFiles(self, True)
        self.text = wx.TextCtrl( self, size = (50,50), pos = (385,605) )
        self.timer = wx.Timer(None)
        self.timer.SetOwner(self, -1)

        self.canvas.Bind(wx.EVT_LEFT_DOWN, self.LBD)
        self.canvas.Bind(wx.EVT_LEFT_UP, self.LBU)
        self.canvas.Bind(wx.EVT_RIGHT_DOWN,self.RBD)
        self.canvas.Bind(wx.EVT_RIGHT_UP,self.RBU)
        self.canvas.Bind(wx.EVT_MOUSEWHEEL, self.WHEEL)
        self.Bind(wx.EVT_KEY_DOWN, self.KEY)
        self.Bind(wx.EVT_KEY_UP, self.KEY2)
        self.Bind(wx.EVT_DROP_FILES, self.Drop)
        self.Bind(wx.EVT_TIMER, self.Timeover)
        self.Show(True)

    def OnDraw(self,event):
        Context = wx.glcanvas.GLContext(self.canvas)
        self.canvas.SetCurrent(Context)
        render()
        self.canvas.SwapBuffers()

    def KEY(self, event):
        global keyboard
        key = event.GetKeyCode()
        #if(key != wx.WXK_NONE):
        #    print(char(key))
        if(key == wx.WXK_LEFT):
            keyboard[0] = 1
            print("left")
        if(key == wx.WXK_RIGHT):
            keyboard[1] = 1
            print("right")
        if(key == wx.WXK_UP):
            keyboard[2] = 1
            print("up")
        if(key == wx.WXK_DOWN):
            keyboard[3] = 1
            print("down")

    def KEY2(self, event):
        global keyboard
        key = event.GetKeyCode()
        if(key == wx.WXK_LEFT):
            keyboard[0] = 0
        if(key == wx.WXK_RIGHT):
            keyboard[1] = 0
        if(key == wx.WXK_UP):
            keyboard[2] = 0
        if(key == wx.WXK_DOWN):
            keyboard[3] = 0

    def LBD(self, event):
        global mode
        if mode!=2:
            mode = 1

    def LBU(self, event):
        global mode
        if mode!=2:
            mode = 0

    def RBD(self, event):
        global mode
        if mode!=1:
            mode = 2

    def RBU(self, event):
        global mode
        if mode!=1:
            mode = 0

    def WHEEL(self, event):
        global r,rx,ry,rz
        if (event.GetWheelRotation() > 0):
            r = r/1.1
        elif (event.GetWheelRotation() < 0):
            r = r*1.1
        rx = r*np.sin(angleXZ)*np.cos(angleY)+trX
        ry = r*np.sin(angleY)+trY
        rz = r*np.cos(angleXZ)*np.cos(angleY)+trZ
        if (animate != 1):
            self.Refresh()

    def MouseMotion(self, event):
        global mode,r,angleY,angleXZ,temX,temY,trX,trY,trZ,rx,ry,rz
        if(event.Dragging()):
            xpos = event.GetX()
            ypos = event.GetY()
            if mode==1:
                angleXZ = angleXZ + (temX-xpos)*np.radians(0.3)
                angleY = angleY - (temY-ypos)*np.radians(0.3)
                rx = r*np.sin(angleXZ)*np.cos(angleY)+trX
                ry = r*np.sin(angleY)+trY
                rz = r*np.cos(angleXZ)*np.cos(angleY)+trZ
                temX = xpos
                temY = ypos
            elif mode==2:
                x = np.array([0,0,0])
                y = np.array([np.cos(angleXZ)*np.cos(angleY+np.radians(90)),np.sin(angleY+np.radians(90)),np.sin(angleXZ)*np.cos(angleY+np.radians(90))])
                if(np.cos(angleXZ)*np.sin(angleXZ) >= 0):
                    x = np.cross(y,np.array([np.cos(angleXZ)*np.cos(angleY),np.sin(angleY),np.sin(angleXZ)*np.cos(angleY)]))
                else:
                    x = -np.cross(y,np.array([np.cos(angleXZ)*np.cos(angleY),np.sin(angleY),np.sin(angleXZ)*np.cos(angleY)]))
                rx = r*np.sin(angleXZ)*np.cos(angleY)+trX
                ry = r*np.sin(angleY)+trY
                rz = r*np.cos(angleXZ)*np.cos(angleY)+trZ
                trX = trX + (temX-xpos)/100*x[0] - (temY-ypos)/100*y[0]
                trY = trY + (temX-xpos)/100*x[1] - (temY-ypos)/100*y[1]
                trZ = trZ + (temX-xpos)/100*x[2] - (temY-ypos)/100*y[2]
                temX = xpos
                temY = ypos
            else :
                temX = xpos
                temY = ypos
            if (animate != 1):
                self.Refresh()
        else:
            temX = event.GetX()
            temY = event.GetY()

    def Timeover(self, event):
        global frames, frame_num,posi,input_data,output_data,face,net,phase
        phase_update(output_data)
        output_data = net(output_to_input(output_data),phase).detach().numpy()
        face += output_data[515]
        po0 = output_data[513]/30.
        po2 = output_data[514]/30.
        f = face/180.*np.pi
        dx = np.cos(f)*po0 - np.sin(f)*po2
        dz = np.sin(f)*po0 + np.cos(f)*po2
        posi[0] += dx
        posi[2] += dz

        pastTraP.pop(0)
        for i in range(60):
            pastTraP[i][0] -= dx
            pastTraP[i][1] -= dz
        pastTraP.append([0.,0.])
        pastTraV.pop(0)
        tv = target_vel(keyboard)
        pastTraV.append([output_data[512],output_data[513]])
        nnPridicTraP = []
        nnPridicTraV = []
        for i in range(5):
            tpx = output_data[2*i+14]
            tpz = output_data[2*i+15]
            tvx = output_data[2*i+38]
            tvz = output_data[2*i+39]
            nnPridicTraP.append([tpx,tpz])
            nnPridicTraV.append([tvx,tvz])
        pridicTraP = blendT(nnPridicTraP,pridictPosition(tv))
        pridicTraV = blendV(nnPridicTraV,[tv,tv,tv,tv,tv])
        print(pridicTraP)
        for i in range(6):
            output_data[2*i] = pastTraP[10*i][0]
            output_data[2*i+1] = pastTraP[10*i][1]
            output_data[2*i+24] = pastTraV[10*i][0]
            output_data[2*i+25] = pastTraV[10*i][1]
        output_data[12] = 0.
        output_data[13] = 0.
        for i in range(5):
            output_data[2*i+14] = pridicTraP[i][0]
            output_data[2*i+15] = pridicTraP[i][1]
            output_data[2*i+38] = pridicTraV[i][0]
            output_data[2*i+39] = pridicTraV[i][1]
        self.text.SetValue(str(frame_num))
        self.Refresh()

    def Drop(self, event):
        global frame_num,face,posi
        filename = event.GetFiles()
        inpu = filename[0][:-4] + ".input"
        phase = filename[0][:-4] + ".phase"
        outp = filename[0][:-4] + ".output"
        frame_num = 0
        self.text.SetValue("0")
        if(self.timer.IsRunning()):
            self.timer.Stop()

        openBVH(filename)
        openNN(inpu,phase)
        #temopen(outp)
        posi = [0.,0.,0.]
        face = np.arctan2(0.9937087189756594,0.11199545451380696)*180/np.pi

        self.Refresh()

    def button1_event(self, event):
        global animate,start,handle_t,frame_num,frames
        if(handle_t == 0):
            wx.MessageBox("Put BVH file First!!","Error",wx.OK,self)
        elif(animate != 1):
            animate = 0
            frame_num -= 1
            if(frame_num < 0):
                frame_num = frames-1
            self.text.SetValue(str(frame_num))
            self.Refresh()

    def button2_event(self, event):
        global animate,start,handle_t,frame_time
        if(handle_t == 0):
            wx.MessageBox("Put BVH file First!!","Error",wx.OK,self)
        elif (animate != 1):
            animate = 1
            self.timer.Start(frame_time)
            self.button2.SetLabel("Stop")
            self.Refresh()
        else:
            animate = 0
            self.timer.Stop()
            self.button2.SetLabel("Start")
            self.Refresh()

    def button3_event(self, event):
        global animate,start,handle_t,frame_num,frames
        if(handle_t == 0):
            wx.MessageBox("Put BVH file First!!","Error",wx.OK,self)
        elif(animate != 1):
            animate = 0
            frame_num += 1
            if(frame_num >= frames):
                frame_num = 0
            self.text.SetValue(str(frame_num))
            self.Refresh()

    def button4_event(self, event):
        global frame_num,frames
        dlg = wx.TextEntryDialog(self, "Enter Frame", "")
        if (dlg.ShowModal()) == wx.ID_OK:
            if(IsInt(dlg.GetValue())):
                frame_num = int(dlg.GetValue())%frames
                self.text.SetValue(str(frame_num))
                self.Refresh()
        dlg.Destroy()

app = wx.App()

bvh = BVH()
bvh.Show(True)

app.MainLoop()