# Two-minute Xylem pitch

When faecal contamination may be moving through a water network, authorities
cannot immediately test every outlet. The dangerous delay is not only finding
that risk exists; it is deciding where a limited test team should go first.

NADI is a software-first mathematical decision system for that bottleneck. It
combines E. coli-referenced evidence with uncertain water movement. Instead of
giving one confident-looking map, it asks: across every risk and network
scenario still compatible with the evidence, which next test protects the
decision from the worst avoidable mistake?

First, a calibrated model produces a current or next-day risk interval. Second,
EPANET/WNTR simulations estimate which nodes could be reached and when under
different sources, demands, tank levels and pipe states. Third, SDAIF uses
minimax regret to select a test. After that result arrives, it removes
incompatible scenarios and chooses again. It also reports its worst-case
regret, the scenario that challenges the decision, and when evidence is too
weak to act—then it abstains.

We tested the full pipeline on 120 locked simulated network events. At a budget
of three tests, SDAIF matched the strongest fair adaptive Bayesian comparator
at 68.6% affected-node coverage, while adding a decision certificate and
adversarial explanation. It substantially exceeded random testing in this
benchmark. We do not claim direct E. coli detection or a Delhi digital twin:
laboratory confirmation and local network calibration remain necessary.

NADI's value is simple: it turns limited evidence and limited testing capacity
into a transparent, mathematically defensible first-response list.
