"""Issue a short-lived classroom token on the Server terminal."""

from __future__ import annotations

import argparse

from jwt_auth.auth import create_demo_token


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a short-lived Smart Device API demo token")
    parser.add_argument("--subject", default="dashboard-client", help="Name recorded in the token")
    parser.add_argument("--lifetime", type=int, default=300, help="Token lifetime in seconds (1-3600)")
    args = parser.parse_args()

    try:
        print(create_demo_token(args.subject, args.lifetime))
    except (RuntimeError, ValueError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
