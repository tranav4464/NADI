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
 document.querySelector('#steps').innerHTML=(data.adaptive_steps||[]).map(s=>`<li><strong>${s.selected_test}</strong> selected, then result revealed: ${s.result_revealed_after_selection?'affected':'not affected'} <small>(${s.compatible_scenarios_before} scenarios before)</small></li>`).join('')||'<li>No sequential decision issued.</li>';
 document.querySelector('#labels').innerHTML=(card.evidence_labels||[]).map(x=>`<span>${x}</span>`).join('');
 document.querySelector('#claim').textContent=card.claim_boundary;
}
async function benchmark(){const b=await fetch('/api/benchmark').then(r=>r.json());document.querySelector('#gate').textContent=`${b.gate||'NOT RUN'} · ${b.superiority_supported?'superior':'no superiority claim'}`;document.querySelector('#comparison').textContent=b.adaptive_mean==null?'Benchmark unavailable':`SDAIF ${pct(b.adaptive_mean)} vs ${b.strongest_fair_baseline} ${pct(b.strongest_baseline_mean)}; paired difference ${pct(b.comparison.mean_difference)} [${pct(b.comparison.paired_bootstrap_95pct[0])}, ${pct(b.comparison.paired_bootstrap_95pct[1])}]`;}
async function run(domain='SIMULATED_NETWORK_EVENT'){document.querySelector('#run').disabled=true;const body={seed:+document.querySelector('#seed').value,budget:+document.querySelector('#budget').value,domain};const data=await fetch('/api/demo',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify(body)}).then(r=>r.json());await draw(data);document.querySelector('#run').disabled=false;}
document.querySelector('#run').onclick=()=>run();document.querySelector('#unsupported').onclick=()=>run('DELHI_DRINKING_NETWORK');fetch('/api/latest').then(r=>r.json()).then(draw);benchmark();

