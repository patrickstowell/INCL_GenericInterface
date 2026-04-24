import ROOT
import sys 
import numpy as np
import math
ROOT.gSystem.Load("libNEUTROOTClass.so")
ROOT.gSystem.Load("libNEUTOutput.so")
ROOT.gSystem.Load("libNEUTReWeight.so")
from enum import Enum

class EventType(Enum):
    MF = 0
    SRC = 1
    twop2h = 2
    piProd = 3
    NC = 4
    NC_piProd = 5

class intChannel_CCQE(Enum):
    noCascadeFSI = 0 
    qeDeEX = 1
    oneProton = 2
    multipleNucleon = 3
    nuclearCluster = 4
    protonPion = 5
    muOnly = 6
    neutronPion = 7
    other = 8

class intChannel_CC0pi(Enum):
    noCascadeFSI = 0 # two protons leave without changing 
    qeDeEX = 1 # two protons leave without changing, plus deexcitation
    twoProton = 2 # both protons change energy. 
    multipleNucleonAndNoFSI = 3 
    multipleNucleons = 4 
    nuclearClustersAndNoFSI = 5
    nuclearClusters = 6
    nucleonPion = 7
    muOnly = 8
    other = 9
    noCascadeFSIoneNucleon = 10
    neutronPion = 11
    oneProtonAndNoFSI = 12

def create_histo(name, title, color, fill_style, data,n_bins,x_min,x_max, line = False):

    h = ROOT.TH1F(name, title, n_bins, x_min, x_max)
    for val in data:
        h.Fill(val)
    
    h.SetLineColor(color-2)  
    h.SetLineWidth(2)
    h.SetFillColor(color)
    h.SetFillStyle(fill_style) 
    
    if line:
        h.SetLineStyle(fill_style) 

    
    # h.SetStats(0)
    return h

class nvect_reader:
    def __init__(self, nvect_,flavour = 2212):
        self.intChannel = None
        self.HMPMom = None
        self.PreFSIProtMom = 0
        self.nvect = nvect_
        self.nopart = self.nvect.Npart()
        self.novert = self.nvect.NnucFsiVert()
        self.nosteps = self.nvect.NnucFsiStep()
        self.beam_flavour = flavour
        self.isnofsi = True if self.nopart <=5 else False

        self.eventType = self.event_type()
        if self.eventType == EventType.MF:
            self.intChannel = self.interaction_channel_CCQE()
        elif self.eventType == (EventType.SRC or EventType.twop2h):
            self.intChannel = self.interaction_channel_CC0pi()

        if (self.eventType == EventType.MF) or (self.eventType == EventType.SRC) or (self.eventType == EventType.twop2h):
            self.E_miss = self.missing_E_calc()
            self.P_miss = self.neutron_mom()
                
    def event_type(self):
        if self.NC_Pi_prod() == True:
            return EventType.NC_piProd
        elif self.NC() == True:
            return EventType.NC
        elif self.pion_prod() == True:
            return EventType.piProd
        elif self.twop2h() == True:
            return EventType.twop2h
        elif self.src() == True:
            return EventType.SRC
        else:
            return EventType.MF
           
    def proton_momentum_per_channel_CCQE(self):
        p_casc_energy = []
        proton = False
        nuclear_remnant = False
        nucleonCounter = 0
        clusterCounter = 0
        transparentProton = False
        transparentEvent = False
        pion = False
        photonCounter = False
        proton_mom_prefsi = 0
        deexcitation_event = False
        init_proton_mom = None

        for i in range(self.nopart):


            pinfo = self.nvect.PartInfo(i)

            if pinfo.fStatus == 10 and (pinfo.fPID < 10000):
                deexcitation_event = True
            
            if pinfo.fPID == abs(2212): #getting proton momentum 
                if (pinfo.fIsAlive == 0 and self.nvect.ParentIdx(i)==2):
                    init_proton_mom = np.array([pinfo.fP.X(),pinfo.fP.Y(), pinfo.fP.Z()])
                    proton_mom_prefsi = np.linalg.norm(init_proton_mom)

                elif (pinfo.fIsAlive == 1 and self.nvect.ParentIdx(i)==2 and self.nopart == 4):
                    p_casc_energy.append(np.sqrt((pinfo.fP.X()**2 + pinfo.fP.Y()**2 +pinfo.fP.Z()**2)))
                    transparentProton = True
                    nucleonCounter += 1
                    proton = True
                                              
                elif (pinfo.fIsAlive == 1):
                    p_casc_energy.append(np.sqrt((pinfo.fP.X()**2 + pinfo.fP.Y()**2 +pinfo.fP.Z()**2)))
                    pre_fsi_proton_mom = np.array([pinfo.fP.X(),pinfo.fP.Y(), pinfo.fP.Z()])
                    nucleonCounter += 1
                    proton = True
                     
                    #if (self.nvect.ParentIdx(i)==4):
                    #    pre_fsi_proton_mom = np.array([pinfo.fP.X(),pinfo.fP.Y(), pinfo.fP.Z()])
                    #    #print(init_proton_mom - pre_fsi_proton_mom )
                    #    #print(np.linalg.norm(init_proton_mom - pre_fsi_proton_mom ))
                    #    if (np.linalg.norm(pre_fsi_proton_mom - init_proton_mom) < 0.007):
                    #        transparentProton = True 
                    if (self.nvect.ParentIdx(i) != 2 and init_proton_mom is not None):
                        if (np.linalg.norm(pre_fsi_proton_mom - init_proton_mom) < 0.007):
                            transparentProton = True


            elif pinfo.fPID == abs(2112):
                if (pinfo.fIsAlive == 1):
                    nucleonCounter += 1

            elif pinfo.fPID > abs(10000):
                if (pinfo.fIsAlive == 1):
                    nuclear_remnant = True

            elif 200 < abs(pinfo.fPID) < 250:
                if (pinfo.fIsAlive == 1):
                    pion = True
            
            elif ((10000 > pinfo.fPID > 1000) and (pinfo.fIsAlive == 1)):
                if((pinfo.fPID != 2212) and (pinfo.fPID != 2112) and (pinfo.fPID != 6011)and (pinfo.fPID != 13)):
                   clusterCounter += 1

            elif (pinfo.fPID == 0 and pinfo.fIsAlive == 1):
                photonCounter +=1
                 
        return p_casc_energy,nuclear_remnant, nucleonCounter, clusterCounter, transparentProton, pion, photonCounter, proton, proton_mom_prefsi,deexcitation_event

    def proton_momentum_per_channel_SRC(self):
        p_casc_energy = []

        init_src_nucleon_mom = 0.0
        init_main_proton_mom = 0.0
        fsi_neutron_energy = []
        fsi_proton_energy = []
        src_partner_flavour = 0
        nucleonCounter = 0
        clusterCounter = 0
        nuclear_remnant = False
        pion = False
        proton = False
        photonCounter = False
        proton_mom_prefsi = 0
        deexcitation_event = False
        init_proton_mom = None

        for i in range(self.nopart):
            pinfo = self.nvect.PartInfo(i)

            if pinfo.fStatus == 10 and (pinfo.fPID < 10000):
                deexcitation_event = True

            if pinfo.fPID ==abs(2112):
                if(pinfo.fIsAlive == 0 and self.nvect.ParentIdx(i)==0 and pinfo.fStatus == 7):
                    init_src_nucleon_mom = np.linalg.norm(np.array([pinfo.fP.X(),pinfo.fP.Y(), pinfo.fP.Z()]))
                    src_partner_flavour = 2212
                elif (pinfo.fIsAlive == 1):
                    #proton = True
                    fsi_neutron_energy.append(np.sqrt((pinfo.fP.X()**2 + pinfo.fP.Y()**2 +pinfo.fP.Z()**2)))
    
                    nucleonCounter += 1
            
            if pinfo.fPID == abs(2212): #getting proton momentum 
                if (pinfo.fIsAlive == 0 and self.nvect.ParentIdx(i)==2 and pinfo.fStatus ==7):
                    init_main_proton_mom = np.linalg.norm(np.array([pinfo.fP.X(),pinfo.fP.Y(), pinfo.fP.Z()]))

                elif(pinfo.fIsAlive == 0 and self.nvect.ParentIdx(i)==0 and pinfo.fStatus ==7):
                    init_src_nucleon_mom = np.linalg.norm(np.array([pinfo.fP.X(),pinfo.fP.Y(), pinfo.fP.Z()]))
                    src_partner_flavour = 2212

                elif (pinfo.fIsAlive == 1):
                    proton = True
                    fsi_proton_energy.append(np.sqrt((pinfo.fP.X()**2 + pinfo.fP.Y()**2 +pinfo.fP.Z()**2)))
    
                    nucleonCounter += 1

            elif pinfo.fPID > abs(10000):
                if (pinfo.fIsAlive == 1):
                    nuclear_remnant = True

            elif 200 < abs(pinfo.fPID) < 250:
                if (pinfo.fIsAlive == 1):
                    pion = True
            
            elif ((10000 > pinfo.fPID > 1000) and (pinfo.fIsAlive == 1)):
                if((pinfo.fPID != 2212) and (pinfo.fPID != 2112) and (pinfo.fPID != 6011)and (pinfo.fPID != 13)):
                   clusterCounter += 1

            elif (pinfo.fPID == 0 and pinfo.fIsAlive == 1):
                photonCounter +=1


        

        all_fsi_energies = fsi_neutron_energy + fsi_proton_energy

        # We use an absolute tolerance (abs_tol) of 0.01, which is equivalent 
        # to checking if they match up to the 2nd decimal place.
        main_present = any(math.isclose(init_main_proton_mom, energy, abs_tol=0.01) for energy in all_fsi_energies)
        src_present = any(math.isclose(init_src_nucleon_mom, energy, abs_tol=0.01) for energy in all_fsi_energies)

        # The if-else logic remains the same
        if main_present and src_present:
            transparentNucleons = 2
        elif main_present or src_present:
            transparentNucleons = 1
        else:
            transparentNucleons = 0
                 

        return fsi_proton_energy, nuclear_remnant, nucleonCounter, clusterCounter, transparentNucleons, pion, photonCounter, deexcitation_event,proton

    def proton_momentum_per_channel_2p2h(self):
        p_casc_energy = []

        init_second_nucleon_mom = 0.0
        init_main_proton_mom = 0.0
        fsi_neutron_energy = []
        fsi_proton_energy = []
        second_partner_flavour = 0
        nucleonCounter = 0
        clusterCounter = 0
        nuclear_remnant = False
        pion = False
        proton = False
        photonCounter = False
        proton_mom_prefsi = 0
        deexcitation_event = False
        init_proton_mom = None

        for i in range(self.nopart):
            pinfo = self.nvect.PartInfo(i)

            if pinfo.fStatus == 10 and (pinfo.fPID < 10000):
                deexcitation_event = True

            if pinfo.fPID ==abs(2112):
                if(pinfo.fIsAlive == 0 and self.nvect.ParentIdx(i)==2 and pinfo.fStatus == 7):
                    init_main_nucleon_mom = np.linalg.norm(np.array([pinfo.fP.X(),pinfo.fP.Y(), pinfo.fP.Z()]))

                if(pinfo.fIsAlive == 0 and self.nvect.ParentIdx(i)==3 and pinfo.fStatus == 7):
                    init_second_nucleon_mom = np.linalg.norm(np.array([pinfo.fP.X(),pinfo.fP.Y(), pinfo.fP.Z()]))
                    second_partner_flavour = 2212

                elif (pinfo.fIsAlive == 1):
                    #proton = True
                    fsi_neutron_energy.append(np.sqrt((pinfo.fP.X()**2 + pinfo.fP.Y()**2 +pinfo.fP.Z()**2)))
    
                    nucleonCounter += 1
            
            if pinfo.fPID == abs(2212): #getting proton momentum 
                if (pinfo.fIsAlive == 0 and self.nvect.ParentIdx(i)==2 and pinfo.fStatus ==7):
                    init_main_proton_mom = np.linalg.norm(np.array([pinfo.fP.X(),pinfo.fP.Y(), pinfo.fP.Z()]))

                elif(pinfo.fIsAlive == 0 and self.nvect.ParentIdx(i)==3 and pinfo.fStatus ==7):
                    init_second_nucleon_mom = np.linalg.norm(np.array([pinfo.fP.X(),pinfo.fP.Y(), pinfo.fP.Z()]))
                    second_partner_flavour = 2212

                elif (pinfo.fIsAlive == 1):
                    proton = True
                    fsi_proton_energy.append(np.sqrt((pinfo.fP.X()**2 + pinfo.fP.Y()**2 +pinfo.fP.Z()**2)))
    
                    nucleonCounter += 1

            elif pinfo.fPID > abs(10000):
                if (pinfo.fIsAlive == 1):
                    nuclear_remnant = True

            elif 200 < abs(pinfo.fPID) < 250:
                if (pinfo.fIsAlive == 1):
                    pion = True
            
            elif ((10000 > pinfo.fPID > 1000) and (pinfo.fIsAlive == 1)):
                if((pinfo.fPID != 2212) and (pinfo.fPID != 2112) and (pinfo.fPID != 6011)and (pinfo.fPID != 13)):
                   clusterCounter += 1

            elif (pinfo.fPID == 0 and pinfo.fIsAlive == 1):
                photonCounter +=1


        all_fsi_energies = fsi_neutron_energy + fsi_proton_energy

        # We use an absolute tolerance (abs_tol) of 0.01, which is equivalent 
        # to checking if they match up to the 2nd decimal place.
        main_present = any(math.isclose(init_main_proton_mom, energy, abs_tol=0.01) for energy in all_fsi_energies)
        second_present = any(math.isclose(init_second_nucleon_mom, energy, abs_tol=0.01) for energy in all_fsi_energies)

        # The if-else logic remains the same
        if main_present and second_present:
            transparentNucleons = 2
        elif main_present or second_present:
            transparentNucleons = 1
        else:
            transparentNucleons = 0
                 

        return fsi_proton_energy, nuclear_remnant, nucleonCounter, clusterCounter, transparentNucleons, pion, photonCounter, deexcitation_event,proton

    def NC(self):
        neutrino_counter = 0
        for i in range(self.nopart):
            pinfo = self.nvect.PartInfo(i)
            if pinfo.fPID == abs(14):
                neutrino_counter += 1
                if neutrino_counter == 2:
                    return True
        return False

    def pion_prod(self):
        for i in range(self.nopart):
            pinfo = self.nvect.PartInfo(i)
            if pinfo.fPID == abs(211) or pinfo.fPID == abs(111):
                 if(self.nvect.ParentIdx(i)== 2 and pinfo.fStatus == 0):
                    return True
        return False

    def NC_Pi_prod(self):
        neutrino_counter = 0
        neutrino = False
        pion = False

        for i in range(self.nopart):
            pinfo = self.nvect.PartInfo(i)
            if pinfo.fPID == abs(14):
                neutrino_counter += 1
                if neutrino_counter == 2:
                    neutrino = True
            if pinfo.fPID == abs(211) or pinfo.fPID == abs(111):
                 if(self.nvect.ParentIdx(i)== 2 and pinfo.fStatus == 0):
                    pion = True

            if(neutrino == True  and pion) == True:
                return True
        return False
   
    def src(self):

        if self.isnofsi == True:
            if self.nopart == 5:
                return True 
            else:
                return False
        else:
            src_counter = 0
            proton_mom2 = 0
            init_proton_mom = 0
            for i in range(self.nopart):
                pinfo = self.nvect.PartInfo(i)
                if pinfo.fPID == abs(2112):
                    if (pinfo.fIsAlive == 0) and (self.nvect.ParentIdx(i)== 0) and (pinfo.fStatus == -1):
                        init_proton_mom = np.array([pinfo.fP.X(),pinfo.fP.Y(), pinfo.fP.Z()])
                        continue

                if pinfo.fPID == abs(2212) or pinfo.fPID == abs(2112):
                    if pinfo.fStatus == 7:
                        proton_mom2 = np.array([-pinfo.fP.X(),-pinfo.fP.Y(), -pinfo.fP.Z()])

                        if np.linalg.norm(init_proton_mom - proton_mom2) < 0.1:
                            return True   
            return False
    
    def twop2h(self):   
        twop2hcounter = 0
        for i in range(self.nopart):
            pinfo = self.nvect.PartInfo(i)
            if pinfo.fPID == abs(2112) or pinfo.fPID == abs(2212):
                 if(self.nvect.ParentIdx(i)== 0 and pinfo.fStatus == -1):
                     twop2hcounter +=1
        if twop2hcounter > 1:
            return True
        return 0

    def missing_E_calc(self):

        E_nu = 0.0
        E_lep = 0.0 
        T_had = 0.0
        for i in range(self.nopart):
            pinfo = self.nvect.PartInfo(i)
            if pinfo.fPID == abs(14):
                E_nu = np.linalg.norm(np.array([pinfo.fP.X(),pinfo.fP.Y(), pinfo.fP.Z()]))
            if pinfo.fPID == abs(13):
                E_lep = np.sqrt(np.linalg.norm(np.array([pinfo.fP.X(),pinfo.fP.Y(), pinfo.fP.Z()]))**2 + 105.0**2)
            if pinfo.fPID == abs(2212) and (self.nvect.ParentIdx(i)==2):
                T_had = np.sqrt(np.linalg.norm(np.array([pinfo.fP.X(),pinfo.fP.Y(), pinfo.fP.Z()]))**2 + 938.00**2) - 938.00

        return E_nu - E_lep - T_had
        
    def excitation_E_CCQE(self):
        print(self.eventType)
        E_nu = 0.0
        E_lep = 0.0 
        E_had = 0.0
        p_had = 0.0
        for i in range(self.nopart):
            pinfo = self.nvect.PartInfo(i)
            if pinfo.fPID == abs(14):
                p_nu = np.array([pinfo.fP.X(),pinfo.fP.Y(), pinfo.fP.Z()])
                E_nu = np.linalg.norm(np.array([pinfo.fP.X(),pinfo.fP.Y(), pinfo.fP.Z()]))
            if pinfo.fPID == abs(13):
                p_lep = np.array([pinfo.fP.X(),pinfo.fP.Y(), pinfo.fP.Z()])
                E_lep = np.sqrt(np.linalg.norm(np.array([pinfo.fP.X(),pinfo.fP.Y(), pinfo.fP.Z()]))**2 + 105.0**2)
            if pinfo.fPID == abs(2212) and (self.nvect.ParentIdx(i)==2):
                p_had += np.array([pinfo.fP.X(),pinfo.fP.Y(), pinfo.fP.Z()])
                E_had += np.sqrt(np.linalg.norm(np.array([pinfo.fP.X(),pinfo.fP.Y(), pinfo.fP.Z()]))**2 + 938.00**2) 
            if (pinfo.fPID == abs(2212) or pinfo.fPID == abs(2112)) and (self.nvect.ParentIdx(i)==0) and (pinfo.fStatus ==7):
                p_had += np.array([pinfo.fP.X(),pinfo.fP.Y(), pinfo.fP.Z()])
                E_had += np.sqrt(np.linalg.norm(np.array([pinfo.fP.X(),pinfo.fP.Y(), pinfo.fP.Z()]))**2 + 938.00**2) 


        E_star = E_nu + 11174.86 - E_lep - E_had
        p_star = p_nu - p_lep - p_had

        E = np.sqrt(E_star**2 - np.linalg.norm(p_star**2)) - 10254.22
        return E   
    
    def excitation_E_SRC(self):
        print(self.eventType)
        E_nu = 0.0
        E_lep = 0.0 
        E_had = 0.0
        p_had = 0.0
        for i in range(self.nopart):
            pinfo = self.nvect.PartInfo(i)
            if pinfo.fPID == abs(14):
                p_nu = np.array([pinfo.fP.X(),pinfo.fP.Y(), pinfo.fP.Z()])
                E_nu = np.linalg.norm(np.array([pinfo.fP.X(),pinfo.fP.Y(), pinfo.fP.Z()]))
            if pinfo.fPID == abs(13):
                p_lep = np.array([pinfo.fP.X(),pinfo.fP.Y(), pinfo.fP.Z()])
                E_lep = np.sqrt(np.linalg.norm(np.array([pinfo.fP.X(),pinfo.fP.Y(), pinfo.fP.Z()]))**2 + 105.0**2)
            if pinfo.fPID == abs(2212) and (self.nvect.ParentIdx(i)==2):
                p_had += np.array([pinfo.fP.X(),pinfo.fP.Y(), pinfo.fP.Z()])
                E_had += np.sqrt(np.linalg.norm(np.array([pinfo.fP.X(),pinfo.fP.Y(), pinfo.fP.Z()]))**2 + 938.00**2) 
            if (pinfo.fPID == abs(2212) or pinfo.fPID == abs(2112)) and (self.nvect.ParentIdx(i)==0) and (pinfo.fStatus ==7):
                p_had += np.array([pinfo.fP.X(),pinfo.fP.Y(), pinfo.fP.Z()])
                E_had += np.sqrt(np.linalg.norm(np.array([pinfo.fP.X(),pinfo.fP.Y(), pinfo.fP.Z()]))**2 + 938.00**2) 


        E_star = E_nu + 11174.86 - E_lep - E_had
        p_star = p_nu - p_lep - p_had

        E = np.sqrt(E_star**2 - np.linalg.norm(p_star**2)) - (10254.22 - 938.27)
        if self.eventType == EventType.SRC:
            print(E)
        return E   
    
    def excitation_E_2p2h(self):

        E_nu = 0.0
        E_lep = 0.0 
        E_had = 0.0
        p_had = 0.0
        for i in range(self.nopart):
            pinfo = self.nvect.PartInfo(i)
            if pinfo.fPID == abs(14):
                p_nu = np.array([pinfo.fP.X(),pinfo.fP.Y(), pinfo.fP.Z()])
                E_nu = np.linalg.norm(np.array([pinfo.fP.X(),pinfo.fP.Y(), pinfo.fP.Z()]))
            if pinfo.fPID == abs(13):
                p_lep = np.array([pinfo.fP.X(),pinfo.fP.Y(), pinfo.fP.Z()])
                E_lep = np.sqrt(np.linalg.norm(np.array([pinfo.fP.X(),pinfo.fP.Y(), pinfo.fP.Z()]))**2 + 105.0**2)
            if pinfo.fPID == abs(2212) and (pinfo.fStatus ==7) and ((self.nvect.ParentIdx(i)==2) or (self.nvect.ParentIdx(i)==3)):
                p_had += np.array([pinfo.fP.X(),pinfo.fP.Y(), pinfo.fP.Z()])
                E_had += np.sqrt(np.linalg.norm(np.array([pinfo.fP.X(),pinfo.fP.Y(), pinfo.fP.Z()]))**2 + 938.00**2)
            if pinfo.fPID == abs(2112) and (pinfo.fStatus ==7) and ((self.nvect.ParentIdx(i)==2) or (self.nvect.ParentIdx(i)==3)):
                p_had += np.array([pinfo.fP.X(),pinfo.fP.Y(), pinfo.fP.Z()])
                E_had += np.sqrt(np.linalg.norm(np.array([pinfo.fP.X(),pinfo.fP.Y(), pinfo.fP.Z()]))**2 + 938.00**2) 

        E_star = E_nu + 11174.86 - E_lep - E_had
        p_star = p_nu - p_lep - p_had

        E = np.sqrt(E_star**2 - np.linalg.norm(p_star**2)) - (11174.86 - 2*938.27)
        print(E)
        return E

    def missing_energy_2p2h(self):

        E_nu = 0.0
        E_lep = 0.0 
        T_had = 0.0
        for i in range(self.nopart):
            pinfo = self.nvect.PartInfo(i)
            if pinfo.fPID == abs(14):
                E_nu = np.linalg.norm(np.array([pinfo.fP.X(),pinfo.fP.Y(), pinfo.fP.Z()]))
            if pinfo.fPID == abs(13):
                E_lep = np.sqrt(np.linalg.norm(np.array([pinfo.fP.X(),pinfo.fP.Y(), pinfo.fP.Z()]))**2 + 105.0**2)
            if pinfo.fPID == abs(2212) and (pinfo.fStatus ==0):
                T_had += np.sqrt(np.linalg.norm(np.array([pinfo.fP.X(),pinfo.fP.Y(), pinfo.fP.Z()]))**2 + 938.00**2) - 938.00
            if pinfo.fPID == abs(2112) and (pinfo.fStatus ==0):
                T_had += np.sqrt(np.linalg.norm(np.array([pinfo.fP.X(),pinfo.fP.Y(), pinfo.fP.Z()]))**2 + 938.00**2) - 938.00

        return E_nu - E_lep - T_had


    def neutron_mom(self):
        for i in range(self.nopart):
            pinfo = self.nvect.PartInfo(i)
            if ((pinfo.fPID == abs(2112)) and  (pinfo.fStatus == -1)):
                return np.linalg.norm(np.array([pinfo.fP.X(),pinfo.fP.Y(), pinfo.fP.Z()]))
            

    def remnant(self):
        A = 0
        Z = 0
        for i in range(self.nopart):
            pinfo = self.nvect.PartInfo(i)
            if ((pinfo.fPID > 1000) and pinfo.fIsAlive == 1):
                if (pinfo.fPID ==2112):
                    A +=1
                elif (pinfo.fPID ==2212):
                    A +=1
                    Z+=1
                else:
                    remnant = str(pinfo.fPID)
                    Z+= int(remnant[0])

                    if remnant[2] != 0:
                        A+= 10*int(remnant[2]) + int(remnant[3])
                    else:
                        A+= int(remnant[3])
        if A != 12:
            self.Print()
        print(A,Z)
        return 0 
    
    def get_deltaPT(self):
        proton_momentum = np.asarray([0,0,0])

        for i in range(self.nopart):

            pinfo = self.nvect.PartInfo(i)
            #get neutrino momentum direction
            if pinfo.fPID == abs(14):
                neutrino_mometum = np.asarray([pinfo.fP.X(), pinfo.fP.Y() ,pinfo.fP.Z()])

            if pinfo.fPID == abs(13):
                lepton_momentum = np.asarray([pinfo.fP.X(), pinfo.fP.Y() ,pinfo.fP.Z()])

            if pinfo.fPID == abs(2212): #getting proton momentum  
                if (pinfo.fIsAlive == 1):
                    proton_mometum_placeholder = np.asarray([pinfo.fP.X(), pinfo.fP.Y() ,pinfo.fP.Z()])
                    if(np.linalg.norm(proton_mometum_placeholder) > np.linalg.norm(proton_momentum)):
                        proton_momentum = proton_mometum_placeholder
        
        if np.linalg.norm(proton_momentum) == 0:
            return -999.99
        else:
            normal_v = neutrino_mometum/np.linalg.norm(neutrino_mometum) 
            proton_momentum_long = np.dot(proton_momentum, normal_v) * normal_v
            proton_momentum_trans = proton_momentum - proton_momentum_long

            lept_momentum_long = np.dot(lepton_momentum, normal_v) * normal_v
            lept_momentum_trans = lepton_momentum - lept_momentum_long
            #print(np.linalg.norm(proton_momentum_trans + lept_momentum_trans))
            DPT = proton_momentum_trans + lept_momentum_trans
            #print(DPT)
            DPT_norm = np.linalg.norm(DPT)
            DaT = np.arccos( ( np.dot(-lept_momentum_trans,DPT) /(  np.linalg.norm(lept_momentum_trans) *  np.linalg.norm(DPT) )   ) )
            #print(DaT)
            #print(np.rad2deg(DaT))
            return DPT_norm, np.rad2deg(DaT)

    def Print(self):
        print("~~~~~~~~~Particles~~~~~~~") 
        print("ID | V. ID  | flag | Parent ID | particle | mom | mass")
        for i in range(self.nopart):
            pinfo = self.nvect.PartInfo(i)
            print(i, " ", pinfo.fIsAlive,"       " , pinfo.fStatus,"  ",self.nvect.ParentIdx(i),"              ", pinfo.fPID, "    ",pinfo.fP.X(), pinfo.fP.Y(), pinfo.fP.Z(), pinfo.fMass)
            pinfo.fP.X()**2 + pinfo.fP.X()**2 +pinfo.fP.Y()**2
            P = (pinfo.fP.X()**2 + pinfo.fP.Y()**2 +pinfo.fP.Z()**2)
            print("energy", np.sqrt(P+pinfo.fMass**2)-pinfo.fMass)
        
        print(self.eventType.name)

        return self.eventType.name
        #print(self.intChannel.name)
    
    def kinetic_energy(self,pinfo):
        return np.sqrt((pinfo.fP.X()**2 + pinfo.fP.Y()**2 +pinfo.fP.Z()**2)+pinfo.fMass**2)-pinfo.fMass


    def interaction_channel_CCQE(self):
        p_casc_energy,nuclear_remnant, nucleonCounter, clusterCounter, transparentProton, pion, photonCounter,proton,prefsi_proton_mom, deex_event = self.proton_momentum_per_channel_CCQE()
        if len(p_casc_energy) > 0:
            self.HMPMom = np.asarray(p_casc_energy).max()
            self.DpT,self.DaT = self.get_deltaPT()

        self.PreFSIProtMom = prefsi_proton_mom
        if(proton != True):
            
            if  (nucleonCounter > 0) or (clusterCounter > 0) or (pion == True):
                return intChannel_CCQE.neutronPion
            else:
                return intChannel_CCQE.muOnly
        
            
        elif (transparentProton == True) and (clusterCounter == 0) and (proton == True)  and (pion == False) and (photonCounter == False) and (deex_event == False):
            return intChannel_CCQE.noCascadeFSI

        elif (transparentProton == True) and (deex_event == True) and (proton == True):  
            return intChannel_CCQE.qeDeEX
        
        elif (transparentProton == False) and (proton == True) and (clusterCounter == 0) and (nucleonCounter == 1)  and (pion == False):
            return intChannel_CCQE.oneProton
            
        elif (transparentProton == False) and (proton == True) and (clusterCounter == 0 ) and (nucleonCounter > 1)  and (pion == False):
            return intChannel_CCQE.multipleNucleon
        
        elif (transparentProton == False) and (proton == True) and (clusterCounter >= 1) and (nucleonCounter >= 1):
            return intChannel_CCQE.nuclearCluster

        elif (transparentProton == False) and (proton == True) and (clusterCounter == 0)  and (pion == True):   
            return intChannel_CCQE.protonPion
        else:
            return intChannel_CCQE.other


    def interaction_channel_CC0pi(self):
        if self.eventType == EventType.SRC:
            p_casc_energy, nuclear_remnant, nucleonCounter, clusterCounter, transparentNucleons, pion, photonCounter, deex_event,proton = self.proton_momentum_per_channel_SRC()
        if self.eventType == EventType.twop2h:
            p_casc_energy, nuclear_remnant, nucleonCounter, clusterCounter, transparentNucleons, pion, photonCounter, deex_event,proton = self.proton_momentum_per_channel_2p2h()

        #print("transparentNucleons, proton, clusterCounter, nucleonCounter, pion")
        #print(transparentNucleons, proton, clusterCounter, nucleonCounter, pion)
        
        if len(p_casc_energy) > 0:
            self.HMPMom = np.asarray(p_casc_energy).max()
            self.DpT,self.DaT = self.get_deltaPT()

        if(proton != True):
            self.intChannel = intChannel_CC0pi.neutronPion
            #self.Print()

            #need to add event with leading neutrons too
            if  (nucleonCounter > 0) or (clusterCounter > 0) or (pion == True):
                return intChannel_CCQE.neutronPion
            else:
                return intChannel_CCQE.muOnly
        
            
        elif (transparentNucleons == 2) and (clusterCounter == 0) and (proton == True)  and (pion == False) and (photonCounter == False) and (deex_event == False):
            return intChannel_CC0pi.noCascadeFSI
        
        elif (transparentNucleons == 1) and (nucleonCounter == 1) and (clusterCounter == 0) and (proton == True)  and (pion == False) and (photonCounter == False) and (deex_event == False):
            return intChannel_CC0pi.noCascadeFSIoneNucleon
        
        elif (transparentNucleons == 2) and (deex_event == True) and (proton == True):  
            return intChannel_CC0pi.qeDeEX
        
        elif (transparentNucleons == 0) and (proton == True) and (clusterCounter == 0) and (nucleonCounter == 2)  and (pion == False):
            return intChannel_CC0pi.twoProton
        
        elif (transparentNucleons == 1) and (proton == True) and (clusterCounter == 0) and (nucleonCounter == 1)  and (pion == False):
            return intChannel_CC0pi.oneProtonAndNoFSI
            
        elif (transparentNucleons == 1) and (proton == True) and (clusterCounter == 0 ) and (nucleonCounter > 1)  and (pion == False):
            return intChannel_CC0pi.multipleNucleonAndNoFSI
        
        elif (transparentNucleons == 0) and (proton == True) and (clusterCounter == 0 ) and (nucleonCounter > 1)  and (pion == False):
            return intChannel_CC0pi.multipleNucleons
        
        elif (transparentNucleons == 1) and (proton == True) and (clusterCounter >= 1) and (nucleonCounter >= 1):
            return intChannel_CC0pi.nuclearClustersAndNoFSI

        elif (transparentNucleons == 0) and (proton == True) and (clusterCounter >= 1) and (nucleonCounter >= 1):
            return intChannel_CC0pi.nuclearClusters

        elif (transparentNucleons < 2) and (proton == True) and (clusterCounter == 0)  and (pion == True):   
            return intChannel_CC0pi.nucleonPion
        else:
            #print(transparentNucleons)
            #self.Print()

            return intChannel_CC0pi.other

def create_ratio(h_in, h_tot):
    h_ratio = h_in.Clone(h_in.GetName() + "_ratio")
    h_ratio.Divide(h_tot) 


    h_ratio.SetFillStyle(0)
    h_ratio.SetLineWidth(2)
    h_ratio.SetLineColor(h_in.GetLineColor()) 
    return h_ratio