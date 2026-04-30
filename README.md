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

Requires Python 3.10+. **One** dependency: `duckdb` (for the HTML/SVG flow). The CLI-only flow (`decide.py`) is stdlib-only.

```bash
git clone https://github.com/osamumiyashita/gc2w-mvc-sg100y-decision.git
cd gc2w-mvc-sg100y-decision
pip install -r requirements.txt
```

## Three usage flows

### A. HTML / SVG flow — serverless I/O app (`decide_io.py`)

**Three languages only**: Python, JS, DuckDB. **No HTTP server**, no daemon — pure one-shot Python with a file-watch.

```
HTML form  -->  JSON download  -->  inbox/  -->  Python  -->  DuckDB  -->  SVG charts  -->  output HTML pop-up
```

```bash
# default: open form, then watch inbox/ until JSON arrives, then auto-process
python decide_io.py
# (Windows: just double-click run.bat)

# only open form
python decide_io.py form

# directly compute from a JSON file
python decide_io.py compute path/to/input.json
```

The output HTML contains: GO/HOLD/NO-GO verdict, plain-language summary, three SVG charts (MVC bar, SG100Y curve, GCC 9-box), full expert table, and the **last 10 decisions from DuckDB** (`data/decisions.duckdb`).

### B. CLI-only flow (`decide.py`) — no I/O, no DB

```bash
python decide.py --mode 101 --input examples/sample_decision.json
python decide.py --mode expert --input examples/sample_decision.json
python decide.py --mode expert \
  --ic 1000 --roic-before 0.08 --roic-after 0.12 \
  --wacc 0.07 --growth 0.05 --connection 0.6 --confidence 0.7 \
  --label "Acquire competitor X"
```

### C. Library flow — import the pure functions

```python
from lib.gc2w import GC2W, composite_score, nine_box_cell
from lib.mvc import MVCInput, monthly_value_created
from lib.sg100y import sg100y_npv
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

| Flow | Format |
|------|--------|
| HTML/SVG (`decide_io.py`) | Output HTML pop-up: verdict badge + plain summary + 3 SVG charts + expert table + DuckDB history |
| CLI 101 (`decide.py --mode 101`) | 5-line natural-language verdict + GO/HOLD/NO-GO |
| CLI expert (`decide.py --mode expert`) | Full table: GC²W vector, ΔMVC/month, SG100Y NPV before/after, ΔSG100Y, 9-box position, WACC ±100bp sensitivity |

## Testing

```bash
python -m unittest discover tests
```

## License

MIT
