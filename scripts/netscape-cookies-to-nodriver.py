#!/usr/bin/env python3
"""Convert a Netscape cookie export to nodriver's pickle format."""

import argparse
import pickle
from pathlib import Path

from nodriver import cdp


def parse_cookie_file(path: Path, all_domains: bool) -> list[cdp.network.Cookie]:
    cookies = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("#") and not line.startswith("#HttpOnly_"):
            continue

        fields = line.split("\t")
        if len(fields) != 7:
            continue

        domain, include_subdomains, cookie_path, secure, expires, name, value = fields
        http_only = domain.startswith("#HttpOnly_")
        if http_only:
            domain = domain.removeprefix("#HttpOnly_")

        normalized_domain = domain.lstrip(".").lower()
        if not all_domains and not (
            normalized_domain == "comix.to" or normalized_domain.endswith(".comix.to")
        ):
            continue

        try:
            expiry = float(expires)
        except ValueError:
            expiry = None

        cookies.append(
            cdp.network.Cookie(
                name=name,
                value=value,
                domain=domain,
                path=cookie_path or "/",
                size=len(name) + len(value),
                http_only=http_only,
                secure=secure.upper() == "TRUE",
                session=expiry in (None, 0),
                priority=cdp.network.CookiePriority.MEDIUM,
                source_scheme=(
                    cdp.network.CookieSourceScheme.SECURE
                    if secure.upper() == "TRUE"
                    else cdp.network.CookieSourceScheme.NON_SECURE
                ),
                source_port=443 if secure.upper() == "TRUE" else 80,
                expires=expiry if expiry not in (None, 0) else None,
            )
        )
    return cookies


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert Netscape cookies.txt to nodriver .dat format"
    )
    parser.add_argument("input", type=Path, help="Netscape cookies.txt file")
    parser.add_argument("output", type=Path, help="Output nodriver .dat file")
    parser.add_argument(
        "--all-domains",
        action="store_true",
        help="Convert cookies for every domain instead of comix.to only",
    )
    args = parser.parse_args()

    cookies = parse_cookie_file(args.input, args.all_domains)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("wb") as output:
        pickle.dump(cookies, output)
    print(f"Converted {len(cookies)} cookies to {args.output}")


if __name__ == "__main__":
    main()
