import json
import math
from argparse import Namespace
from typing import Any

from Bio import SeqIO

from jsrc.core import DataFormatError

_NN_DH: dict[str, float] = {
    "AA": -7.9,
    "AT": -7.2,
    "TA": -7.2,
    "CA": -8.5,
    "GT": -8.4,
    "CT": -7.8,
    "GA": -8.2,
    "CG": -10.6,
    "GC": -9.8,
    "GG": -8.0,
    "AC": -7.8,
    "TG": -8.5,
    "AG": -7.8,
    "TC": -8.2,
    "TT": -7.9,
    "CC": -8.0,
}
_NN_DS: dict[str, float] = {
    "AA": -22.2,
    "AT": -20.4,
    "TA": -21.3,
    "CA": -22.7,
    "GT": -22.4,
    "CT": -21.0,
    "GA": -22.2,
    "CG": -27.2,
    "GC": -24.4,
    "GG": -19.9,
    "AC": -21.0,
    "TG": -22.7,
    "AG": -21.0,
    "TC": -22.2,
    "TT": -22.2,
    "CC": -19.9,
}
_R = 1.987


def _tm_wallace(seq: str) -> float:
    s = seq.upper().replace("U", "T")
    a = s.count("A")
    t = s.count("T")
    g = s.count("G")
    c = s.count("C")
    if len(s) < 14:
        return 2 * (a + t) + 4 * (g + c)
    return 64.9 + 41 * (g + c - 16.4) / (a + t + g + c)


def _tm_nearest_neighbor(seq: str, conc_nm: float = 250.0) -> float:
    s = seq.upper().replace("U", "T")
    dh = sum(_NN_DH.get(s[i : i + 2], -8.0) for i in range(len(s) - 1))
    ds = sum(_NN_DS.get(s[i : i + 2], -21.0) for i in range(len(s) - 1))
    ds += -10.8
    dh *= 1000
    conc = conc_nm * 1e-9
    tm = dh / (ds + _R * math.log(conc / 4.0)) - 273.15
    return round(tm, 2)


def _has_hairpin(seq: str, min_stem: int = 3, loop: int = 4) -> bool:
    s = seq.upper().replace("U", "T")
    comp = {"A": "T", "T": "A", "G": "C", "C": "G"}
    n = len(s)
    for i in range(n - min_stem - loop - min_stem + 1):
        stem = s[i : i + min_stem]
        j = i + min_stem + loop
        if j + min_stem > n:
            break
        rc = "".join(comp.get(b, "N") for b in reversed(s[j : j + min_stem]))
        if stem == rc:
            return True
    return False


def _gc_clamp(seq: str, n: int = 3) -> bool:
    tail = seq.upper()[-n:]
    return tail[-1] in "GC" and tail.count("G") + tail.count("C") >= 1


def cmd(args: Namespace) -> None:
    records = list(SeqIO.parse(args.fa, "fasta"))
    if not records:
        raise DataFormatError("No sequences found in FASTA")
    results = []
    for rec in records:
        seq = str(rec.seq).upper().replace("U", "T")
        gc = (seq.count("G") + seq.count("C")) / len(seq) * 100 if seq else 0.0
        tm_w = _tm_wallace(seq)
        tm_nn = _tm_nearest_neighbor(seq, args.conc)
        results.append(
            {
                "id": rec.id,
                "length": len(seq),
                "gc_percent": round(gc, 2),
                "tm_wallace": tm_w,
                "tm_nearest_neighbor": tm_nn,
                "gc_clamp": _gc_clamp(seq),
                "hairpin_risk": _has_hairpin(seq),
            }
        )

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
        return
    print("id\tlength\tgc_percent\ttm_wallace\ttm_nn\tgc_clamp\thairpin_risk")
    for r in results:
        print(
            f"{r['id']}\t{r['length']}\t{r['gc_percent']}\t"
            f"{r['tm_wallace']}\t{r['tm_nearest_neighbor']}\t"
            f"{r['gc_clamp']}\t{r['hairpin_risk']}"
        )


def register(subparsers: Any) -> None:
    p = subparsers.add_parser("primer", help="Primer Tm, GC, hairpin analysis")
    p.add_argument("-fa", required=True, help="FASTA file of primer sequences")
    p.add_argument(
        "--conc",
        type=float,
        default=250.0,
        help="Primer concentration nM for nearest-neighbor Tm (default: 250)",
    )
    p.add_argument("--json", action="store_true", help="Print JSON")
    p.set_defaults(func=cmd)
