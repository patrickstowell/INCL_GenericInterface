import ROOT
import sys
import os

def copy_pad_contents(src_pad, tgt_pad):
    """Recursively copies pads, adding a vertical gap between stacked ratio panels."""
    tgt_pad.SetLogx(src_pad.GetLogx())
    tgt_pad.SetLogy(src_pad.GetLogy())
    tgt_pad.SetLogz(src_pad.GetLogz())
    tgt_pad.SetLeftMargin(src_pad.GetLeftMargin())
    tgt_pad.SetRightMargin(src_pad.GetRightMargin())
    tgt_pad.SetTopMargin(src_pad.GetTopMargin())
    tgt_pad.SetBottomMargin(src_pad.GetBottomMargin())
    tgt_pad.SetGridx(src_pad.GetGridx())
    tgt_pad.SetGridy(src_pad.GetGridy())
    tgt_pad.SetTickx(src_pad.GetTickx())
    tgt_pad.SetTicky(src_pad.GetTicky())
    tgt_pad.SetFillColor(src_pad.GetFillColor())
    tgt_pad.SetFillStyle(src_pad.GetFillStyle())

    tgt_pad.cd()

    prim_list = src_pad.GetListOfPrimitives()
    if not prim_list:
        return

    lnk = prim_list.FirstLink()
    while lnk:
        prim = lnk.GetObject()
        draw_opt = lnk.GetOption() or ""
        lnk = lnk.Next()

        if not prim or prim.GetName() == "TFrame":
            continue

        if prim.InheritsFrom("TPad"):
            x1 = prim.GetXlowNDC()
            y1 = prim.GetYlowNDC()
            x2 = x1 + prim.GetWNDC()
            y2 = y1 + prim.GetHNDC()

            # DETECT VERTICALLY STACKED PADS (Ratio Plots)
            # If this sub-pad sits at the bottom (y1 close to 0) and doesn't span full height:
            if y1 < 0.15 and y2 < 0.85:
                # Add a 4% vertical gap by lowering the top border of the bottom pad
                # and adjusting margins so labels aren't clipped at the screen bottom
                gap = 0.04
                y2 = max(y1 + 0.05, y2 - gap)
                
            sub_pad = ROOT.TPad(f"sub_{prim.GetName()}_{id(prim)}", "", x1, y1, x2, y2)
            ROOT.SetOwnership(sub_pad, False)
            
            # Ensure bottom ratio pad leaves extra margin at the bottom for axis ticks
            if y1 < 0.15 and y2 < 0.85:
                sub_pad.SetBottomMargin(0.35)
                
            sub_pad.Draw()

            copy_pad_contents(prim, sub_pad)
        else:
            clone_obj = prim.Clone()
            ROOT.SetOwnership(clone_obj, False)
            clone_obj.Draw(draw_opt)

    tgt_pad.Modified()
    tgt_pad.Update()

def combine_canvases(file_names, output_filename="combined_canvases.root"):
    ROOT.gROOT.SetBatch(True)
    ROOT.TH1.AddDirectory(False)
    ROOT.gErrorIgnoreLevel = ROOT.kWarning

    root_files = [ROOT.TFile.Open(f) for f in file_names if os.path.exists(f)]
    if len(root_files) != len(file_names):
        print("Error: One or more input files could not be opened.")
        return

    print(f"Successfully opened {len(root_files)} files.")

    ref_file = root_files[0]
    obj_names = []
    for key in ref_file.GetListOfKeys():
        if key.GetClassName() in ["TCanvas", "TPad"]:
            name = key.GetName()
            if name not in obj_names:
                obj_names.append(name)

    if not obj_names:
        print("Error: No canvases found in reference file.")
        return

    print(f"Found {len(obj_names)} total canvases to process.")

    num_files = len(root_files)
    out_file = ROOT.TFile(output_filename, "RECREATE")

    for idx, obj_name in enumerate(obj_names):
        print(f"Processing ({idx+1}/{len(obj_names)}): {obj_name}...")
        
        ref_canvas = ref_file.Get(obj_name)
        if not ref_canvas:
            continue
            
        orig_w = ref_canvas.GetWindowWidth()
        orig_h = ref_canvas.GetWindowHeight()
        if orig_w <= 0: orig_w = ref_canvas.GetWw()
        if orig_h <= 0: orig_h = ref_canvas.GetWh()
        
        if orig_w <= 10: orig_w = 800
        if orig_h <= 10: orig_h = 800
            
        subpads = []
        lnk = ref_canvas.GetListOfPrimitives().FirstLink()
        while lnk:
            prim = lnk.GetObject()
            if prim and prim.InheritsFrom("TPad"):
                subpads.append(prim)
            lnk = lnk.Next()
            
        is_side_by_side = (len(subpads) == 2 and subpads[0].GetWNDC() < 0.6 and subpads[1].GetWNDC() < 0.6)

        if is_side_by_side:
            print(f"  -> Detected horizontally divided pads. Splitting into _left and _right.")
            
            pad_variants = [
                ("left", lambda p: p.GetXlowNDC() < 0.5),
                ("right", lambda p: p.GetXlowNDC() >= 0.5)
            ]
            
            for variant_name, condition in pad_variants:
                combined_name = f"{obj_name}_{variant_name}"
                panel_w = int(orig_w / 2)
                
                c_main = ROOT.TCanvas(f"combined_{combined_name}", f"Combined {combined_name}", panel_w * num_files, orig_h)
                
                for i, r_file in enumerate(root_files):
                    c_main.cd()
                    target_subpad = ROOT.TPad(f"container_{i}", "", i/num_files, 0.0, (i+1)/num_files, 1.0)
                    target_subpad.SetMargin(0, 0, 0, 0)
                    target_subpad.SetFillStyle(4000)
                    target_subpad.Draw()
                    target_subpad.cd()
                    
                    c_in = r_file.Get(obj_name)
                    if not c_in: continue
                    
                    in_subpads = []
                    lnk_in = c_in.GetListOfPrimitives().FirstLink()
                    while lnk_in:
                        p = lnk_in.GetObject()
                        if p and p.InheritsFrom("TPad"):
                            in_subpads.append(p)
                        lnk_in = lnk_in.Next()
                        
                    matching_pad = next((p for p in in_subpads if condition(p)), None)
                    if matching_pad:
                        copy_pad_contents(matching_pad, target_subpad)
                        
                c_main.Update()
                out_file.cd()
                c_main.Write(combined_name)
                c_main.Close()
                
        else:
            c_main = ROOT.TCanvas(f"combined_{obj_name}", f"Combined {obj_name}", orig_w * num_files, orig_h)

            for i, r_file in enumerate(root_files):
                c_main.cd()
                target_subpad = ROOT.TPad(f"container_{i}", "", i/num_files, 0.0, (i+1)/num_files, 1.0)
                target_subpad.SetMargin(0, 0, 0, 0)
                target_subpad.SetFillStyle(4000)
                target_subpad.Draw()
                target_subpad.cd()
                
                c_in = r_file.Get(obj_name)
                if c_in:
                    copy_pad_contents(c_in, target_subpad)

            c_main.Update()
            out_file.cd()
            c_main.Write(obj_name)
            c_main.Close()

    out_file.Close()

    for r_file in root_files:
        r_file.Close()

    print(f"\nDone! Successfully generated '{output_filename}'.")

if __name__ == "__main__":
    input_files = sys.argv[1:]
    if len(input_files) < 2:
        print("Usage: python combine_plots.py <file1.root> <file2.root> [file3.root ...]")
    else:
        combine_canvases(input_files)