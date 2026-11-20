"""Command line: `uv run a198683 <command>`."""

import argparse
import pathlib
import sys

from a198683 import core


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="a198683",
        description="Distinct values of i^i^...^i over all bracketings (OEIS A198683).",
    )
    parser.add_argument("--bits", type=int, default=core.DEFAULT_PRECISION_BITS,
                        help="working precision of the ball arithmetic (default: %(default)s)")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("count", help="lower and upper bounds for a(1)..a(n) (about 2 seconds)")
    p.add_argument("-n", type=int, default=12, help="largest n, at most 12 (default: %(default)s)")

    sub.add_parser("verify", help="run every independent check (about 90 seconds)")

    p = sub.add_parser("table", help="write the full n = 12 table (a few seconds)")
    p.add_argument("--out", type=pathlib.Path, default=None, help="output file (default: tables/a198683_n12.txt)")

    sub.add_parser("tiny", help="check a(1)..a(9) with plain Python complex numbers")

    args = parser.parse_args(argv)
    core.set_precision(args.bits)

    if args.command == "count":
        from a198683 import count

        result = count.bounds(args.n)
        print(count.report(result))
        return 0 if result.rows[-1].exact else 1

    if args.command == "verify":
        from a198683 import verify

        return 0 if all(c.passed for c in verify.run_all()) else 1

    if args.command == "table":
        from a198683 import table

        out = args.out or table.DEFAULT_OUT
        lines = table.write(out)
        print("published n = 11 table regenerated identically, line for line")
        print(f"wrote {out} ({len(lines)} lines); {lines[-2]}")
        return 0

    if args.command == "tiny":
        from a198683 import tiny

        ok = True
        for n, expected in enumerate(tiny.KNOWN, start=1):
            got = tiny.count(n)
            ok = ok and got == expected
            print(f"n = {n}: {len(tiny.all_values(n)):>5} bracketings, {got:>4} distinct values  (OEIS: {expected})")
        return 0 if ok else 1

    return 2


if __name__ == "__main__":
    sys.exit(main())
