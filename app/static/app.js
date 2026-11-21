const pct=x=>`${(100*x).toFixed(1)}%`;
async function draw(data){
 const risk=data.risk_after_transfer_gate||data.forecast;
 document.querySelector('#origin').textContent=`${data.event_origin||'MODEL'} · ${data.input_reference||data.card?.event_id||''}`;
 document.querySelector('#risk').textContent=pct(risk.probability);
 document.querySelector('#interval-fill').style.width=pct(risk.upper);
 document.querySelector('#interval-label').textContent=`Uncertainty interval ${pct(risk.lower)}–${pct(risk.upper)} · support ${pct(risk.support_score)}`;
 const card=data.decision_card||data.card;
 document.querySelector('#action').textContent=card.abstained?'ABSTAIN':`Test ${card.selected_tests.join(' → ')||'no additional node'}`;
 document.querySelector('#certificate').textContent=card.certified?'ε-regret certificate: YES':'ε-regret certificate: NO';
 document.querySelector('#regret').textContent=card.worst_case_regret==null?'regret unavailable':`worst-case regret ${card.worst_case_regret.toFixed(3)}`;
 document.querySelector('#abstention').textContent=card.abstention_reason||`Dominant uncertainty: ${card.dominant_uncertainty}`;
 document.querySelector('#nodes').innerHTML=(data.affected_region||[]).map(n=>`<div class="node" style="border-color:hsl(${170+120*n.probability} 70% 42%)"><strong>${n.node_id}</strong><small>${pct(n.probability)} reach</small><small>${n.earliest_hours==null?'not reached':n.earliest_hours+'–'+n.latest_hours+' h'}</small></div>`).join('');
 document.querySelector('#actions').innerHTML=(data.protective_actions||[]).slice(0,5).map(a=>`<div class="node"><strong>${a.name.replaceAll('_',' ')}</strong><small>score ${a.decision_score.toFixed(3)}</small><small>coverage ${pct(a.coverage)} · delay ${a.delay_hours}h</small></div>`).join('')||'<div class="node"><small>No action ranking issued.</small></div>';
 document.querySelector('#steps').innerHTML=(data.adaptive_steps||[]).map(s=>`<li><strong>${s.selected_test}</strong> selected, then result revealed: ${s.result_revealed_after_selection?'affected':'not affected'} <small>(${s.compatible_scenarios_before} scenarios before)</small></li>`).join('')||'<li>No sequential decision issued.</li>';
 document.querySelector('#labels').innerHTML=(card.evidence_labels||[]).map(x=>`<span>${x}</span>`).join('');
 const ih=data.intrusion_hazard; document.querySelector('#intrusion').textContent=ih?`Intrusion-context evidence: ${pct(ih.score)} · support ${pct(ih.support)} · ${ih.abstain?'insufficient context — abstained':'context available'}`:'';
 const fe=data.fused_evidence; document.querySelector('#fusion').textContent=fe?`Fused evidence interval: ${pct(fe.lower)}–${pct(fe.upper)} · dominant uncertainty: ${fe.dominant_uncertainty}`:'';
 document.querySelector('#claim').textContent=card.claim_boundary;
 const ranked=(data.affected_region||[]).slice().sort((a,b)=>b.probability-a.probability);
 const status=card.abstained?'NO ACTION CERTIFICATE — MORE EVIDENCE REQUIRED':(ranked.length?'SUSPECTED EVENT — CONFIRMATORY TESTING REQUIRED':'NO AFFECTED REGION IDENTIFIED');
 document.querySelector('#outcome-status').textContent=status;
 document.querySelector('#outcome-zone').textContent=ranked.length?`${ranked.slice(0,5).map(n=>`${n.node_id} (${pct(n.probability)})`).join(', ')} · ${ranked[0].kind||'MODELLED'} region`:'No region ranked';
 document.querySelector('#outcome-tests').textContent=card.selected_tests?.length?card.selected_tests.join(' → '):'No test list issued';
 const firstAction=(data.protective_actions||[])[0];
 document.querySelector('#outcome-action').textContent=firstAction?firstAction.operational_note:'Operator review required before action';
 document.querySelector('#outcome-note').textContent=`This output is a decision aid: it flags a suspected event, marks a probable region and prioritises laboratory confirmation. It does not directly detect E. coli or authorize automatic utility action. Origin: ${data.event_origin||'MODEL'}.`;
}
async function benchmark(){const b=await fetch('/api/benchmark').then(r=>r.json());document.querySelector('#gate').textContent=`${b.gate||'NOT RUN'} · ${b.superiority_supported?'superior':'no superiority claim'}`;document.querySelector('#comparison').textContent=b.adaptive_mean==null?'Benchmark unavailable':`SDAIF ${pct(b.adaptive_mean)} vs ${b.strongest_fair_baseline} ${pct(b.strongest_baseline_mean)}; paired difference ${pct(b.comparison.mean_difference)} [${pct(b.comparison.paired_bootstrap_95pct[0])}, ${pct(b.comparison.paired_bootstrap_95pct[1])}]`;}
async function authentic(){
 const a=await fetch('/api/authentic').then(r=>r.json());
 const surface=a.surface_water_ecoli?.models?.hist_gradient_boosting;
 const panel=a.physchem_panel?.models?.laboratory_detection?.physicochemical_only?.xgb_prior_art_reproduction;
 const high=a.physchem_panel?.models?.high_risk_500_cfu_per_100ml?.physicochemical_only?.xgb_prior_art_reproduction;
 const rows=[];
 if(surface) rows.push(`<div class="node"><strong>EA laboratory E. coli · 14,069 samples</strong><small>F1 ${pct(surface.f1)} · recall ${pct(surface.recall)} · ROC-AUC ${pct(surface.roc_auc)}</small><small>authentic surface-water temporal holdout</small></div>`);
 if(panel) rows.push(`<div class="node"><strong>Sample-matched pH/temperature/conductivity</strong><small>F1 ${pct(panel.f1)} · recall ${pct(panel.recall)} · ROC-AUC ${pct(panel.roc_auc)}</small><small>648 authentic samples; XGBoost prior-art track</small></div>`);
 if(high) rows.push(`<div class="node"><strong>500-CFU risk endpoint</strong><small>F1 ${pct(high.f1)} · recall ${pct(high.recall)} · ROC-AUC ${pct(high.roc_auc)}</small><small>bathing-water convention, not drinking standard</small></div>`);
 document.querySelector('#authentic-metrics').innerHTML=rows.join('')||'<div class="node"><small>Authentic metrics unavailable.</small></div>';
 document.querySelector('#authentic-boundary').textContent=a.claim_boundary||'';
}
async function run(domain='SIMULATED_NETWORK_EVENT'){document.querySelector('#run').disabled=true;const body={seed:+document.querySelector('#seed').value,budget:+document.querySelector('#budget').value,domain};const data=await fetch('/api/demo',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify(body)}).then(r=>r.json());await draw(data);document.querySelector('#run').disabled=false;}
document.querySelector('#run').onclick=()=>run();document.querySelector('#unsupported').onclick=()=>run('DELHI_DRINKING_NETWORK');fetch('/api/latest').then(r=>r.json()).then(draw);benchmark();authentic();

