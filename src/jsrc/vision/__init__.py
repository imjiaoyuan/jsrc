import importlib


def _dispatch(module_name: str):
    def _runner(args):
        module = importlib.import_module(module_name)
        module.cmd(args)

    return _runner


def register_subparser(subparsers):
    vision_parser = subparsers.add_parser("vision", help="Image recognition and shape descriptors")
    vision_sub = vision_parser.add_subparsers(dest="vision_cmd")
    vision_parser.set_defaults(_group_parser=vision_parser)

    p = vision_sub.add_parser("extract", help="Extract object contours from a single image")
    p.add_argument("-i", "--input", required=True, help="Input image file")
    p.add_argument("-o", "--output", required=True, help="Output directory")
    p.add_argument(
        "--channel",
        choices=["gray", "a", "b", "s", "v"],
        default="gray",
        help="Channel used for Otsu thresholding",
    )
    p.add_argument("--invert", action="store_true", help="Invert threshold result")
    p.add_argument("--blur", type=int, default=5, help="Gaussian blur kernel size (odd)")
    p.add_argument("--kernel", type=int, default=3, help="Morphology kernel size")
    p.add_argument("--open-iters", type=int, default=2, help="Open operation iterations")
    p.add_argument("--close-iters", type=int, default=2, help="Close operation iterations")
    p.add_argument("--min-area-ratio", type=float, default=0.0005, help="Minimum contour area ratio")
    p.add_argument("--max-area-ratio", type=float, default=0.8, help="Maximum contour area ratio")
    p.add_argument("--min-aspect-ratio", type=float, default=0.1, help="Minimum width/height ratio")
    p.add_argument("--max-aspect-ratio", type=float, default=10.0, help="Maximum width/height ratio")
    p.add_argument("--sort-by", choices=["x", "y"], default="x", help="Sort extracted objects by x or y")
    p.add_argument("--save-mask", action="store_true", help="Save binary mask image")
    p.set_defaults(func=_dispatch("jsrc.vision.extract"))

    p = vision_sub.add_parser("efd", help="Convert extracted contours (.npy) to EFD descriptors")
    p.add_argument("-i", "--input", required=True, help="Input .npy file or directory")
    p.add_argument("-o", "--output", required=True, help="Output directory for CSV/plot files")
    p.add_argument("--harmonics", type=int, default=20, help="Number of EFD harmonics")
    p.add_argument("--points", type=int, default=300, help="Reconstruction points for preview plot")
    p.add_argument("--no-plot", action="store_true", help="Skip reconstruction plot output")
    p.set_defaults(func=_dispatch("jsrc.vision.efd"))

    p = vision_sub.add_parser("traits", help="Compute morphology traits from image object")
    p.add_argument("-i", "--input", required=True, help="Input image file")
    p.add_argument("--channel", choices=["gray", "a", "b", "s", "v"], default="gray", help="Threshold channel")
    p.add_argument("--invert", action="store_true", help="Invert threshold")
    p.add_argument("--blur", type=int, default=5, help="Gaussian blur size (odd)")
    p.add_argument("--kernel", type=int, default=3, help="Morphology kernel size")
    p.set_defaults(func=_dispatch("jsrc.vision.traits"))
