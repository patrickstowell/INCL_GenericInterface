import numpy as np
import sys 
import ROOT
ROOT.gSystem.Load("libNEUTROOTClass.so")
ROOT.gSystem.Load("libNEUTOutput.so")
ROOT.gSystem.Load("libNEUTReWeight.so")
ROOT.TH1.AddDirectory(False)


f = ROOT.TFile("out_cc0pi_inclcascade.root")
t = f.Get("neuttree")
for event in t:
    nvect = event.vectorbranch
    nopart = nvect.Npart()
    print("new event")
    for i in range(nopart):
        
        pinfo = nvect.PartInfo(i)
        print(i, " ", pinfo.fIsAlive,"       ",nvect.ParentIdx(i),"              ", pinfo.fPID, "    ",pinfo.fP.X(), pinfo.fP.Y(), pinfo.fP.Z(), pinfo.fMass)
        pinfo.fP.X()**2 + pinfo.fP.X()**2 +pinfo.fP.Y()**2
        
        P = (pinfo.fP.X()**2 + pinfo.fP.Y()**2 +pinfo.fP.Z()**2)
        print("energy", np.sqrt(P+pinfo.fMass**2)-pinfo.fMass)
