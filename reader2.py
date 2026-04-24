from helpful_functions import *
import numpy as np
import sys 

ROOT.gSystem.Load("libNEUTROOTClass.so")
ROOT.gSystem.Load("libNEUTOutput.so")
ROOT.gSystem.Load("libNEUTReWeight.so")
ROOT.TH1.AddDirectory(False)

def create_histo(name, title, color, fill_style, data,n_bins,x_min,x_max):

    h = ROOT.TH1F(name, title, n_bins, x_min, x_max)
    for val in data:
        h.Fill(val)
    
    h.SetLineColor(color-2)  
    h.SetLineWidth(2)
    h.SetFillColor(color)
    h.SetFillStyle(fill_style) 
    
    # h.SetStats(0)
    return h


def main():
    filename = sys.argv[1]
    filename_chunk = filename.split(".")[0].split("out_")[1]

    f = ROOT.TFile(filename)
    t = f.Get("neuttree")
    i =0
    proton_energies = []
    other_counter = 0
    src_counter = 0
    evt_counter = 0

    noCascadeFSI_pt = []
    QE_deex_pt = []
    multipleNucleon_noCluster_pt = []
    multipleNucleon_noCluster_pt_src = []
    nuclearCluster_pt = []
    nuclearCluster_pt_src = []
    oneProton_pt = []
    protonPion_pt = []
    other_pt = []

    noCascadeFSI_at = []
    QE_deex_at = []
    multipleNucleon_noCluster_at = []
    multipleNucleon_noCluster_at_src = []
    nuclearCluster_at = []
    nuclearCluster_at_src = []
    oneProton_at = []
    protonPion_at = []
    other_at = []

    noCascadeFSI = []
    QE_deex = []
    multipleNucleon_noCluster = []
    multipleNucleon_noCluster_src = []
    nuclearCluster = []
    nuclearCluster_src = []
    oneProton = []
    protonPion = []
    other = []

    noCascadeFSI_pre = []
    QE_deex_pre = []
    multipleNucleon_noCluster_pre = []
    multipleNucleon_noCluster_pre_src = []
    nuclearCluster_pre = []
    nuclearCluster_pre_src = []
    oneProton_pre = []
    protonPion_pre = []
    mu_only = []
    no_protons = []
    other_pre = []
    """
    for event in t:
        i+=1
        #print(i)
        nvect = event.vectorbranch
        #nvect_reader(nvect).remnant()
        nvect_class = nvect_reader(nvect)
        nvect_class.Print()
        if (nvect_class.src() == True):
            pass
            #print("src")
            #input(" ")
    """
   
    for event in t:
        i+=1
        #print(i)
        nvect = event.vectorbranch
        #nvect_reader(nvect).remnant()
        nvect_class = nvect_reader(nvect)
        nvect_class.Print()
        p_casc_energy,nuclear_remnant, nucleonCounter, clusterCounter, transparentProton, pion, photonCounter,proton,prefsi_proton_mom, deex_event = nvect_class.proton_momentum_per_channel()
        src = False
        evt_counter +=1
        if src == True:
            src_counter +=1 
            #continue

        if proton == True:
            HMP_proton = np.asarray(p_casc_energy).max()
        else: 
            no_protons.append(prefsi_proton_mom)
            #if (nucleonCounter > 0) or (pion == True) or (clusterCounter > 0) or (photonCounter > 0):
            #    
            #else:
            #    mu_only.append(prefsi_proton_mom)
            #    nvect_reader(nvect).Print()
            continue

        DPT, dat = nvect_class.get_deltaPT()
        
        if (transparentProton == True) and (clusterCounter == 0) and (proton == True)  and (pion == False) and (photonCounter == False) and (deex_event == False):
            nvect_class.Print()
            noCascadeFSI.append(HMP_proton)
            noCascadeFSI_at.append(dat)
            noCascadeFSI_pt.append(DPT)
            if(prefsi_proton_mom != 0):
                noCascadeFSI_pre.append(prefsi_proton_mom)
            else:
                noCascadeFSI_pre.append(HMP_proton)

        elif (transparentProton == True) and (deex_event == True) and (proton == True):  
            QE_deex.append(HMP_proton)
            QE_deex_at.append(dat)
            QE_deex_pt.append(DPT)
            QE_deex_pre.append(prefsi_proton_mom)
        
        elif (transparentProton == False) and (proton == True) and (clusterCounter == 0) and (nucleonCounter == 1)  and (pion == False):
            #nvect_class.Print()
            oneProton.append(HMP_proton)
            oneProton_at.append(dat)
            oneProton_pt.append(DPT)
            oneProton_pre.append(prefsi_proton_mom)
        

        elif (transparentProton == False) and (proton == True) and (clusterCounter == 0 ) and (nucleonCounter > 1)  and (pion == False):
            if src == False:
                multipleNucleon_noCluster.append(HMP_proton)
                multipleNucleon_noCluster_at.append(dat)
                multipleNucleon_noCluster_pt.append(DPT)
                multipleNucleon_noCluster_pre.append(prefsi_proton_mom)
            elif src == True:
                multipleNucleon_noCluster_src.append(HMP_proton)
                multipleNucleon_noCluster_at_src.append(dat)
                multipleNucleon_noCluster_pt_src.append(DPT)
                multipleNucleon_noCluster_pre_src.append(prefsi_proton_mom)
        
        elif (transparentProton == False) and (proton == True) and (clusterCounter >= 1) and (nucleonCounter >= 1):
            if src == False:
                nuclearCluster.append(HMP_proton)
                nuclearCluster_at.append(dat)
                nuclearCluster_pt.append(DPT)
                nuclearCluster_pre.append(prefsi_proton_mom)
            else:
                nuclearCluster_src.append(HMP_proton)
                nuclearCluster_at_src.append(dat)
                nuclearCluster_pt_src.append(DPT)
                nuclearCluster_pre_src.append(prefsi_proton_mom)


        elif (transparentProton == False) and (proton == True) and (clusterCounter == 0)  and (pion == True):   
            protonPion.append(HMP_proton)
            protonPion_at.append(dat)
            protonPion_pt.append(DPT)
            protonPion_pre.append(prefsi_proton_mom)
            
        else:
            other_counter +=1 
            nvect_class.Print()
            #input(" ")
            #print("transparentProton | proton  | nucleonCounter  | pion |photonCounter")
            #print( transparentProton, " " , proton, " " ,nucleonCounter, " " , pion, " ", photonCounter)
            #input(" ")
            other.append(HMP_proton)
            other_at.append(dat)
            other_pt.append(DPT)
            other_pre.append(prefsi_proton_mom)

    print("total src events" , src_counter/evt_counter)
    print("other counter", other_counter)  
    file = ROOT.TFile("proton_channels_{}_test.root".format(filename_chunk),"RECREATE")

    c1 = ROOT.TCanvas("c1", "Proton Momentum Distributions", 800, 600)
    c1.cd() 
    pad1 = ROOT.TPad("pad1", "pad1", 0, 0.3, 1, 1.0)
    pad1.SetBottomMargin(0.02) 
    pad1.SetLeftMargin(0.12)
    pad1.SetTicks(1, 1)        
    pad1.Draw()

    pad2 = ROOT.TPad("pad2", "pad2", 0, 0.0, 1, 0.3)
    pad2.SetTopMargin(0.01)  
    pad2.SetBottomMargin(0.25) 
    pad2.SetLeftMargin(0.12)
    pad2.SetTicks(1, 1)
    pad2.Draw()

    n_bins = 40
    x_min = 0
    x_max = 1500   

    h_nucCluster = create_histo("h_nuc", "Nuclear Clusters",       ROOT.kViolet-4, 3001, nuclearCluster,n_bins,x_min,x_max)
    h_nucCluster_src = create_histo("h_nuc_src", "Nuclear Clusters, SRC",       ROOT.kViolet-1, 3001, nuclearCluster_src,n_bins,x_min,x_max)
    h_noCascade  = create_histo("h_noC", "No Cascade FSI",         ROOT.kOrange-4, 3001, noCascadeFSI,n_bins,x_min,x_max)
    h_QE         = create_histo("h_qe",  "QE Proton + De-ex",      ROOT.kOrange+7, 3001, QE_deex,n_bins,x_min,x_max)
    h_multiNuc   = create_histo("h_mul", "Multiple Nucleons",      ROOT.kRed+2,    3001, multipleNucleon_noCluster,n_bins,x_min,x_max)
    h_multiNuc_src = create_histo("h_mul_src", "Multiple Nucleons, SRC",      ROOT.kRed,    3001, multipleNucleon_noCluster_src,n_bins,x_min,x_max)
    h_oneProton  = create_histo("h_one", "One Proton",             ROOT.kGreen,  3001, oneProton,n_bins,x_min,x_max)
    h_protonPion = create_histo("h_pion","Proton + Pion",          ROOT.kYellow-9, 3001, protonPion,n_bins,x_min,x_max)
    h_other      = create_histo("h_oth", "Other",                  ROOT.kGray,     3001, other,n_bins,x_min,x_max)

    pad1.cd() 

    hs = ROOT.THStack("hs", "Proton Momentum by Channel;Momentum [MeV/c];Events")
    hs.Add(h_protonPion)
    hs.Add(h_other)
    hs.Add(h_oneProton)
    hs.Add(h_multiNuc)
    hs.Add(h_multiNuc_src)
    hs.Add(h_nucCluster)
    hs.Add(h_nucCluster_src)
    hs.Add(h_noCascade)
    hs.Add(h_QE)

    hs.Draw("hist") 
    hs.GetXaxis().SetLabelSize(0)
    hs.SetTitle("; ;Number of Events") 


    hs.GetYaxis().SetLabelSize(0.04)
    hs.GetYaxis().SetTitleSize(0.05)
    hs.GetYaxis().SetTitleOffset(1.1)

    max_h = hs.GetMaximum()
    hs.SetMaximum(max_h * 1.2) 

    total_integral = sum(hist.Integral() for hist in hs.GetHists())

    print(f"Total visible events in the stack: {total_integral}")


    legend = ROOT.TLegend(0.55, 0.55, 0.88, 0.88)
    legend.SetBorderSize(0)
    legend.SetFillStyle(0) # Transparent
    legend.AddEntry(h_noCascade, "no cascade FSI", "f")
    legend.AddEntry(h_QE, "QE proton + de-excitation", "f")
    legend.AddEntry(h_multiNuc, "multiple nucleons", "f")
    legend.AddEntry(h_multiNuc_src, "multiple nucleons, SRC", "f")
    legend.AddEntry(h_nucCluster, "nuclear clusters", "f")
    legend.AddEntry(h_nucCluster_src, "nuclear clusters", "f")
    legend.AddEntry(h_oneProton, "one proton", "f")
    legend.AddEntry(h_protonPion, "proton + pion", "f")
    legend.Draw()


    pad2.cd() 

    h_total = h_nucCluster.Clone("h_total")
    h_total.Add(h_nucCluster_src)
    h_total.Add(h_noCascade)
    h_total.Add(h_QE)
    h_total.Add(h_multiNuc)
    h_total.Add(h_multiNuc_src)
    h_total.Add(h_oneProton)
    h_total.Add(h_protonPion)
    h_total.Add(h_other)


    def create_ratio(h_in, h_tot):
        h_ratio = h_in.Clone(h_in.GetName() + "_ratio")
        h_ratio.Divide(h_tot) 


        h_ratio.SetFillStyle(0)
        h_ratio.SetLineWidth(2)
        h_ratio.SetLineColor(h_in.GetLineColor()) 
        return h_ratio

    r_nuc   = create_ratio(h_nucCluster, h_total) + create_ratio(h_nucCluster_src, h_total)
    
    r_noCas = create_ratio(h_noCascade, h_total)
    r_qe    = create_ratio(h_QE, h_total)
    r_mul   = create_ratio(h_multiNuc, h_total) + create_ratio(h_multiNuc_src, h_total)
    #r_mul_src   = create_ratio(h_multiNuc_src, h_total)
    r_one   = create_ratio(h_oneProton, h_total)
    r_pion  = create_ratio(h_protonPion, h_total)


    r_nuc.Draw("HIST") 
    r_nuc.SetTitle(";P_{aft} (GeV/c);Fractional Contributions")


    y_axis = r_nuc.GetYaxis()
    y_axis.SetRangeUser(0, 1.1)
    y_axis.SetNdivisions(505)
    y_axis.SetLabelSize(0.08)
    y_axis.SetTitleSize(0.09)
    y_axis.SetTitleOffset(0.5)

    x_axis = r_nuc.GetXaxis()
    x_axis.SetLabelSize(0.08)
    x_axis.SetTitleSize(0.10)
    x_axis.SetTitleOffset(1.0)

    r_noCas.Draw("HIST SAME")
    r_qe.Draw("HIST SAME")
    r_mul.Draw("HIST SAME")
    #r_mul_src.Draw("hist SAME")
    r_one.Draw("HIST SAME")
    r_pion.Draw("HIST SAME")

    c1.Update()
    #c1.SaveAs("proton_fractional_plot_{}_newdefs.png".format(filename_chunk))

    c2 = ROOT.TCanvas("c2", "deltaPT", 800, 600)
    c2.cd()

    n_bins = 50    
    x_min = 0
    x_max = 1000   

    h_nucCluster = create_histo("h_nuc_pt", "Nuclear Clusters",       ROOT.kViolet-4, 3001, nuclearCluster_pt,n_bins,x_min,x_max)
    h_noCascade  = create_histo("h_noC_pt", "No Cascade FSI",         ROOT.kOrange-4, 3001, noCascadeFSI_pt,n_bins,x_min,x_max)
    h_QE         = create_histo("h_qe_pt",  "QE Proton + De-ex",      ROOT.kOrange+7, 3001, QE_deex_pt,n_bins,x_min,x_max)
    h_multiNuc   = create_histo("h_mul_pt", "Multiple Nucleons",      ROOT.kRed+2,    3001, multipleNucleon_noCluster_pt,n_bins,x_min,x_max)
    h_oneProton  = create_histo("h_one_pt", "One Proton",             ROOT.kGreen,  3001, oneProton_pt,n_bins,x_min,x_max)
    h_protonPion = create_histo("h_pion_pt","Proton + Pion",          ROOT.kYellow-9, 3001, protonPion_pt,n_bins,x_min,x_max)
    h_other      = create_histo("h_oth_pt", "Other",                  ROOT.kGray,     3001, other_pt,n_bins,x_min,x_max)


    hs1 = ROOT.THStack("hs_pt", "DPT by Channel;Momentum [MeV/c];Events")
    hs1.Add(h_protonPion)
    hs1.Add(h_other)
    hs1.Add(h_oneProton)
    hs1.Add(h_multiNuc)
    hs1.Add(h_nucCluster)
    hs1.Add(h_noCascade)
    hs1.Add(h_QE)


    hs1.Draw("hist") 
    hs1.SetTitle("; DPT;Number of Events") 

    hs1.GetYaxis().SetLabelSize(0.03)
    hs1.GetYaxis().SetTitleSize(0.04)
    hs1.GetYaxis().SetTitleOffset(1.1)

    hs1.GetXaxis().SetTitle("DPT")

    max_h = hs1.GetMaximum()
    hs1.SetMaximum(max_h * 1.2) 

    legend1 = ROOT.TLegend(0.55, 0.55, 0.88, 0.88)
    legend1.SetBorderSize(0)
    legend1.SetFillStyle(0) # Transparent
    legend1.AddEntry(h_noCascade, "no cascade FSI", "f")
    legend1.AddEntry(h_QE, "QE proton + de-excitation", "f")
    legend1.AddEntry(h_multiNuc, "multiple nucleons", "f")
    legend1.AddEntry(h_nucCluster, "nuclear clusters", "f")
    legend1.AddEntry(h_oneProton, "one proton", "f")
    legend1.AddEntry(h_protonPion, "proton + pion", "f")

    legend1.Draw()




    c3 = ROOT.TCanvas("c3", "deltaPT", 800, 600)
    c3.cd()

    n_bins = 50    
    x_min = 0
    x_max = 180  

    h_nucCluster = create_histo("h_nuc_at", "Nuclear Clusters",       ROOT.kViolet-4, 3001, nuclearCluster_at,n_bins,x_min,x_max)
    h_noCascade  = create_histo("h_noC_at", "No Cascade FSI",         ROOT.kOrange-4, 3001, noCascadeFSI_at,n_bins,x_min,x_max)
    h_QE         = create_histo("h_qe_at",  "QE Proton + De-ex",      ROOT.kOrange+7, 3001, QE_deex_at,n_bins,x_min,x_max)
    h_multiNuc   = create_histo("h_mul_at", "Multiple Nucleons",      ROOT.kRed+2,    3001, multipleNucleon_noCluster_at,n_bins,x_min,x_max)
    h_oneProton  = create_histo("h_one_at", "One Proton",             ROOT.kGreen,  3001, oneProton_at,n_bins,x_min,x_max)
    h_protonPion = create_histo("h_pion_at","Proton + Pion",          ROOT.kYellow-9, 3001, protonPion_at,n_bins,x_min,x_max)
    h_other      = create_histo("h_oth_at", "Other",                  ROOT.kGray,     3001, other_at,n_bins,x_min,x_max)


    hs2 = ROOT.THStack("hs_at", "DaT by Channel;Momentum [MeV/c];Events")
    hs2.Add(h_noCascade)
    hs2.Add(h_QE)
    hs2.Add(h_oneProton)
    hs2.Add(h_protonPion)
    hs2.Add(h_multiNuc)
    hs2.Add(h_other)
    hs2.Add(h_nucCluster)


    hs2.Draw("hist") 
    hs2.SetTitle("; DaT;Number of Events") 

    hs2.GetYaxis().SetLabelSize(0.03)
    hs2.GetYaxis().SetTitleSize(0.04)
    hs2.GetYaxis().SetTitleOffset(1.1)

    hs2.GetXaxis().SetTitle("DaT")

    max_h = hs2.GetMaximum()
    hs2.SetMaximum(max_h * 1.2) 

    legend2 = ROOT.TLegend(0.55, 0.55, 0.88, 0.88)
    legend2.SetBorderSize(0)
    legend2.SetFillStyle(0) # Transparent
    legend2.AddEntry(h_noCascade, "no cascade FSI", "f")
    legend2.AddEntry(h_QE, "QE proton + de-excitation", "f")
    legend2.AddEntry(h_multiNuc, "multiple nucleons", "f")
    legend2.AddEntry(h_nucCluster, "nuclear clusters", "f")
    legend2.AddEntry(h_oneProton, "one proton", "f")
    legend2.AddEntry(h_protonPion, "proton + pion", "f")

    legend2.Draw()

    c4 = ROOT.TCanvas("c4", "Proton Momentum Distributions", 800, 600)
    c4.cd() 
    pad3 = ROOT.TPad("pad3", "pad3", 0, 0.3, 1, 1.0)
    pad3.SetBottomMargin(0.02) 
    pad3.SetLeftMargin(0.12)
    pad3.SetTicks(1, 1)        
    pad3.Draw()

    pad4 = ROOT.TPad("pad4", "pad4", 0, 0.0, 1, 0.3)
    pad4.SetTopMargin(0.01)  
    pad4.SetBottomMargin(0.25) 
    pad4.SetLeftMargin(0.12)
    pad4.SetTicks(1, 1)
    pad4.Draw()

    n_bins = 90    
    x_min = 0
    x_max = 1500   

    h_nucCluster_pre = create_histo("h_nuc_prefsi", "Nuclear Clusters",       ROOT.kViolet-4, 3001, nuclearCluster_pre,n_bins,x_min,x_max)
    h_noCascade_pre  = create_histo("h_noC_prefsi", "No Cascade FSI",         ROOT.kOrange-4, 3001, noCascadeFSI_pre,n_bins,x_min,x_max)
    h_QE_pre         = create_histo("h_qe_prefsi",  "QE Proton + De-ex",      ROOT.kOrange+7, 3001, QE_deex_pre,n_bins,x_min,x_max)
    h_multiNuc_pre   = create_histo("h_mul_prefsi", "Multiple Nucleons",      ROOT.kRed+2,    3001, multipleNucleon_noCluster_pre,n_bins,x_min,x_max)
    h_oneProton_pre  = create_histo("h_one_prefsi", "One Proton",             ROOT.kGreen,    3001, oneProton_pre,n_bins,x_min,x_max)
    h_protonPion_pre = create_histo("h_pion_prefsi","Proton + Pion",          ROOT.kYellow-9, 3001, protonPion_pre,n_bins,x_min,x_max)
    h_muonly_pre     = create_histo("h_muonly_prefsi","muonly",               ROOT.kViolet-9,  3001, mu_only,n_bins,x_min,x_max)
    h_noproton_pre   = create_histo("h_noproton_prefsi","no protons",         ROOT.kGreen-9,  3001, no_protons,n_bins,x_min,x_max)
    h_other_pre      = create_histo("h_oth_prefsi", "Other",                  ROOT.kGray,     3001, other_pre,n_bins,x_min,x_max)

    pad3.cd() 

    hs3 = ROOT.THStack("hs3", "Proton Momentum by Channel;Momentum [MeV/c];Events")
    hs3.Add(h_protonPion_pre)
    hs3.Add(h_other_pre)
    hs3.Add(h_oneProton_pre)
    hs3.Add(h_multiNuc_pre)
    hs3.Add(h_nucCluster_pre)
    hs3.Add(h_noCascade_pre)
    hs3.Add(h_QE_pre)
    hs3.Add(h_muonly_pre)
    hs3.Add(h_noproton_pre)

    hs3.Draw("hist") 
    hs3.GetXaxis().SetLabelSize(0)
    hs3.SetTitle("; ;Number of Events") 


    hs3.GetYaxis().SetLabelSize(0.04)
    hs3.GetYaxis().SetTitleSize(0.05)
    hs3.GetYaxis().SetTitleOffset(1.1)

    max_h = hs3.GetMaximum()
    hs3.SetMaximum(max_h * 1.2) 

    total_integral = sum(hist.Integral() for hist in hs2.GetHists())

    print(f"Total visible events in the stack: {total_integral}")


    legend4 = ROOT.TLegend(0.55, 0.55, 0.88, 0.88)
    legend4.SetBorderSize(0)
    legend4.SetFillStyle(0) # Transparent
    legend4.AddEntry(h_noCascade_pre, "no cascade FSI", "f")
    legend4.AddEntry(h_QE_pre, "QE proton + de-excitation", "f")
    legend4.AddEntry(h_multiNuc_pre, "multiple nucleons", "f")
    legend4.AddEntry(h_nucCluster_pre, "nuclear clusters", "f")
    legend4.AddEntry(h_oneProton_pre, "one proton", "f")
    legend4.AddEntry(h_protonPion_pre, "proton + pion", "f")
    legend4.AddEntry(h_muonly_pre, "mu only", "f")
    legend4.AddEntry(h_noproton_pre, "no protons", "f")
    legend4.Draw()


    pad4.cd() 

    h_total2 = h_nucCluster_pre.Clone("h_total")
    h_total2.Add(h_noCascade_pre)
    h_total2.Add(h_QE_pre)
    h_total2.Add(h_multiNuc_pre)
    h_total2.Add(h_oneProton_pre)
    h_total2.Add(h_protonPion_pre)
    h_total2.Add(h_other_pre)


    def create_ratio(h_in, h_tot):
        h_ratio = h_in.Clone(h_in.GetName() + "_ratio")
        h_ratio.Divide(h_tot) 


        h_ratio.SetFillStyle(0)
        h_ratio.SetLineWidth(2)
        h_ratio.SetLineColor(h_in.GetLineColor()) 
        return h_ratio

    r_nuc1   = create_ratio(h_nucCluster_pre, h_total2)
    r_noCas1 = create_ratio(h_noCascade_pre, h_total2)
    r_qe1    = create_ratio(h_QE_pre, h_total2)
    r_mul1   = create_ratio(h_multiNuc_pre, h_total2)
    r_one1   = create_ratio(h_oneProton_pre, h_total2)
    r_pion1  = create_ratio(h_protonPion_pre, h_total2)
    r_muonly1= create_ratio(h_muonly_pre, h_total2)
    r_noproton =create_ratio(h_noproton_pre, h_total2)


    r_nuc1.Draw("HIST") 
    r_nuc1.SetTitle(";P_{aft} (GeV/c);Fractional Contributions")


    y_axis = r_nuc1.GetYaxis()
    y_axis.SetRangeUser(0, 1.1)
    y_axis.SetNdivisions(505)
    y_axis.SetLabelSize(0.08)
    y_axis.SetTitleSize(0.09)
    y_axis.SetTitleOffset(0.5)

    x_axis = r_nuc1.GetXaxis()
    x_axis.SetLabelSize(0.08)
    x_axis.SetTitleSize(0.10)
    x_axis.SetTitleOffset(1.0)


    r_noCas1.Draw("HIST SAME")
    r_qe1.Draw("HIST SAME")
    r_mul1.Draw("HIST SAME")
    r_one1.Draw("HIST SAME")
    r_pion1.Draw("HIST SAME")
    r_muonly1.Draw("HIST SAME")
    r_noproton.Draw("HIST SAME")

    c4.Update()



    file.cd()
    c1.Write()
    c2.Write()
    c3.Write()
    c4.Write()
    file.Close()
    #c1.SaveAs("proton_channels_{}.root".format(filename_chunk)) 

    input("Press Enter...")



main()


"""
    for event in t:
        i+=1
        #print(i)
        nvect = event.vectorbranch
        #nvect_reader(nvect).remnant()
        nvect_class = nvect_reader(nvect)
        p_casc_energy,carbon11, nucleonCounter, clusterCounter, transparentProton, pion, photonCounter,proton,prefsi_proton_mom = nvect_class.proton_momentum_per_channel()
        

        if len(p_casc_energy) > 0:
            HMP_proton = np.asarray(p_casc_energy).max()
        else: 
            if (nucleonCounter > 0) or (pion == True) or (clusterCounter > 0) or (proton == False):
                no_protons.append(prefsi_proton_mom)
            else:
                mu_only.append(prefsi_proton_mom)
                nvect_reader(nvect).Print()
            continue

        DPT, dat = nvect_class.get_deltaPT()

        if (transparentProton == True) and (clusterCounter == 0) and (nucleonCounter == 1)  and (pion == False):
            noCascadeFSI.append(HMP_proton)
            noCascadeFSI_at.append(dat)
            noCascadeFSI_pt.append(DPT)
            if(prefsi_proton_mom != 0):
                noCascadeFSI_pre.append(prefsi_proton_mom)
            else:
                noCascadeFSI_pre.append(HMP_proton)

        elif (transparentProton == True):  
            QE_deex.append(HMP_proton)
            QE_deex_at.append(dat)
            QE_deex_pt.append(DPT)
            QE_deex_pre.append(prefsi_proton_mom)

        elif (transparentProton == False) and (proton == True) and (clusterCounter <= 1 ) and (nucleonCounter >= 1)  and (pion == False):
            multipleNucleon_noCluster.append(HMP_proton)
            multipleNucleon_noCluster_at.append(dat)
            multipleNucleon_noCluster_pt.append(DPT)
            multipleNucleon_noCluster_pre.append(prefsi_proton_mom)
        
        elif (transparentProton == False) and (proton == True) and (clusterCounter > 1) and (nucleonCounter >= 1):
            nuclearCluster.append(HMP_proton)
            nuclearCluster_at.append(dat)
            nuclearCluster_pt.append(DPT)
            nuclearCluster_pre.append(prefsi_proton_mom)

        elif (transparentProton == False) and (proton == True) and (clusterCounter == 0) and (nucleonCounter ==1)  and (pion == False):
            oneProton.append(HMP_proton)
            oneProton_at.append(dat)
            oneProton_pt.append(DPT)
            oneProton_pre.append(prefsi_proton_mom)
        

        elif (transparentProton == False) and (proton == True) and (nucleonCounter >= 1 ) and (clusterCounter <= 1)  and (pion == True):   
            protonPion.append(HMP_proton)
            protonPion_at.append(dat)
            protonPion_pt.append(DPT)
            protonPion_pre.append(prefsi_proton_mom)
            
        else:
            nvect_class.Print()
            input(" ")
            print("transparentProton | proton  | nucleonCounter  | pion |photonCounter")
            print( transparentProton, " " , proton, " " ,nucleonCounter, " " , pion, " ", photonCounter)
            input(" ")
            other.append(HMP_proton)
            other_at.append(dat)
            other_pt.append(DPT)
            other_pre.append(prefsi_proton_mom)
"""