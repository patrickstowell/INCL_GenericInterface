import ROOT
import sys 
import numpy as np
import math
ROOT.gSystem.Load("libNEUTROOTClass.so")
ROOT.gSystem.Load("libNEUTOutput.so")
ROOT.gSystem.Load("libNEUTReWeight.so")





f = ROOT.TFile("out_mp_test.root")
t = f.Get("neuttree")


for event in t:
    nvect = event.vectorbranch

    for i in range(nvect.Npart()):
        pinfo = nvect.PartInfo(i)
        print(i, " ", pinfo.fIsAlive,"       " , pinfo.fStatus,"  ",nvect.ParentIdx(i),"              ", pinfo.fPID, "    ",pinfo.fP.X(), pinfo.fP.Y(), pinfo.fP.Z(), pinfo.fMass)
        if  ( i == 2 and pinfo.fPID == 14 and pinfo.fIsAlive != 1 and  pinfo.fStatus != 0):
            input("Missing something...")