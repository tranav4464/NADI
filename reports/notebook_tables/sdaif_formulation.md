| Concept         | Notation                   | Operational meaning                        |
|:----------------|:---------------------------|:-------------------------------------------|
| Candidate set   | V = {1, …, n}              | Locations eligible for a confirmatory test |
| Plan            | A ⊆ V                      | Ordered testing plan                       |
| Budget          | |A| ≤ k                    | Maximum available tests                    |
| Risk            | p_mi                       | Model m probability for candidate i        |
| Loss            | L_m(A)                     | Model-specific missed-risk / test loss     |
| Regret          | R_m(A)=L_m(A)-min_B L_m(B) | Loss relative to model-m optimal plan      |
| SDAIF objective | min_A max_m R_m(A)         | Conservative fixed-budget decision         |
