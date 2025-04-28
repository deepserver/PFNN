import sys
import os
import torch
import torch.nn as nn
import torch.nn.functional as F

inp = 384
outp = 554
hid1 = 256
hid2 = 256

def work(net, inp,outp,p):
    input1 = []
    output = []
    phase = []
    num = 0
    with open(inpu,'r') as fi:
        tem = fi.read().split('\n')
        for i in range(len(tem)):
            if(len(tem[i]) != 0):
                input1.append([])
                for data in tem[i].split('\t'):
                    input1[i].append(float(data))

    with open(outpu,'r') as fi:
        tem = fi.read().split('\n')
        for i in range(len(tem)):
            if(len(tem[i]) != 0):
                output.append([])
                for data in tem[i].split('\t'):
                    output[i].append(float(data))

    with open(p,'r') as fi:
        tem = fi.read().split('\n')
        for i in range(61,len(tem)):
            if(len(tem[i]) != 0):
                phase.append(float(tem[i]))

    criterion = nn.MSELoss(reduction='mean')
    optimizer = torch.optim.SGD(net.parameters(), lr= 0.000001, weight_decay = 0.01)

    for i in range(100):
        num = 0
        while(num < len(input1) and num < len(output)):
            t_input = torch.tensor(input1[num])
            t_output = torch.tensor(output[num])
            out = net(t_input,phase[num])

            loss = criterion(out, t_output)
            if(num%100 == 0):
                print(loss)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            num += 1

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
        w = (phase*4.)%1
        k = -(int(phase*-4.))
        li = [[self.fc01,self.fc02,self.fc03],[self.fc11,self.fc12,self.fc13],[self.fc21,self.fc22,self.fc23],[self.fc31,self.fc32,self.fc33]]
        a1 = li[k%4]
        a2 = li[(k+1)%4]
        a3 = li[(k+2)%4]
        a4 = li[(k+3)%4]
        hid_lay1 = F.elu(a1[0](x) + w*(a2[0](x)/2. - a4[0](x)/2.) + (w**2.)*(a4[0](x)-a1[0](x)*5./2. + 2.*a2[0](x) - a3[0](x)/2.) + (w**3.)*(a1[0](x)*3./2. - a2[0](x)*3./2. + a3[0](x)/2. - a4[0](x)/2.))
        hid_lay2 = F.elu(a1[1](hid_lay1) + w*(a2[1](hid_lay1)/2. - a4[1](hid_lay1)/2.) + (w**2.)*(a4[1](hid_lay1)-a1[1](hid_lay1)*5./2. + 2.*a2[1](hid_lay1) - a3[1](hid_lay1)/2.) + (w**3.)*(a1[1](hid_lay1)*3./2. - a2[1](hid_lay1)*3./2. + a3[1](hid_lay1)/2. - a4[1](hid_lay1)/2.))
        out =  (a1[2](hid_lay2) + w*(a2[2](hid_lay2)/2. - a4[2](hid_lay2)/2.) + (w**2.)*(a4[2](hid_lay2)-a1[2](hid_lay2)*5./2. + 2.*a2[2](hid_lay2) - a3[2](hid_lay2)/2.) + (w**3.)*(a1[2](hid_lay2)*3./2. - a2[2](hid_lay2)*3./2. + a3[2](hid_lay2)/2. - a4[2](hid_lay2)/2.))
        return out


net = Net()

filepath = "C:\\Users\\chang\\Desktop\\PFNN_chang"
for (path, dir, files) in os.walk(filepath):
    for filename in files:
        ext = os.path.splitext(filename)[-1]
        if ext == '.bvh':
            inpu = path + "\\" + filename[:-4] + ".input"
            outpu = path + "\\" + filename[:-4] + ".output"
            phase = path + "\\" + filename[:-4] + ".phase"
            work(net, inpu, outpu, phase)