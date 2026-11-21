const pct = value => `${(100 * value).toFixed(1)}%`;
let currentData = null;
let outcomesRevealed = false;
function renderSites(){
  const data = currentData;
  document.querySelector('#site-table').innerHTML = `<table><thead><tr><th>Priority</th><th>Site</th><th>Model risk</th><th>Model disagreement</th><th>Monitoring zone</th><th>Authentic lab result</th></tr></thead><tbody>${data.sites.map(site => `<tr><td>${site.selected_by_sdaif ? data.selected_order.indexOf(site.site_id)+1 : '—'}</td><td>${site.site_label || site.site_id}</td><td>${pct(site.probability)}</td><td>±${pct(site.model_probability_std)}</td><td>${site.monitoring_zone}</td><td>${outcomesRevealed ? (site.laboratory_high_500 ? '≥500' : '<500') : 'HIDDEN'}</td></tr>`).join('')}</tbody></table>`;
  const width=900, height=360, pad=28;
  const xs=data.sites.map(site=>site.easting_km), ys=data.sites.map(site=>site.northing_km);
  const xmin=Math.min(...xs), xmax=Math.max(...xs), ymin=Math.min(...ys), ymax=Math.max(...ys);
  const sx=x=>pad+(x-xmin)/Math.max(xmax-xmin,1)*(width-2*pad);
  const sy=y=>height-pad-(y-ymin)/Math.max(ymax-ymin,1)*(height-2*pad);
  const marks=data.sites.map(site=>{const priority=site.selected_by_sdaif?data.selected_order.indexOf(site.site_id)+1:'';const fill=site.selected_by_sdaif?'#e52b24':`rgba(32,113,214,${Math.max(.2,site.probability)})`;return `<g><circle cx="${sx(site.easting_km)}" cy="${sy(site.northing_km)}" r="${site.selected_by_sdaif?10:6}" fill="${fill}" stroke="#fff" stroke-width="2"><title>${site.site_label}: risk ${pct(site.probability)}, disagreement ${pct(site.model_probability_std)}</title></circle><text x="${sx(site.easting_km)}" y="${sy(site.northing_km)+4}" text-anchor="middle" font-size="10" fill="#fff">${priority}</text></g>`}).join('');
  document.querySelector('#site-map').innerHTML=`<svg viewBox="0 0 ${width} ${height}" role="img"><rect width="${width}" height="${height}" rx="16" fill="#eef4fa"/>${marks}</svg><p class="boundary">Observed British National Grid coordinates. Red numbered sites are the frozen SDAIF order; this is a monitoring map, not a pipe network.</p>`;
}
async function loadRound(round){
  const suffix = round ? `?round=${encodeURIComponent(round)}` : '';
  const data = await fetch(`/api/authentic-xylem${suffix}`).then(response => response.json());
  currentData = data;
  outcomesRevealed = false;
  const chooser = document.querySelector('#round');
  if(!chooser.options.length){
    data.available_rounds.forEach(value => chooser.add(new Option(value, value)));
  }
  chooser.value = data.round;
  document.querySelector('#round-title').textContent = data.round;
  document.querySelector('#selected').textContent = data.selected_order.join(' → ') || 'No sites selected';
  const m = data.model_report;
  document.querySelector('#metrics').innerHTML = `<div class="metric"><strong>${m.f1.toFixed(3)}</strong><small>F1</small></div><p>ROC-AUC ${m.roc_auc.toFixed(3)} · PR-AUC ${m.pr_auc.toFixed(3)} · balanced accuracy ${m.balanced_accuracy.toFixed(3)}</p>`;
  renderSites();
  document.querySelector('#policies').innerHTML = data.policy_summary.map(row => `<div class="node"><strong>${row.policy.replaceAll('_',' ')}</strong><small>${row.total_positives_found} confirmed results found</small><small>mean ${row.mean_positives_found_at_budget.toFixed(2)} per round · missed-positive rate ${pct(row.missed_positive_round_rate)}</small></div>`).join('');
  document.querySelector('#replay').innerHTML = data.adaptive_replay.map(step => {
    const result = outcomesRevealed ? (step.authentic_lab_result_revealed_after_selection ? 'HISTORICAL HIGH E. COLI RESULT' : 'HISTORICAL LOWER RESULT') : 'HISTORICAL RESULT HIDDEN IN DISPLAY';
    return `<div class="node"><strong>Step ${step.step}: ${step.selected_site}</strong><small>predicted high-result probability ${pct(step.selected_site_predictive_positive_probability)} · model disagreement ${pct(Math.sqrt(step.selected_site_model_disagreement))}</small><small>evidence value ${step.selected_site_information_value.toFixed(4)} · worst-case regret ${step.pre_result_worst_case_regret.toFixed(3)}</small><small>${result}</small></div>`;
  }).join('');
  const auxiliary = await fetch('/api/authentic').then(response => response.json());
  const physical = auxiliary.texas_physical_pressure;
  document.querySelector('#physical-evidence').innerHTML = physical ? `<div class="node"><strong>Controlled physical pipe runs</strong><small>ROC-AUC ${physical.out_of_fold_metrics.roc_auc.toFixed(3)} · grouped whole-run holdout · ${physical.files} observed pressure recordings</small><small>Balanced accuracy ${physical.out_of_fold_metrics.balanced_accuracy.toFixed(3)}; always-leak baseline is retained because leak prevalence is high.</small><small>${physical.claim_boundary}</small></div>` : '<div class="node"><small>Physical-pipe evidence has not yet been generated.</small></div>';
  document.querySelector('#boundary').textContent = data.claim_boundary;
}
document.querySelector('#load').onclick = () => loadRound(document.querySelector('#round').value);
document.querySelector('#reveal').onclick = () => { outcomesRevealed = true; renderSites(); };
loadRound();
