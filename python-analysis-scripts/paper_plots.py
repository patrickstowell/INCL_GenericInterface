import numpy as np
from array import array
import sys 
import argparse
import ROOT
from incl_analysis_functions import *

ROOT.gSystem.Load("libNEUTROOTClass.so")
ROOT.gSystem.Load("libNEUTOutput.so")
ROOT.gSystem.Load("libNEUTReWeight.so")
ROOT.TH1.AddDirectory(False)


def spectral_function2d(filename,additional_filename):
    import ROOT

    ROOT.gStyle.SetOptStat(0)

    # --- First File ---
    filename_chunk = filename.split(".")[0].split("out_")[1]
    f = ROOT.TFile(filename)
    t = f.Get("neuttree")   

    h_miss = ROOT.TH2D("h_miss", "; P_{N} [MeV/c]; E_{RMV} [MeV/c]", 150, 0, 450, 80, 0, 80)

    for event in t:
        nvect = event.vectorbranch
        nvect_class = nvect_reader(nvect)
        eMiss = nvect_class.E_miss
        pMiss = nvect_class.P_miss
        h_miss.Fill(pMiss, eMiss)


    # --- Second File ---
    f2 = ROOT.TFile(additional_filename)
    t2 = f2.Get("neuttree")  

    # IMPORTANT: Ensure the internal ROOT name ("h2_miss") is unique so it doesn't overwrite h_miss
    h2_miss = ROOT.TH2D("h2_miss", "; P_{N} [MeV/c]; E_{RMV} [MeV/c]", 150, 0, 450, 80, 0, 80)

    for event in t2:
        nvect = event.vectorbranch
        nvect_class = nvect_reader(nvect)
        eMiss = nvect_class.E_miss
        pMiss = nvect_class.P_miss
        h2_miss.Fill(pMiss, eMiss)


    # --- Syncing the Color Scales ---
    # Find the global maximum to ensure the color scales map exactly the same way
    global_max = max(h_miss.GetMaximum(), h2_miss.GetMaximum())

    h_miss.SetMaximum(global_max)
    h2_miss.SetMaximum(global_max)

    h_miss.SetMinimum(0.00001)
    h2_miss.SetMinimum(0.00001)


    # --- Styling ---
    ROOT.gStyle.SetPalette(ROOT.kBlueRedYellow)
    ROOT.gStyle.SetNumberContours(99)

    # Create a wider canvas to accommodate two plots
    c1 = ROOT.TCanvas("c1", "c1", 1600, 700) 
    c1.Divide(2, 1) # Divide into 1 row, 2 columns

    # Helper function to apply the same axis formatting
    def format_axes(hist):
        for axis in [hist.GetXaxis(), hist.GetYaxis()]:
            axis.SetLabelColor(ROOT.kBlack)
            axis.SetTitleColor(ROOT.kBlack)
            axis.SetAxisColor(ROOT.kWhite) 

    # --- Draw Pad 1 ---
    pad1 = c1.cd(1)
    pad1.SetFillColor(ROOT.kWhite) 
    pad1.SetFrameFillColor(ROOT.kBlack)
    pad1.SetRightMargin(0.15) # Give space for the Z-axis color palette
    format_axes(h_miss)
    h_miss.Draw() # Use COLZ to draw the 2D color map

    # --- Draw Pad 2 ---
    pad2 = c1.cd(2)
    pad2.SetFillColor(ROOT.kWhite) 
    pad2.SetFrameFillColor(ROOT.kBlack)
    pad2.SetRightMargin(0.15) # Give space for the Z-axis color palette
    format_axes(h2_miss)
    h2_miss.Draw() # Use COLZ to draw the 2D color map

    # --- Update and Save ---
    c1.Update()
    c1.SaveAs("spectral_function_{}.png".format(filename_chunk))

def SRC_plot(filename,additional_filename):
    ROOT.gStyle.SetOptStat(0)

    # Helper function to apply the same axis formatting
    def format_axes(hist):
        for axis in [hist.GetXaxis(), hist.GetYaxis()]:
            axis.SetLabelColor(ROOT.kBlack)
            axis.SetTitleColor(ROOT.kBlack)
            axis.SetAxisColor(ROOT.kWhite)

    # --- First File ---
    filename_chunk = filename.split(".")[0].split("out_")[1] if "out_" in filename else "output"
    f = ROOT.TFile(filename)
    t = f.Get("neuttree")   

    p_mf_1, e_mf_1 = array('d'), array('d')
    p_src_1, e_src_1 = array('d'), array('d')

    for event in t:
        nvect = event.vectorbranch
        nvect_class = nvect_reader(nvect)
        if nvect_class.eventType == EventType.MF:
            p_mf_1.append(nvect_class.P_miss)
            e_mf_1.append(nvect_class.E_miss)
        elif nvect_class.eventType == EventType.SRC:
            p_src_1.append(nvect_class.P_miss)
            e_src_1.append(nvect_class.E_miss)

    g1_mf = ROOT.TGraph(len(p_mf_1), p_mf_1, e_mf_1)
    g1_src = ROOT.TGraph(len(p_src_1), p_src_1, e_src_1)

    # --- Second File ---
    f2 = ROOT.TFile(additional_filename)
    t2 = f2.Get("neuttree")  

    p_mf_2, e_mf_2 = array('d'), array('d')
    p_src_2, e_src_2 = array('d'), array('d')

    for event in t2:
        nvect = event.vectorbranch
        nvect_class = nvect_reader(nvect)
        if nvect_class.eventType == EventType.MF:
            p_mf_2.append(nvect_class.P_miss)
            e_mf_2.append(nvect_class.E_miss)
        elif nvect_class.eventType == EventType.SRC:
            p_src_2.append(nvect_class.P_miss)
            e_src_2.append(nvect_class.E_miss)

    g2_mf = ROOT.TGraph(len(p_mf_2), p_mf_2, e_mf_2)
    g2_src = ROOT.TGraph(len(p_src_2), p_src_2, e_src_2)

    # --- Styling the Scatter Points ---
    # High contrast colors for black background: Cyan and Magenta
    color_mf = ROOT.kAzure-3
    color_src = ROOT.kRed-4

    for g in [g1_mf, g2_mf]:
        g.SetMarkerStyle(20) 
        g.SetMarkerSize(0.4)
        g.SetMarkerColor(color_mf) 

    for g in [g1_src, g2_src]:
        g.SetMarkerStyle(20)
        g.SetMarkerSize(0.4)
        g.SetMarkerColor(color_src)

    # --- Dummy Histograms for Axes Formatting ---
    h_dummy1 = ROOT.TH2D("hd1", "; P_{N} [MeV/c]; E_{RMV} [MeV/c]", 150, 0, 450, 150, 0, 150)
    h_dummy2 = ROOT.TH2D("hd2", "; P_{N} [MeV/c]; E_{RMV} [MeV/c]", 150, 0, 450, 150, 0, 150)

    # --- Legend Setup (Clearer & Bigger Markers) ---
    # Create dummy graphs just for the legend so the markers appear larger in the box
    leg_dummy_mf = ROOT.TGraph()
    leg_dummy_mf.SetMarkerStyle(20)
    leg_dummy_mf.SetMarkerColor(color_mf)
    leg_dummy_mf.SetMarkerSize(1.5) # Much larger for visibility

    leg_dummy_src = ROOT.TGraph()
    leg_dummy_src.SetMarkerStyle(20)
    leg_dummy_src.SetMarkerColor(color_src)
    leg_dummy_src.SetMarkerSize(1.5)

    def create_legend():
        # Better positioning and sizing
        leg = ROOT.TLegend(0.60, 0.75, 0.88, 0.88)
        leg.AddEntry(leg_dummy_mf, "Mean Field", "p")
        leg.AddEntry(leg_dummy_src, "SRC", "p")
        leg.SetTextColor(ROOT.kWhite)
        # Add a semi-transparent dark background with a white border
        leg.SetFillColorAlpha(ROOT.kBlack, 0.7) 
        leg.SetLineColor(ROOT.kWhite)
        leg.SetBorderSize(1)
        return leg

    # --- Setup Canvas ---
    c1 = ROOT.TCanvas("c1", "c1", 1600, 700) 
    c1.Divide(2, 1)

    # --- Draw Pad 1 ---
    pad1 = c1.cd(1)
    pad1.SetFillColor(ROOT.kWhite) 
    pad1.SetFrameFillColor(ROOT.kBlack)
    format_axes(h_dummy1)
    
    h_dummy1.Draw()           
    g1_mf.Draw("P SAME")      
    g1_src.Draw("P SAME")

    leg1 = create_legend()
    leg1.Draw()

    # --- Draw Pad 2 ---
    pad2 = c1.cd(2)
    pad2.SetFillColor(ROOT.kWhite) 
    pad2.SetFrameFillColor(ROOT.kBlack)
    format_axes(h_dummy2)
    
    h_dummy2.Draw()
    g2_mf.Draw("P SAME")
    g2_src.Draw("P SAME")

    leg2 = create_legend()
    leg2.Draw()

    # --- Update and Save ---
    c1.Update()
    c1.SaveAs("spectral_scatter_{}.png".format(filename_chunk))
