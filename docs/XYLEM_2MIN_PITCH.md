# Two-minute Xylem pitch — authentic-evidence version

When contamination is invisible, authorities depend on laboratory testing. But they cannot collect and process every possible sample at the same time. The real decision is: **with only three tests available now, which locations should we check first?**

NADI is an applied-mathematical system for that decision. It learns how each location behaved in earlier laboratory tests, how its region behaved, and how risk changes with season and place. Three different calibrated models estimate the chance of a serious E. coli result. They do not always agree, and NADI does not hide that disagreement.

Our SDAIF mathematics converts those probabilities and disagreements into a testing list. A mixed-integer optimisation chooses the combination that balances good average performance with protection against the model that could make the list look worst. The most informative site in that list is tested first. After its real laboratory result arrives, NADI updates which model is credible and recalculates the remaining locations.

We tested this using 13,405 authentic Environment Agency records from 920 monitoring sites. Every prediction used only information available before that day's result. Training, calibration, model selection and the final test period were separated chronologically.

On the untouched final period, our selected model achieved F1 0.838, ROC-AUC 0.866 and PR-AUC 0.916. More importantly, across 41 real sampling rounds, with the same budget of three tests, NADI found 114 confirmed high-E.-coli results. Random testing found 80 and routine-frequency priority found 84. NADI did not miss any round that contained a positive site.

This is not a claim that ordinary sensors directly detect E. coli, and it is not a claimed municipal pipe deployment. It is a reproducible demonstration that authentic historical evidence plus transparent decision mathematics can direct a limited testing team toward more confirmed contamination. Our next step is prospective validation with a monitoring authority.
