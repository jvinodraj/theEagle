#!/usr/bin/env python3
"""Helper for Strava OAuth reauthorization.

Usage:
  python scripts/strava_oauth_helper.py authorize-url --client-id 123 --redirect-uri http://localhost/exchange_token
  python scripts/strava_oauth_helper.py exchange-code --client-id 123 --client-secret abc --code xyz
"""

from __future__ import annotations

import argparse
import json
import sys
from urllib import error, parse, request


AUTHORIZE_URL = "https://www.strava.com/oauth/authorize"
TOKEN_URL = "https://www.strava.com/api/v3/oauth/token"
DEFAULT_SCOPES = "activity:read,activity:write"


def http_post_form(url: str, payload: dict[str, str]) -> dict:
    data = parse.urlencode(payload).encode("utf-8")
    req = request.Request(
        url=url,
        method="POST",
        data=data,
        headers={
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
        },
    )
    try:
        with request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code} POST {url} failed: {body}") from exc


def build_authorize_url(args: argparse.Namespace) -> str:
    params = {
        "client_id": args.client_id,
        "redirect_uri": args.redirect_uri,
        "response_type": "code",
        "approval_prompt": "force",
        "scope": args.scope,
    }
    return f"{AUTHORIZE_URL}?{parse.urlencode(params)}"


def cmd_authorize_url(args: argparse.Namespace) -> int:
    print(build_authorize_url(args))
    return 0


def cmd_exchange_code(args: argparse.Namespace) -> int:
    payload = {
        "client_id": args.client_id,
        "client_secret": args.client_secret,
        "code": args.code,
        "grant_type": "authorization_code",
    }
    data = http_post_form(TOKEN_URL, payload)

    result = {
        "athlete_id": data.get("athlete", {}).get("id") if isinstance(data.get("athlete"), dict) else None,
        "access_token": data.get("access_token"),
        "refresh_token": data.get("refresh_token"),
        "scope": data.get("scope"),
        "expires_at": data.get("expires_at"),
    }
    print(json.dumps(result, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Strava OAuth reauthorization helper")
    sub = parser.add_subparsers(dest="command", required=True)

    auth_cmd = sub.add_parser("authorize-url", help="Print the Strava consent URL")
    auth_cmd.add_argument("--client-id", required=True, help="Strava app client ID")
    auth_cmd.add_argument(
        "--redirect-uri",
        default="http://localhost/exchange_token",
        help="Redirect URI configured in the Strava app",
    )
    auth_cmd.add_argument(
        "--scope",
        default=DEFAULT_SCOPES,
        help="Comma-separated scopes to request",
    )
    auth_cmd.set_defaults(func=cmd_authorize_url)

    exchange_cmd = sub.add_parser("exchange-code", help="Exchange an authorization code for tokens")
    exchange_cmd.add_argument("--client-id", required=True, help="Strava app client ID")
    exchange_cmd.add_argument("--client-secret", required=True, help="Strava app client secret")
    exchange_cmd.add_argument("--code", required=True, help="Authorization code returned by Strava")
    exchange_cmd.set_defaults(func=cmd_exchange_code)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise
