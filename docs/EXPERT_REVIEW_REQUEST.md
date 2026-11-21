# Independent mathematical and water-quality review request

## Email draft

**Subject:** Short technical review request: authentic E. coli testing-prioritisation project

Dear Dr. `[Name]`,

I am a high-school student developing NADI, an applied-mathematical system that prioritises limited confirmatory E. coli testing. It uses calibrated predictions from authentic historical laboratory observations and a mixed-integer decision rule that balances posterior average regret with worst-case regret across model families.

The current locked evaluation contains 13,405 authentic site-day records from 920 Environment Agency monitoring sites. With a three-test budget across 41 untouched multi-site rounds, NADI found 114 confirmed high results, compared with 80 for deterministic random selection and 84 for routine sampling-frequency priority. It tied the strongest single-model and adaptive-Bayesian comparators. Transfer performance was weaker on sites absent from training, so local calibration remains a stated requirement.

Would you be willing to review the attached two-page method summary and answer the questions below? I am seeking criticism, not endorsement. I will document your exact contribution and will not use your name or institution publicly without permission.

1. Does the regret formulation match the stated limited-testing decision?
2. Does the mixed-integer programme correctly represent the objective?
3. Are the chronological split and same-date leakage controls adequate?
4. Are random, routine, single-model, ensemble, Bayesian, and robust policies fair comparators?
5. Which claim should be narrowed or tested next?

The project does not claim direct sensor detection, drinking-water-pipeline localisation, Delhi-NCR validation, or avoided illness.

Thank you for considering a brief review.

Sincerely,

`[Student name, school, email]`

## Attachments to send

- `docs/AUTHENTIC_XYLEM_METHOD_AND_RESULTS.md`
- `docs/MATHEMATICAL_ASSURANCE_CASE.md`
- `docs/XYLEM_APPLICATION_DRAFT.md`
- `results/authentic_locked/authentic_experiment_report.json`
- `results/authentic_locked/authentic_test_summary.csv`
- repository or reproducibility archive link

## Review record

Record the date, reviewer name, area of expertise, version reviewed, comments received, changes made, and permission to cite the reviewer. A review does not convert retrospective evidence into field validation.
