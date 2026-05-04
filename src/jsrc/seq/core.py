def parse_gff_attributes(attr_string: str) -> dict[str, str]:
    """Parse a GFF3/GTF attribute column string into a key-value dict.

    Supports both GFF3 ``key=value`` and GTF ``key "value"`` formats.
    Values wrapped in double quotes are unquoted automatically.

    Parameters
    ----------
    attr_string : str
        The 9th column of a GFF/GTF line (e.g. ``ID=gene1;Parent=tx1``).

    Returns
    -------
    dict[str, str]
        Parsed attribute key-value pairs.
    """
    attrs: dict[str, str] = {}
    for item in attr_string.strip().strip(";").split(";"):
        if "=" in item:
            key, value = item.strip().split("=", 1)
            attrs[key] = value.strip('"')
        elif " " in item:
            parts = item.strip().split(None, 1)
            if len(parts) == 2:
                attrs[parts[0]] = parts[1].strip('"')
    return attrs
