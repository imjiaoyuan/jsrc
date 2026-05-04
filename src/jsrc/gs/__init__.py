import importlib


def _dispatch(module_name: str):
    def _runner(args):
        module = importlib.import_module(module_name)
        module.cmd(args)

    return _runner


def register_subparser(subparsers):
    gs_parser = subparsers.add_parser("gs", help="Genomic selection dataset and model workflows")
    gs_sub = gs_parser.add_subparsers(dest="gs_cmd")
    gs_parser.set_defaults(_group_parser=gs_parser)

    p = gs_sub.add_parser("build", help="Build GS dataset from GWAS PLINK + phenotype")
    p.add_argument("-pheno", required=True, help="Phenotype file with IID and PHENO columns")
    p.add_argument("-plink", required=True, help="PLINK binary prefix (without .bed/.bim/.fam)")
    p.add_argument("-o", required=True, help="Output dataset directory")
    p.add_argument("--plink-bin", default="plink", help="Path to plink executable")
    p.add_argument("--n-sim", type=int, default=500, help="Number of simulated samples")
    p.add_argument("--top-k", type=int, default=2000, help="Top markers used as causal candidates")
    p.add_argument("--h2", type=float, default=0.5, help="Target heritability for simulation")
    p.add_argument("--seed", type=int, default=42, help="Random seed")
    p.set_defaults(func=_dispatch("jsrc.gs.build"))

    p = gs_sub.add_parser("split", help="Generate CV split indices (real samples for test, sim in train)")
    p.add_argument("-i", "--input", required=True, help="Dataset directory containing y.npy and sample_ids.txt")
    p.add_argument("--folds", type=int, default=5, help="Number of CV folds")
    p.add_argument("--seed", type=int, default=2024, help="Random seed")
    p.set_defaults(func=_dispatch("jsrc.gs.split"))

    p = gs_sub.add_parser("train", help="Train and evaluate GS models with CV indices")
    p.add_argument("-i", "--input", required=True, help="Dataset directory containing X.npy/y.npy/cv_indices/")
    p.add_argument("-o", dest="output", help="Output directory for result CSV files")
    p.add_argument("--folds", type=int, default=5, help="Number of folds to run")
    p.add_argument("--select-k", type=int, default=1000, help="Top K features selected by ANOVA")
    p.add_argument(
        "--models",
        default="gbdt,rf,et,lr,svm,nb",
        help="Comma-separated models from: gbdt,rf,et,ada,dt,lr,svm,nb",
    )
    p.add_argument("--seed", type=int, default=42, help="Random seed")
    p.set_defaults(func=_dispatch("jsrc.gs.train"))
