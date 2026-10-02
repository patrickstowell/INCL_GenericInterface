import ROOT
import matplotlib.pyplot as plt
import scienceplots
import latex



class histogram:

    def __init__(self, bin_center, bin_value, xlim, ylim, xtitle, ytitle):
        self.bin_center = bin_center
        self.bin_value = bin_value
        self.xlim = xlim
        self.ylim = ylim
        self.xtitle = xtitle
        self.ytitle = ytitle


class canvas:

    def __init__(self, name=""):
        self.name = name
        self.histograms = []


def extract_canvas(root_canvas,xtitle,ytitle):
    # Create the custom canvas object
    c_obj = canvas(name=root_canvas.GetName())

    for obj in root_canvas.GetListOfPrimitives():
        if obj.InheritsFrom("TH1"):
            xaxis = obj.GetXaxis()
            nbins = obj.GetNbinsX()

            centers = [xaxis.GetBinCenter(i) for i in range(1, nbins + 1)]
            values = [obj.GetBinContent(i) for i in range(1, nbins + 1)]

            #xtitle = xaxis.GetTitle()
            #ytitle = obj.GetYaxis().GetTitle()

            xlim = (xaxis.GetXmin(), xaxis.GetXmax())
            ylim = (obj.GetMinimum(), obj.GetMaximum())

            # Instantiate individual histogram
            h_obj = histogram(
                bin_center=centers,
                bin_value=values,
                xlim=xlim,
                ylim=ylim,
                xtitle=xtitle,
                ytitle=ytitle,
            )

            # Store in canvas instance
            c_obj.histograms.append(h_obj)

    return c_obj


"""
rfile = ROOT.TFile.Open("paper_transparency_combined_output.root")

plt.style.use('/software/physrev.mplstyle')
plt.rcParams['figure.dpi'] = 300

canvases = []

xtitle = r"T$_{\mathrm{P}}$ [MeV]"
ytitle = " p-C Transparency"

legend = ["Position Swap", "Random Swap", "Momentum Swap"] 

for key in rfile.GetListOfKeys():
    obj = key.ReadObj()
    if obj.InheritsFrom("TCanvas"):
        canvases.append(extract_canvas(obj,xtitle,ytitle))

print(f"Loaded {len(canvases)} canvas(es) total.\n")

for c in canvases:
    print(f"Canvas '{c.name}': {len(c.histograms)} histogram(s)")



for c in canvases:
    if not c.histograms:
        continue

    fig, ax = plt.subplots(figsize=(6, 4.5))

    for idx, h in enumerate(c.histograms):
        ax.plot(
            h.bin_center[1:],
            h.bin_value[1:],
            label=legend[idx],
            linewidth=1.5,
        )

        ax.set_xlabel(h.xtitle, fontsize=14)
        ax.set_ylabel(h.ytitle, fontsize=14)
        ax.set_xlim(0, 500)
        ax.set_ylim(0, 1)
        #x.set_xlim(h.xlim)
        #ax.set_ylim(h.ylim)
        ax.grid()

    #ax.autoscale(tight=True)

    if len(c.histograms) > 1:
        ax.legend(title="Swap Type")

    output_name = f"{c.name}.pdf"
    fig.savefig(output_name, bbox_inches="tight", dpi=300)
    plt.close(fig)

    print(f"Saved: {output_name}")
"""

def plot_formatter(rfile,xtitle,ytitle,legend = [], target_canvas_name = None):
    rfile = ROOT.TFile.Open("paper_transparency_combined_output.root")

    plt.style.use('/software/physrev.mplstyle')
    plt.rcParams['figure.dpi'] = 300

    target_canvas_name = "c8"  

    xtitle = r"E_X  [MeV]" 
    ytitle = "Number of Events"
    legend = ["Position Swap", "Random Swap", "Momentum Swap"]



    obj = rfile.Get(target_canvas_name)


    if not obj or not obj.InheritsFrom("TCanvas"):
        raise KeyError(f"Canvas '{target_canvas_name}' was not found or is not a TCanvas in {rfile.GetName()}.")

    c = extract_canvas(obj, xtitle, ytitle)

    if c.histograms:
        fig, ax = plt.subplots(figsize=(6, 4.5))

        for idx, h in enumerate(c.histograms):
            label_text = legend[idx] if idx < len(legend) else f"Hist {idx+1}"
            
            ax.plot(
                h.bin_center[1:],
                h.bin_value[1:],
                label=label_text,
                linewidth=1.5,
            )

        ax.set_xlabel(xtitle, fontsize=14)
        ax.set_ylabel(ytitle, fontsize=14)
        ax.set_xlim(0, 500)
        ax.set_ylim(0, 1)
        ax.grid(True)

        if len(c.histograms) > 1:
            ax.legend(title="Swap Type")

        output_name = f"{c.name}.pdf"
        fig.savefig(output_name, bbox_inches="tight", dpi=300)
        plt.close(fig)

        print(f"Saved: {output_name}")


plot_formatter()