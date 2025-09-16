from __future__ import annotations

import argparse
import json
import secrets
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "config" / "settings.json"


def generate_secret(length: int) -> str:
    # ``token_urlsafe`` roughly returns 1.3 characters per byte requested.
    bytes_required = max(32, int(length * 3 / 4))
    return secrets.token_urlsafe(bytes_required)[:length]


def rotate_secret(length: int) -> None:
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(
            f"Configuration file not found at {CONFIG_PATH}. Ensure the repo structure is intact."
        )

    with CONFIG_PATH.open("r", encoding="utf-8") as config_file:
        data = json.load(config_file)

    security = data.setdefault("security", {})
    previous_secret = security.get("jwt_secret_key")
    security["jwt_secret_key"] = generate_secret(length)

    with CONFIG_PATH.open("w", encoding="utf-8") as config_file:
        json.dump(data, config_file, indent=2)
        config_file.write("\n")

    preview = previous_secret[:6] + "***" if previous_secret else "<none>"
    print(f"Rotated JWT secret key (previous prefix: {preview}).")
    print(f"Updated file: {CONFIG_PATH}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Rotate the JWT secret in config/settings.json")
    parser.add_argument(
        "--length",
        type=int,
        default=64,
        help="Desired length of the generated secret (default: 64 characters)",
    )
    args = parser.parse_args()
    rotate_secret(length=max(32, args.length))


if __name__ == "__main__":
    main()

