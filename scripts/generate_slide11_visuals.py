from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'figures/nadi_slide11_outputs'; OUT.mkdir(parents=True,exist_ok=True)
AUTH=ROOT/'results/canonical/authentic/audit_20261120_07/authentic_locked_site_predictions_and_zones.csv'
df=pd.read_csv(AUTH); df['y']=df['high_500'].astype(int); df['p']=df['predicted_probability'].astype(float)
C={'green':'#178a52','darkgreen':'#004b36','red':'#c43c39','gold':'#d99b21','blue':'#2878b5','grey':'#667085','ink':'#17202a'}
plt.rcParams.update({'figure.dpi':150,'savefig.dpi':300,'font.size':10,'axes.titlesize':14,'axes.labelsize':10,'axes.spines.top':False,'axes.spines.right':False,'axes.grid':True,'grid.alpha':.2})
def footer(fig,text): fig.text(.06,.02,text,fontsize=7,color=C['grey']); fig.tight_layout(rect=(0,.06,1,.94))

# 1. FRaCTAL-style risk hotspot map, authentic model estimate.
q=df.p.quantile(.9); hot=df[df.p>=q]
fig,ax=plt.subplots(figsize=(8.2,6)); ax.scatter(df.easting_km,df.northing_km,c=df.p,cmap='YlOrRd',vmin=0,vmax=1,s=18,alpha=.5,edgecolors='none'); ax.scatter(hot.easting_km,hot.northing_km,s=62,facecolors='none',edgecolors=C['red'],linewidths=1.5,label='Estimated-risk top decile'); ax.set(xlabel='Easting (km, rounded)',ylabel='Northing (km, rounded)'); cb=fig.colorbar(ax.collections[0],ax=ax,label='Estimated high-result probability'); ax.legend(frameon=False,loc='best'); ax.set_title('Figure 11A. Estimated risk hotspots',loc='left',fontweight='bold'); footer(fig,'MODEL_ESTIMATE | UK Environment Agency | LOCKED TEST | rounded coordinates; not direct contamination detection'); fig.savefig(OUT/'11A_estimated_risk_hotspots.png',bbox_inches='tight',facecolor='white'); plt.close(fig)

# 2. Estimated versus confirmed endpoint map.
fig,ax=plt.subplots(figsize=(8.2,6));
cases=[((df.p>=q)&(df.y==1),C['green'],'Estimated high-risk + confirmed high'),((df.p>=q)&(df.y==0),C['red'],'Estimated high-risk + not high'),((df.p<q)&(df.y==1),C['gold'],'Not high-risk + confirmed high'),((df.p<q)&(df.y==0),C['blue'],'Not high-risk + not high')]
for mask,color,label in cases: ax.scatter(df.loc[mask,'easting_km'],df.loc[mask,'northing_km'],s=24,c=color,alpha=.75,label=label)
ax.set(xlabel='Easting (km, rounded)',ylabel='Northing (km, rounded)'); ax.legend(frameon=False,fontsize=8,loc='best'); ax.set_title('Figure 11B. Estimated hotspots versus laboratory endpoints',loc='left',fontweight='bold'); footer(fig,'LAB_CONFIRMED + MODEL_ESTIMATE | UK Environment Agency | LOCKED TEST | comparison, not direct detection'); fig.savefig(OUT/'11B_estimated_vs_confirmed_hotspots.png',bbox_inches='tight',facecolor='white'); plt.close(fig)

# 3. Ranked hotspot strip for an authority.
top=df.sort_values('p',ascending=False).head(12).copy().iloc[::-1]
fig,ax=plt.subplots(figsize=(9,6)); ax.barh(np.arange(len(top)),top.p,color=[C['red'] if x>=top.p.quantile(.75) else C['gold'] for x in top.p]); ax.set_yticks(np.arange(len(top)),[str(x)[:42] for x in top.site_label]); ax.set_xlim(0,1); ax.set_xlabel('Estimated probability of high laboratory endpoint'); ax.set_title('Figure 11C. First locations for confirmatory testing',loc='left',fontweight='bold');
for i,v in enumerate(top.p): ax.text(v+.015,i,f'{v:.2f}',va='center',fontsize=8)
footer(fig,'MODEL_ESTIMATE | UK Environment Agency | LOCKED TEST | ordered risk estimate, not confirmed contamination'); fig.savefig(OUT/'11C_ranked_testing_hotspots.png',bbox_inches='tight',facecolor='white'); plt.close(fig)

# 4. Real network topology visual, conditional simulation track.
try:
    import wntr
    inp=ROOT/'data/external/ltown/L-TOWN.inp'; wn=wntr.network.WaterNetworkModel(str(inp)); pos={n:(wn.get_node(n).coordinates[0],wn.get_node(n).coordinates[1]) for n in wn.node_name_list if wn.get_node(n).coordinates is not None};
    fig,ax=plt.subplots(figsize=(9,6));
    for link in wn.link_name_list:
        l=wn.get_link(link); a=pos.get(l.start_node_name); b=pos.get(l.end_node_name)
        if a and b: ax.plot([a[0],b[0]],[a[1],b[1]],color='#B7C9C2',lw=.35,alpha=.65,zorder=1)
    nodes=list(pos); degree={n:0 for n in nodes}
    for link in wn.link_name_list:
        l=wn.get_link(link); degree[l.start_node_name]=degree.get(l.start_node_name,0)+1; degree[l.end_node_name]=degree.get(l.end_node_name,0)+1
    selected=sorted(nodes,key=lambda n:(degree.get(n,0),n),reverse=True)[:3]
    ax.scatter([pos[n][0] for n in nodes],[pos[n][1] for n in nodes],s=5,c=C['blue'],alpha=.55,zorder=2)
    ax.scatter([pos[n][0] for n in selected],[pos[n][1] for n in selected],s=80,c=C['red'],edgecolors='white',linewidths=1.2,zorder=3,label='Illustrative scenario nodes')
    ax.set_aspect('equal'); ax.set_axis_off(); ax.legend(frameon=False,loc='best'); ax.set_title('Figure 11D. Network topology for conditional source-tracing scenarios',loc='left',fontweight='bold'); footer(fig,'SIMULATED | L-TOWN EPANET network | conditional topology illustration; not biological field validation'); fig.savefig(OUT/'11D_network_topology_conditional_scenario.png',bbox_inches='tight',facecolor='white'); plt.close(fig)
except Exception as exc:
    print('Network figure skipped:',exc)
print('Generated',len(list(OUT.glob('*.png'))),'Slide 11 visuals in',OUT)

# 5. Code-derived dashboard inspired by the reference layout.
# Every point is read from the locked authentic table; rounded coordinates are used.
fig, axes = plt.subplots(1, 4, figsize=(15, 4.2), gridspec_kw={'width_ratios':[1.15,1.15,1.15,.8]})
panels=[('All locked observations',df,'p','YlGnBu'),('Estimated top-decile risk',df[df.p>=df.p.quantile(.9)],'p','YlOrRd'),('Confirmed high endpoint',df[df.y==1],'y','Reds')]
for ax,(title,sub,col,cmap) in zip(axes[:3],panels):
    if col=='p':
        sc=ax.scatter(sub.easting_km,sub.northing_km,c=sub[col],cmap=cmap,vmin=0,vmax=1,s=12,alpha=.72,edgecolors='none')
    else:
        sc=ax.scatter(sub.easting_km,sub.northing_km,c=np.ones(len(sub)),cmap=cmap,vmin=0,vmax=1,s=12,alpha=.72,edgecolors='none')
    ax.set_title(title,fontsize=10,fontweight='bold'); ax.set_xlabel('Easting (km, rounded)'); ax.set_ylabel('Northing (km, rounded)'); ax.grid(alpha=.18)
    if col=='p': fig.colorbar(sc,ax=ax,fraction=.046,pad=.04,label='Estimated risk')
    ax.text(.02,.02,'AUTHENTIC / MODEL_ESTIMATE' if col=='p' else 'LAB_CONFIRMED',transform=ax.transAxes,fontsize=6,color=C['grey'],bbox={'facecolor':'white','alpha':.75,'edgecolor':'none'})
cats=pd.cut(df.p,bins=[-1,.25,.5,.75,1.0],labels=['Low','Moderate','Elevated','High']); counts=cats.value_counts().reindex(['Low','Moderate','Elevated','High']).fillna(0)
axes[3].pie(counts.values,labels=counts.index,autopct=lambda x:f'{x:.1f}%',startangle=90,colors=['#18a558','#f2c94c','#e67e22','#c43c39'],wedgeprops={'width':.42,'edgecolor':'white'},textprops={'fontsize':8}); axes[3].set_title('Estimated risk distribution',fontsize=10,fontweight='bold'); axes[3].text(.5,-.12,'MODEL_ESTIMATE\nlocked test',ha='center',transform=axes[3].transAxes,fontsize=7,color=C['grey'])
fig.suptitle('Figure 11E. NADI authentic risk dashboard',x=.04,ha='left',fontsize=15,fontweight='bold',color=C['ink']); fig.text(.04,.02,'Derived directly from the locked UK Environment Agency prediction table | rounded coordinates | risk estimates are not direct contamination detection',fontsize=7,color=C['grey']); fig.tight_layout(rect=(0,.06,1,.91)); fig.savefig(OUT/'11E_authentic_risk_dashboard.png',bbox_inches='tight',facecolor='white',dpi=300); plt.close(fig)
print('Generated code-derived dashboard:',OUT/'11E_authentic_risk_dashboard.png')

# 6–9. Individual panels from the dashboard, each generated independently.
def standalone(fig, path, title, footer):
    fig.suptitle(title,x=.08,ha='left',fontsize=15,fontweight='bold',color=C['ink'])
    fig.text(.08,.025,footer,fontsize=7,color=C['grey'])
    fig.tight_layout(rect=(0,.06,1,.93)); fig.savefig(OUT/path,bbox_inches='tight',facecolor='white',dpi=300); plt.close(fig)

fig,ax=plt.subplots(figsize=(7.2,5.6)); sc=ax.scatter(df.easting_km,df.northing_km,c=df.p,cmap='YlGnBu',vmin=0,vmax=1,s=18,alpha=.75,edgecolors='none'); ax.set(xlabel='Easting (km, rounded)',ylabel='Northing (km, rounded)'); fig.colorbar(sc,ax=ax,label='Estimated high-result probability'); standalone(fig,'11F_all_locked_observations.png','Figure 11F. All locked observations','AUTHENTIC_OBSERVED + MODEL_ESTIMATE | UK Environment Agency | locked test')

fig,ax=plt.subplots(figsize=(7.2,5.6)); hot=df[df.p>=df.p.quantile(.9)]; sc=ax.scatter(hot.easting_km,hot.northing_km,c=hot.p,cmap='YlOrRd',vmin=0,vmax=1,s=34,alpha=.85,edgecolors='white',linewidths=.3); ax.set(xlabel='Easting (km, rounded)',ylabel='Northing (km, rounded)'); fig.colorbar(sc,ax=ax,label='Estimated high-result probability'); standalone(fig,'11G_estimated_top_decile_hotspots.png','Figure 11G. Estimated top-decile risk hotspots','MODEL_ESTIMATE | UK Environment Agency | locked test | not direct biological detection')

fig,ax=plt.subplots(figsize=(7.2,5.6)); high=df[df.y==1]; ax.scatter(high.easting_km,high.northing_km,c=C['red'],s=30,alpha=.78,edgecolors='white',linewidths=.3); ax.set(xlabel='Easting (km, rounded)',ylabel='Northing (km, rounded)'); standalone(fig,'11H_confirmed_high_endpoints.png','Figure 11H. Laboratory-confirmed high endpoints','LAB_CONFIRMED | UK Environment Agency | locked test | rounded coordinates')

cats=pd.cut(df.p,bins=[-1,.25,.5,.75,1.0],labels=['Low','Moderate','Elevated','High']); counts=cats.value_counts().reindex(['Low','Moderate','Elevated','High']).fillna(0)
fig,ax=plt.subplots(figsize=(6.4,5.2)); ax.pie(counts.values,labels=counts.index,autopct=lambda x:f'{x:.1f}%',startangle=90,colors=['#18a558','#f2c94c','#e67e22','#c43c39'],wedgeprops={'width':.42,'edgecolor':'white'},textprops={'fontsize':10}); standalone(fig,'11I_risk_distribution_donut.png','Figure 11I. Estimated risk distribution','MODEL_ESTIMATE | UK Environment Agency | locked test')
print('Generated individual dashboard panels 11F–11I')

# 10. Extraordinary but evidence-correct priority-lift figure.
# Shows how quickly confirmed high endpoints accumulate down NADI's locked risk ranking.
ordered=df.sort_values('p',ascending=False).reset_index(drop=True)
k=np.arange(1,len(ordered)+1); cumulative=ordered.y.cumsum(); capture=cumulative/cumulative.iloc[-1]; prevalence=df.y.mean(); expected=k*prevalence/cumulative.iloc[-1]
fig,ax=plt.subplots(figsize=(8.6,5.2)); ax.plot(k,capture,color=C['green'],lw=3,label='NADI risk ordering'); ax.plot(k,expected,color=C['grey'],ls='--',lw=2,label='Background-prevalence expectation');
for kk in [3,10,25,50,100]:
    if kk<=len(ordered): ax.scatter([kk],[capture.iloc[kk-1]],s=45,color=C['red'],zorder=4); ax.annotate(f'top {kk}',(kk,capture.iloc[kk-1]),xytext=(6,6),textcoords='offset points',fontsize=8,color=C['red'])
ax.set(xlabel='Number of confirmatory tests in NADI rank order',ylabel='Fraction of locked high endpoints captured',ylim=(0,1)); ax.legend(frameon=False,loc='lower right'); ax.set_title('Figure 11J. Priority lift under a fixed testing sequence',loc='left',fontweight='bold'); footer(fig,'LAB_CONFIRMED + MODEL_ESTIMATE | UK Environment Agency | LOCKED TEST | retrospective ranking; not prospective deployment'); fig.savefig(OUT/'11J_priority_lift_curve.png',bbox_inches='tight',facecolor='white',dpi=300); plt.close(fig)
print('Generated extraordinary priority-lift figure:',OUT/'11J_priority_lift_curve.png')
