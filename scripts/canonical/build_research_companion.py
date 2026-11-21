"""Build the artifact-driven NADI executable research companion notebook.

The generated notebook only reads frozen/canonical evidence and writes figures
and derived reporting artifacts to new, non-frozen locations.
"""
from __future__ import annotations

import json
from pathlib import Path
from textwrap import dedent


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "notebooks" / "NADI_executable_research_companion.ipynb"


def markdown(text: str) -> dict:
    return {"cell_type": "markdown", "metadata": {}, "source": dedent(text).strip() + "\n"}


def code(text: str) -> dict:
    # The first line begins directly after the triple quotes while the remaining
    # lines inherit this generator's indentation. `dedent` alone cannot remove
    # that asymmetry, so remove the shared generator prefix first.
    raw_lines = text.strip("\n").splitlines()
    indents = [len(line) - len(line.lstrip()) for line in raw_lines if line.strip() and line[:1].isspace()]
    has_zero_indented_content = any(line.strip() and not line[:1].isspace() for line in raw_lines)
    if has_zero_indented_content and indents:
        common = min(indents)
        raw_lines = [line[common:] if line.startswith(" " * common) else line for line in raw_lines]
    source = dedent("\n".join(raw_lines)).strip() + "\n"
    return {
        "cell_type": "code", "execution_count": None, "metadata": {},
        "outputs": [], "source": source,
    }


cells = [
    markdown("""
    # NADI executable research companion

    **Network-Adaptive Decision Intelligence for Water Safety (NADI)**<br>
    **Research question:** Can historical laboratory evidence, calibrated risk
    modelling, explicit model uncertainty, and SDAIF fixed-budget optimization
    improve prioritization of limited confirmatory water-quality testing compared
    with routine and simpler ranking policies?

    This is an executable, artifact-driven research companion. It regenerates
    figures and tables from saved canonical artifacts; it does not retrain models,
    alter frozen results, or convert simulated/hydraulic evidence into biological
    validation.

    **Primary supported claim:** NADI is an evidence-separated,
    uncertainty-aware decision-intelligence framework that estimates risk and
    prioritizes confirmatory testing under a limited budget.

    **Evidence boundary:** the primary result is retrospective UK Environment
    Agency mixed-environmental-water E. coli prioritization—not direct sensor
    detection, drinking-water pipe localization, Delhi/Ghaziabad validation, or
    illness reduction.
    """),
    markdown("## 1. Research identity and evidence-to-action architecture"),
    code("""
    from __future__ import annotations
    import csv, hashlib, json, platform, subprocess, sys
    from datetime import datetime, timezone
    from pathlib import Path

    import joblib
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd
    from matplotlib.lines import Line2D
    from sklearn.calibration import calibration_curve
    from sklearn.metrics import auc, precision_recall_curve, roc_curve

    def find_root() -> Path:
        candidates = [Path.cwd().resolve(), Path.cwd().resolve().parent]
        for candidate in candidates:
            if (candidate / "pyproject.toml").exists() and (candidate / "src" / "nadi").exists():
                return candidate
        raise RuntimeError("Run from repository root or notebooks/ directory.")

    ROOT = find_root()
    if str(ROOT / "src") not in sys.path:
        sys.path.insert(0, str(ROOT / "src"))
    from nadi.authentic.policy import update_model_weights
    from nadi.canonical_cli import _random_permutation_totals

    FIG_DIR = ROOT / "figures" / "nadi_research_companion"
    TABLE_DIR = ROOT / "reports" / "notebook_tables"
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    TABLE_DIR.mkdir(parents=True, exist_ok=True)

    plt.rcParams.update({"figure.dpi": 130, "savefig.dpi": 180, "font.size": 9,
                         "axes.titlesize": 11, "axes.labelsize": 9,
                         "legend.fontsize": 8, "axes.grid": True,
                         "grid.alpha": 0.22, "axes.spines.top": False,
                         "axes.spines.right": False})
    PALETTE = {"blue": "#2B6CB0", "red": "#C53030", "yellow": "#D69E2E",
               "green": "#2F855A", "purple": "#6B46C1", "grey": "#718096",
               "dark": "#1A202C"}
    EVIDENCE = {"LAB_CONFIRMED": "LAB_CONFIRMED", "OBSERVED": "OBSERVED",
                "MODEL_ESTIMATE": "MODEL_ESTIMATE", "SIMULATED": "SIMULATED",
                "RECONSTRUCTED": "RECONSTRUCTED", "ASSUMED": "ASSUMED",
                "HISTORICAL": "HISTORICAL", "CURRENT_CANONICAL": "CURRENT_CANONICAL"}
    FIGURES, TABLES, CHECKS = [], [], []

    def sha256(path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()

    def require(path: Path, expected: str | None = None) -> Path:
        assert path.exists(), f"Required artifact is missing: {path}"
        actual = sha256(path)
        if expected is not None:
            assert actual == expected, f"Hash mismatch for {path.name}"
        CHECKS.append({"artifact": str(path.relative_to(ROOT)), "sha256": actual, "passed": True})
        return path

    def tag(ax, evidence: str, dataset: str, split: str, run: str = "CURRENT_CANONICAL") -> None:
        ax.text(0.01, -0.20, f"Evidence: {evidence} | Dataset: {dataset} | Split: {split} | Run: {run}",
                transform=ax.transAxes, fontsize=7, color=PALETTE["dark"], va="top")

    def savefig(fig, number: int, slug: str, caption: str, evidence: str, dataset: str, split: str) -> Path:
        path = FIG_DIR / f"figure_{number:03d}_{slug}.png"
        fig.tight_layout()
        fig.savefig(path, bbox_inches="tight")
        plt.close(fig)
        FIGURES.append({"kind": "figure", "number": number, "name": slug, "path": str(path.relative_to(ROOT)),
                        "sha256": sha256(path), "evidence_status": evidence, "dataset": dataset,
                        "split": split, "caption": caption})
        return path

    def save_table(name: str, frame: pd.DataFrame, evidence: str, caption: str) -> Path:
        csv_path = TABLE_DIR / f"{name}.csv"
        md_path = TABLE_DIR / f"{name}.md"
        frame.to_csv(csv_path, index=False)
        md_path.write_text(frame.to_markdown(index=False) + "\\n", encoding="utf-8")
        TABLES.append({"kind": "table", "number": "", "name": name, "path": str(csv_path.relative_to(ROOT)),
                       "sha256": sha256(csv_path), "evidence_status": evidence, "dataset": "NADI artifacts",
                       "split": "artifact-derived", "caption": caption})
        return csv_path

    print(f"Repository root: {ROOT}")
    print("Notebook mode: read-only for frozen evidence; derived figures/tables only.")
    """),
    code("""
    # Figure 1: conceptual architecture, clearly marked as the current canonical workflow.
    stages = ["Historical laboratory\\nevidence", "Causal feature\\nconstruction", "Risk-model\\nfamily",
              "Probability\\ncalibration", "Model disagreement\\nand uncertainty", "SDAIF fixed-budget\\noptimization",
              "Ordered confirmatory\\ntesting list", "Sequential evidence\\nupdate", "Auditable\\ndecision card"]
    fig, ax = plt.subplots(figsize=(14, 3.2)); ax.axis("off")
    for i, stage in enumerate(stages):
        x = 0.02 + i * 0.108
        ax.text(x, 0.55, stage, ha="center", va="center", fontsize=8,
                bbox={"boxstyle": "round,pad=0.45", "facecolor": "#E6F0FA", "edgecolor": PALETTE["blue"]})
        if i < len(stages) - 1:
            ax.annotate("", xy=(x + 0.065, 0.55), xytext=(x + 0.044, 0.55),
                        arrowprops={"arrowstyle": "->", "color": PALETTE["dark"]})
    ax.set_title("Figure 1. NADI evidence-to-action architecture")
    tag(ax, "CURRENT_CANONICAL / ASSUMED", "NADI canonical workflow", "architecture")
    savefig(fig, 1, "evidence_to_action_architecture", "Canonical evidence-to-action workflow.",
            "CURRENT_CANONICAL / ASSUMED", "NADI workflow", "architecture")
    """),
    markdown("## 2. Project structure, evidence tracks, and dependencies"),
    code("""
    # Required artifact and hash verification happens before any display.
    AUTH_DIR = ROOT / "results" / "canonical" / "authentic" / "audit_20261120_07"
    DECISION_DIR = ROOT / "results" / "canonical" / "decision" / "audit_20261120_03"
    HYDRO_DIR = ROOT / "results" / "canonical" / "hydraulics" / "audit_20261120_01"
    SIM_DIR = ROOT / "results" / "canonical" / "simulation" / "audit_20261120_01"
    AUTH_MANIFEST = json.loads(require(AUTH_DIR / "run_manifest.json").read_text())
    for filename, digest in AUTH_MANIFEST["outputs_sha256"].items():
        require(AUTH_DIR / filename, digest)
    require(DECISION_DIR / "sdaif_evaluation.json")
    require(HYDRO_DIR / "hydraulic_evaluation.json")
    require(SIM_DIR / "net3_simulation_summary.json")
    assert AUTH_MANIFEST["evidence_class"] == "LAB_CONFIRMED"
    assert json.loads((SIM_DIR / "net3_simulation_summary.json").read_text())["evidence_class"] == "SIMULATED"
    assert (ROOT / "reports" / "prohibited_claims.md").exists()

    structure = ["src/", "scripts/", "configs/", "data/", "results/", "docs/", "tests/", "app/", "provenance/"]
    tracks = ["Authentic microbial\\nLAB_CONFIRMED", "BWFLnet hydraulic\\nOBSERVED + MODEL_ESTIMATE",
              "Net3/L-TOWN network\\nSIMULATED", "Transfer / telemetry\\nHISTORICAL", "Dashboard / reports\\nCURRENT_CANONICAL"]
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.2))
    axes[0].axis("off"); axes[0].set_title("Figure 2. Repository architecture")
    for i, item in enumerate(structure): axes[0].text(0.08 + (i % 3)*0.3, 0.82 - (i//3)*0.28, item, bbox={"boxstyle":"round", "facecolor":"#EDF2F7"})
    axes[1].axis("off"); axes[1].set_title("Figure 3. Evidence-track separation")
    colors=[PALETTE["blue"], PALETTE["green"], PALETTE["purple"], PALETTE["yellow"], PALETTE["grey"]]
    for i, (track, color) in enumerate(zip(tracks, colors)):
        axes[1].text(0.5, 0.88-i*0.18, track, ha="center", va="center", bbox={"boxstyle":"round,pad=.35", "facecolor":color+"33", "edgecolor":color})
    axes[2].axis("off"); axes[2].set_title("Figure 4. Artifact dependency graph")
    chain=["source data", "preprocess", "model", "calibration", "policy", "evaluation", "report", "notebook"]
    for i, item in enumerate(chain):
        axes[2].text(0.5, 0.94-i*0.115, item, ha="center", va="center", bbox={"boxstyle":"round", "facecolor":"#E6FFFA"})
        if i < len(chain)-1: axes[2].annotate("", (0.5,0.84-i*.115), (0.5,0.875-i*.115), arrowprops={"arrowstyle":"->"})
    for ax in axes: tag(ax, "CURRENT_CANONICAL", "NADI repository", "structure and lineage")
    savefig(fig, 2, "repository_evidence_dependency", "Repository architecture, separated evidence tracks, and artifact dependency graph.", "CURRENT_CANONICAL", "NADI repository", "structure")
    """),
    markdown("## 3. Provenance, integrity, and reproducibility"),
    code("""
    provenance_rows = []
    for label, path, evidence, command, frozen in [
        ("Authentic EA evaluation", AUTH_DIR / "run_manifest.json", "LAB_CONFIRMED / CURRENT_CANONICAL", "nadi evaluate-authentic", True),
        ("SDAIF decision audit", DECISION_DIR / "run_manifest.json", "LAB_CONFIRMED / CURRENT_CANONICAL", "nadi evaluate-sdaif", False),
        ("BWFLnet pressure evaluation", HYDRO_DIR / "run_manifest.json", "OBSERVED + MODEL_ESTIMATE", "nadi evaluate-hydraulics", True),
        ("Net3 benchmark", SIM_DIR / "run_manifest.json", "SIMULATED", "nadi run-simulation", True),
    ]:
        provenance_rows.append({"Artifact": label, "Evidence status": evidence, "SHA-256": sha256(path), "Generation command": command, "Frozen": frozen})
    provenance = pd.DataFrame(provenance_rows)
    display(provenance)
    save_table("provenance_table", provenance, "CURRENT_CANONICAL", "Canonical artifact provenance and integrity table.")
    fig, ax = plt.subplots(figsize=(12, 2.8)); ax.axis("off")
    chain=["Dataset hash", "Manifest hash", "Config hash", "Code commit", "Run manifest", "Result hash", "Figure/table hash"]
    for i, item in enumerate(chain):
        x=.05+i*.15; ax.text(x,.55,item,ha="center",va="center",fontsize=8,bbox={"boxstyle":"round","facecolor":"#F7FAFC"})
        if i<len(chain)-1: ax.annotate("",(x+.07,.55),(x+.11,.55),arrowprops={"arrowstyle":"->"})
    ax.set_title("Figure 5. Reproducibility chain"); tag(ax,"CURRENT_CANONICAL","Hash-pinned artifacts","canonical runs")
    savefig(fig,5,"reproducibility_chain","Hash and manifest chain used to reproduce notebook evidence.","CURRENT_CANONICAL","NADI artifacts","canonical runs")
    """),
    markdown("## 4. Limited-budget decision problem and SDAIF formulation"),
    code("""
    decision_math = pd.DataFrame([
        ["Candidate set", r"V = {1, …, n}", "Locations eligible for a confirmatory test"],
        ["Plan", r"A ⊆ V", "Ordered testing plan"], ["Budget", r"|A| ≤ k", "Maximum available tests"],
        ["Risk", r"p_mi", "Model m probability for candidate i"],
        ["Loss", r"L_m(A)", "Model-specific missed-risk / test loss"],
        ["Regret", r"R_m(A)=L_m(A)-min_B L_m(B)", "Loss relative to model-m optimal plan"],
        ["SDAIF objective", r"min_A max_m R_m(A)", "Conservative fixed-budget decision"],
    ], columns=["Concept", "Notation", "Operational meaning"])
    display(decision_math); save_table("sdaif_formulation", decision_math, "CURRENT_CANONICAL / ASSUMED", "Decision formulation used by SDAIF.")
    fig, axes = plt.subplots(1, 3, figsize=(14, 3.6))
    xs=np.arange(12); risk=np.array([.11,.72,.36,.88,.49,.18,.55,.62,.29,.93,.42,.68])
    axes[0].scatter(xs,risk,c=np.where(np.argsort(-risk)<3,PALETTE["red"],PALETTE["blue"]),s=75)
    axes[0].axhline(.5,color=PALETTE["grey"],ls="--"); axes[0].set(title="Figure 6. Limited test budget",xlabel="candidate site",ylabel="estimated risk")
    axes[1].axis("off"); axes[1].set_title("Figure 7. Prediction-to-action")
    for i,t in enumerate(["risk prediction", "uncertainty", "regret", "testing priority", "confirmatory test"]):
        axes[1].text(.5,.88-i*.18,t,ha="center",bbox={"boxstyle":"round","facecolor":"#EBF8FF"})
        if i<4: axes[1].annotate("",(.5,.80-i*.18),(.5,.84-i*.18),arrowprops={"arrowstyle":"->"})
    axes[2].axis("off"); axes[2].set_title("Figure 8. Decision timing")
    for i,t in enumerate(["historical evidence", "decision issued", "site selected", "lab result revealed", "posterior update"]):
        axes[2].text(.03+i*.2,.55,t,ha="center",fontsize=8,bbox={"boxstyle":"round","facecolor":"#F0FFF4"})
        if i<4: axes[2].annotate("",(.13+i*.2,.55),(.18+i*.2,.55),arrowprops={"arrowstyle":"->"})
    for ax in axes: tag(ax,"CURRENT_CANONICAL / ASSUMED","NADI decision formulation","fixed budget")
    savefig(fig,6,"limited_budget_decision_problem","Testing-budget, prediction-to-action, and timing diagrams.","CURRENT_CANONICAL / ASSUMED","NADI decision model","fixed budget")
    """),
    markdown("## 5. Authentic Environment Agency microbial dataset"),
    code("""
    DATA_PATH = ROOT / "data_processed" / "ea_authentic_site_rounds_2024.csv"
    assert sha256(DATA_PATH) == AUTH_MANIFEST["input_sha256"], "Processed EA input hash differs from canonical run"
    ea = pd.read_csv(DATA_PATH, parse_dates=["round_date", "collection_time", "feature_cutoff"])
    partitions = pd.cut(ea["round_date"], bins=pd.to_datetime(["2024-01-01","2024-06-01","2024-07-16","2024-10-01","2025-01-01"]), right=False, labels=["Training","Calibration","Validation","Locked test"])
    ea["partition"] = partitions.astype(str)
    dataset_summary = pd.DataFrame({"metric":["observations","sites","sampling dates","positive prevalence","duplicate site-days"],
        "value":[len(ea),ea['samplingPoint.notation'].nunique(),ea['round_date'].nunique(),ea['high_500'].mean(),ea.duplicated(['round_date','samplingPoint.notation']).sum()]})
    display(dataset_summary); save_table("authentic_dataset_summary",dataset_summary,"LAB_CONFIRMED","EA site-day dataset scope and declared endpoint.")
    assert ea.duplicated(["round_date","samplingPoint.notation"]).sum()==0
    assert (ea["feature_cutoff"] < ea["round_date"]).all()
    """),
    code("""
    fig, axes = plt.subplots(2, 4, figsize=(16, 8))
    monthly=ea.groupby([pd.Grouper(key="round_date",freq="14D"),"partition"]).size().unstack(fill_value=0)
    monthly.plot.area(ax=axes[0,0],color=[PALETTE["blue"],PALETTE["yellow"],PALETTE["purple"],PALETTE["red"]]); axes[0,0].set(title="Figure 9. Authentic timeline",ylabel="site-day records")
    # Rounded coordinate scatter maps are not base maps and do not expose site labels.
    coords=ea.dropna(subset=["easting","northing"]).copy(); coords["x_round"]=(coords.easting/5000).round()*5; coords["y_round"]=(coords.northing/5000).round()*5
    axes[0,1].scatter(coords.x_round,coords.y_round,c=coords.high_500.map({0:PALETTE["blue"],1:PALETTE["red"]}),s=5,alpha=.35); axes[0,1].set(title="Figure 10. Rounded monitoring coordinates",xlabel="easting (km, rounded)",ylabel="northing (km, rounded)")
    density=coords.groupby(["x_round","y_round"]).size().reset_index(name="n"); axes[0,2].scatter(density.x_round,density.y_round,s=np.sqrt(density.n)*5,c=density.n,cmap="viridis",alpha=.7); axes[0,2].set(title="Figure 11. Sampling density",xlabel="easting (km, rounded)",ylabel="northing (km, rounded)")
    weekly=ea.set_index("round_date").high_500.resample("14D").agg(["mean","count"]); se=np.sqrt(weekly['mean']*(1-weekly['mean'])/weekly['count']); axes[0,3].plot(weekly.index,weekly['mean'],color=PALETTE["red"]); axes[0,3].fill_between(weekly.index,np.maximum(0,weekly['mean']-1.96*se),np.minimum(1,weekly['mean']+1.96*se),color=PALETTE["red"],alpha=.2); axes[0,3].set(title="Figure 12. Declared endpoint prevalence",ylabel="proportion high_500")
    prev=ea.groupby(['partition','region']).high_500.mean().unstack(0).head(10); prev.plot.bar(ax=axes[1,0]); axes[1,0].set(title="Figure 13. Prevalence by region",ylabel="proportion")
    ea.sampling_purpose.value_counts().head(8).sort_values().plot.barh(ax=axes[1,1],color=PALETTE["blue"]); axes[1,1].set(title="Figure 14. Sampling purpose",xlabel="records")
    material=ea.groupby('material').agg(records=('high_500','size'),prevalence=('high_500','mean')).sort_values('records',ascending=False).head(8); material['prevalence'].sort_values().plot.barh(ax=axes[1,2],color=PALETTE["green"]); axes[1,2].set(title="Figure 15. Material prevalence",xlabel="proportion")
    feature_groups=['site_prior_samples','site_prior_positive_rate','site_prior_mean_log_count','site_last_positive','days_since_site_sample','easting','northing']; miss=ea[feature_groups].isna().groupby(ea.partition).mean().T; axes[1,3].imshow(miss,aspect='auto',cmap='magma'); axes[1,3].set(title="Figure 16. Missingness heatmap",yticks=range(len(miss.index)),yticklabels=miss.index,xticks=range(len(miss.columns)),xticklabels=miss.columns)
    for ax in axes.ravel(): tag(ax,"LAB_CONFIRMED / CURRENT_CANONICAL","UK EA mixed environmental water","2024 chronological partitions","audit_20261120_07")
    savefig(fig,9,"authentic_dataset_overview","Timeline, rounded coordinate views, prevalence, sampling-program composition, and missingness.","LAB_CONFIRMED / CURRENT_CANONICAL","UK EA mixed environmental water","2024")
    """),
    markdown("## 6. Causal feature construction and leakage prevention"),
    code("""
    feature_names=['site_prior_samples','site_prior_positive_rate','site_prior_mean_log_count','site_last_positive','days_since_site_sample','region_prior_samples','region_prior_positive_rate','global_prior_samples','global_prior_positive_rate','easting','northing','region','material','sampling_purpose','day_sin','day_cos','month']
    feature_table=pd.DataFrame({"feature":feature_names,"available_before_decision":[True]*len(feature_names),"evidence":"OBSERVED / derived from prior records"})
    save_table("causal_feature_inventory",feature_table,"OBSERVED","Decision-time feature inventory.")
    example=ea.groupby('samplingPoint.notation').size().sort_values(ascending=False).index[0]
    history=ea[ea['samplingPoint.notation']==example].sort_values('round_date').copy(); history['site_alias']='SITE_'+hashlib.sha256(example.encode()).hexdigest()[:6].upper()
    fig,axes=plt.subplots(1,4,figsize=(16,3.6))
    axes[0].plot(history.round_date,history.site_prior_samples,marker='o',color=PALETTE['blue']); axes[0].set(title="Figure 17. Historical-window example",ylabel="prior samples",xlabel="date")
    axes[1].axis('off'); axes[1].set_title("Figure 18. Causal feature timeline"); axes[1].text(.5,.62,"past results → feature cutoff → current prediction\\n(current label unavailable)",ha='center',va='center',bbox={"boxstyle":"round","facecolor":"#EBF8FF"})
    axes[2].axis('off'); axes[2].set_title("Figure 19. Leakage prevention"); axes[2].text(.5,.62,"same-date outcomes are aggregated\\nafter every site-day feature is frozen",ha='center',va='center',bbox={"boxstyle":"round","facecolor":"#F0FFF4"})
    avail=pd.DataFrame(1,index=['past site','past region','global history','coordinates','material','season'],columns=['Training','Calibration','Validation','Locked test']); axes[3].imshow(avail,cmap='Blues',vmin=0,vmax=1); axes[3].set(title="Figure 20. Feature availability",yticks=range(6),yticklabels=avail.index,xticks=range(4),xticklabels=avail.columns)
    for ax in axes: tag(ax,"OBSERVED / CURRENT_CANONICAL","UK EA historical records","causal feature construction")
    savefig(fig,17,"causal_feature_construction","Causal feature timeline, leakage controls, and feature availability.","OBSERVED / CURRENT_CANONICAL","UK EA mixed environmental water","pre-decision history")
    """),
    markdown("## 7. Risk-model family and locked performance"),
    code("""
    auth_report=json.loads((AUTH_DIR/'authentic_experiment_report.json').read_text())
    model_metrics=[]
    for name, payload in auth_report['model_reports'].items():
        metrics=payload['locked_test'].copy(); metrics['model']=name; model_metrics.append(metrics)
    model_metrics=pd.DataFrame(model_metrics).set_index('model')
    display(model_metrics[['f1','roc_auc','pr_auc','sensitivity','specificity','balanced_accuracy','brier','ece_10']])
    save_table('locked_model_family_metrics',model_metrics.reset_index(),'LAB_CONFIRMED / MODEL_ESTIMATE','Locked model-family performance from frozen authentic evaluation.')
    locked=ea[ea.partition=='Locked test'].merge(pd.read_csv(AUTH_DIR/'authentic_locked_site_predictions_and_zones.csv')[['round_id','samplingPoint.notation','predicted_probability','high_500','probability_logistic','probability_xgboost','probability_hist_gradient']],on=['round_id','samplingPoint.notation','high_500'],how='inner')
    assert len(locked)==545
    fig,axes=plt.subplots(2,3,figsize=(15,8))
    model_metrics[['f1','roc_auc','pr_auc','sensitivity','specificity','balanced_accuracy']].plot.bar(ax=axes[0,0]); axes[0,0].set(title='Figure 21. Model-family locked metrics',ylabel='score'); axes[0,0].tick_params(axis='x',rotation=0)
    for col,color in [('probability_logistic',PALETTE['blue']),('probability_xgboost',PALETTE['red']),('probability_hist_gradient',PALETTE['green'])]:
        fpr,tpr,_=roc_curve(locked.high_500,locked[col]); axes[0,1].plot(fpr,tpr,label=col.replace('probability_',''),color=color)
        precision,recall,_=precision_recall_curve(locked.high_500,locked[col]); axes[0,2].plot(recall,precision,label=col.replace('probability_',''),color=color)
    axes[0,1].plot([0,1],[0,1],'--',color=PALETTE['grey']); axes[0,1].legend(); axes[0,1].set(title='Figure 22. Locked ROC curves',xlabel='false-positive rate',ylabel='true-positive rate')
    axes[0,2].legend(); axes[0,2].set(title='Figure 23. Locked precision-recall curves',xlabel='recall',ylabel='precision')
    for col,color in [('probability_logistic',PALETTE['blue']),('probability_xgboost',PALETTE['red']),('probability_hist_gradient',PALETTE['green'])]:
        obs,pred=calibration_curve(locked.high_500,locked[col],n_bins=10,strategy='quantile'); axes[1,0].plot(pred,obs,marker='o',label=col.replace('probability_',''),color=color)
    axes[1,0].plot([0,1],[0,1],'--',color=PALETTE['grey']); axes[1,0].legend(); axes[1,0].set(title='Figure 24. Locked calibration curves',xlabel='mean predicted probability',ylabel='observed frequency')
    cm_raw=auth_report['model_reports'][auth_report['best_model_selected_on_validation']]['locked_test']['confusion_matrix']; cm=np.array([[cm_raw['tn'],cm_raw['fp']],[cm_raw['fn'],cm_raw['tp']]]); axes[1,1].imshow(cm,cmap='Blues'); axes[1,1].set(title='Figure 25. Locked confusion matrix',xticks=[0,1],yticks=[0,1],xticklabels=['pred low','pred high'],yticklabels=['observed low','observed high']); [axes[1,1].text(j,i,str(cm[i,j]),ha='center',va='center') for i in range(2) for j in range(2)]
    threshold=auth_report['model_reports'][auth_report['best_model_selected_on_validation']]['locked_test']['threshold']; grid=np.linspace(.05,.95,60); rows=[]
    for t in grid:
        y=(locked.predicted_probability>=t).astype(int); tp=((y==1)&(locked.high_500==1)).sum(); fp=((y==1)&(locked.high_500==0)).sum(); fn=((y==0)&(locked.high_500==1)).sum(); tn=((y==0)&(locked.high_500==0)).sum();
        rows.append((t,tp/(tp+fn) if tp+fn else np.nan,tn/(tn+fp) if tn+fp else np.nan,2*tp/(2*tp+fp+fn) if 2*tp+fp+fn else np.nan))
    curve=pd.DataFrame(rows,columns=['threshold','sensitivity','specificity','f1']); curve.set_index('threshold').plot(ax=axes[1,2],color=[PALETTE['red'],PALETTE['blue'],PALETTE['green']]); axes[1,2].axvline(threshold,color=PALETTE['dark'],ls='--',label='preselected threshold'); axes[1,2].legend(); axes[1,2].set(title='Figure 26. Threshold trade-off')
    for ax in axes.ravel(): tag(ax,'LAB_CONFIRMED + MODEL_ESTIMATE','UK EA mixed environmental water','locked Oct–Dec 2024','audit_20261120_07')
    savefig(fig,21,'locked_risk_model_evaluation','Locked model metrics, discrimination, calibration, confusion matrix, and threshold trade-off.','LAB_CONFIRMED + MODEL_ESTIMATE','UK EA mixed environmental water','locked Oct–Dec 2024')
    """),
    markdown("## 8. Calibration, uncertainty, and abstention"),
    code("""
    weights=auth_report['model_uncertainty_weights_from_validation_log_loss']; weight_series=pd.Series(weights).sort_values(ascending=False)
    locked['model_std']=locked[['probability_logistic','probability_xgboost','probability_hist_gradient']].std(axis=1)
    fig,axes=plt.subplots(2,3,figsize=(15,8))
    axes[0,0].hist(locked.predicted_probability,bins=25,color=PALETTE['blue'],alpha=.75); axes[0,0].set(title='Figure 27. Calibrated probability distribution',xlabel='calibrated probability')
    axes[0,1].bar(weight_series.index,weight_series.values,color=[PALETTE['red'],PALETTE['green'],PALETTE['blue']]); axes[0,1].set(title='Figure 28. Validation log-loss weights',ylabel='weight'); axes[0,1].tick_params(axis='x',rotation=20)
    axes[0,2].hist(locked.model_std,bins=25,color=PALETTE['purple']); axes[0,2].set(title='Figure 29. Model disagreement distribution',xlabel='standard deviation across models')
    axes[1,0].scatter(locked.predicted_probability,locked.model_std,c=locked.high_500.map({0:PALETTE['blue'],1:PALETTE['red']}),s=10,alpha=.55); axes[1,0].set(title='Figure 30. Risk versus disagreement',xlabel='risk probability',ylabel='model disagreement')
    axes[1,1].axis('off'); axes[1,1].set_title('Figure 31. Adversarial-model explanation'); axes[1,1].text(.5,.55,'SDAIF evaluates candidate plans\\nunder each calibrated model vertex\\nand limits worst-case regret.',ha='center',va='center',bbox={"boxstyle":"round","facecolor":"#FFF5F5"})
    axes[1,2].axis('off'); axes[1,2].set_title('Figure 32. Abstention flow'); axes[1,2].text(.5,.55,'weak transfer support\\nor unresolved model disagreement\\n→ abstain / request confirmation',ha='center',va='center',bbox={"boxstyle":"round","facecolor":"#E2E8F0"})
    for ax in axes.ravel(): tag(ax,'MODEL_ESTIMATE / CURRENT_CANONICAL','UK EA locked predictions','locked Oct–Dec 2024')
    savefig(fig,27,'calibration_uncertainty_abstention','Probability distribution, validation weights, disagreement and abstention logic.','MODEL_ESTIMATE / CURRENT_CANONICAL','UK EA mixed environmental water','locked Oct–Dec 2024')
    """),
    markdown("## 9. Risk maps and detection-style evaluation (estimated risk, not direct detection)"),
    code("""
    # Coordinate views use rounded public monitoring coordinates; no base map or direct-detection claim.
    map_df=locked.dropna(subset=['easting','northing']).copy(); map_df['x_round']=(map_df.easting/5000).round()*5; map_df['y_round']=(map_df.northing/5000).round()*5
    sdaif_events=pd.read_csv(AUTH_DIR/'authentic_test_events.csv'); example_round=sdaif_events[sdaif_events.policy=='adaptive_sdaif'].iloc[0].round_id; selected=set(sdaif_events[(sdaif_events.policy=='adaptive_sdaif')&(sdaif_events.round_id==example_round)].iloc[0].selected_sites.split('|'))
    round_map=map_df[map_df.round_id==example_round].copy(); round_map['selected']=round_map['samplingPoint.notation'].isin(selected)
    fig,axes=plt.subplots(2,4,figsize=(16,8))
    sc=axes[0,0].scatter(map_df.x_round,map_df.y_round,c=map_df.predicted_probability,cmap='YlOrRd',s=10,alpha=.65); fig.colorbar(sc,ax=axes[0,0],label='estimated risk'); axes[0,0].set(title='Figure 33. Geographic risk-probability view',xlabel='easting km rounded',ylabel='northing km rounded')
    axes[0,1].scatter(round_map.x_round,round_map.y_round,c=round_map.predicted_probability,cmap='YlOrRd',s=55); axes[0,1].scatter(round_map.loc[round_map.selected,'x_round'],round_map.loc[round_map.selected,'y_round'],facecolors='none',edgecolors='black',s=150,linewidths=1.5); axes[0,1].set(title='Figure 34. Selected testing sites (one round)')
    axes[0,2].scatter(map_df.x_round,map_df.y_round,c=map_df.high_500.map({0:PALETTE['blue'],1:PALETTE['red']}),s=10,alpha=.6); axes[0,2].set(title='Figure 35. Observed laboratory endpoint')
    axes[0,3].scatter(map_df.x_round,map_df.y_round,c=map_df.model_std,cmap='viridis',s=10,alpha=.65); axes[0,3].set(title='Figure 36. Model disagreement')
    bins=np.linspace(0,1,11); map_df['risk_bin']=pd.cut(map_df.predicted_probability,bins,include_lowest=True); rank=map_df.groupby('risk_bin',observed=True).high_500.mean(); axes[1,0].plot(np.arange(len(rank)),rank.values,marker='o',color=PALETTE['red']); axes[1,0].set(title='Figure 37. Risk-ranking calibration',xlabel='risk-probability bin',ylabel='observed high fraction')
    y=map_df.high_500.to_numpy(); order=np.argsort(-map_df.predicted_probability.to_numpy()); captured=np.cumsum(y[order])/y.sum(); axes[1,1].plot(np.arange(1,len(captured)+1),captured,color=PALETTE['green']); axes[1,1].set(title='Figure 38. Top-k confirmed-result capture',xlabel='ranked tests',ylabel='fraction captured')
    pred=(map_df.predicted_probability>=threshold).astype(int); category=np.select([(pred==1)&(map_df.high_500==1),(pred==1)&(map_df.high_500==0),(pred==0)&(map_df.high_500==1)],['TP selected-risk','false alarm','missed high'],default='TN'); color_map={'TP selected-risk':PALETTE['green'],'false alarm':PALETTE['yellow'],'missed high':PALETTE['red'],'TN':PALETTE['grey']}; axes[1,2].scatter(map_df.x_round,map_df.y_round,c=[color_map[v] for v in category],s=10,alpha=.65); axes[1,2].set(title='Figure 39. Site-level error view')
    policy_events=sdaif_events.copy(); policy_events['rank_1_positive']=policy_events.selected_outcomes.str.split('|').str[0].astype(int); policy_events.groupby('policy').positives_found.mean().sort_values().plot.barh(ax=axes[1,3],color=PALETTE['blue']); axes[1,3].set(title='Figure 40. Mean positives found',xlabel='mean within budget')
    for ax in axes.ravel(): tag(ax,'LAB_CONFIRMED + MODEL_ESTIMATE','UK EA mixed environmental water','locked sites / retrospective maps','audit_20261120_07')
    savefig(fig,33,'risk_priority_detection_style_views','Estimated risk, selection, observed endpoint, disagreement, capture and error views.','LAB_CONFIRMED + MODEL_ESTIMATE','UK EA mixed environmental water','locked retrospective evaluation')
    """),
    markdown("## 10. SDAIF policy comparison, random uncertainty, and sequential demonstration"),
    code("""
    decision=json.loads((DECISION_DIR/'sdaif_evaluation.json').read_text())
    policy_summary=pd.read_csv(AUTH_DIR/'authentic_test_summary.csv').set_index('policy')
    random_dist=decision['random_permutation_distribution']
    raw_predictions=pd.read_csv(AUTH_DIR/'authentic_locked_site_predictions_and_zones.csv')
    random_totals=_random_permutation_totals(raw_predictions, sorted(sdaif_events.round_id.unique()), 3, 2000, 2026)
    fig,axes=plt.subplots(2,3,figsize=(15,8))
    policy_summary.total_positives_found.sort_values().plot.barh(ax=axes[0,0],color=PALETTE['blue']); axes[0,0].axvline(114,color=PALETTE['red'],ls='--'); axes[0,0].set(title='Figure 41. Policy totals',xlabel='confirmed high results found')
    policy_summary.mean_tests_to_first_positive_positive_rounds.sort_values().plot.barh(ax=axes[0,1],color=PALETTE['green']); axes[0,1].set(title='Figure 42. Tests to first positive')
    policy_summary.missed_positive_round_rate.sort_values().plot.barh(ax=axes[0,2],color=PALETTE['red']); axes[0,2].set(title='Figure 43. Missed-positive-round rate')
    policy_summary.mean_positive_discovery_regret.sort_values().plot.barh(ax=axes[1,0],color=PALETTE['purple']); axes[1,0].set(title='Figure 44. Positive-discovery regret')
    axes[1,1].hist(random_totals,bins=np.arange(random_totals.min(),random_totals.max()+2)-.5,color=PALETTE['grey'],alpha=.75); axes[1,1].axvline(114,color=PALETTE['red'],lw=2,label='SDAIF / tied strongest policies'); axes[1,1].legend(); axes[1,1].set(title='Figure 45. Random-permutation uncertainty',xlabel='total high results found')
    chosen=sdaif_events[(sdaif_events.policy=='adaptive_sdaif')].iloc[0]; round_data=raw_predictions[raw_predictions.round_id==chosen.round_id].copy(); models=['probability_logistic','probability_xgboost','probability_hist_gradient']; truth=dict(zip(round_data['samplingPoint.notation'].astype(str),round_data.high_500.astype(bool))); predictions={m.replace('probability_',''):dict(zip(round_data['samplingPoint.notation'].astype(str),round_data[m])) for m in models}; initial={k:weights[k] for k in predictions}; selected=chosen.selected_sites.split('|'); evolution=[initial]
    observed={}
    for site in selected[:-1]: observed[site]=truth[site]; updated,_=update_model_weights(predictions,initial,observed); evolution.append(updated)
    pd.DataFrame(evolution,index=['initial']+[f'after test {i+1}' for i in range(len(evolution)-1)]).plot.bar(ax=axes[1,2]); axes[1,2].set(title='Figure 46. Sequential posterior weights',ylabel='weight'); axes[1,2].tick_params(axis='x',rotation=0)
    for ax in axes.ravel(): tag(ax,'LAB_CONFIRMED + MODEL_ESTIMATE','UK EA site rounds','41 rounds, budget 3','audit_20261120_03')
    savefig(fig,41,'sdaif_policy_and_sequential_analysis','Policy outcomes, random-permutation uncertainty, regret and sequential weight update.','LAB_CONFIRMED + MODEL_ESTIMATE','UK EA site rounds','41 rounds / budget 3')
    """),
    markdown("## 11. Transfer and robustness"),
    code("""
    transfer=json.loads((ROOT/'results/ea_ecoli_physchem_geographic_holdout_v1.json').read_text())['models']['xgb_prior_art_reproduction']
    in_domain=auth_report['model_reports'][auth_report['best_model_selected_on_validation']]['locked_test']
    fig,axes=plt.subplots(1,3,figsize=(15,3.8))
    pd.DataFrame({'in-domain':[in_domain['f1'],in_domain['roc_auc']],'unseen-site':[transfer['f1'],transfer['roc_auc']]},index=['F1','ROC-AUC']).plot.bar(ax=axes[0],color=[PALETTE['blue'],PALETTE['yellow']]); axes[0].set(title='Figure 47. In-domain vs unseen-site transfer',ylabel='score'); axes[0].tick_params(axis='x',rotation=0)
    axes[1].hist(locked.model_std,bins=25,color=PALETTE['purple']); axes[1].axvline(locked.model_std.quantile(.9),color=PALETTE['yellow'],ls='--'); axes[1].set(title='Figure 48. Weak-support proxy',xlabel='model disagreement')
    axes[2].axis('off'); axes[2].set_title('Figure 49. Abstention under weak support'); axes[2].text(.5,.55,'Transfer weakness or high disagreement\\n→ do not generalize automatically\\n→ request local confirmation',ha='center',va='center',bbox={"boxstyle":"round","facecolor":"#E2E8F0"})
    for ax in axes: tag(ax,'LAB_CONFIRMED / HISTORICAL','EA transfer stress test','site holdout')
    savefig(fig,47,'transfer_and_abstention','In-domain versus site-held-out performance and abstention rationale.','LAB_CONFIRMED / HISTORICAL','EA transfer stress test','site holdout')
    """),
    markdown("## 12. Separate BWFLnet real-network hydraulic validation"),
    code("""
    hydro_path=ROOT/'results/bwflnet_full_hybrid/heldout_predictions.csv'; logger_path=ROOT/'results/bwflnet_full_hybrid/per_logger_metrics.csv'
    hydro=pd.read_csv(hydro_path); logger=pd.read_csv(logger_path)
    assert {'observed_pressure_m','hybrid_pressure_m','physics_pressure_m'}.issubset(hydro.columns)
    fig,axes=plt.subplots(1,3,figsize=(15,4))
    sample=hydro.sample(min(2500,len(hydro)),random_state=2026); axes[0].scatter(sample.observed_pressure_m,sample.hybrid_pressure_m,s=5,alpha=.35,color=PALETTE['blue']); lo=min(sample.observed_pressure_m.min(),sample.hybrid_pressure_m.min()); hi=max(sample.observed_pressure_m.max(),sample.hybrid_pressure_m.max()); axes[0].plot([lo,hi],[lo,hi],'--',color=PALETTE['grey']); axes[0].set(title='Figure 50. Observed vs hybrid pressure',xlabel='observed pressure (m)',ylabel='hybrid prediction (m)')
    logger.dropna(subset=['hybrid_state_estimator_mae']).sort_values('hybrid_state_estimator_mae').head(20).plot.bar(x='logger',y='hybrid_state_estimator_mae',ax=axes[1],legend=False,color=PALETTE['green']); axes[1].set(title='Figure 51. Per-logger MAE',ylabel='MAE (m)'); axes[1].tick_params(axis='x',rotation=70)
    residual=hydro.hybrid_pressure_m-hydro.observed_pressure_m; axes[2].hist(residual,bins=40,color=PALETTE['purple']); axes[2].axvline(0,color=PALETTE['dark']); axes[2].set(title='Figure 52. Pressure residual distribution',xlabel='prediction error (m)')
    for ax in axes: tag(ax,'OBSERVED + MODEL_ESTIMATE / CURRENT_CANONICAL','BWFLnet measured pressure','stored held-out predictions','audit_20261120_01')
    savefig(fig,50,'bwflnet_hydraulic_validation','Separate real-network pressure reconstruction evidence. Hydraulic state estimation only; not biological contamination localization.','OBSERVED + MODEL_ESTIMATE / CURRENT_CANONICAL','BWFLnet','stored held-out predictions')
    """),
    markdown("## 13. Separate simulated network and source-tracing track"),
    code("""
    sim=json.loads((SIM_DIR/'net3_simulation_summary.json').read_text())
    ltown=json.loads((ROOT/'results/ltown_decision_stress_v1.json').read_text())
    fig,axes=plt.subplots(1,3,figsize=(15,3.8))
    axes[0].axis('off'); axes[0].set_title('Figure 53. Simulated source-tracing workflow'); axes[0].text(.5,.55,'assumed source → tracer propagation\\n→ affected node set → placement policy\\n→ Coverage@k',ha='center',va='center',bbox={"boxstyle":"round","facecolor":"#FAF5FF"})
    net_vals=[sim['adaptive_mean'],sim['strongest_baseline_mean']]; axes[1].bar(['SDAIF','adaptive Bayesian'],net_vals,color=[PALETTE['purple'],PALETTE['blue']]); axes[1].set_ylim(0,1); axes[1].set(title='Figure 54. Net3 Coverage@3',ylabel='coverage')
    lt=ltown['mean_coverage_nonempty']; axes[2].bar(['SDAIF','adaptive Bayesian'],[lt['adaptive_sdaif'],lt['adaptive_bayesian']],color=[PALETTE['purple'],PALETTE['blue']]); axes[2].set_ylim(0,1); axes[2].set(title='Figure 55. L-TOWN transfer stress',ylabel='coverage')
    for ax in axes: tag(ax,'SIMULATED / CURRENT_CANONICAL','Net3 and L-TOWN','conditional scenarios')
    savefig(fig,53,'simulated_network_stress_tests','Simulated source-tracing workflow and Net3/L-TOWN Coverage@3 comparison.','SIMULATED / CURRENT_CANONICAL','Net3 and L-TOWN','conditional scenarios')
    """),
    markdown("## 14. Decision card, claim boundary, and operator workflow"),
    code("""
    event=sdaif_events[(sdaif_events.policy=='adaptive_sdaif')].iloc[0]
    selected_rows=raw_predictions[(raw_predictions.round_id==event.round_id)&raw_predictions['samplingPoint.notation'].isin(event.selected_sites.split('|'))].copy().sort_values('predicted_probability',ascending=False)
    card=selected_rows[['samplingPoint.notation','predicted_probability','model_probability_std','high_500']].copy(); card['site_alias']=card['samplingPoint.notation'].map(lambda x:'SITE_'+hashlib.sha256(str(x).encode()).hexdigest()[:6].upper()); card['laboratory_confirmation']='revealed in retrospective replay only'; card['evidence_origin']='LAB_CONFIRMED + MODEL_ESTIMATE'; card=card[['site_alias','predicted_probability','model_probability_std','laboratory_confirmation','evidence_origin']]
    display(card); save_table('example_decision_card',card,'LAB_CONFIRMED + MODEL_ESTIMATE','One retrospective auditable SDAIF decision card, pseudonymized.')
    claims=pd.read_csv(ROOT/'reports/claim_to_evidence_matrix.csv')
    save_table('claim_to_artifact_traceability',claims,'CURRENT_CANONICAL','Permitted/prohibited claim traceability from the repository audit.')
    fig,axes=plt.subplots(1,3,figsize=(15,4))
    axes[0].axis('off'); axes[0].set_title('Figure 56. Decision card'); axes[0].table(cellText=card.round(3).values,colLabels=card.columns,loc='center',cellLoc='center'); axes[0].axis('off')
    allowed=claims[claims.astype(str).apply(lambda r:r.str.contains('permit|supported|approved',case=False).any(),axis=1)]; prohibited=claims[claims.astype(str).apply(lambda r:r.str.contains('prohibit|not claim|unsupported',case=False).any(),axis=1)]; axes[1].bar(['traceable rows','prohibited rows'],[len(claims),len(prohibited)],color=[PALETTE['green'],PALETTE['red']]); axes[1].set(title='Figure 57. Claim-boundary audit',ylabel='rows')
    axes[2].axis('off'); axes[2].set_title('Figure 58. Operator workflow'); axes[2].text(.5,.55,'ranked test list\\n→ qualified sampling\\n→ laboratory confirmation\\n→ documented response\\n(no automatic public-health action)',ha='center',va='center',bbox={"boxstyle":"round","facecolor":"#EBF8FF"})
    for ax in axes: tag(ax,'CURRENT_CANONICAL','NADI decision artifacts','retrospective decision card')
    savefig(fig,56,'decision_card_and_claim_boundary','Pseudonymized decision card, claim boundary, and operator workflow.','CURRENT_CANONICAL','NADI decision artifacts','retrospective replay')
    """),
    markdown("## 15. Final contribution, limitations, and next decisive experiment"),
    code("""
    limitations=pd.DataFrame({"limitation":[
        'No unified event-level microbiology-plus-network dataset', 'Primary microbial source is mixed environmental water',
        'Unseen-site transfer is weaker than in-domain performance', 'High locked-period prevalence and low specificity',
        'Hydraulic validation is not biological contamination validation', 'Net3/L-TOWN source tracing remains simulated',
        'Retrospective same-round outcome reveal is not laboratory turnaround validation'],
        "next decisive experiment":[
        'Collect paired microbiology, network state and timing data prospectively', 'Validate a separately collected drinking-water domain',
        'Predeclare local recalibration and abstention gates', 'Use a prospective representative sampling stream',
        'Compare hydraulic state estimates with verified utility operations', 'Run field-confirmed tracer/response study',
        'Issue frozen priorities before independent laboratory outcomes']})
    display(limitations); save_table('limitations_and_next_experiment',limitations,'CURRENT_CANONICAL','Limitations and prospective validation pathway.')
    fig,ax=plt.subplots(figsize=(13,4)); ax.axis('off'); ax.set_title('Figure 59. Current evidence to prospective validation pathway')
    nodes=['retrospective lab evidence','fixed-budget decision replay','separate pressure reconstruction','conditional simulation stress tests','prospective paired field pilot']
    for i,node in enumerate(nodes):
        x=.06+i*.22; color=[PALETTE['blue'],PALETTE['purple'],PALETTE['green'],PALETTE['yellow'],PALETTE['grey']][i]
        ax.text(x,.55,node,ha='center',va='center',fontsize=8,bbox={"boxstyle":"round,pad=.4","facecolor":color+'33','edgecolor':color})
        if i<len(nodes)-1: ax.annotate('',(x+.085,.55),(x+.135,.55),arrowprops={'arrowstyle':'->'})
    tag(ax,'CURRENT_CANONICAL / PROPOSED NEXT EXPERIMENT','NADI evidence pathway','current to prospective')
    savefig(fig,59,'current_to_prospective_validation','Current demonstrated evidence and prospective validation path.','CURRENT_CANONICAL / ASSUMED','NADI evidence pathway','current to prospective')
    """),
    markdown("## 16. Final reproducibility manifest and execution summary"),
    code("""
    # Final notebook-owned artifacts and traceability outputs. Nothing in a frozen directory is changed.
    artifact_rows=FIGURES+TABLES
    artifact_manifest=pd.DataFrame(artifact_rows)
    artifact_manifest_path=ROOT/'reports/notebook_artifact_manifest.csv'; artifact_manifest.to_csv(artifact_manifest_path,index=False)
    claim_out=ROOT/'reports/notebook_claim_traceability.csv'; claims.to_csv(claim_out,index=False)
    index_path=ROOT/'reports/notebook_figure_index.md'
    index_path.write_text('# NADI research companion figure index\\n\\n'+ '\\n'.join(f"- Figure {r['number']}: `{r['name']}` — {r['evidence_status']}; {r['caption']}" for r in FIGURES)+'\\n',encoding='utf-8')
    execution={"notebook":"notebooks/NADI_executable_research_companion.ipynb","executed_utc":datetime.now(timezone.utc).isoformat(),"python":sys.version,"platform":platform.platform(),"figure_count":len(FIGURES),"table_count":len(TABLES),"integrity_checks":CHECKS,"claim_boundary":"Retrospective UK EA mixed environmental-water test prioritization; separate BWFLnet pressure reconstruction; separate simulation."}
    report_path=ROOT/'reports/notebook_execution_report.md'
    report_path.write_text('# NADI executable research companion report\\n\\n'+json.dumps(execution,indent=2)+'\\n',encoding='utf-8')
    display(artifact_manifest[['kind','number','name','evidence_status','path']])
    print(json.dumps({"status":"PASS","figures":len(FIGURES),"tables":len(TABLES),"integrity_checks":len(CHECKS),"artifact_manifest":str(artifact_manifest_path.relative_to(ROOT))},indent=2))
    """),
]


def main() -> None:
    notebook = {
        "cells": cells,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "version": "3.10"},
            "nadi": {"version": "2026.11", "purpose": "artifact-driven research companion"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(notebook, indent=2) + "\n", encoding="utf-8")
    print(f"{OUTPUT}: {len(cells)} cells")


if __name__ == "__main__":
    main()
