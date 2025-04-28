import wx
from wx import *
from OpenGL.GL import *
import numpy as np 
from OpenGL.GLU import *
from wx.glcanvas import *


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
    animate = -1
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

def draw(tem):
    if(np.dot(tem,tem) != 0):
        glColor3ub(255, 255, 255) 
        glBegin(GL_LINES)
        glVertex3fv(np.array([0.,0.,0.]))
        glVertex3fv(tem)
        glEnd()


def drawmodel():
    global offset,level_list,motion,min_y,frame,frame_time,animate,frames,X,Y,Z, frame_num
    i = 1
    n = 1
    last = 0
    m = 0
    glPushMatrix()
    glTranslatef(0.,-min_y,0.)
    if(animate != -1):
        glTranslatef(-motion[0][0]/30,-motion[0][1]/30,-motion[0][2]/30)
    glPushMatrix()
    if(animate != -1):
        m = frame_num
        glTranslatef(motion[m][0]/30,motion[m][1]/30,motion[m][2]/30)
        glRotatef(motion[m][3], X[0], Y[0], Z[0]) 
        glRotatef(motion[m][4], X[1], Y[1], Z[1]) 
        glRotatef(motion[m][5], X[2], Y[2], Z[2]) 
    while(len(offset)>i):
        tem = np.array(offset[i])
        if(level_list[i-1] <= level_list[i]):
            draw(tem)
            if(not(is_end_site(i))):
                glPushMatrix()
                glTranslatef(tem[0],tem[1],tem[2])
                if(animate != -1):
                    glRotatef(motion[m][3*n+3], X[3*n], Y[3*n], Z[3*n]) 
                    glRotatef(motion[m][3*n+4], X[3*n+1], Y[3*n+1], Z[3*n+1]) 
                    glRotatef(motion[m][3*n+5], X[3*n+2], Y[3*n+2], Z[3*n+2]) 
                    n = n + 1
        else:
            ii = level_list[i-1]-level_list[i]
            for t in range(ii):
                glPopMatrix()
            draw(tem)
            if(not(is_end_site(i))):
                glPushMatrix()
                glTranslatef(tem[0],tem[1],tem[2])
                if(animate != -1):
                    glRotatef(motion[m][3*n+3], X[3*n], Y[3*n], Z[3*n]) 
                    glRotatef(motion[m][3*n+4], X[3*n+1], Y[3*n+1], Z[3*n+1]) 
                    glRotatef(motion[m][3*n+5], X[3*n+2], Y[3*n+2], Z[3*n+2]) 
                    n = n + 1
        last = level_list[i]
        i = i+1
    for tt in range(last-1):
        glPopMatrix()
    glPopMatrix()
    glPopMatrix()

def render():
    global r,angleXZ,angleY,trX,trY,trZ,filled,l0,l1,rx,ry,rz
    glClear(GL_COLOR_BUFFER_BIT) 
    glEnable(GL_DEPTH_TEST) 
    glLoadIdentity()
    gluPerspective(45, 1, 1,25)

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
    drawmodel()
    
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
        self.Bind(wx.EVT_DROP_FILES, self.Drop)
        self.Bind(wx.EVT_TIMER, self.Timeover)
        self.Show(True)

    def OnDraw(self,event):
        Context = wx.glcanvas.GLContext(self.canvas)
        self.canvas.SetCurrent(Context)
        render()

        self.canvas.SwapBuffers()

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
        global frames, frame_num
        frame_num += 1
        if(frame_num >= frames):
            frame_num = 0
        self.text .SetValue(str(frame_num))
        self.Refresh()

    def Drop(self, event):
        global frame_num
        filename = event.GetFiles()
        frame_num = 0
        self.text.SetValue("0")
        if(self.timer.IsRunning()):
            self.timer.Stop()
        openBVH(filename)
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