from __future__ import annotations

from pathlib import Path
from typing import Iterable

from PIL import Image, ImageDraw, ImageFont
from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "dist" / "NADI_XYLEM_Project_Dossier_2026.docx"
ASSET_DIR = ROOT / "dist" / "nadi_dossier_assets"

NAVY = "17365D"
BLUE = "2F75B5"
TEAL = "1F8A8A"
PALE_BLUE = "EAF2F8"
PALE_TEAL = "E9F5F4"
PALE_GRAY = "F3F5F7"
MID_GRAY = "D9E1E8"
TEXT_GRAY = RGBColor(70, 70, 70)


def set_cell_shading(cell, fill: str) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = tc_pr.find(qn("w:shd"))
    if shd is None:
        shd = OxmlElement("w:shd")
        tc_pr.append(shd)
    shd.set(qn("w:fill"), fill)


def set_cell_margins(cell, top=100, start=120, bottom=100, end=120) -> None:
    tc = cell._tc
    tc_pr = tc.get_or_add_tcPr()
    tc_mar = tc_pr.first_child_found_in("w:tcMar")
    if tc_mar is None:
        tc_mar = OxmlElement("w:tcMar")
        tc_pr.append(tc_mar)
    for margin, value in (("top", top), ("start", start), ("bottom", bottom), ("end", end)):
        node = tc_mar.find(qn(f"w:{margin}"))
        if node is None:
            node = OxmlElement(f"w:{margin}")
            tc_mar.append(node)
        node.set(qn("w:w"), str(value))
        node.set(qn("w:type"), "dxa")


def set_table_borders(table, color="D9D9D9", size="6") -> None:
    tbl_pr = table._tbl.tblPr
    borders = tbl_pr.first_child_found_in("w:tblBorders")
    if borders is None:
        borders = OxmlElement("w:tblBorders")
        tbl_pr.append(borders)
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        tag = qn(f"w:{edge}")
        element = borders.find(tag)
        if element is None:
            element = OxmlElement(f"w:{edge}")
            borders.append(element)
        element.set(qn("w:val"), "single")
        element.set(qn("w:sz"), size)
        element.set(qn("w:color"), color)


def set_repeat_table_header(row) -> None:
    tr_pr = row._tr.get_or_add_trPr()
    tbl_header = OxmlElement("w:tblHeader")
    tbl_header.set(qn("w:val"), "true")
    tr_pr.append(tbl_header)


def set_run_font(run, name="Arial", size=None, bold=None, color=None, italic=None) -> None:
    run.font.name = name
    run._element.get_or_add_rPr().rFonts.set(qn("w:ascii"), name)
    run._element.get_or_add_rPr().rFonts.set(qn("w:hAnsi"), name)
    if size is not None:
        run.font.size = Pt(size)
    if bold is not None:
        run.bold = bold
    if italic is not None:
        run.italic = italic
    if color is not None:
        run.font.color.rgb = RGBColor.from_string(color)


def add_page_number(paragraph) -> None:
    paragraph.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    run = paragraph.add_run("Page ")
    set_run_font(run, size=8, color="666666")
    fld_char1 = OxmlElement("w:fldChar")
    fld_char1.set(qn("w:fldCharType"), "begin")
    instr_text = OxmlElement("w:instrText")
    instr_text.set(qn("xml:space"), "preserve")
    instr_text.text = " PAGE "
    fld_char2 = OxmlElement("w:fldChar")
    fld_char2.set(qn("w:fldCharType"), "end")
    run._r.append(fld_char1)
    run._r.append(instr_text)
    run._r.append(fld_char2)


def add_table(doc: Document, headers: list[str], rows: Iterable[Iterable[str]], widths: list[float] | None = None):
    table = doc.add_table(rows=1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    set_table_borders(table)
    header = table.rows[0]
    set_repeat_table_header(header)
    for i, text in enumerate(headers):
        cell = header.cells[i]
        set_cell_shading(cell, NAVY)
        set_cell_margins(cell)
        cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        run = p.add_run(str(text))
        set_run_font(run, size=9, bold=True, color="FFFFFF")
        if widths:
            cell.width = Inches(widths[i])
    for row_index, values in enumerate(rows):
        cells = table.add_row().cells
        fill = "FFFFFF" if row_index % 2 == 0 else PALE_BLUE
        for i, value in enumerate(values):
            cell = cells[i]
            set_cell_shading(cell, fill)
            set_cell_margins(cell)
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.05
            run = p.add_run(str(value))
            set_run_font(run, size=8.6, color="222222")
            if widths:
                cell.width = Inches(widths[i])
    doc.add_paragraph().paragraph_format.space_after = Pt(0)
    return table


def add_bullets(doc: Document, items: Iterable[str], level: int = 0) -> None:
    for item in items:
        p = doc.add_paragraph(style="List Bullet" if level == 0 else "List Bullet 2")
        p.paragraph_format.space_after = Pt(3)
        p.add_run(item)


def add_numbered(doc: Document, items: Iterable[str]) -> None:
    for item in items:
        p = doc.add_paragraph(style="List Number")
        p.paragraph_format.space_after = Pt(3)
        p.add_run(item)


def add_equation(doc: Document, text: str) -> None:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(5)
    p.paragraph_format.space_after = Pt(8)
    run = p.add_run(text)
    set_run_font(run, name="Cambria Math", size=11.5, italic=True, color="17365D")


def heading(doc: Document, text: str, level: int = 1) -> None:
    p = doc.add_heading(text, level=level)
    p.paragraph_format.keep_with_next = True


def body(doc: Document, text: str, bold_lead: str | None = None) -> None:
    p = doc.add_paragraph()
    if bold_lead and text.startswith(bold_lead):
        r1 = p.add_run(bold_lead)
        r1.bold = True
        p.add_run(text[len(bold_lead):])
    else:
        p.add_run(text)


def font(size: int, bold=False):
    candidates = [
        Path("C:/Windows/Fonts/arial.ttf"),
        Path("C:/Windows/Fonts/calibri.ttf"),
    ]
    if bold:
        candidates = [Path("C:/Windows/Fonts/arialbd.ttf"), Path("C:/Windows/Fonts/calibrib.ttf")]
    for path in candidates:
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


def make_architecture(path: Path) -> None:
    img = Image.new("RGB", (1800, 500), "white")
    d = ImageDraw.Draw(img)
    labels = [
        "Past evidence\nand context",
        "Calibrated\nrisk models",
        "Uncertainty\nset",
        "SDAIF\noptimisation",
        "Ordered tests\nand actions",
        "Laboratory\nfeedback",
    ]
    fills = ["#EAF2F8", "#DCEAF7", "#E9F5F4", "#D7EEEC", "#EAF2F8", "#F3F5F7"]
    x0, y0, w, h, gap = 40, 135, 245, 190, 48
    for i, (label, fill) in enumerate(zip(labels, fills)):
        x = x0 + i * (w + gap)
        d.rounded_rectangle((x, y0, x + w, y0 + h), radius=20, fill=fill, outline="#2F75B5", width=4)
        lines = label.split("\n")
        for j, line in enumerate(lines):
            bb = d.textbbox((0, 0), line, font=font(32, True))
            tx = x + (w - (bb[2] - bb[0])) / 2
            ty = y0 + 55 + j * 45
            d.text((tx, ty), line, font=font(32, True), fill="#17365D")
        if i < len(labels) - 1:
            ax1 = x + w + 8
            ax2 = x + w + gap - 8
            ay = y0 + h / 2
            d.line((ax1, ay, ax2, ay), fill="#1F8A8A", width=8)
            d.polygon([(ax2, ay), (ax2 - 18, ay - 13), (ax2 - 18, ay + 13)], fill="#1F8A8A")
    d.text((45, 40), "NADI decision pathway", font=font(44, True), fill="#111111")
    img.save(path, quality=95)


def make_bar_chart(path: Path, title: str, labels: list[str], values: list[float], maximum: float, suffix: str = "") -> None:
    img = Image.new("RGB", (1500, 850), "white")
    d = ImageDraw.Draw(img)
    d.text((70, 45), title, font=font(42, True), fill="#111111")
    left, top, right, bottom = 155, 150, 1400, 700
    d.line((left, bottom, right, bottom), fill="#555555", width=3)
    colors = ["#2F75B5", "#1F8A8A", "#8FAADC", "#A5A5A5", "#5B9BD5", "#70AD47"]
    count = len(values)
    slot = (right - left) / count
    bw = slot * 0.55
    for i, (label, value) in enumerate(zip(labels, values)):
        x = left + slot * i + slot * 0.22
        height = (value / maximum) * (bottom - top)
        y = bottom - height
        d.rounded_rectangle((x, y, x + bw, bottom), radius=10, fill=colors[i % len(colors)])
        value_text = f"{value:g}{suffix}"
        bb = d.textbbox((0, 0), value_text, font=font(32, True))
        d.text((x + (bw - (bb[2] - bb[0])) / 2, y - 48), value_text, font=font(32, True), fill="#17365D")
        label_lines = label.split("\n")
        for j, line in enumerate(label_lines):
            bb = d.textbbox((0, 0), line, font=font(24))
            d.text((x + (bw - (bb[2] - bb[0])) / 2, bottom + 22 + j * 30), line, font=font(24), fill="#333333")
    img.save(path, quality=95)


def caption(doc: Document, text: str) -> None:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(9)
    r = p.add_run(text)
    set_run_font(r, size=8.5, italic=True, color="555555")


def configure_document(doc: Document) -> None:
    section = doc.sections[0]
    section.page_width = Inches(8.5)
    section.page_height = Inches(11)
    section.top_margin = Inches(0.72)
    section.bottom_margin = Inches(0.72)
    section.left_margin = Inches(0.78)
    section.right_margin = Inches(0.78)

    normal = doc.styles["Normal"]
    normal.font.name = "Arial"
    normal._element.rPr.rFonts.set(qn("w:ascii"), "Arial")
    normal._element.rPr.rFonts.set(qn("w:hAnsi"), "Arial")
    normal.font.size = Pt(10.2)
    normal.font.color.rgb = RGBColor(35, 35, 35)
    normal.paragraph_format.space_after = Pt(6)
    normal.paragraph_format.line_spacing = 1.12

    title = doc.styles["Title"]
    title.font.name = "Arial"
    title._element.rPr.rFonts.set(qn("w:ascii"), "Arial")
    title._element.rPr.rFonts.set(qn("w:hAnsi"), "Arial")
    title.font.size = Pt(28)
    title.font.bold = True
    title.font.color.rgb = RGBColor(0, 0, 0)
    # Word's built-in Title style may inherit a theme bottom border.  The
    # dossier uses a clean cover title without decorative rules.
    title_ppr = title._element.get_or_add_pPr()
    title_border = title_ppr.find(qn("w:pBdr"))
    if title_border is not None:
        title_ppr.remove(title_border)

    for name, size in (("Heading 1", 18), ("Heading 2", 14), ("Heading 3", 11.5)):
        style = doc.styles[name]
        style.font.name = "Arial"
        style._element.rPr.rFonts.set(qn("w:ascii"), "Arial")
        style._element.rPr.rFonts.set(qn("w:hAnsi"), "Arial")
        style.font.size = Pt(size)
        style.font.bold = True
        style.font.color.rgb = RGBColor(0, 0, 0)
        style.paragraph_format.space_before = Pt(12 if name == "Heading 1" else 8)
        style.paragraph_format.space_after = Pt(5)
        style.paragraph_format.keep_with_next = True

    footer = section.footer
    p = footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    r = p.add_run("NADI Framework  |  Xylem Global Student Innovation Challenge 2026")
    set_run_font(r, size=8, color="666666")
    p.add_run(" " * 8)
    add_page_number(p)


def build() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    ASSET_DIR.mkdir(parents=True, exist_ok=True)
    architecture = ASSET_DIR / "nadi_architecture.png"
    testing = ASSET_DIR / "nadi_testing_outcomes.png"
    metrics = ASSET_DIR / "nadi_model_metrics.png"
    hydraulics = ASSET_DIR / "nadi_hydraulic_improvement.png"
    make_architecture(architecture)
    make_bar_chart(testing, "High E. coli results found within three tests", ["Adaptive\nSDAIF", "Routine\nfrequency", "Deterministic\nrandom"], [114, 84, 80], 125)
    make_bar_chart(metrics, "Locked microbial risk performance", ["F1", "ROC\nAUC", "PR\nAUC", "Sensitivity", "Balanced\naccuracy", "Specificity"], [83.8, 86.6, 91.6, 96.6, 67.8, 39.0], 100, "%")
    make_bar_chart(hydraulics, "Median internal pressure error on real BWFLnet", ["Raw\nphysics", "Training\nmean", "Hybrid\nNADI"], [1.056, 0.827, 0.278], 1.2, " m")

    doc = Document()
    configure_document(doc)

    # Cover
    p = doc.add_paragraph(style="Title")
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_before = Pt(72)
    cover_ppr = p._p.get_or_add_pPr()
    cover_border = cover_ppr.find(qn("w:pBdr"))
    if cover_border is not None:
        cover_ppr.remove(cover_border)
    p.add_run("NADI Framework")
    p2 = doc.add_paragraph()
    p2.paragraph_format.space_after = Pt(18)
    r = p2.add_run("Network Adaptive Decision Intelligence for Water Safety")
    set_run_font(r, size=17, bold=True, color=NAVY)
    p3 = doc.add_paragraph()
    r = p3.add_run("Detailed project dossier for the Xylem Global Student Innovation Challenge 2026")
    set_run_font(r, size=12.5, color="333333")
    doc.add_paragraph()
    cover_figure = doc.add_picture(str(architecture), width=Inches(6.85))
    cover_figure._inline.docPr.set("descr", "NADI decision pathway from past evidence through calibrated risk, uncertainty-aware SDAIF optimisation, ordered testing and laboratory feedback.")
    caption(doc, "From past evidence to an ordered testing decision under uncertainty")
    p4 = doc.add_paragraph()
    p4.paragraph_format.space_before = Pt(24)
    r = p4.add_run("Project status")
    set_run_font(r, size=10, bold=True, color=NAVY)
    p4.add_run("  Working applied-mathematics and software prototype with authentic retrospective validation and separate real-network hydraulic validation")
    p5 = doc.add_paragraph()
    r = p5.add_run("Document version")
    set_run_font(r, size=10, bold=True, color=NAVY)
    p5.add_run("  20 November 2026")
    p6 = doc.add_paragraph()
    r = p6.add_run("Central decision")
    set_run_font(r, size=10, bold=True, color=NAVY)
    p6.add_run("  When only a few confirmatory tests are available, where should testing begin?")
    doc.add_page_break()

    heading(doc, "Executive Summary", 1)
    body(doc, "NADI is a software-first applied-mathematics project designed to help water-quality teams decide where limited confirmatory testing should begin. It addresses a practical bottleneck: contamination can be invisible, laboratory capacity and field teams are limited, and a monitoring authority cannot test every possible location at the same moment. NADI converts strictly past evidence into calibrated risk estimates, represents disagreement among model families as uncertainty, and applies the SDAIF decision framework to produce an ordered testing list under a fixed budget.")
    body(doc, "The current Xylem evidence uses 13,405 authentic 2024 site-day observations from the UK Environment Agency, covering 920 monitoring sites. Training, probability calibration, model selection and locked testing are separated chronologically. On 545 locked observations, the selected XGBoost model achieved F1 0.838, ROC-AUC 0.866, PR-AUC 0.916 and sensitivity 0.966. Across 41 eligible multi-site monitoring rounds with a budget of three tests, adaptive SDAIF found 114 confirmed high-E.-coli results, compared with 84 for routine-frequency ordering and 80 for one deterministic-random ordering. SDAIF equalled, rather than exceeded, the strongest single-model and adaptive-Bayesian comparators.")
    body(doc, "A separate real-network study uses BWFLnet, an authentic operational drinking-water network with 2,548 nodes and 2,606 links. NADI's hybrid physical and statistical model reconstructed internal pressure from sparse boundary observations with a median internal-node error of 0.278 m, a 66.3% reduction relative to a training-mean baseline. This supports the feasibility of network-state estimation but does not validate E. coli transport or a contaminated pipe branch.")
    body(doc, "The demonstrated project is therefore an authentic testing-prioritisation system with a separately validated hydraulic extension. It does not claim direct E. coli detection by ordinary sensors, a Delhi or Ghaziabad digital twin, prospective municipal deployment, illness reduction, or a fully validated biological contamination-to-pipeline chain. These boundaries strengthen the project because each claim is tied to the evidence that actually supports it.")

    heading(doc, "Xylem Project Snapshot", 2)
    add_table(doc, ["Question", "Current answer"], [
        ("What problem is solved?", "Prioritising limited confirmatory E. coli testing when many locations compete for attention."),
        ("Who uses it?", "Water-quality monitoring teams, sampling coordinators and utility decision-makers."),
        ("What is built?", "A reproducible risk-modelling pipeline, SDAIF optimisation engine, authentic replay dashboard and real-network hydraulic estimator."),
        ("What is the key output?", "An ordered list of locations to test first, accompanied by uncertainty, regret and an explanation of why they were selected."),
        ("What is the main result?", "114 high-E.-coli results found in the top three positions across 41 locked rounds, versus 84 under routine-frequency ordering."),
        ("What remains future work?", "Prospective validation on a linked drinking-water network with microbiology, operations and network telemetry from the same events."),
    ], [2.0, 4.85])

    heading(doc, "Document Map", 2)
    add_bullets(doc, [
        "Sections 1 to 4 define the problem, system scope, research questions and full architecture.",
        "Sections 5 to 9 explain the datasets, machine learning, SDAIF mathematics, experiment and authentic results.",
        "Sections 10 to 13 cover hydraulics, integration, deployment and the user-facing prototype.",
        "Sections 14 to 18 address innovation, reproducibility, safety, limitations and the Xylem scale pathway; the appendices provide metrics, definitions and jury questions.",
    ])

    heading(doc, "1 Problem Landscape", 1)
    heading(doc, "1.1 Why faecal contamination is difficult to manage", 2)
    body(doc, "E. coli is used as an indicator of faecal contamination because its presence can signal that water has been exposed to faecal material and may also contain disease-causing organisms. It is microscopic and cannot be reliably identified through appearance, smell or taste. Confirmatory microbiological testing is therefore essential, but sampling, transport, incubation and laboratory processing create delays and resource constraints.")
    body(doc, "In intermittent or ageing drinking-water systems, risk can be amplified by loss of pressure, pipe defects, cross-connections, nearby sewage, compromised storage tanks and uncertain valve or demand conditions. Yet the current Xylem experiment does not assume that every high-risk monitoring point belongs to such a network. It treats faecal-risk prioritisation and hydraulic-network modelling as separate evidence tracks until common event-level data exist.")
    heading(doc, "1.2 The decision bottleneck", 2)
    body(doc, "The central bottleneck is not simply the absence of sensors or laboratory testing. The bottleneck is allocation: a team has more possible locations than it can test immediately. Routine schedules may spend scarce capacity at historically frequent sites, while an untested location with a higher current risk remains undiscovered.")
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("When only three tests are available, which three locations should be tested first?")
    set_run_font(r, size=13, bold=True, color=NAVY)
    body(doc, "This question is measurable. A policy can be evaluated by how many independently confirmed positives it finds in its first k tests, how quickly it reaches the first positive, how often it misses an event, and how much regret it incurs relative to an oracle that already knows the results.")
    heading(doc, "1.3 Why a probability map is insufficient", 2)
    body(doc, "A risk map can identify locations with high estimated probabilities, but it does not decide how to spend a limited test budget when models disagree, evidence is delayed, and the cost of missing one location differs from another. NADI's applied-mathematics contribution operates at this decision boundary. Prediction supplies evidence; mathematics converts that evidence into an auditable action.")

    heading(doc, "2 Project Scope and Claim Boundary", 1)
    body(doc, "NADI has a broad long-term vision and a narrower validated Xylem claim. Keeping these levels separate prevents a future capability from being presented as a completed result.")
    add_table(doc, ["Capability", "Evidence status", "Permitted interpretation"], [
        ("E. coli risk estimation", "Demonstrated in authentic UK surface-water data", "Retrospective risk and test-priority evidence in the source domain."),
        ("Limited-test prioritisation", "Demonstrated in 41 locked authentic rounds", "NADI can rank already observed monitoring candidates more effectively than routine frequency in this replay."),
        ("Uncertainty-aware SDAIF", "Implemented and tested", "Produces robust plans, regret, adversarial model and abstention; no superiority over strongest simple model is claimed."),
        ("Real-network pressure reconstruction", "Demonstrated on BWFLnet", "Supports hydraulic state estimation from sparse boundary measurements."),
        ("Affected-pipe localisation", "Demonstrated only in simulation", "Plausible routes under declared EPANET/WNTR scenarios, not confirmed biological spread."),
        ("Delhi or Ghaziabad deployment", "Not established", "Requires local topology, operating state, historical labels and prospective evaluation."),
        ("Direct E. coli detection", "Not implemented", "Ordinary physicochemical sensors remain proxy evidence, not biological confirmation."),
        ("Reduced illness or exposure", "Not established", "Requires prospective operational and health-outcome evidence."),
    ], [1.65, 1.65, 3.55])
    heading(doc, "2.1 Validated Xylem claim", 2)
    body(doc, "NADI uses authentic historical E. coli monitoring evidence and transparent decision mathematics to prioritise a limited confirmatory-testing budget. In a retrospective locked evaluation, its three-site lists found substantially more high-E.-coli results than routine-frequency or deterministic-random ordering. A separate hydraulic study demonstrates that sparse real-network measurements can reconstruct internal pressure conditions accurately enough to support future network-aware extensions.")
    heading(doc, "2.2 Prohibited overclaims", 2)
    add_bullets(doc, [
        "NADI does not directly detect E. coli using pressure, chlorine, turbidity, conductivity, pH, temperature or fluorescence proxies.",
        "The authentic surface-water sites are not represented as drinking-water pipe nodes.",
        "Coordinate-based monitoring zones are not pipe routes or hydraulically affected regions.",
        "Simulation does not establish Delhi-NCR field performance or prove that a particular branch is contaminated.",
        "Model performance does not prove illness prevention or regulatory safety.",
    ])

    heading(doc, "3 Research Questions and Objectives", 1)
    body(doc, "The research is structured around a primary decision question and a set of bounded technical questions.")
    add_numbered(doc, [
        "Can past-only laboratory history, season, region and location estimate the probability of a high E. coli result without using the current result?",
        "Can disagreement among calibrated model families be propagated into the final testing decision instead of being hidden behind one score?",
        "Under an equal three-test budget, does SDAIF find more confirmed positives than random and routine-frequency ordering?",
        "Does the robust decision layer add value beyond a single strong model and Bayesian averaging?",
        "Can a physical water-network model reconstruct internal hydraulic conditions from sparse boundary observations on an authentic operational network?",
        "When transfer support is inadequate, can NADI abstain rather than produce unjustified confidence?",
    ])
    heading(doc, "3.1 Primary objectives", 2)
    add_table(doc, ["Objective", "Measurable outcome"], [
        ("Risk estimation", "F1, sensitivity, specificity, balanced accuracy, ROC-AUC, PR-AUC, Brier score and calibration error."),
        ("Testing prioritisation", "Positives found within first k tests, tests to first positive, missed-positive rounds and positive-discovery regret."),
        ("Uncertainty management", "Worst-case regret, model disagreement, adversarial witness, support status and abstention."),
        ("Hydraulic feasibility", "MAE, RMSE, bias, R-squared, interval coverage and comparison with raw-physics and mean baselines."),
        ("Reproducibility", "Frozen hashes, executable scripts, deterministic seeds, automated tests and claim-boundary audits."),
    ], [2.1, 4.75])

    heading(doc, "4 NADI System Architecture", 1)
    architecture_figure = doc.add_picture(str(architecture), width=Inches(6.85))
    architecture_figure._inline.docPr.set("descr", "NADI system architecture showing calibrated risk models, an uncertainty set, SDAIF optimisation and ordered testing decisions.")
    caption(doc, "Figure 1  NADI converts past evidence into an ordered decision and updates only after a result becomes available")
    heading(doc, "4.1 Functional layers", 2)
    add_table(doc, ["Layer", "Function", "Current Xylem implementation"], [
        ("Evidence", "Collects historical microbial results, dates, location, material and monitoring context.", "Authentic EA records with causal historical features."),
        ("Risk models", "Estimate probability of a high E. coli endpoint.", "Logistic regression, histogram gradient boosting and XGBoost."),
        ("Calibration", "Transforms raw model scores into probabilities using an earlier calibration period.", "Platt calibration fitted before validation and locked testing."),
        ("Uncertainty", "Represents structural disagreement among model families.", "Each calibrated model becomes a weighted uncertainty vertex."),
        ("SDAIF", "Chooses a fixed-budget testing list under expected and worst-case regret.", "Mixed-integer optimisation with sequential re-ranking."),
        ("Feedback", "Updates model weights after a result arrives.", "Retrospective replay using authentic laboratory outcomes revealed only after selection."),
        ("Hydraulics", "Estimates movement and internal network state.", "Separate BWFLnet real-network estimator plus simulated source-tracing research track."),
        ("Interface", "Explains risk, selected tests, uncertainty and evidence origin.", "Flask dashboard and auditable JSON APIs."),
    ], [1.25, 2.45, 3.15])
    heading(doc, "4.2 Hardware-free and future hardware modes", 2)
    body(doc, "The Xylem version is intentionally hardware-free. It can operate from historical laboratory data, site metadata, weather or operational context and network files. Future sentinel hardware can enter through the same evidence interface, but measurements must be calibrated and paired with independent biological truth before they influence an E. coli claim. Hardware is therefore an optional evidence adapter, not the scientific foundation of the current result.")

    heading(doc, "5 Data and Evidence Architecture", 1)
    heading(doc, "5.1 Authentic microbial dataset", 2)
    body(doc, "The main dataset contains 13,405 authentic 2024 site-day records derived from official Environment Agency E. coli observations. It covers 920 sites and 285 sampling dates. Each record includes collection date, site identifier, coordinates, region, material, sampling purpose and laboratory E. coli result. Multiple observations for the same site-day are consolidated using a declared rule, while replicate count is retained.")
    body(doc, "The binary endpoint is a laboratory E. coli value at or above 500 in the source record. This is used as a severe-result prioritisation threshold for the experiment; it is not a drinking-water safety standard and must not be transferred into a regulatory drinking-water claim.")
    heading(doc, "5.2 Evidence classes", 2)
    add_table(doc, ["Evidence class", "Meaning", "Examples"], [
        ("LAB CONFIRMED", "An accepted microbiological observation from its original source.", "Environment Agency E. coli result."),
        ("OBSERVED", "A measured physical, operational, weather or network input.", "BWFLnet pressure and flow logger values."),
        ("MODEL ESTIMATE", "An output produced from observed inputs.", "Calibrated probability, monitoring zone, pressure reconstruction."),
        ("SIMULATED", "A constructed network state or hidden benchmark truth.", "Net3 or L-TOWN source-tracing event."),
        ("ASSUMED", "A declared parameter used because direct evidence is unavailable.", "Candidate cost, consequence weight or hypothetical valve state."),
    ], [1.45, 2.6, 2.8])
    heading(doc, "5.3 Supporting datasets", 2)
    add_table(doc, ["Resource", "Permitted use", "Prohibited inference"], [
        ("BWFLnet", "Real operational pressure and flow reconstruction on a drinking-water network.", "E. coli presence or contaminant spread."),
        ("Net3 and L-TOWN", "Hydraulic source tracing, uncertainty and policy stress testing.", "Field validation or a real city contamination event."),
        ("GECCO and Bristol telemetry", "Operational anomaly and data-pipeline evidence.", "Direct microbial detection."),
        ("Bangladesh drinking-water survey", "Endpoint and geographic-transfer stress analysis.", "Time-series pipe forecasting."),
        ("Marion County and NOAA", "Reconstruction of weather and E. coli forecasting prior art.", "Indian drinking-water distribution performance."),
        ("Open E. coli Models", "Prior-art architecture and controlled XGBoost adaptation.", "Bit-for-bit replication of unavailable full source tables."),
    ], [1.65, 2.55, 2.65])
    heading(doc, "5.4 Non-merging rule", 2)
    body(doc, "Microbial labels, hydraulic telemetry and simulated pipe scenarios are not combined row by row unless they share a verified event, location and time key. Integration currently occurs through mathematical interfaces and separately labelled demonstrations. This prevents a model from appearing biologically validated merely because authentic microbiology and authentic network data both exist somewhere in the repository.")

    heading(doc, "6 Microbial Risk Modelling", 1)
    heading(doc, "6.1 Causal feature construction", 2)
    body(doc, "For each sampling date, historical features are frozen immediately before that date. No result from the current date is allowed to influence another prediction from the same date. The features include spatial coordinates, cyclic day-of-year terms, month, prior sample count, prior positive rate, prior mean log count, last positive indicator, days since the previous sample, region-level history and global history. Categorical context includes region, water material and sampling purpose.")
    heading(doc, "6.2 Model family", 2)
    add_table(doc, ["Model", "Purpose", "Role in uncertainty"], [
        ("Logistic regression", "Transparent linear baseline with balanced class weighting.", "Structurally simple probability vertex."),
        ("Histogram gradient boosting", "Nonlinear continuous-history model.", "Alternative structure that omits categorical one-hot interactions."),
        ("XGBoost", "Stronger nonlinear prior-art family with regularisation and subsampling.", "Selected prediction model on validation PR-AUC and balanced accuracy."),
    ], [1.8, 2.6, 2.45])
    heading(doc, "6.3 Probability calibration", 2)
    body(doc, "Each candidate is fitted on the training period and calibrated on a later chronological period using a high-regularisation logistic mapping of raw log-odds. Calibration is separated from final validation and testing because a ranking score alone cannot be treated as a trustworthy probability.")
    add_equation(doc, "p_cal = sigmoid(a + b * logit(p_raw))")
    heading(doc, "6.4 Threshold and classification interpretation", 2)
    body(doc, "The decision threshold is selected using the validation period, prioritising balanced accuracy and then F1. The locked test is evaluated once under that threshold. High sensitivity is valuable for prioritisation, but it comes with low specificity in the locked period. Therefore NADI is best interpreted as a risk-ranking and test-allocation system, not as an automatic contamination declaration.")

    heading(doc, "7 SDAIF Applied Mathematics", 1)
    heading(doc, "7.1 Decision state", 2)
    body(doc, "For a monitoring round, each calibrated model supplies a probability for every candidate site. A model vertex contains the complete vector of site probabilities. Validation log loss determines the initial weight assigned to each model. SDAIF operates over this finite uncertainty set rather than collapsing every model into one unexplained average.")
    heading(doc, "7.2 Testing-plan loss", 2)
    body(doc, "Let V be the candidate sites, A be a selected test plan, p_mi be the risk assigned to site i under model m, w_i be a consequence weight and c be the cost per test. The missed-risk loss is:")
    add_equation(doc, "L(A, m) = sum over i not in A of w_i * p_mi + c * |A|")
    body(doc, "For the authentic experiment, consequence weights are equal and every compared plan uses the same three-test budget. The model-specific oracle selects the three highest-risk sites under that model.")
    heading(doc, "7.3 Regret", 2)
    body(doc, "Regret measures how much worse a plan is than the oracle plan for the same model state:")
    add_equation(doc, "R(A, m) = L(A, m) - min over B of L(B, m)")
    body(doc, "This is more informative than raw predicted risk because it asks whether the chosen list remains defensible if another calibrated model is correct.")
    heading(doc, "7.4 Posterior robust objective", 2)
    body(doc, "SDAIF balances weighted expected regret against maximum regret. The robustness parameter lambda is selected using validation rounds only.")
    add_equation(doc, "A* = arg min over A [(1 - lambda) * E_m R(A,m) + lambda * max_m R(A,m)]")
    body(doc, "The optimisation is implemented as a mixed-integer linear program. Binary variables indicate whether each site is selected, a budget equality fixes the number of tests, and an auxiliary variable upper-bounds regret for every model vertex. The solver returns the selected plan and the adversarial model that makes that plan look worst.")
    heading(doc, "7.5 Sequential evidence and posterior updating", 2)
    body(doc, "After a site is selected and its actual historical laboratory outcome is revealed, model weights are updated according to the probability each model assigned to that outcome:")
    add_equation(doc, "weight_m,new proportional to weight_m,old * p_mj^y * (1 - p_mj)^(1-y)")
    body(doc, "Within the current robust plan, the next site maximises a proxy for information value: weighted disagreement among model probabilities multiplied by predictive outcome uncertainty. The plan is then re-optimised after the result is known.")
    heading(doc, "7.6 Certificate and abstention", 2)
    body(doc, "In the hydraulic SDAIF engine, a decision is certified when its worst-case regret is no greater than a declared epsilon within the enumerated uncertainty set. This is a conditional mathematical statement, not a universal safety guarantee. If observed evidence contradicts every scenario, or transfer support is inadequate, the system abstains and requests additional evidence instead of returning false certainty.")
    heading(doc, "7.7 Current mathematical result", 2)
    body(doc, "SDAIF provides a transparent uncertainty-to-action calculation, but the authentic evaluation does not show superiority over the strongest simple model or adaptive Bayesian averaging. Its current additional value is assurance: regret, adversarial explanation, model uncertainty, evidence timing and abstention are explicit. A future prospective study must determine whether these properties improve real operational decisions under distribution shift or model failure.")

    heading(doc, "8 Experimental Design", 1)
    heading(doc, "8.1 Chronological protocol", 2)
    add_table(doc, ["Partition", "Dates", "Purpose", "Records"], [
        ("Training", "Through 31 May 2024", "Fit model parameters from earlier observations.", "3,270"),
        ("Calibration", "1 June to 15 July 2024", "Fit probability calibration only.", "3,641"),
        ("Validation", "16 July to 30 September 2024", "Choose model, threshold and SDAIF robustness weight.", "5,949"),
        ("Locked test", "1 October to 31 December 2024", "Final retrospective evaluation.", "545"),
    ], [1.25, 1.55, 3.05, 1.0])
    heading(doc, "8.2 Monitoring-round protocol", 2)
    body(doc, "A decision round contains sites observed on the same date. Rounds with 5 to 25 candidate sites are included so that a three-test budget creates a meaningful allocation problem without an uncontrolled candidate explosion. Forty-one of 56 locked dates meet this criterion, covering 455 of 545 locked site-day records. The exclusion rule must be retained and justified in sensitivity analysis because it removes 15 dates and 90 observations.")
    heading(doc, "8.3 Comparator policies", 2)
    add_table(doc, ["Policy", "Decision rule"], [
        ("Deterministic random", "Hash-derived ordering used as one reproducible random comparator."),
        ("Routine frequency", "Sites with the largest historical sample counts first."),
        ("Historical positive rate", "Sites with the largest prior positive proportions first."),
        ("Best single model", "Highest XGBoost probabilities first."),
        ("Fixed ensemble", "Highest validation-weighted average probability first."),
        ("Adaptive Bayesian", "Posterior-mean risk ranking updated after each revealed result."),
        ("Adaptive SDAIF", "Posterior and worst-case regret plan with information-aware ordering."),
    ], [2.0, 4.85])
    heading(doc, "8.4 Primary decision metrics", 2)
    add_bullets(doc, [
        "Positives found within the first three tests.",
        "Positive-discovery regret relative to an oracle with the same budget.",
        "Tests required to reach the first positive in positive rounds.",
        "Fraction of positive rounds in which the policy finds no positive.",
        "Fraction of all available positives captured within the budget.",
    ])

    heading(doc, "9 Authentic Results", 1)
    metrics_figure = doc.add_picture(str(metrics), width=Inches(6.65))
    metrics_figure._inline.docPr.set("descr", "Bar chart of locked microbial-risk model performance: F1 83.8 percent, ROC-AUC 86.6 percent, PR-AUC 91.6 percent, sensitivity 96.6 percent, balanced accuracy 67.8 percent and specificity 39.0 percent.")
    caption(doc, "Figure 2  Locked classifier performance shows strong ranking and sensitivity but limited specificity")
    heading(doc, "9.1 Locked classification results", 2)
    add_table(doc, ["Metric", "Result", "Interpretation"], [
        ("F1", "0.838", "Strong positive-class balance, but below the requested 0.85 target."),
        ("ROC-AUC", "0.866", "Good ranking across thresholds in the locked source domain."),
        ("PR-AUC", "0.916", "Strong ranking in the high-positive-prevalence locked period."),
        ("Sensitivity", "0.966", "Only 12 of 350 positives were missed at the selected threshold."),
        ("Specificity", "0.390", "119 of 195 negatives were flagged positive."),
        ("Balanced accuracy", "0.678", "Class-balanced performance is materially weaker than recall."),
        ("Precision", "0.740", "About three quarters of predicted positives were positive."),
        ("Brier score", "0.141", "Probability error under the locked distribution."),
        ("Calibration error", "0.073", "Average ten-bin probability calibration deviation."),
    ], [1.55, 1.0, 4.3])
    body(doc, "The locked period differs strongly from the earlier periods: prevalence is 64.2% in the locked test compared with 27.3% in validation. This distribution shift explains why recall remains high while specificity falls. A diagnostic threshold audit confirms that no threshold on the existing locked scores can make accuracy, balanced accuracy, F1, precision and sensitivity all exceed 0.85 simultaneously. The model must not be tuned on the locked labels to manufacture such a claim.")
    heading(doc, "9.2 Testing-priority results", 2)
    testing_figure = doc.add_picture(str(testing), width=Inches(6.35))
    testing_figure._inline.docPr.set("descr", "Bar chart comparing confirmed high E. coli results found in the first three tests across locked monitoring rounds: SDAIF 114, routine-frequency ordering 84 and deterministic random ordering 80.")
    caption(doc, "Figure 3  Confirmed high results found across 41 locked rounds under the same three-test budget")
    add_table(doc, ["Policy", "High results found", "Mean per round", "Missed positive rounds"], [
        ("Adaptive SDAIF", "114", "2.780", "0.0%"),
        ("Adaptive Bayesian", "114", "2.780", "0.0%"),
        ("Best single model", "114", "2.780", "0.0%"),
        ("Fixed ensemble", "114", "2.780", "0.0%"),
        ("Historical positive rate", "111", "2.707", "0.0%"),
        ("Routine frequency", "84", "2.049", "4.9%"),
        ("Deterministic random", "80", "1.951", "4.9%"),
    ], [2.2, 1.45, 1.35, 1.65])
    body(doc, "The paired round-level difference between SDAIF and deterministic random is 0.829 additional positives per round, with a bootstrap 95% interval from 0.609 to 1.073. Against routine frequency, the difference is 0.732 per round, with an interval from 0.488 to 0.976. These intervals condition on the one deterministic-random ordering; a final scientific report should also average many random permutations.")
    heading(doc, "9.3 Transfer stress test", 2)
    body(doc, "Fifty locked observations came from 31 sites that supplied no labels to model training. On these sites, F1 fell to 0.722, ROC-AUC to 0.705 and balanced accuracy to 0.555. This is an important negative result. It demonstrates that the model cannot be presented as globally transferable without local calibration, support testing and an abstention rule.")

    heading(doc, "10 Real Network Hydraulic Validation", 1)
    heading(doc, "10.1 Dataset and task", 2)
    body(doc, "BWFLnet is an authentic operational drinking-water network containing 2,548 nodes and 2,606 links. The NADI study uses 16 observed boundary sensors as contemporaneous inputs and predicts pressure at 27 internal monitored nodes. Six publisher roughness variants are compared on training data, and the Hazen-Williams grouped variant is selected. The hybrid model combines physical pressure predictions, Fourier time terms and boundary observations to estimate the residual between physics and measured internal pressure.")
    add_equation(doc, "observed pressure = physical pressure + learned residual correction")
    heading(doc, "10.2 Training and evaluation", 2)
    body(doc, "The designated 24-hour training day is used for model fitting and expanding-window cross-validation. A separate seven-day validation period contains 673 timestamps and 18,171 internal-node predictions. Ridge regression with regularisation 1 is selected from ridge, partial least squares, extra-trees and random-forest candidates using training-only cross-validation.")
    hydraulics_figure = doc.add_picture(str(hydraulics), width=Inches(6.35))
    hydraulics_figure._inline.docPr.set("descr", "Bar chart of median internal pressure error on BWFLnet: raw physics 1.056 metres, training-mean baseline 0.827 metres and hybrid NADI estimator 0.278 metres.")
    caption(doc, "Figure 4  Hybrid physics and data correction reduces median internal pressure error")
    add_table(doc, ["Hydraulic metric", "Result"], [
        ("Median internal-node MAE", "0.278 m"),
        ("Raw-physics median MAE", "1.056 m"),
        ("Training-mean median MAE", "0.827 m"),
        ("Improvement versus mean", "66.3%"),
        ("Aggregate MAE", "0.415 m"),
        ("Aggregate RMSE", "0.706 m"),
        ("Aggregate R-squared", "0.996"),
        ("Median per-logger R-squared", "0.730"),
        ("Positive per-logger R-squared", "24 of 27 loggers"),
        ("Nominal 90% interval coverage", "84.9%"),
    ], [3.7, 3.15])
    heading(doc, "10.3 Interpretation and limitations", 2)
    body(doc, "The result demonstrates real-network hydraulic state estimation, not biological contamination localisation. Aggregate R-squared is inflated by stable pressure-level differences between nodes, so median per-logger R-squared and MAE are more informative. Three loggers retain negative R-squared, prediction intervals under-cover their nominal 90% target, and the validation week had been inspected during an earlier offset benchmark. It remains held out from final hybrid fitting, but it is no longer a pristine untouched test.")

    heading(doc, "11 Hydraulic Source Tracing and Affected Regions", 1)
    heading(doc, "11.1 Simulated research track", 2)
    body(doc, "The wider NADI research prototype uses EPANET and WNTR to represent pipes, junctions, tanks, demands, valves and source tracing. Ensembles vary source location, demand, tank level and closed-pipe state. A tracer identifies nodes that could receive water originating from a candidate source under each scenario. These affected sets feed the hydraulic form of SDAIF.")
    body(doc, "On Net3, SDAIF's Coverage@3 equals the strongest adaptive Bayesian baseline at 0.615 in the corrected benchmark. On L-TOWN transfer stress testing, SDAIF reaches 0.257 while adaptive Bayesian or hydraulic ranking reaches 0.359. The negative transfer result is retained because it shows that a robust policy is not automatically superior when the scenario set or network changes.")
    heading(doc, "11.2 Why this track remains separate", 2)
    body(doc, "The tracer is not E. coli, and the surface-water risk score is common across network nodes. A common scalar risk changes the magnitude of regret but generally does not identify which branch is biologically contaminated. Until node-specific biological evidence exists, the hydraulic model estimates plausible movement conditional on a hypothesised source; it does not prove contamination.")
    heading(doc, "11.3 Future unified chain", 2)
    add_equation(doc, "risk evidence -> node-specific uncertainty -> hydraulic reach -> affected-zone probability -> constrained testing action")
    body(doc, "A valid unified evaluation requires microbiology, telemetry, supply operations and network location from the same events. NADI already defines the interfaces and mathematics; the missing asset is paired field evidence.")

    heading(doc, "12 Practical Operation", 1)
    heading(doc, "12.1 Current authentic workflow", 2)
    add_numbered(doc, [
        "Import a monitoring authority's historical laboratory table with site identifiers, dates, coordinates, endpoint and metadata.",
        "Generate only past-looking site, regional, seasonal and contextual features.",
        "Train candidate models and calibrate probabilities on a later but pre-test period.",
        "At a monitoring round, generate a probability vector for all eligible candidate sites.",
        "Construct the model-uncertainty set and run SDAIF under the available test budget.",
        "Issue an ordered list with predicted risk, model disagreement, worst-case regret and adversarial model.",
        "After a laboratory result becomes available, record it with provenance and update the next supported decision.",
        "Compare the action and outcome against the authority's routine policy without changing the frozen endpoint or budget.",
    ])
    heading(doc, "12.2 Output decision card", 2)
    add_table(doc, ["Field", "Meaning for the operator"], [
        ("Ordered test list", "Locations recommended first under the available budget."),
        ("Calibrated probability", "Estimated chance of the declared endpoint in the source domain."),
        ("Model disagreement", "How strongly calibrated model families differ at the location."),
        ("Worst-case regret", "Maximum performance gap relative to the scenario-specific oracle."),
        ("Adversarial model", "The model under which the selected list looks worst."),
        ("Transfer support", "Whether the location resembles the model's calibration experience."),
        ("Abstention reason", "Why NADI refuses to issue a confident recommendation."),
        ("Evidence origin", "Whether each input is observed, laboratory-confirmed, modelled, simulated or assumed."),
    ], [2.0, 4.85])
    heading(doc, "12.3 Timing realism", 2)
    body(doc, "The current retrospective adaptive replay reveals each historical laboratory result immediately after site selection. In a real programme, culture-based results may arrive after the remaining samples from that day have already been collected. The deployment-safe interpretation is therefore a static initial list or adaptation between successive monitoring rounds. Same-round adaptivity is permitted only if an independently validated rapid assay returns before the next decision deadline.")

    heading(doc, "13 Software Prototype and Demonstration", 1)
    body(doc, "The Flask prototype exposes an authentic-data interface as the primary Xylem view and retains the simulated hydraulic prototype as a separately labelled legacy view. The authentic API reconstructs a frozen decision round from stored model probabilities, reruns the SDAIF sequence and verifies that the selected order matches the frozen event table. A mismatch raises an error rather than silently displaying a different result.")
    heading(doc, "13.1 Demonstration sequence", 2)
    add_numbered(doc, [
        "Choose one locked monitoring date without revealing the laboratory outcomes.",
        "Display the candidate sites, calibrated risks, model disagreement and transfer-support status.",
        "Run SDAIF and show the first recommended location, robust fallback plan and worst-case model.",
        "Reveal the authentic historical result only after selection.",
        "Update posterior model weights and recompute the next decision.",
        "After three tests, compare confirmed positives with routine and random ordering.",
        "Open the evidence page to show data origin, hashes, metrics and claim boundary.",
    ])
    heading(doc, "13.2 Failure-safe behaviour", 2)
    add_bullets(doc, [
        "Invalid prospective input is rejected before any score is calculated.",
        "Unsupported transfer causes uncertainty inflation or abstention.",
        "Inconsistent revealed evidence invalidates the scenario-bound certificate.",
        "Pending results cannot be treated as known evidence.",
        "Protective actions remain advisory and require operator review.",
    ])

    heading(doc, "14 Innovation and Prior Work", 1)
    heading(doc, "14.1 What is reused", 2)
    body(doc, "NADI intentionally reuses established techniques: calibrated classification, boosted trees, Bayesian model updating, EPANET/WNTR hydraulics, minimax regret, mixed-integer optimisation and value-of-information ideas. The project does not claim that these foundations were invented here.")
    heading(doc, "14.2 What NADI contributes", 2)
    add_bullets(doc, [
        "A single auditable pipeline from causal historical features to calibrated model vertices and a budget-constrained testing decision.",
        "Explicit propagation of model disagreement into expected and worst-case regret rather than displaying one unqualified probability.",
        "An adversarial explanation showing which calibrated model challenges the selected list.",
        "Evidence-timing controls that prevent a future laboratory result from affecting an earlier action.",
        "A strict evidence taxonomy separating authentic microbiology, observed hydraulics, model estimates and simulated reach.",
        "A reproducible comparison against routine, historical, single-model, ensemble, Bayesian and random policies.",
    ])
    heading(doc, "14.3 Honest novelty position", 2)
    body(doc, "The strongest current innovation is the executable uncertainty-to-action integration, not a globally proven new theorem. Global mathematical novelty would require a precise theorem, proof, counterexample against the closest robust-decision formulations and independent expert review. The Xylem submission can confidently present NADI as a novel student implementation and decision architecture without overstating theorem originality.")

    heading(doc, "15 Reproducibility and Scientific Assurance", 1)
    add_table(doc, ["Control", "Implementation"], [
        ("Frozen provenance", "Source files, intended uses, prohibited inferences and SHA-256 hashes are recorded."),
        ("Chronological splits", "Training, calibration, validation and test periods are separated."),
        ("Future-leakage tests", "Features for a date are frozen before results from that date update history."),
        ("Common decision budget", "All policies receive the same candidate set, budget and authentic outcomes."),
        ("Negative-result log", "L-TOWN transfer weakness, comparator ties and prior benchmark repairs are preserved."),
        ("Automated testing", "Seventy-one unit and integration tests currently pass."),
        ("Claim audit", "Automated scripts reject prohibited biological and field claims from generated artifacts."),
        ("Reproduction bundle", "Pinned dependencies, scripts, metrics, manifests and the dashboard are packaged."),
    ], [2.1, 4.75])
    heading(doc, "15.1 Protocol corrections", 2)
    body(doc, "Earlier hydraulic benchmarks contained comparator-fairness, configuration-hash, budget-accounting and empty-event metric problems. Those results were preserved as historical artifacts, the defects were documented, and corrected versions were run under new configurations. This history is scientifically valuable because it shows that the project does not erase negative findings or silently replace an inconvenient result.")
    heading(doc, "15.2 Current release-control issue", 2)
    body(doc, "The latest BWFLnet model and metric-feasibility audit were produced after the existing evidence bundle and reproducibility manifest. Before final submission, the authoritative manifest, dashboard, claim matrix and release archive must be regenerated so every headline number appears in one consistent version.")

    heading(doc, "16 Safety Ethics and Responsible Use", 1)
    body(doc, "NADI is a decision-support prototype, not a substitute for certified laboratory testing, utility engineering judgement or public-health authority. Its principal ethical risk is false reassurance: a confident software output could delay protective action if it is treated as biological confirmation. The system therefore keeps confirmatory testing central, records evidence origin and abstains when domain support is inadequate.")
    add_table(doc, ["Risk", "Control"], [
        ("False negative", "High-sensitivity evaluation, explicit missed-event reporting and confirmatory testing."),
        ("False positive", "Probability calibration, specificity disclosure and operator review before action."),
        ("Unsafe transfer", "Unseen-site evaluation, support gate, local recalibration and abstention."),
        ("Infrastructure sensitivity", "Use bounded or pseudonymised topology and avoid publishing operationally sensitive control data."),
        ("Privacy", "Use pseudonymous site or node identifiers and omit household or personal information."),
        ("Automation bias", "Show uncertainty, alternatives, adversarial model and claim boundary beside the recommendation."),
        ("Simulation confusion", "Label every simulated network result visibly and keep it separate from authentic biological evidence."),
    ], [2.0, 4.85])

    heading(doc, "17 Limitations and Negative Results", 1)
    add_table(doc, ["Limitation", "Why it matters", "Required resolution"], [
        ("No paired drinking-network microbiology and telemetry", "The biological and hydraulic chains cannot be validated together.", "Prospective or utility-provided linked event records."),
        ("Surface-water source domain", "Results do not establish drinking-water distribution performance.", "Local endpoint-compatible calibration and holdout."),
        ("High test-period prevalence", "F1 and PR-AUC appear stronger while specificity falls.", "Report class-balanced metrics and evaluate another period."),
        ("Sampling-program selection bias", "Purpose and material partially encode why the agency sampled.", "Sampling-design metadata, controlled prospective selection and inverse-probability sensitivity."),
        ("SDAIF ties strongest comparator", "Complex mathematics has not improved total positives over simpler ranking.", "Evaluate under shift, missingness, consequence differences and model failure."),
        ("Immediate result reveal", "Same-round adaptive decisions may be operationally impossible.", "Use static initial plans or measured delayed-result evaluation."),
        ("Poor unseen-site transfer", "A new city cannot safely use the source model without labels.", "Minimum-data rule, local calibration, uncertainty inflation and abstention."),
        ("Coordinate monitoring zones", "They can be mistaken for affected pipe regions.", "Keep distinct or replace with verified network connectivity."),
        ("Hydraulic test no longer pristine", "The validation week was inspected in an earlier baseline.", "Freeze a new time period or independent network before further tuning."),
        ("Random comparator uses one ordering", "Randomisation uncertainty is understated.", "Average many random permutations and report a distribution."),
    ], [1.75, 2.45, 2.65])
    heading(doc, "17.1 What the 85 percent audit established", 2)
    body(doc, "An explicit threshold-feasibility audit tested 1,001 thresholds on the already evaluated locked probabilities. No threshold made accuracy, balanced accuracy, F1, precision and sensitivity all reach 0.85. Even an invalid oracle threshold selected after seeing the test labels achieved F1 0.861 but balanced accuracy only 0.760. This proves that the present limitation cannot be solved by threshold manipulation; stronger independent predictive information or a different validated task is required.")

    heading(doc, "18 Xylem Value Scale and Development Path", 1)
    heading(doc, "18.1 Why the project fits Xylem", 2)
    add_bullets(doc, [
        "It addresses water-quality monitoring and the efficient use of limited testing capacity.",
        "It produces a concrete operational output rather than only a model score or awareness map.",
        "It uses authentic laboratory observations and discloses negative transfer results.",
        "It can begin as software and later accept utility telemetry or sentinel hardware through the same evidence interface.",
        "It offers a bounded pilot that can be evaluated against an authority's existing sampling order.",
    ])
    heading(doc, "18.2 Scale model", 2)
    body(doc, "The scalable product is a configurable decision engine rather than one universal E. coli model. A new authority supplies historical laboratory results, location metadata, sampling constraints and, where available, a network package. NADI trains locally, checks support, calibrates uncertainty and compares its frozen ranking prospectively against routine operations. A city that lacks network topology can still use the monitoring-priority mode; a utility with a calibrated network can add hydraulic consequence and source-tracing layers.")
    heading(doc, "18.3 Staged development plan", 2)
    add_table(doc, ["Stage", "Deliverable", "Evidence gate"], [
        ("1  Submission", "Authentic retrospective prioritisation, SDAIF mathematics, real-network hydraulic evidence and reproducibility package.", "Current locked results and audited claim boundary."),
        ("2  Prospective monitoring pilot", "Frozen rankings issued before laboratory outcomes, compared with routine order.", "Independent endpoint, timing and result records."),
        ("3  Utility network pilot", "Linked sampling sites, topology, supply operations, pressure and flow.", "Verified node mapping and hydraulic calibration."),
        ("4  Unified contamination events", "Node-specific biological evidence propagated through uncertain routes to actions.", "Paired microbiology, telemetry and network state."),
        ("5  Multi-city transfer", "City package, minimum-data rule and abstention under shift.", "Held-out cities and prospective external validation."),
    ], [1.45, 3.1, 2.3])
    heading(doc, "18.4 Partnership request", 2)
    body(doc, "The most valuable Xylem support would be access to a bounded monitoring programme, a water-quality mentor and a utility-compatible evaluation design. The first partnership does not require city-wide pipe data. It requires a prospective sampling list, independent laboratory outcomes, timestamps and a routine comparator. A later hydraulic pilot can use a pseudonymised connectivity graph and coarse operating states.")

    heading(doc, "19 Conclusion", 1)
    body(doc, "NADI demonstrates that water-quality intelligence should not stop at prediction. Its authentic experiment converts historical E. coli evidence into an auditable three-test decision and finds substantially more high results than routine-frequency and deterministic-random ordering. Its SDAIF layer makes uncertainty, regret and alternative models visible, while its real-network hydraulic study shows that sparse measurements can support accurate internal-state reconstruction.")
    body(doc, "The project is strongest when presented precisely. It is already a working testing-prioritisation and applied-mathematics prototype. It is not yet a fully validated contamination-to-pipeline-response system. The next scientific milestone is not a more impressive threshold or a larger dashboard. It is one prospective event-level dataset that links a frozen decision, independent microbiology, real timing and a verified monitoring or network context.")
    body(doc, "For Xylem, NADI offers a credible combination of environmental relevance, authentic evidence, transparent mathematics, reproducibility and a practical scale pathway. Its value is the decision it supports: where limited testing should begin when waiting or testing blindly may leave serious contamination undiscovered.")

    doc.add_page_break()
    heading(doc, "Appendix A Complete Performance Summary", 1)
    add_table(doc, ["Track", "Primary result", "Scientific boundary"], [
        ("Canonical authentic E. coli model", "F1 0.838; ROC-AUC 0.866; PR-AUC 0.916; sensitivity 0.966.", "UK surface-water source domain."),
        ("Authentic SDAIF", "114 positives in top three across 41 rounds; zero missed positive rounds.", "Retrospective replay; tied strongest model and Bayesian policies."),
        ("Unseen-site transfer", "F1 0.722; ROC-AUC 0.705; balanced accuracy 0.555.", "Supports abstention, not plug-and-play transfer."),
        ("BWFLnet internal pressure", "Median MAE 0.278 m; 66.3% improvement over mean baseline.", "Hydraulic state estimation only."),
        ("Net3 SDAIF", "Coverage@3 0.615, equal to adaptive Bayesian.", "Simulated tracer events."),
        ("L-TOWN transfer", "Coverage@3 0.257 versus 0.359 for stronger comparator.", "Negative simulated transfer result."),
        ("GECCO event model", "F1 0.483; ROC-AUC 0.937.", "Rare operational anomaly, not microbial truth."),
        ("Texas physical pipe runs", "ROC-AUC 0.826; F1 0.882; balanced accuracy 0.594.", "Leak evidence only; always-leak F1 is stronger."),
    ], [2.05, 2.35, 2.45])

    heading(doc, "Appendix B Key Definitions", 1)
    add_table(doc, ["Term", "Definition"], [
        ("Nowcast", "An estimate of current risk using information already available at the decision time."),
        ("Forecast", "An estimate for a defined future horizon using no information from after the forecast issue time."),
        ("Calibration", "Agreement between predicted probability and observed frequency."),
        ("F1", "Harmonic mean of precision and sensitivity for the positive class."),
        ("Balanced accuracy", "Mean of sensitivity and specificity, useful when class prevalence is uneven."),
        ("Regret", "Additional loss relative to the action that would have been best if the true state were known."),
        ("Worst-case regret", "Largest regret over the declared compatible uncertainty states."),
        ("Adversarial model", "The compatible model under which the selected plan performs worst."),
        ("Abstention", "A deliberate refusal to produce a confident recommendation when evidence support is inadequate."),
        ("Affected set", "Nodes receiving a declared tracer under a particular hydraulic scenario; not automatically biological contamination."),
        ("Transfer support", "Evidence that the target location resembles conditions represented during model development."),
    ], [1.7, 5.15])

    heading(doc, "Appendix C Jury Questions and Defensible Answers", 1)
    add_table(doc, ["Question", "Defensible answer"], [
        ("Does NADI detect E. coli?", "No. It estimates risk and prioritises confirmatory testing. Laboratory results remain the biological truth."),
        ("Why use mathematics instead of sorting probabilities?", "SDAIF exposes model disagreement, worst-case regret, an adversarial model and abstention. In the present authentic test it ties the strongest simple ranking, so assurance rather than superior yield is its demonstrated added value."),
        ("Is 114 versus 80 caused by high prevalence?", "High prevalence helps every policy. The fair comparison uses the same rounds and budget; expected random yield is about 82.6. The improvement over routine and random remains substantial, but the strongest model ties SDAIF."),
        ("Why is specificity low?", "The locked period has a major prevalence and sampling-program shift. NADI is therefore framed as a ranking tool, not an automatic contamination declaration."),
        ("Are the monitoring zones pipe routes?", "No. They are coordinate-based clusters explicitly labelled as monitoring zones."),
        ("What does BWFLnet prove?", "It proves that the hybrid physical and statistical method reconstructs internal pressure on a real network from sparse boundary observations. It does not prove E. coli transport."),
        ("Can Delhi use it tomorrow?", "No. Delhi would require endpoint-compatible local data, support testing and prospective validation. The framework can be configured, but local performance is unproven."),
        ("What is original?", "The student contribution is the executable evidence-to-action architecture, robust testing optimisation, evidence timing controls, provenance separation and comparative evaluation. Global theorem novelty is not claimed."),
        ("What is the next decisive experiment?", "Issue frozen rankings prospectively before laboratory outcomes and compare them with routine sampling under the same test budget."),
    ], [2.15, 4.7])

    heading(doc, "Appendix D Selected Technical Resources", 1)
    add_bullets(doc, [
        "UK Environment Agency Water Quality Data Archive and observation services, authentic E. coli source records.",
        "BWFLnet real operational water distribution network dataset, Mendeley Data DOI 10.17632/srt4vr5k38.3.",
        "United States Environmental Protection Agency EPANET 2.2, hydraulic and water-quality network simulation engine.",
        "Water Network Tool for Resilience, WNTR, Python tools for water-distribution modelling and uncertainty scenarios.",
        "Cognizant River Deep Mountain AI Open E. coli Models, prior-art data-processing and XGBoost architecture.",
        "Society for Science 2024 E. coli forecasting abstract, method-reconstruction reference using weather and historical observations.",
        "L-TOWN BattLeDIM benchmark, hydraulic operational and leak-event stress-testing resource.",
    ])
    body(doc, "Project artifacts include the claim matrix, mathematical assurance case, authentic experiment report, performance matrix, negative-results log, real-network validation report and reproducibility manifest. The final public bundle should be regenerated after all artifacts are frozen.")

    doc.core_properties.title = "NADI Framework Detailed Xylem Project Dossier"
    doc.core_properties.subject = "Water quality testing prioritisation and applied mathematics"
    doc.core_properties.author = "NADI Project Team"
    doc.core_properties.keywords = "NADI, Xylem, E. coli, water quality, SDAIF, applied mathematics, hydraulics"
    doc.save(OUT)
    print(OUT)


if __name__ == "__main__":
    build()
