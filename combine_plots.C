

// Extracts the '*' part from 'paper_combined_comparisons_*.root'
TString ExtractLabel(TString filepath) {
    Ssiz_t last_slash = filepath.Last('/');
    if (last_slash != kNPOS) {
        filepath = filepath(last_slash + 1, filepath.Length() - last_slash - 1);
    }
    if (filepath.EndsWith(".root")) {
        filepath.Remove(filepath.Length() - 5);
    }
    TString prefix = "paper_combined_comparisons_";
    if (filepath.BeginsWith(prefix)) {
        filepath.Remove(0, prefix.Length());
    }
    return filepath;
}

void CopyPadToTarget(TPad* src_pad, TCanvas* target_canvas, Double_t x1_target, Double_t y1_target, Double_t x2_target, Double_t y2_target, TString label = "") {
    if (!src_pad) return;

    TList* prim_list = src_pad->GetListOfPrimitives();
    if (!prim_list) return;

    // Check for nested child TPads (e.g. pad1 and pad2 in ratio plots)
    std::vector<TPad*> child_pads;
    TObjLink* lnk = prim_list->FirstLink();
    while (lnk) {
        TObject* obj = lnk->GetObject();
        if (obj && obj->InheritsFrom(TPad::Class()) && std::string(obj->GetName()) != "TFrame") {
            child_pads.push_back((TPad*)obj);
        }
        lnk = lnk->Next();
    }

    if (!child_pads.empty()) {
        // Recursively map child pads directly to the target canvas slot
        for (auto* child : child_pads) {
            Double_t c_x1 = x1_target + child->GetXlowNDC() * (x2_target - x1_target);
            Double_t c_x2 = x1_target + (child->GetXlowNDC() + child->GetWNDC()) * (x2_target - x1_target);
            Double_t c_y1 = y1_target + child->GetYlowNDC() * (y2_target - y1_target);
            Double_t c_y2 = y1_target + (child->GetYlowNDC() + child->GetHNDC()) * (y2_target - y1_target);

            CopyPadToTarget(child, target_canvas, c_x1, c_y1, c_x2, c_y2, label);
        }
    } else {
        // Create leaf pad directly on the main canvas with 1:1 coordinate scaling
        TString new_name = Form("pad_%s_%p", src_pad->GetName(), (void*)src_pad);
        TPad* new_pad = new TPad(new_name, "", x1_target, y1_target, x2_target, y2_target);
        
        // Match exact margins, scale settings, and flags from source
        new_pad->SetLogx(src_pad->GetLogx());
        new_pad->SetLogy(src_pad->GetLogy());
        new_pad->SetLogz(src_pad->GetLogz());
        new_pad->SetLeftMargin(src_pad->GetLeftMargin());
        new_pad->SetRightMargin(src_pad->GetRightMargin());
        new_pad->SetTopMargin(src_pad->GetTopMargin());
        new_pad->SetBottomMargin(src_pad->GetBottomMargin());
        new_pad->SetGridx(src_pad->GetGridx());
        new_pad->SetGridy(src_pad->GetGridy());
        new_pad->SetTickx(src_pad->GetTickx());
        new_pad->SetTicky(src_pad->GetTicky());
        new_pad->SetFillColor(src_pad->GetFillColor());
        new_pad->SetFillStyle(src_pad->GetFillStyle());

        target_canvas->cd();
        new_pad->Draw();
        new_pad->cd();

        // Copy primitives
        lnk = prim_list->FirstLink();
        while (lnk) {
            TObject* prim = lnk->GetObject();
            TString draw_opt = lnk->GetOption();
            lnk = lnk->Next();

            if (!prim || std::string(prim->GetName()) == "TFrame") continue;

            if (!prim->InheritsFrom(TPad::Class())) {
                TObject* clone_obj = prim->Clone();
                clone_obj->Draw(draw_opt);
            }
        }

        // Draw section label in the top margin of the upper pad
        if (!label.IsNull() && y2_target > 0.8) {
            new_pad->cd();
            Double_t y_pos = 1.0 - (new_pad->GetTopMargin() * 0.45);
            TLatex* lat = new TLatex(0.5, y_pos, label);
            lat->SetNDC(kTRUE);
            lat->SetTextFont(62);    // Bold Helvetica
            lat->SetTextSize(0.045);  // Adjusted for legibility
            lat->SetTextAlign(22);   // Center-aligned horizontally and vertically
            lat->Draw();
        }

        new_pad->Modified();
        new_pad->Update();
    }
}

void combine_plots(TString f1, TString f2, TString f3 = "", TString f4 = "", TString output_filename = "combined_canvases.root") {
    gROOT->SetBatch(kTRUE);
    TH1::AddDirectory(kFALSE);
    gErrorIgnoreLevel = kWarning;

    std::vector<TString> raw_files = {f1, f2, f3, f4};
    std::vector<TFile*> root_files;
    std::vector<TString> file_labels;

    for (const auto& fn : raw_files) {
        if (fn.IsNull()) continue;
        TFile* f = TFile::Open(fn, "READ");
        if (f && !f->IsZombie()) {
            root_files.push_back(f);
            file_labels.push_back(ExtractLabel(fn));
        } else {
            std::cout << "Error opening file: " << fn << std::endl;
            return;
        }
    }

    if (root_files.empty()) return;

    TFile* ref_file = root_files[0];
    std::vector<std::string> obj_names;

    TList* keys = ref_file->GetListOfKeys();
    for (Int_t i = 0; i < keys->GetSize(); ++i) {
        TKey* key = (TKey*)keys->At(i);
        TString clName = key->GetClassName();
        if (clName == "TCanvas" || clName == "TPad") {
            std::string name = key->GetName();
            if (std::find(obj_names.begin(), obj_names.end(), name) == obj_names.end()) {
                obj_names.push_back(name);
            }
        }
    }

    Int_t num_files = root_files.size();
    TFile* out_file = new TFile(output_filename, "RECREATE");

    for (size_t idx = 0; idx < obj_names.size(); ++idx) {
        std::string obj_name = obj_names[idx];
        std::cout << "Processing (" << idx + 1 << "/" << obj_names.size() << "): " << obj_name << "..." << std::endl;

        TCanvas* ref_canvas = (TCanvas*)ref_file->Get(obj_name.c_str());
        if (!ref_canvas) continue;

        Int_t orig_w = ref_canvas->GetWw();
        Int_t orig_h = ref_canvas->GetWh();
        if (orig_w <= 10) orig_w = 800;
        if (orig_h <= 10) orig_h = 800;

        std::vector<TPad*> subpads;
        TObjLink* lnk = ref_canvas->GetListOfPrimitives()->FirstLink();
        while (lnk) {
            TObject* p = lnk->GetObject();
            if (p && p->InheritsFrom(TPad::Class()) && std::string(p->GetName()) != "TFrame") {
                subpads.push_back((TPad*)p);
            }
            lnk = lnk->Next();
        }

        bool is_side_by_side = (subpads.size() == 2 && subpads[0]->GetWNDC() < 0.6 && subpads[1]->GetWNDC() < 0.6);

        if (is_side_by_side) {
            std::cout << "  -> Detected side-by-side pads. Splitting into _left and _right." << std::endl;

            std::vector<std::pair<std::string, bool>> variants = {{"left", true}, {"right", false}};
            for (const auto& var : variants) {
                std::string combined_name = obj_name + "_" + var.first;
                Int_t panel_w = orig_w / 2;

                TCanvas* c_main = new TCanvas(Form("combined_%s", combined_name.c_str()), Form("Combined %s", combined_name.c_str()), panel_w * num_files, orig_h);

                for (Int_t i = 0; i < num_files; ++i) {
                    TCanvas* c_in = (TCanvas*)root_files[i]->Get(obj_name.c_str());
                    if (!c_in) continue;

                    TObjLink* lnk_in = c_in->GetListOfPrimitives()->FirstLink();
                    TPad* matching_pad = nullptr;
                    while (lnk_in) {
                        TObject* p = lnk_in->GetObject();
                        if (p && p->InheritsFrom(TPad::Class()) && std::string(p->GetName()) != "TFrame") {
                            TPad* pad_candidate = (TPad*)p;
                            if (var.second && pad_candidate->GetXlowNDC() < 0.5) {
                                matching_pad = pad_candidate;
                                break;
                            } else if (!var.second && pad_candidate->GetXlowNDC() >= 0.5) {
                                matching_pad = pad_candidate;
                                break;
                            }
                        }
                        lnk_in = lnk_in->Next();
                    }

                    if (matching_pad) {
                        Double_t x1 = (Double_t)i / num_files;
                        Double_t x2 = (Double_t)(i + 1) / num_files;
                        CopyPadToTarget(matching_pad, c_main, x1, 0.0, x2, 1.0, file_labels[i]);
                    }
                }

                c_main->Update();
                out_file->cd();
                c_main->Write(combined_name.c_str());
                delete c_main;
            }
        } else {
            TCanvas* c_main = new TCanvas(Form("combined_%s", obj_name.c_str()), Form("Combined %s", obj_name.c_str()), orig_w * num_files, orig_h);

            for (Int_t i = 0; i < num_files; ++i) {
                TCanvas* c_in = (TCanvas*)root_files[i]->Get(obj_name.c_str());
                if (c_in) {
                    Double_t x1 = (Double_t)i / num_files;
                    Double_t x2 = (Double_t)(i + 1) / num_files;
                    CopyPadToTarget(c_in, c_main, x1, 0.0, x2, 1.0, file_labels[i]);
                }
            }

            c_main->Update();
            out_file->cd();
            c_main->Write(obj_name.c_str());
            delete c_main;
        }
    }

    out_file->Close();
    for (auto* f : root_files) f->Close();
    std::cout << "\nDone! Successfully written to " << output_filename << std::endl;
}