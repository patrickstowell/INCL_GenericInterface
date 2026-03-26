from helpful_functions import *
import numpy as np
ROOT.gSystem.Load("libNEUTROOTClass.so")
ROOT.gSystem.Load("libNEUTOutput.so")
ROOT.gSystem.Load("libNEUTReWeight.so")
ROOT.TH1.AddDirectory(False)



f = ROOT.TFile("test50k.root")
t = f.Get("neuttree")
i =0
proton_energies = []

noCascadeFSI = []
QE_deex = []
multipleNucleon_noCluster = []
nuclearCluster = []
oneProton = []
protonPion = []
other = []




for event in t:
    i+=1
    print(i)
    nvect = event.vectorbranch
    #nvect_reader(nvect).remnant()
    p_casc_energy,carbon11, nucleonCounter, clusterCounter, transparentProton, pion, photonCounter,proton = nvect_reader(nvect).proton_momentum_per_channel()

   
    if len(p_casc_energy) > 0:
        HMP_proton = np.asarray(p_casc_energy).max()
    else: 
        continue
    
    if (transparentProton == True) and (carbon11 == True) and (clusterCounter == 0) and (nucleonCounter == 1)  and (pion == False) and (photonCounter == False):
        noCascadeFSI.append(HMP_proton)
        print("nocascadefsi")
    elif (transparentProton == True) and (clusterCounter != 0):
        QE_deex.append(HMP_proton)
    elif (transparentProton == False) and (proton == True) and (clusterCounter < 2 ) and (nucleonCounter > 1)  and (pion == False) and (photonCounter == False):
        multipleNucleon_noCluster.append(HMP_proton)
    elif (transparentProton == False) and (proton == True) and (clusterCounter >=2) and (nucleonCounter >= 1):
        nuclearCluster.append(HMP_proton)
    elif (transparentProton == False) and (proton == True) and (clusterCounter ==0 ) and (nucleonCounter ==1 )  and (pion == False) and (photonCounter == False):
        oneProton.append(HMP_proton)
    elif (transparentProton == False) and (proton == True) and (nucleonCounter >1 )  and (pion == True) and (photonCounter == False):
        protonPion.append(HMP_proton)
    else:
        print("transparentProton | proton  | nucleonCounter  | pion |photonCounter")
        print( transparentProton, " " , proton, " " ,nucleonCounter, " " , pion, " ", photonCounter)
        other.append(HMP_proton)


        nvect_reader(nvect).Print()
        
        



c1 = ROOT.TCanvas("c1", "Proton Momentum Distributions", 800, 600)

legend = ROOT.TLegend(0.6, 0.65, 0.88, 0.88)
legend.SetBorderSize(0)
legend.SetTextSize(0.03)


n_bins = 50
x_min = 0.0
x_max = 1500.0  


def create_histo(name, title, color, data_array):
    h = ROOT.TH1F(name, title, n_bins, x_min, x_max)
    h.SetLineColor(color)
    h.SetLineWidth(2)
    h.SetStats(0) 

    for value in data_array:
        h.Fill(value)
        
    return h

h_noCascade  = create_histo("h1", "No Cascade FSI",       ROOT.kRed,     noCascadeFSI)
h_QE         = create_histo("h2", "QE De-excitation",     ROOT.kBlue,    QE_deex)
h_multiNuc   = create_histo("h3", "Multi-Nucleon No Cl.", ROOT.kGreen+2, multipleNucleon_noCluster)
h_nucCluster = create_histo("h4", "Nuclear Cluster",      ROOT.kMagenta, nuclearCluster)
h_oneProton  = create_histo("h5", "One Proton",           ROOT.kCyan+1,  oneProton)
h_protonPion = create_histo("h6", "Proton + Pion",        ROOT.kOrange+7,protonPion)
h_other      = create_histo("h7", "Other",                ROOT.kBlack,   other)


hs = ROOT.THStack("hs", "Proton Momentum by Channel;Momentum [MeV/c];Events")



hs.Add(h_protonPion)
hs.Add(h_other)
hs.Add(h_oneProton)
hs.Add(h_multiNuc)
hs.Add(h_nucCluster)
hs.Add(h_noCascade)
hs.Add(h_QE)


legend.AddEntry(h_noCascade, "No Cascade FSI", "l")
legend.AddEntry(h_QE, "QE De-excitation", "l")
legend.AddEntry(h_multiNuc, "Multi-Nucleon (No Clust)", "l")
legend.AddEntry(h_nucCluster, "Nuclear Cluster", "l")
legend.AddEntry(h_oneProton, "One Proton", "l")
legend.AddEntry(h_protonPion, "Proton + Pion", "l")
legend.AddEntry(h_other, "Other", "l")


hs.Draw("hist") 

legend.Draw()

c1.Update()


c1.SaveAs("proton_channels.png")
c1.SaveAs("proton_channels.root") # Save as root file to edit later


input("Press Enter to exit...")

