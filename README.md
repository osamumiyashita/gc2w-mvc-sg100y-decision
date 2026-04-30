# gc2w-mvc-sg100y-decision

GC²W × MVC × SG100Y decision-making CLI.

Two modes:
- **101 mode** — plain-language explanation for non-finance readers
- **Expert mode** — full mathematical breakdown (GC²W 4D vector, MVC monthly delta, SG100Y NPV, GCC 9-box positioning)

Serverless. Pure-function CLI. No HTTP listener. No DB daemon.

## Theoretical foundation

```
GC²W  = (Growth, Connection, Confidence, WACC)        # 4-dimensional decision space
MVC_t = IC × (ROIC_t - WACC) / 12                     # monthly value created
SG100Y= Σ_{t=1..1200} MVC_t / (1 + WACC/12)^t         # 100-year NPV (1200 months)
```

A decision is **value-creating** ⟺ ΔSG100Y > 0 after the decision.

## Install

Requires Python 3.10+. No external dependencies (stdlib only).

```bash
git clone https://github.com/osamumiyashita/gc2w-mvc-sg100y-decision.git
cd gc2w-mvc-sg100y-decision
python decide.py --help
```

## Usage

```bash
# 101 mode — plain language
python decide.py --mode 101 --input examples/sample_decision.json

# expert mode — full math
python decide.py --mode expert --input examples/sample_decision.json

# inline parameters
python decide.py --mode expert \
  --ic 1000 --roic-before 0.08 --roic-after 0.12 \
  --wacc 0.07 --growth 0.05 --connection 0.6 --confidence 0.7 \
  --label "Acquire competitor X"
```

## Input schema

```json
{
  "label": "Decision name",
  "ic": 1000,
  "roic_before": 0.08,
  "roic_after": 0.12,
  "wacc_before": 0.07,
  "wacc_after": 0.07,
  "growth": 0.05,
  "connection": 0.6,
  "confidence": 0.7,
  "horizon_months": 1200
}
```

All financial fields in the same currency unit (e.g. USD millions).
Rates as decimals: `0.08` = 8%.

## Output

| Mode | Format |
|------|--------|
| 101 | 5-line natural-language verdict + GO/NO-GO recommendation |
| expert | Full table: GC²W vector, ΔMVC/month, SG100Y NPV before/after, ΔSG100Y, 9-box position, sensitivity to WACC ±1pp |

## Testing

```bash
python -m unittest discover tests
```

## License

MIT
