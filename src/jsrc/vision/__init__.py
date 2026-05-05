from jsrc.vision import efd, extract, traits


def register_subparser(subparsers):
    vision_parser = subparsers.add_parser(
        "vision", help="Image recognition and shape descriptors"
    )
    vision_sub = vision_parser.add_subparsers(dest="vision_cmd")
    vision_parser.set_defaults(_group_parser=vision_parser)

    extract.register(vision_sub)
    efd.register(vision_sub)
    traits.register(vision_sub)
