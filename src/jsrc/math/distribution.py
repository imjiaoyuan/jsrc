from jsrc.math.core import (
    normal_cdf, normal_pdf, t_cdf, f_cdf, chi2_cdf,
    normal_quantile,
)
from jsrc.math.core import write_output
import math


def cmd(args):
    dist = args.dist
    x = args.x
    if dist == "normal":
        cdf_val = normal_cdf(x)
        pdf_val = normal_pdf(x)
        lines = [f"distribution\tnormal", f"x\t{x}", f"cdf\t{cdf_val}"]
        if args.pdf:
            lines.append(f"pdf\t{pdf_val}")
        write_output(lines, args.output)
    elif dist == "t":
        df = args.df1
        if df is None:
            print("Error: --df1 required for t distribution")
            return
        cdf_val = t_cdf(x, df)
        log_pdf = (math.lgamma((df + 1) / 2) - math.lgamma(df / 2)
                   - 0.5 * math.log(df * math.pi)
                   - (df + 1) / 2 * math.log(1 + x * x / df))
        pdf_val = math.exp(log_pdf)
        lines = [f"distribution\tt", f"x\t{x}", f"df\t{df}", f"cdf\t{cdf_val}"]
        if args.pdf:
            lines.append(f"pdf\t{pdf_val}")
        write_output(lines, args.output)
    elif dist == "f":
        df1 = args.df1
        df2 = args.df2
        if df1 is None or df2 is None:
            print("Error: --df1 and --df2 required for F distribution")
            return
        cdf_val = f_cdf(x, df1, df2)
        lines = [f"distribution\tf", f"x\t{x}", f"df1\t{df1}", f"df2\t{df2}", f"cdf\t{cdf_val}"]
        if args.pdf:
            num = math.lgamma((df1 + df2) / 2) + (df1 / 2) * math.log(df1) + (df2 / 2) * math.log(df2)
            den = math.lgamma(df1 / 2) + math.lgamma(df2 / 2)
            log_pdf = num - den + (df1 / 2 - 1) * math.log(x) - (df1 + df2) / 2 * math.log(df1 * x + df2)
            pdf_val = math.exp(log_pdf) if x > 0 else 0
            lines.append(f"pdf\t{pdf_val}")
        write_output(lines, args.output)
    elif dist == "chi2":
        df = args.df1
        if df is None:
            print("Error: --df1 required for chi2 distribution")
            return
        cdf_val = chi2_cdf(x, df)
        lines = [f"distribution\tchi2", f"x\t{x}", f"df\t{df}", f"cdf\t{cdf_val}"]
        if args.pdf:
            log_pdf = (df / 2 - 1) * math.log(x) - x / 2 - df / 2 * math.log(2) - math.lgamma(df / 2)
            pdf_val = math.exp(log_pdf) if x > 0 else 0
            lines.append(f"pdf\t{pdf_val}")
        write_output(lines, args.output)
