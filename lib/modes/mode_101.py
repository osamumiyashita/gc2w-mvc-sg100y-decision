"""101 mode — plain-language verdict for non-finance readers.

No jargon. No formulas. 5 lines + GO / NO-GO / HOLD.
"""
from ..gc2w import GC2W, composite_score, nine_box_cell
from ..mvc import MVCInput, mvc_delta
from ..sg100y import delta_sg100y


def render_101(
    label: str,
    gc2w: GC2W,
    before: MVCInput,
    after: MVCInput,
    horizon_months: int = 1200,
) -> str:
    d_mvc = mvc_delta(before, after)
    d_sg = delta_sg100y(before, after, horizon_months)
    score = composite_score(gc2w)
    _, _, cell_label = nine_box_cell(gc2w)

    if d_sg > 0 and score >= 1.0:
        verdict = "GO"
        gut = "この意思決定は持続的に価値を生みます。数字と戦略ポジションの両方が肯定しています。"
    elif d_sg > 0 and score < 1.0:
        verdict = "HOLD"
        gut = "数字は肯定的ですが、戦略ポジションが弱いです。前提を再確認してから実行してください。"
    elif d_sg <= 0 and score >= 1.0:
        verdict = "HOLD"
        gut = "戦略ポジションは強いですが、数字が価値創造を示していません。IC / ROIC の入力を見直してください。"
    else:
        verdict = "NO-GO"
        gut = "この意思決定は価値を破壊します。見送るか、再設計してから再評価してください。"

    money_per_month = f"{d_mvc:+,.1f}"
    money_100y = f"{d_sg:+,.1f}"

    return "\n".join([
        f"案件:     {label}",
        f"判定:     {verdict}",
        f"  -> 月次の価値変化:   {money_per_month}",
        f"  -> 100年累計の価値変化: {money_100y}",
        f"  -> 戦略ポジション:   {cell_label}",
        f"  -> ひとこと: {gut}",
    ])
