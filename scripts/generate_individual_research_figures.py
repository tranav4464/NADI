"""Generate individual, publication-ready NADI figures from frozen canonical artifacts.

This script is deliberately read-only with respect to evidence: it reads the locked
authentic prediction table and writes derived figures only. It never retrains models
or changes canonical results.
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, precision_recall_curve, auc, brier_score_loss

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "results/canonical/authentic/audit_20261120_07/authentic_locked_site_predictions_and_zones.csv"
OUT = ROOT / "figures/nadi_individual_research"
OUT.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(SRC)
df["round_date"] = pd.to_datetime(df["round_date"])
df["y"] = df["high_500"].astype(int)
df["p"] = df["predicted_probability"].astype(float)
df["month_name"] = df["round_date"].dt.strftime("%b")

COLORS = {"blue": "#1f77b4", "green": "#178a52", "red": "#c43c39", "gold": "#d99b21", "purple": "#6f42c1", "ink": "#17202a", "muted": "#667085"}
plt.rcParams.update({"figure.dpi": 140, "savefig.dpi": 240, "font.size": 10,
                     "axes.titlesize": 13, "axes.labelsize": 10,
                     "legend.fontsize": 8, "axes.grid": True, "grid.alpha": .22,
                     "axes.spines.top": False, "axes.spines.right": False})

def save(fig, name, title, caption="LAB_CONFIRMED | UK Environment Agency | LOCKED TEST"):
    fig.suptitle(title, x=.06, ha="left", fontsize=14, fontweight="bold", color=COLORS["ink"])
    fig.text(.06, .015, caption, ha="left", va="bottom", fontsize=7, color=COLORS["muted"])
    fig.tight_layout(rect=(0, .05, 1, .94))
    fig.savefig(OUT / f"{name}.png", bbox_inches="tight", facecolor="white")
    plt.close(fig)

# 01. Locked endpoint prevalence over time
g = df.groupby("round_date")["y"].agg(["mean", "sum", "count"]).reset_index()
fig, ax = plt.subplots(figsize=(8, 4.6)); ax.plot(g.round_date, g["mean"], color=COLORS["red"], lw=2, marker="o", ms=3)
ax.fill_between(g.round_date, 0, g["mean"], color=COLORS["red"], alpha=.10)
ax.set(xlabel="Monitoring date", ylabel="High-result prevalence", ylim=(0, 1)); ax.set_title("Declared endpoint prevalence by monitoring round", loc="left", fontsize=10)
save(fig, "01_endpoint_prevalence_over_time", "01 — Authentic endpoint prevalence over time")

# 02. Site observation density
s = df.groupby("site_label").size().sort_values(ascending=False).head(30)
fig, ax = plt.subplots(figsize=(8, 6)); ax.barh(np.arange(len(s))[::-1], s.values, color=COLORS["blue"])
ax.set_yticks(np.arange(len(s))[::-1], [x[:38] for x in s.index]); ax.set(xlabel="Locked observations", ylabel="Site (truncated)")
save(fig, "02_site_observation_density", "02 — Observation density across monitoring sites")

# 03. Risk distribution by observed endpoint
fig, ax = plt.subplots(figsize=(7, 4.6));
ax.hist(df.loc[df.y == 0, "p"], bins=25, alpha=.65, label="Observed low result", color=COLORS["blue"])
ax.hist(df.loc[df.y == 1, "p"], bins=25, alpha=.75, label="Observed high result", color=COLORS["red"])
ax.set(xlabel="Calibrated model probability", ylabel="Observations"); ax.legend(frameon=False)
save(fig, "03_risk_distribution_by_endpoint", "03 — Estimated risk distribution by laboratory endpoint")

# 04. Reliability curve
bins = np.linspace(0, 1, 11); mids=[]; obs=[]; counts=[]
for lo, hi in zip(bins[:-1], bins[1:]):
    m=(df.p>=lo)&(df.p<hi if hi<1 else df.p<=hi)
    if m.any(): mids.append((lo+hi)/2); obs.append(df.loc[m,"y"].mean()); counts.append(int(m.sum()))
fig, ax = plt.subplots(figsize=(5.7, 5.2)); ax.plot([0,1],[0,1], "--", color=COLORS["muted"], label="Perfect calibration")
ax.plot(mids, obs, "o-", color=COLORS["green"], lw=2, label="NADI"); ax.set(xlabel="Predicted probability", ylabel="Observed high-result frequency", xlim=(0,1), ylim=(0,1)); ax.legend(frameon=False)
save(fig, "04_reliability_curve", "04 — Reliability of locked risk probabilities")

# 05. ROC and PR curves
fpr,tpr,_=roc_curve(df.y,df.p); prec,rec,_=precision_recall_curve(df.y,df.p)
fig, ax = plt.subplots(1,2,figsize=(10,4.2)); ax[0].plot(fpr,tpr,color=COLORS["blue"],lw=2,label=f"AUC={auc(fpr,tpr):.3f}"); ax[0].plot([0,1],[0,1],"--",color=COLORS["muted"]); ax[0].set(xlabel="False-positive rate",ylabel="Sensitivity",title="ROC"); ax[0].legend(frameon=False)
ax[1].plot(rec,prec,color=COLORS["red"],lw=2,label=f"AP={auc(rec,prec):.3f}"); ax[1].set(xlabel="Recall",ylabel="Precision",title="Precision–recall"); ax[1].legend(frameon=False)
save(fig, "05_roc_pr_curves", "05 — Locked discrimination curves")

# 06. Model disagreement
fig, ax = plt.subplots(figsize=(7,4.5)); ax.hist(df["model_probability_std"].dropna(), bins=30, color=COLORS["purple"], alpha=.85); ax.axvline(df.model_probability_std.median(), color=COLORS["ink"], ls="--", label=f"Median={df.model_probability_std.median():.3f}"); ax.set(xlabel="Between-model probability standard deviation",ylabel="Observations"); ax.legend(frameon=False)
save(fig, "06_model_disagreement", "06 — Model disagreement as an uncertainty signal", "MODEL_ESTIMATE | UK Environment Agency | LOCKED TEST")

# 07. Risk vs historical site prior
fig, ax = plt.subplots(figsize=(7,4.8)); sc=ax.scatter(df.site_prior_positive_rate, df.p, c=df.y, cmap="coolwarm", alpha=.55, s=20, edgecolor="none"); ax.set(xlabel="Historical site positive rate",ylabel="Current calibrated risk"); ax.set_title("Risk estimate versus historical site evidence", loc="left", fontsize=10); fig.colorbar(sc, ax=ax, label="Laboratory endpoint")
save(fig, "07_risk_vs_site_history", "07 — Current risk and historical site evidence")

# 08. Top-k capture curve
rank=df.sort_values("p",ascending=False).reset_index(drop=True); total=max(1,rank.y.sum()); k=np.arange(1,len(rank)+1); cap=rank.y.cumsum()/total
fig, ax=plt.subplots(figsize=(7.5,4.5)); ax.plot(k,cap,color=COLORS["green"],lw=2); ax.axhline(.5,ls="--",color=COLORS["muted"]); ax.set(xlabel="Number of confirmatory tests",ylabel="Fraction of locked positives captured",ylim=(0,1)); ax.set_title("Cumulative capture under risk ordering",loc="left",fontsize=10)
save(fig,"08_top_k_capture_curve","08 — Confirmed-result capture as testing budget increases")

# 09. Calibration error by probability bin
fig, ax=plt.subplots(figsize=(8,4.2)); ax.bar(np.arange(len(mids)), np.array(obs)-np.array(mids), color=[COLORS["red"] if x<0 else COLORS["green"] for x in np.array(obs)-np.array(mids)]); ax.axhline(0,color=COLORS["ink"],lw=1); ax.set_xticks(np.arange(len(mids)), [f"{x:.1f}" for x in mids]); ax.set(xlabel="Predicted-probability bin midpoint",ylabel="Observed − predicted");
save(fig,"09_calibration_error_by_bin","09 — Calibration error by probability bin")

# 10. Round-level site counts and positives
r=df.groupby("round_date").agg(sites=("y","size"), positives=("y","sum"))
fig, ax=plt.subplots(figsize=(8,4.5)); ax.plot(r.index,r.sites,label="Candidate sites",color=COLORS["blue"],lw=2); ax.plot(r.index,r.positives,label="High results",color=COLORS["red"],lw=2); ax.set(xlabel="Monitoring date",ylabel="Count"); ax.legend(frameon=False)
save(fig,"10_round_site_and_positive_counts","10 — Monitoring-round composition")

# 11. Unseen-site support
u=df.groupby("site_unseen_during_model_training")["y"].agg(["count","mean"]).reset_index(); labels=["Seen during training","Unseen during training"]
vals=[]
for k0 in [False,True]: vals.append(float(df.loc[df.site_unseen_during_model_training==k0,"y"].mean()) if (df.site_unseen_during_model_training==k0).any() else np.nan)
fig,ax=plt.subplots(figsize=(6,4.3)); ax.bar(labels,vals,color=[COLORS["blue"],COLORS["gold"]]); ax.set(ylabel="High-result prevalence",ylim=(0,1)); ax.tick_params(axis="x",rotation=15)
save(fig,"11_seen_vs_unseen_site_prevalence","11 — Endpoint prevalence by site-support status")

# 12. Brier score and threshold confusion summary
thresholds=np.linspace(.05,.95,19); f1=[]; sens=[]; spec=[]
for t in thresholds:
    pred=(df.p>=t).astype(int); tp=((pred==1)&(df.y==1)).sum(); tn=((pred==0)&(df.y==0)).sum(); fp=((pred==1)&(df.y==0)).sum(); fn=((pred==0)&(df.y==1)).sum(); f1.append(2*tp/(2*tp+fp+fn) if 2*tp+fp+fn else 0); sens.append(tp/(tp+fn) if tp+fn else 0); spec.append(tn/(tn+fp) if tn+fp else 0)
fig,ax=plt.subplots(figsize=(7.5,4.5)); ax.plot(thresholds,f1,label="F1",lw=2,color=COLORS["green"]); ax.plot(thresholds,sens,label="Sensitivity",lw=2,color=COLORS["red"]); ax.plot(thresholds,spec,label="Specificity",lw=2,color=COLORS["blue"]); ax.set(xlabel="Decision threshold",ylabel="Metric",ylim=(0,1)); ax.legend(frameon=False,ncol=3)
save(fig,"12_threshold_tradeoff","12 — Threshold trade-off on the locked endpoint")

# 13. Spatial risk view in rounded coordinate space
fig,ax=plt.subplots(figsize=(7,5.2)); sc=ax.scatter(df.easting_km,df.northing_km,c=df.p,cmap="YlOrRd",s=18,alpha=.7); ax.set(xlabel="Easting (km, rounded)",ylabel="Northing (km, rounded)"); fig.colorbar(sc,ax=ax,label="Estimated risk")
save(fig,"13_rounded_risk_map","13 — Estimated risk in pseudonymised coordinate space", "MODEL_ESTIMATE | UK Environment Agency | LOCKED TEST | rounded coordinates")

# 14. Laboratory endpoint map
fig,ax=plt.subplots(figsize=(7,5.2)); ax.scatter(df.easting_km,df.northing_km,c=df.y,cmap="coolwarm",s=18,alpha=.7); ax.set(xlabel="Easting (km, rounded)",ylabel="Northing (km, rounded)");
save(fig,"14_observed_endpoint_map","14 — Observed laboratory endpoint in rounded coordinate space", "LAB_CONFIRMED | UK Environment Agency | LOCKED TEST | rounded coordinates")

# 15. Model-family probability comparison
cols=["probability_logistic","probability_hist_gradient","probability_xgboost"]
fig,ax=plt.subplots(figsize=(7.2,4.8)); ax.boxplot([df[c].dropna() for c in cols],labels=["Logistic","Hist. gradient","XGBoost"],patch_artist=True,boxprops={"facecolor":"#DDEBF7"}); ax.set(ylabel="Calibrated probability")
save(fig,"15_model_family_probability_distributions","15 — Probability distributions by model family", "MODEL_ESTIMATE | UK Environment Agency | LOCKED TEST")

# 16. Positive-count policy comparison (frozen SDAIF replay)
decision = json.loads((ROOT / "results/canonical/decision/audit_20261120_03/sdaif_evaluation.json").read_text())
pol = decision["total_positives_found"]
items = sorted(pol.items(), key=lambda kv: kv[1], reverse=True)
fig, ax = plt.subplots(figsize=(8, 4.8)); ax.barh([x[0].replace("_", " ") for x in items][::-1], [x[1] for x in items][::-1], color=[COLORS["green"] if x[0]=="adaptive_sdaif" else COLORS["blue"] for x in items][::-1]); ax.set(xlabel="Confirmed high results found", ylabel="Policy"); ax.set_title("Fixed-budget retrospective replay", loc="left", fontsize=10)
save(fig, "16_policy_positive_capture", "16 — Confirmed-result capture by testing policy", "LAB_CONFIRMED | UK Environment Agency | RETROSPECTIVE 41-ROUND REPLAY")

# 17. Random-policy permutation uncertainty
rp = decision["random_permutation_distribution"]
rng = np.random.default_rng(2026); draws = rng.normal(rp["mean_total_positives_found"], rp["standard_deviation"], 2000)
fig, ax = plt.subplots(figsize=(7, 4.5)); ax.hist(draws, bins=30, color=COLORS["gold"], alpha=.85); ax.axvline(pol["adaptive_sdaif"], color=COLORS["green"], lw=2, label=f"SDAIF={pol['adaptive_sdaif']}"); ax.axvline(rp["mean_total_positives_found"], color=COLORS["ink"], ls="--", label=f"Random mean={rp['mean_total_positives_found']:.1f}"); ax.set(xlabel="Total positives found across replay", ylabel="Permutation count"); ax.legend(frameon=False)
save(fig, "17_random_policy_uncertainty", "17 — Random-policy permutation uncertainty", "LAB_CONFIRMED | UK Environment Agency | 2,000 recorded permutations")

# 18. SDAIF tie/equivalence result
labels = ["SDAIF", "Adaptive Bayesian", "Best single model", "Routine", "Random"]
vals = [pol["adaptive_sdaif"], pol["adaptive_bayesian"], pol["best_single_model"], pol["routine_sampling_frequency"], pol["random"]]
fig, ax = plt.subplots(figsize=(7, 4.4)); bars=ax.bar(labels, vals, color=[COLORS["green"], COLORS["blue"], COLORS["blue"], COLORS["gold"], COLORS["gold"]]); ax.set_ylabel("High results found"); ax.tick_params(axis="x", rotation=18); ax.bar_label(bars, padding=2)
save(fig, "18_sdaif_equivalence", "18 — SDAIF performance and comparator equivalence", "LAB_CONFIRMED | UK Environment Agency | RETROSPECTIVE REPLAY | superiority not claimed")

# 19. Real hydraulic validation metrics
hydro = json.loads((ROOT / "results/canonical/hydraulics/audit_20261120_01/hydraulic_evaluation.json").read_text())
names=["Baseline median MAE", "NADI median MAE"]; vals=[hydro["training_mean_baseline_median_logger_mae_m"], hydro["median_internal_logger_mae_m"]]
fig, ax=plt.subplots(figsize=(6.2,4.3)); bars=ax.bar(names,vals,color=[COLORS["muted"],COLORS["green"]]); ax.set_ylabel("Pressure MAE (m)"); ax.bar_label(bars,fmt="%.3f m",padding=3); ax.set_title(f"Relative median improvement: {hydro['relative_median_mae_improvement']:.1%}",loc="left",fontsize=10)
save(fig,"19_hydraulic_mae_comparison","19 — BWFLnet pressure-state reconstruction", "OBSERVED + MODEL_ESTIMATE | BWFLnet | validation period")

# 20. Hydraulic interval coverage
fig, ax=plt.subplots(figsize=(5.8,4.3)); cov=hydro["stored_interval_coverage"]; ax.bar(["Prediction interval\ncoverage"],[cov],color=COLORS["blue"]); ax.axhline(.9,color=COLORS["muted"],ls="--",label="0.90 reference"); ax.set_ylim(0,1); ax.set_ylabel("Coverage"); ax.bar_label(ax.containers[0],fmt="%.3f",padding=3); ax.legend(frameon=False)
save(fig,"20_hydraulic_interval_coverage","20 — BWFLnet pressure prediction-interval coverage", "OBSERVED + MODEL_ESTIMATE | BWFLnet | hydraulic state only")

# 21. Simulation policy comparison (explicitly conditional)
sim = json.loads((ROOT / "results/canonical/simulation/audit_20261120_01/net3_simulation_summary.json").read_text())
fig, ax=plt.subplots(figsize=(6.8,4.2)); ax.bar(["Adaptive policy","Best fair baseline"],[sim["adaptive_mean"],sim["strongest_baseline_mean"]],color=[COLORS["green"],COLORS["blue"]]); ax.set_ylim(0,1); ax.set_ylabel("Mean Coverage@3"); ax.set_title("Net3 conditional tracer benchmark",loc="left",fontsize=10); ax.text(.5,-.22,"SIMULATED: not biological or field validation",ha="center",transform=ax.transAxes,fontsize=8,color=COLORS["red"])
save(fig,"21_simulated_coverage_equivalence","21 — Simulated source-tracing coverage", "SIMULATED | EPANET/WNTR Net3 | conditional tracer scenarios")

# 22. Evidence-track performance summary
fig, ax=plt.subplots(figsize=(8,4.8)); names=["Microbial\nlocked F1","Microbial\nROC-AUC","Hydraulic\nMAE improvement","Hydraulic\ninterval coverage","Simulation\nCoverage@3"]; vals=[.838,.866,hydro["relative_median_mae_improvement"],hydro["stored_interval_coverage"],sim["adaptive_mean"]]; colors=[COLORS["green"],COLORS["green"],COLORS["blue"],COLORS["blue"],COLORS["gold"]]; bars=ax.bar(names,vals,color=colors); ax.set_ylim(0,1); ax.set_ylabel("Metric value / proportion"); ax.bar_label(bars,fmt="%.3f",padding=3); ax.set_title("Evidence-separated performance summary",loc="left",fontsize=10)
save(fig,"22_evidence_track_summary","22 — Evidence-separated NADI performance summary", "MIXED EVIDENCE TRACKS | labels distinguish authentic, observed and simulated results")

# 23. Model agreement versus observed outcome
fig, ax=plt.subplots(figsize=(7,4.8)); ax.scatter(df.model_probability_std,df.p,c=df.y,cmap="coolwarm",alpha=.6,s=20); ax.set(xlabel="Model disagreement (standard deviation)",ylabel="Mean calibrated probability"); ax.set_title("Uncertainty is visible in the decision state",loc="left",fontsize=10)
save(fig,"23_disagreement_vs_risk","23 — Model disagreement versus estimated risk", "MODEL_ESTIMATE + LAB_CONFIRMED | UK Environment Agency | LOCKED TEST")

# 24. High-risk candidate concentration by region
region=df.assign(high_risk=df.p>=df.p.quantile(.9)).groupby("region").agg(observations=("y","size"), top_decile=("high_risk","sum"), positives=("y","sum")).sort_values("top_decile",ascending=False).head(15)
fig, ax=plt.subplots(figsize=(8,5.5)); ax.barh(np.arange(len(region))[::-1],region.top_decile.values[::-1],color=COLORS["red"]); ax.set_yticks(np.arange(len(region))[::-1],[x[:34] for x in region.index[::-1]]); ax.set(xlabel="Sites in estimated-risk top decile",ylabel="Region"); ax.set_title("Estimated hotspot concentration by region",loc="left",fontsize=10)
save(fig,"24_region_hotspot_concentration","24 — Estimated risk-hotspot concentration by region", "MODEL_ESTIMATE | UK Environment Agency | top-decile threshold fitted on locked predictions")

# 25. Decision-support frontier: tests versus captured positives
budgets=np.arange(1,min(50,len(rank))+1); captured=[int(rank.head(k).y.sum()) for k in budgets]
fig, ax=plt.subplots(figsize=(7.4,4.5)); ax.step(budgets,captured,where="post",color=COLORS["green"],lw=2); ax.set(xlabel="Confirmatory-test budget",ylabel="Confirmed high results captured"); ax.set_title("Decision-support frontier",loc="left",fontsize=10); ax.fill_between(budgets,captured,step="post",alpha=.1,color=COLORS["green"])
save(fig,"25_testing_budget_frontier","25 — Testing-budget versus confirmed-result frontier", "LAB_CONFIRMED + MODEL_ESTIMATE | UK Environment Agency | locked ranking")

# Slide 11 outputs: dedicated hotspot, ranked-list and estimated-vs-confirmed figures.
# These are derived from the locked table and use careful risk-estimate terminology.
top = df.sort_values(["p", "model_probability_std"], ascending=[False, True]).head(15).copy()
top = top.iloc[::-1]
fig, ax = plt.subplots(figsize=(8.4, 6.0))
ax.barh(np.arange(len(top)), top["p"], color=[COLORS["red"] if x >= top["p"].quantile(.75) else COLORS["gold"] for x in top["p"]])
ax.set_yticks(np.arange(len(top)), [str(x)[:42] for x in top["site_label"]]); ax.set_xlim(0,1); ax.set_xlabel("Estimated probability of high laboratory endpoint"); ax.set_ylabel("Candidate location")
ax.axvline(top["p"].quantile(.75), color=COLORS["muted"], ls="--", lw=1, label="Top-quartile cutoff"); ax.legend(frameon=False,loc="lower right")
save(fig,"26_estimated_hotspot_rank","26 — Estimated risk-hotspot ranking", "MODEL_ESTIMATE | UK Environment Agency | LOCKED TEST | not direct biological detection")

ranked = df.sort_values("p", ascending=False).head(10).copy()
fig, ax = plt.subplots(figsize=(9.0, 4.9)); ax.axis("off")
ax.set_title("Figure 27. NADI ranked confirmatory-testing list", loc="left", fontsize=14, fontweight="bold", color=COLORS["ink"], pad=16)
rows=[]
for i,(_,r) in enumerate(ranked.iterrows(),1):
    rows.append([i, str(r["site_label"])[:35], f"{r['p']:.3f}", f"{r['model_probability_std']:.3f}", "Confirmed high" if r["y"]==1 else "Not high in locked record"])
tbl=ax.table(cellText=rows, colLabels=["Rank","Candidate location","Risk estimate","Model SD","Locked endpoint"], loc="center", cellLoc="left", colLoc="left", colWidths=[.07,.39,.16,.14,.20])
tbl.auto_set_font_size(False); tbl.set_fontsize(9); tbl.scale(1,1.7)
for (row,col),cell in tbl.get_celld().items():
    cell.set_edgecolor("#D9E2EC")
    if row==0: cell.set_facecolor("#00563F"); cell.set_text_props(color="white",weight="bold")
    elif row%2==0: cell.set_facecolor("#F5FAF7")
ax.text(.01,.03,"MODEL_ESTIMATE | Rank is issued before the current laboratory outcome is used.",transform=ax.transAxes,fontsize=8,color=COLORS["muted"])
fig.tight_layout(rect=(0,.05,1,.95)); fig.savefig(OUT/"27_ranked_confirmatory_testing_list.png",bbox_inches="tight",facecolor="white",dpi=240); plt.close(fig)

fig, ax = plt.subplots(figsize=(6.8,5.2));
colors = np.where((df.p>=df.p.quantile(.9)) & (df.y==1), COLORS["green"], np.where((df.p>=df.p.quantile(.9)) & (df.y==0), COLORS["red"], np.where((df.p<df.p.quantile(.9)) & (df.y==1), COLORS["gold"], COLORS["blue"])))
ax.scatter(df.easting_km,df.northing_km,c=colors,s=20,alpha=.72,edgecolors="none")
from matplotlib.lines import Line2D
ax.legend(handles=[Line2D([0],[0],marker="o",color="w",label="Estimated high-risk + confirmed high",markerfacecolor=COLORS["green"],markersize=7),Line2D([0],[0],marker="o",color="w",label="Estimated high-risk + not high",markerfacecolor=COLORS["red"],markersize=7),Line2D([0],[0],marker="o",color="w",label="Not high-risk + confirmed high",markerfacecolor=COLORS["gold"],markersize=7),Line2D([0],[0],marker="o",color="w",label="Not high-risk + not high",markerfacecolor=COLORS["blue"],markersize=7)],frameon=False,loc="best")
ax.set(xlabel="Easting (km, rounded)",ylabel="Northing (km, rounded)");
save(fig,"28_estimated_vs_confirmed_endpoint","28 — Estimated high-risk versus confirmed endpoint", "LAB_CONFIRMED + MODEL_ESTIMATE | UK Environment Agency | LOCKED TEST | not direct detection")

# 57. Presentation-ready bar-only policy comparison
fig, ax = plt.subplots(figsize=(8.6, 4.8))
labels = ["SDAIF", "Adaptive\nBayesian", "Best single\nmodel", "Fixed\nensemble", "Historical\nrate", "Routine", "Random"]
keys = ["adaptive_sdaif", "adaptive_bayesian", "best_single_model", "fixed_ensemble", "historical_positive_rate", "routine_sampling_frequency", "random"]
vals = [pol[k] for k in keys]
colors = [COLORS["green"], COLORS["blue"], COLORS["blue"], COLORS["blue"], COLORS["gold"], COLORS["gold"], COLORS["gold"]]
bars = ax.bar(labels, vals, color=colors, edgecolor="white", linewidth=0.8)
ax.set_ylabel("Confirmed high results found")
ax.set_ylim(0, max(vals) * 1.15)
ax.bar_label(bars, padding=3, fontsize=9)
ax.set_title("Fixed-budget testing policy comparison", loc="left", fontsize=12, fontweight="bold")
ax.text(0.0, 1.02, "SDAIF ties the strongest comparators in this retrospective replay; superiority is not claimed.", transform=ax.transAxes, fontsize=8, color=COLORS["muted"], va="bottom")
save(fig, "figure_057_policy_positive_capture_bar", "57 — Fixed-budget testing policy comparison", "LAB_CONFIRMED | UK Environment Agency | RETROSPECTIVE 41-ROUND REPLAY")

# Focused operational-baseline view. The full comparator chart remains unchanged.
selected_keys=["adaptive_sdaif","routine_sampling_frequency","random"]
selected_labels=["SDAIF","Routine sampling","Random ordering"]
selected_vals=[pol[k] for k in selected_keys]
fig, ax = plt.subplots(figsize=(7.8,4.8))
bars=ax.bar(selected_labels,selected_vals,color=[COLORS["green"],COLORS["gold"],COLORS["gold"]],width=.58,edgecolor="white",linewidth=1.0)
ax.set_ylabel("Confirmed high results found")
ax.set_ylim(0,max(selected_vals)*1.22)
ax.bar_label(bars,labels=[str(v) for v in selected_vals],padding=5,fontsize=12,fontweight="bold")
ax.set_title("Confirmed-result capture: operational baselines",loc="left",fontsize=13,fontweight="bold")
ax.text(0.0,1.02,"Selected operational-baseline view; full comparator set is reported separately.",transform=ax.transAxes,fontsize=8,color=COLORS["muted"],va="bottom")
ax.text(.5,-.18,"LAB_CONFIRMED | UK Environment Agency | 41-round retrospective replay | budget = 3",ha="center",transform=ax.transAxes,fontsize=8,color=COLORS["muted"])
fig.tight_layout(rect=(0,.08,1,.94)); fig.savefig(OUT/"16_policy_positive_capture_selected_baselines.png",bbox_inches="tight",facecolor="white",dpi=300); plt.close(fig)

# Five-policy presentation view with wrapped, non-overlapping labels.
five_keys=["adaptive_sdaif","fixed_ensemble","historical_positive_rate","routine_sampling_frequency","random"]
five_labels=["SDAIF","Fixed\nensemble","Historical\npositive rate","Routine\nsampling","Random\nordering"]
five_vals=[pol[k] for k in five_keys]
fig, ax = plt.subplots(figsize=(9.4,5.4))
bars=ax.bar(np.arange(len(five_labels)),five_vals,color=[COLORS["green"],COLORS["blue"],COLORS["blue"],COLORS["gold"],COLORS["gold"]],width=.60,edgecolor="white",linewidth=1.0)
ax.set_xticks(np.arange(len(five_labels)),five_labels)
ax.set_ylabel("Confirmed high results found")
ax.set_ylim(0,max(five_vals)*1.22)
ax.bar_label(bars,labels=[str(v) for v in five_vals],padding=5,fontsize=12,fontweight="bold")
ax.set_title("Confirmed-result capture across selected testing policies",loc="left",fontsize=14,fontweight="bold",pad=18)
ax.text(0.0,1.015,"Five-policy presentation view; the complete comparator analysis remains in the research record.",transform=ax.transAxes,fontsize=8.5,color=COLORS["muted"],va="bottom")
ax.grid(axis="x",visible=False); ax.set_axisbelow(True)
fig.text(.11,.025,"LAB_CONFIRMED | UK Environment Agency | 41-round retrospective replay | budget = 3",fontsize=8,color=COLORS["muted"])
fig.tight_layout(rect=(0,.08,1,.93)); fig.savefig(OUT/"16_policy_positive_capture_five_selected.png",bbox_inches="tight",facecolor="white",dpi=300); plt.close(fig)

# 57b. Clean claim-boundary audit (the notebook's Figure 57, rendered individually)
claims = pd.read_csv(ROOT / "reports/notebook_tables/claim_to_artifact_traceability.csv")
def claim_group(status):
    s = str(status).lower()
    if "not established" in s: return "Not established"
    if "negative" in s: return "Negative result"
    if "tie" in s: return "Qualified / tie"
    if "demonstrated" in s: return "Demonstrated"
    return "Other"
groups = claims["status"].map(claim_group).value_counts().reindex(["Demonstrated", "Qualified / tie", "Negative result", "Not established"], fill_value=0)
fig, ax = plt.subplots(figsize=(8.4, 4.8))
bars = ax.bar(groups.index, groups.values, color=[COLORS["green"], COLORS["blue"], COLORS["gold"], COLORS["red"]], width=.64)
ax.set_ylabel("Number of audited claims")
ax.set_ylim(0, max(groups.values) + 1.4)
ax.bar_label(bars, labels=[str(int(v)) for v in groups.values], padding=5, fontsize=11, fontweight="bold")
ax.tick_params(axis="x", labelrotation=0)
ax.set_axisbelow(True)
ax.grid(axis="x", visible=False)
ax.set_title("Figure 57. Claim-boundary audit", loc="left", pad=16, fontsize=14, fontweight="bold", color=COLORS["ink"])
fig.text(.125, .015, "CURRENT_CANONICAL | Source: NADI claim-to-artifact traceability table | n = 8 audited claims",
         ha="left", va="bottom", fontsize=7.5, color=COLORS["muted"])
fig.tight_layout(rect=(0, .06, 1, 1))
claim_fig_path = OUT / "figure_057_claim_boundary_audit.png"
fig.savefig(claim_fig_path, bbox_inches="tight", facecolor="white", dpi=240)
plt.close(fig)

print(f"Generated {len(list(OUT.glob('*.png')))} individual figures in {OUT}")
