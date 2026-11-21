from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.calibration import calibration_curve

ROOT = Path(__file__).resolve().parents[1]
AUTH = ROOT / "results/canonical/authentic/audit_20261120_07/authentic_locked_site_predictions_and_zones.csv"
OUT = ROOT / "figures/nadi_slide10_math"
OUT.mkdir(parents=True, exist_ok=True)
df = pd.read_csv(AUTH)
df["y"] = df["high_500"].astype(int)
df["p"] = df["predicted_probability"].astype(float)
P = {"ink":"#17202A", "blue":"#2878B5", "green":"#178A52", "amber":"#D99B21", "red":"#C43C39", "purple":"#7153A6", "muted":"#667085"}
plt.rcParams.update({"figure.dpi":150,"savefig.dpi":300,"font.size":11,"axes.titlesize":15,"axes.labelsize":11,"axes.grid":True,"grid.alpha":.22,"axes.spines.top":False,"axes.spines.right":False})

def save(fig, name, title, footer):
    fig.suptitle(title, x=.08, ha="left", y=.98, fontsize=16, fontweight="bold", color=P["ink"])
    fig.text(.08,.025,footer,ha="left",va="bottom",fontsize=8,color=P["muted"])
    fig.tight_layout(rect=(0,.07,1,.93))
    fig.savefig(OUT / name, bbox_inches="tight", facecolor="white")
    plt.close(fig)

# A: individual model outputs and ensemble uncertainty
fig, ax = plt.subplots(figsize=(8.4,5.0))
sample = df.sort_values("p", ascending=False).head(80).reset_index(drop=True)
x=np.arange(len(sample))
for c, label, color in [("probability_logistic","Logistic",P["blue"]),("probability_hist_gradient","Gradient boosting",P["purple"]),("probability_xgboost","XGBoost",P["red"])]:
    ax.plot(x, sample[c], lw=1.4, alpha=.8, label=label, color=color)
ax.plot(x, sample["model_probability_mean"], lw=3, color=P["green"], label="Ensemble mean")
ax.fill_between(x, sample["model_probability_mean"]-sample["model_probability_std"], sample["model_probability_mean"]+sample["model_probability_std"], color=P["green"], alpha=.16, label="±1 model SD")
ax.set(xlabel="Locations ordered by ensemble risk",ylabel="Calibrated probability",ylim=(0,1)); ax.legend(frameon=False,ncol=2)
save(fig,"10A_model_predictions_and_uncertainty.png","Figure 10A — Model predictions and ensemble uncertainty","LAB_CONFIRMED + MODEL_ESTIMATE | UK Environment Agency | locked test")

# B: probability calibration
prob_true, prob_pred = calibration_curve(df.y, df.p, n_bins=10, strategy="uniform")
fig, ax = plt.subplots(figsize=(6.2,5.4)); ax.plot([0,1],[0,1],"--",color=P["muted"],lw=1.5,label="Perfect calibration"); ax.plot(prob_pred,prob_true,"o-",color=P["green"],lw=2.5,ms=7,label="NADI probabilities"); ax.set(xlabel="Predicted probability",ylabel="Observed high-result frequency",xlim=(0,1),ylim=(0,1)); ax.legend(frameon=False,loc="upper left")
save(fig,"10B_probability_calibration.png","Figure 10B — Probability calibration","LAB_CONFIRMED + MODEL_ESTIMATE | UK Environment Agency | locked test")

# C: uncertainty propagation pathway
fig, ax = plt.subplots(figsize=(11,3.3)); ax.axis("off")
stages=[("Model\ndisagreement",P["blue"]),("Risk\ninterval",P["purple"]),("Plausible\nnetwork states",P["amber"]),("Affected-region\nscenarios",P["red"]),("Action\nregret",P["green"])]
for i,(label,color) in enumerate(stages):
    x=.08+i*.21; ax.text(x,.53,label,ha="center",va="center",fontsize=12,fontweight="bold",color="white",bbox={"boxstyle":"round,pad=.75","facecolor":color,"edgecolor":"white","linewidth":1.5})
    if i<len(stages)-1: ax.annotate("",xy=(x+.105,.53),xytext=(x+.085,.53),arrowprops={"arrowstyle":"->","lw":2,"color":P["ink"]})
ax.text(.5,.14,"Uncertainty is carried forward instead of being discarded after prediction.",ha="center",fontsize=12,color=P["ink"])
save(fig,"10C_uncertainty_propagation_pathway.png","Figure 10C — Decision-valid uncertainty propagation","CURRENT_CANONICAL | FRAMEWORK FORMULATION | conceptual mathematical pathway")

# D: SDAIF optimisation
fig, ax = plt.subplots(figsize=(10,4.8)); ax.axis("off")
ax.text(.5,.89,"Choose a limited action set that remains safest across plausible states",ha="center",fontsize=14,fontweight="bold",color=P["ink"])
nodes=[(.12,"Candidate\nlocations V",P["blue"]),(.36,"Testing\nbudget k",P["amber"]),(.60,"Plausible\nstates Θ",P["purple"]),(.84,"SDAIF\naction A*",P["green"])]
for x,label,color in nodes: ax.text(x,.54,label,ha="center",va="center",fontsize=12,fontweight="bold",color="white",bbox={"boxstyle":"round,pad=.65","facecolor":color,"edgecolor":"white","linewidth":1.5})
for x1,x2 in zip([.19,.43,.67],[.29,.53,.77]): ax.annotate("",xy=(x2,.54),xytext=(x1,.54),arrowprops={"arrowstyle":"->","lw":2,"color":P["ink"]})
ax.text(.5,.25,r"$A^*=\arg\min_{A\subseteq V,\;|A|\leq k}\;\max_{\theta\in\Theta}L(A,\theta)$",ha="center",fontsize=16,color=P["ink"])
ax.text(.5,.10,"Minimise worst-case consequence under the available testing budget",ha="center",fontsize=11,color=P["muted"])
save(fig,"10D_sdaif_fixed_budget_optimization.png","Figure 10D — SDAIF fixed-budget optimisation","CURRENT_CANONICAL | FRAMEWORK FORMULATION | equation is the decision rule")

# E: threshold trade-off
thresholds=np.linspace(.05,.95,19); f1=[]; sens=[]; spec=[]
for t in thresholds:
    pred=(df.p>=t).astype(int); tp=((pred==1)&(df.y==1)).sum(); tn=((pred==0)&(df.y==0)).sum(); fp=((pred==1)&(df.y==0)).sum(); fn=((pred==0)&(df.y==1)).sum(); f1.append(2*tp/(2*tp+fp+fn) if 2*tp+fp+fn else 0); sens.append(tp/(tp+fn) if tp+fn else 0); spec.append(tn/(tn+fp) if tn+fp else 0)
fig, ax=plt.subplots(figsize=(7.8,4.8)); ax.plot(thresholds,f1,lw=2.5,color=P["green"],label="F1"); ax.plot(thresholds,sens,lw=2,color=P["red"],label="Sensitivity"); ax.plot(thresholds,spec,lw=2,color=P["blue"],label="Specificity"); ax.set(xlabel="Decision threshold",ylabel="Metric value",ylim=(0,1)); ax.legend(frameon=False,ncol=3)
save(fig,"10E_decision_threshold_tradeoff.png","Figure 10E — Decision-threshold trade-off","LAB_CONFIRMED + MODEL_ESTIMATE | UK Environment Agency | locked test")
print(f"Generated {len(list(OUT.glob('*.png')))} standalone Slide 10 figures in {OUT}")
