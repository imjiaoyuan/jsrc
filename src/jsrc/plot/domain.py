import csv
import sys

from jsrc.plot.core import natural_sort_key, setup_matplotlib

plt = setup_matplotlib()


def cmd(args):
    with open(args.tsv, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f, delimiter="\t"))
    required = {"protein", "domain", "start", "end"}
    if not rows or not required.issubset(rows[0].keys()):
        print("Error: TSV must have columns protein,domain,start,end", file=sys.stderr)
        sys.exit(1)

    proteins = sorted({row["protein"] for row in rows}, key=natural_sort_key)
    fig, ax = plt.subplots(figsize=(12, max(6, len(proteins) * 0.5)))
    for i, prot in enumerate(proteins):
        y = len(proteins) - i - 1
        prot_rows = [r for r in rows if r["protein"] == prot]
        max_pos = max(float(r["end"]) for r in prot_rows)
        ax.plot([0, max_pos], [y, y], "k-", linewidth=2)
        for row in prot_rows:
            start, end = float(row["start"]), float(row["end"])
            ax.add_patch(
                plt.Rectangle((start, y - 0.2), end - start, 0.4, facecolor="orange", edgecolor="black", alpha=0.7)
            )
            ax.text((start + end) / 2, y, row["domain"], ha="center", va="center", fontsize=8)
    ax.set_yticks(range(len(proteins)))
    ax.set_yticklabels(proteins[::-1])
    ax.set_xlabel("Position (aa)")
    ax.set_title("Protein Domain Architecture")
    plt.tight_layout()
    plt.savefig(args.o, dpi=args.dpi, bbox_inches="tight")
    plt.close()
    print(f"Protein domain plot saved to {args.o}")

