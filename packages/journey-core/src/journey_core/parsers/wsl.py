"""Parser for ``wsl -l -v`` output into a :class:`WslListing` (feature 015, ADR-0022).

Pure text parsing — the subprocess call to ``wsl.exe`` (and decoding its UTF-16 output) is the
impure boundary handled in a later, manual-validation slice. ``wsl -l -v`` emits UTF-16 with a
``*`` marking the default distribution; this parser tolerates stray null bytes and whitespace.
"""

from __future__ import annotations

from journey_core.models.environment import WslDistro, WslListing


def parse_wsl_list_verbose(raw: str) -> WslListing:
    """Parse the text of ``wsl -l -v`` into a :class:`WslListing`.

    Tolerant of the UTF-16 null bytes, the header row, and the leading ``*`` default marker.
    Unparseable or empty input yields an empty listing (no distros, no default) — never a guess.
    """
    text = raw.replace("\x00", "")
    listing = WslListing()
    for line in text.splitlines():
        tokens = line.split()
        if not tokens:
            continue
        is_default = tokens[0] == "*"
        if is_default:
            tokens = tokens[1:]
        # A data row is NAME STATE VERSION with an integer version; skip the header and any noise.
        if len(tokens) < 3:
            continue
        try:
            version = int(tokens[-1])
        except ValueError:
            continue  # header row ("NAME STATE VERSION") or non-data line
        listing.distros.append(WslDistro(name=tokens[0], state=tokens[1], version=version))
        if is_default:
            listing.default_distro = tokens[0]
    return listing
