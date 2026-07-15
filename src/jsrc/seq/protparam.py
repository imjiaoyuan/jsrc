from __future__ import annotations

import json
import logging
from argparse import Namespace
from typing import Any

from Bio.SeqUtils.ProtParam import ProteinAnalysis

from jsrc.core import load_fasta

logger = logging.getLogger(__name__)

_AA_VOLUMES: dict[str, float] = {
    "A": 1.0,
    "R": 6.13,
    "N": 2.95,
    "D": 2.78,
    "C": 2.43,
    "Q": 3.95,
    "E": 3.78,
    "G": 0.0,
    "H": 4.66,
    "I": 4.0,
    "L": 4.0,
    "K": 4.77,
    "M": 4.43,
    "F": 5.89,
    "P": 2.72,
    "S": 1.6,
    "T": 2.6,
    "W": 8.08,
    "Y": 6.47,
    "V": 3.0,
}


def _aliphatic_index(seq: str) -> float:
    """Aliphatic index per Ikai (1980)."""
    aa = seq.upper()
    total = len(aa)
    if total == 0:
        return 0.0
    a = aa.count("A")
    v = aa.count("V")
    ile = aa.count("I")
    leu = aa.count("L")
    return (a + 2.9 * v + 3.9 * (ile + leu)) / total * 100.0


def _safe_protparam(func, default, label, rec_id):
    try:
        return func()
    except (ValueError, KeyError, IndexError, ZeroDivisionError, TypeError) as exc:
        logger.warning("ProteinAnalysis.%s failed for %s: %s", label, rec_id, exc)
        return default


def cmd(args: Namespace) -> None:
    records = load_fasta(args.fa)

    results = []
    for rec in records:
        seq = str(rec.seq).upper().replace("U", "T")
        clean = "".join(c for c in seq if c.isalpha())
        if not clean:
            continue
        pa = ProteinAnalysis(clean)
        mw = _safe_protparam(pa.molecular_weight, 0.0, "molecular_weight", rec.id)
        pi = _safe_protparam(pa.isoelectric_point, 0.0, "isoelectric_point", rec.id)
        ec = _safe_protparam(
            pa.molar_extinction_coefficient,
            (0, 0),
            "molar_extinction_coefficient",
            rec.id,
        )
        ii = _safe_protparam(pa.instability_index, 0.0, "instability_index", rec.id)
        ai = _safe_protparam(
            lambda c=clean: _aliphatic_index(c), 0.0, "aliphatic_index", rec.id
        )
        gv = _safe_protparam(pa.gravy, 0.0, "gravy", rec.id)
        ar = _safe_protparam(pa.aromaticity, 0.0, "aromaticity", rec.id)
        ss = _safe_protparam(
            pa.secondary_structure_fraction,
            (0.0, 0.0, 0.0),
            "secondary_structure_fraction",
            rec.id,
        )
        charge = pa.charge_at_pH(args.ph) if args.ph is not None else None

        entry: dict[str, Any] = {
            "id": rec.id,
            "length": len(clean),
            "molecular_weight": round(mw, 2),
            "isoelectric_point": round(pi, 2),
            "extinction_coefficient_reduced": round(ec[0], 2),
            "extinction_coefficient_oxidized": round(ec[1], 2),
            "instability_index": round(ii, 2),
            "aliphatic_index": round(ai, 2),
            "gravy": round(gv, 4),
            "aromaticity": round(ar, 4),
            "helix_fraction": round(ss[0], 4),
            "turn_fraction": round(ss[1], 4),
            "sheet_fraction": round(ss[2], 4),
        }
        if charge is not None:
            entry["charge_at_pH"] = round(charge, 4)
        results.append(entry)

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
        return
    header = (
        "id\tlength\tmw\tpI\tEC_red\tEC_ox\tinstability\taliphatic\t"
        "gravy\taromaticity\thelix\tturn\tsheet"
    )
    if args.ph is not None:
        header += "\tcharge"
    print(header)
    for r in results:
        row = (
            f"{r['id']}\t{r['length']}\t{r['molecular_weight']}\t"
            f"{r['isoelectric_point']}\t{r['extinction_coefficient_reduced']}\t"
            f"{r['extinction_coefficient_oxidized']}\t{r['instability_index']}\t"
            f"{r['aliphatic_index']}\t{r['gravy']}\t{r['aromaticity']}\t"
            f"{r['helix_fraction']}\t{r['turn_fraction']}\t{r['sheet_fraction']}"
        )
        if args.ph is not None:
            row += f"\t{r.get('charge_at_pH', '')}"
        print(row)
    logger.info("Analyzed %d protein sequences", len(results))


def register(subparsers: Any) -> None:
    p = subparsers.add_parser("protparam", help="Protein physicochemical properties")
    p.add_argument("-fa", required=True, help="Protein FASTA file")
    p.add_argument("--json", action="store_true", help="Print JSON output")
    p.add_argument("--ph", type=float, default=None, help="pH for net charge")
    p.set_defaults(func=cmd)
