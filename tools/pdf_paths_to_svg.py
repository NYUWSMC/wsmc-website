#!/usr/bin/env python3
"""Convert simple Ghostscript PDF content streams to clean SVG logos."""

from __future__ import annotations

import re
import zlib
from pathlib import Path

TOKEN_RE = re.compile(
    r"/(?:Document/\w+|[\w.]+)|"
    r"[-+]?(?:\d+\.\d*|\.\d+|\d+)(?:[eE][-+]?\d+)?|"
    r"[A-Za-z*]+|"
    r"[\[\]()]|"
    r"<<|>>"
)


class Mat:
    __slots__ = ("a", "b", "c", "d", "e", "f")

    def __init__(self, a=1.0, b=0.0, c=0.0, d=1.0, e=0.0, f=0.0):
        self.a, self.b, self.c, self.d, self.e, self.f = a, b, c, d, e, f

    def copy(self) -> "Mat":
        return Mat(self.a, self.b, self.c, self.d, self.e, self.f)

    def apply(self, x: float, y: float) -> tuple[float, float]:
        return (
            self.a * x + self.c * y + self.e,
            self.b * x + self.d * y + self.f,
        )


def extract_streams(pdf_bytes: bytes) -> list[bytes]:
    streams = []
    for m in re.finditer(rb"stream\r?\n(.*?)\r?\nendstream", pdf_bytes, re.S):
        raw = m.group(1)
        try:
            streams.append(zlib.decompress(raw))
        except Exception:
            streams.append(raw)
    return streams


def get_mediabox(pdf_bytes: bytes) -> tuple[float, float, float, float]:
    m = re.search(
        rb"/MediaBox\s*\[\s*([\d.\-]+)\s+([\d.\-]+)\s+([\d.\-]+)\s+([\d.\-]+)\s*\]",
        pdf_bytes,
    )
    if not m:
        return (0.0, 0.0, 100.0, 100.0)
    return tuple(float(x) for x in m.groups())


def tokenize(text: str) -> list[str]:
    return TOKEN_RE.findall(text)


def cmyk_to_rgb(c: float, m: float, y: float, k: float) -> tuple[float, float, float]:
    r = 1 - min(1.0, c * (1 - k) + k)
    g = 1 - min(1.0, m * (1 - k) + k)
    b = 1 - min(1.0, y * (1 - k) + k)
    return (r, g, b)


def choose_content(streams: list[bytes]) -> str:
    best = None
    best_score = -1
    for s in streams:
        t = s.decode("latin-1", "replace")
        if t.lstrip().startswith("<?"):
            continue
        score = t.count(" m") + t.count("\nm") + t.count(" l") + t.count(" c") + t.count(" f")
        if score > best_score:
            best_score = score
            best = t
    if best is None:
        raise RuntimeError("No content stream found")
    return best


def parse_shapes(content: str):
    tokens = tokenize(content)
    stack: list[str] = []
    ctm = Mat()
    gs_stack: list[tuple[Mat, tuple[float, float, float]]] = []
    path_cmds: list[tuple] = []
    shapes: list[tuple[list[tuple], tuple[float, float, float]]] = []
    fill_rgb = (0.0, 0.0, 0.0)
    i = 0
    n = len(tokens)

    def popn(k: int) -> list[float]:
        vals: list[float] = []
        while len(vals) < k and stack:
            raw = stack.pop()
            try:
                vals.append(float(raw))
            except ValueError:
                # Skip names / junk left by ignored operators
                continue
        if len(vals) < k:
            raise RuntimeError(f"stack underflow: needed {k}, got {len(vals)}")
        vals.reverse()
        return vals

    IGNORE = {
        "BDC",
        "EMC",
        "BMC",
        "MP",
        "DP",
        "BI",
        "ID",
        "EI",
        "CS",
        "cs",
        "SCN",
        "scn",
        "SC",
        "sc",
        "rg",
        "RG",
        "g",
        "G",
        "w",
        "J",
        "j",
        "M",
        "d",
        "ri",
        "i",
        "gs",
        "Do",
        "sh",
        "BX",
        "EX",
        "W",
        "W*",
        "Tr",
        "Ts",
        "Tc",
        "Tw",
        "Tz",
        "TL",
        "Tf",
        "Tm",
        "Td",
        "TD",
        "T*",
        "Tj",
        "TJ",
        "'",
        '"',
    }

    while i < n:
        tok = tokens[i]
        i += 1

        if tok.startswith("/"):
            stack.append(tok)
            continue

        if re.fullmatch(r"[-+]?(?:\d+\.\d*|\.\d+|\d+)(?:[eE][-+]?\d+)?", tok):
            stack.append(tok)
            continue

        if tok in ("[", "]", "(", ")", "<<", ">>"):
            continue

        if tok == "q":
            gs_stack.append((ctm.copy(), fill_rgb))
        elif tok == "Q":
            if gs_stack:
                ctm, fill_rgb = gs_stack.pop()
        elif tok == "cm":
            a, b, c, d, e, f = popn(6)
            M = Mat(a, b, c, d, e, f)
            # CTM_new = M × CTM_old
            ctm = Mat(
                M.a * ctm.a + M.b * ctm.c,
                M.a * ctm.b + M.b * ctm.d,
                M.c * ctm.a + M.d * ctm.c,
                M.c * ctm.b + M.d * ctm.d,
                M.e * ctm.a + M.f * ctm.c + ctm.e,
                M.e * ctm.b + M.f * ctm.d + ctm.f,
            )
        elif tok == "k":
            c, m, y, k = popn(4)
            fill_rgb = cmyk_to_rgb(c, m, y, k)
        elif tok == "K":
            popn(4)
        elif tok == "m":
            x, y = popn(2)
            x, y = ctm.apply(x, y)
            path_cmds.append(("M", x, y))
        elif tok == "l":
            x, y = popn(2)
            x, y = ctm.apply(x, y)
            path_cmds.append(("L", x, y))
        elif tok == "c":
            x1, y1, x2, y2, x3, y3 = popn(6)
            x1, y1 = ctm.apply(x1, y1)
            x2, y2 = ctm.apply(x2, y2)
            x3, y3 = ctm.apply(x3, y3)
            path_cmds.append(("C", x1, y1, x2, y2, x3, y3))
        elif tok == "v":
            x2, y2, x3, y3 = popn(4)
            if path_cmds:
                last = path_cmds[-1]
                x0, y0 = last[-2], last[-1]
            else:
                x0 = y0 = 0.0
            x2, y2 = ctm.apply(x2, y2)
            x3, y3 = ctm.apply(x3, y3)
            path_cmds.append(("C", x0, y0, x2, y2, x3, y3))
        elif tok == "y":
            x1, y1, x3, y3 = popn(4)
            x1, y1 = ctm.apply(x1, y1)
            x3, y3 = ctm.apply(x3, y3)
            path_cmds.append(("C", x1, y1, x3, y3, x3, y3))
        elif tok == "re":
            x, y, w, h = popn(4)
            p0 = ctm.apply(x, y)
            p1 = ctm.apply(x + w, y)
            p2 = ctm.apply(x + w, y + h)
            p3 = ctm.apply(x, y + h)
            path_cmds.append(("M", *p0))
            path_cmds.append(("L", *p1))
            path_cmds.append(("L", *p2))
            path_cmds.append(("L", *p3))
            path_cmds.append(("Z",))
        elif tok == "h":
            path_cmds.append(("Z",))
        elif tok in ("f", "f*", "B", "B*", "b", "b*"):
            if path_cmds:
                shapes.append((list(path_cmds), fill_rgb))
            path_cmds = []
        elif tok in ("S", "s", "n"):
            path_cmds = []
        elif tok in IGNORE:
            # Drop leftover operands for ignored ops that consume stack values
            if tok in {"w", "j", "J", "M", "i", "Tr", "Ts", "Tc", "Tw", "Tz", "TL", "g", "G"}:
                if stack:
                    stack.pop()
            elif tok in {"rg", "RG"}:
                for _ in range(3):
                    if stack:
                        stack.pop()
            elif tok in {"Td", "TD"}:
                for _ in range(2):
                    if stack:
                        stack.pop()
            elif tok == "Tf":
                # /Font size Tf — size then name may be interleaved; clear up to 2 items
                for _ in range(2):
                    if stack:
                        stack.pop()
            elif tok == "Tm":
                for _ in range(6):
                    if stack:
                        stack.pop()
            elif tok in {"CS", "cs", "gs", "Do", "sh", "ri"}:
                if stack:
                    stack.pop()
            elif tok in {"SCN", "scn", "SC", "sc"}:
                while stack and re.fullmatch(
                    r"[-+]?(?:\d+\.\d*|\.\d+|\d+)(?:[eE][-+]?\d+)?", stack[-1]
                ):
                    stack.pop()
                if stack and str(stack[-1]).startswith("/"):
                    stack.pop()
            elif tok in {"BDC", "BMC", "MP", "DP"}:
                while stack:
                    stack.pop()
            elif tok in {"Tj", "TJ", "'", '"'}:
                if stack:
                    stack.pop()
            continue
        elif tok in {"BT", "ET"}:
            continue
        else:
            # Unknown operator — leave stack alone
            pass

    if path_cmds:
        shapes.append((list(path_cmds), fill_rgb))
    return shapes


def shapes_to_svg(
    shapes,
    mediabox: tuple[float, float, float, float],
    aria_label: str = "WSMC",
) -> str:
    x0, y0, x1, y1 = mediabox

    def flip(x: float, y: float) -> tuple[float, float]:
        return (x - x0, (y1 - y))

    path_ds: list[str] = []
    all_xs: list[float] = []
    all_ys: list[float] = []

    for cmds, _rgb in shapes:
        parts: list[str] = []
        for cmd in cmds:
            if cmd[0] == "M":
                x, y = flip(cmd[1], cmd[2])
                parts.append(f"M{x:.2f} {y:.2f}")
                all_xs.append(x)
                all_ys.append(y)
            elif cmd[0] == "L":
                x, y = flip(cmd[1], cmd[2])
                parts.append(f"L{x:.2f} {y:.2f}")
                all_xs.append(x)
                all_ys.append(y)
            elif cmd[0] == "C":
                coords = []
                for j in range(1, 7, 2):
                    x, y = flip(cmd[j], cmd[j + 1])
                    coords.extend([x, y])
                    all_xs.append(x)
                    all_ys.append(y)
                parts.append(
                    "C"
                    f"{coords[0]:.2f} {coords[1]:.2f} "
                    f"{coords[2]:.2f} {coords[3]:.2f} "
                    f"{coords[4]:.2f} {coords[5]:.2f}"
                )
            elif cmd[0] == "Z":
                parts.append("Z")
        path_ds.append("".join(parts))

    if not all_xs:
        raise RuntimeError("No path geometry found")

    pad = 2.0
    minx, maxx = min(all_xs) - pad, max(all_xs) + pad
    miny, maxy = min(all_ys) - pad, max(all_ys) + pad
    vb_w, vb_h = maxx - minx, maxy - miny

    def shift_d(d: str, dx: float, dy: float) -> str:
        def repl(m: re.Match) -> str:
            op = m.group(1)
            nums = [float(n) for n in re.findall(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?", m.group(2))]
            out = []
            for idx, n in enumerate(nums):
                out.append(f"{(n + dx) if idx % 2 == 0 else (n + dy):.2f}")
            return op + " ".join(out)

        return re.sub(r"([MLC])([-\d.\seE+]+)", repl, d)

    shifted = [shift_d(d, -minx, -miny) for d in path_ds]
    # Prefer one path for simple currentColor theming
    combined = " ".join(shifted)

    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {vb_w:.2f} {vb_h:.2f}" '
        f'fill="none" role="img" aria-label="{aria_label}">\n'
        f'  <path fill="currentColor" d="{combined}"/>\n'
        "</svg>\n"
    )


def pdf_to_svg(pdf_path: Path, svg_path: Path, aria_label: str = "WSMC") -> None:
    data = pdf_path.read_bytes()
    mediabox = get_mediabox(data)
    content = choose_content(extract_streams(data))
    shapes = parse_shapes(content)
    svg = shapes_to_svg(shapes, mediabox, aria_label=aria_label)
    svg_path.write_text(svg)
    print(
        f"{pdf_path.name}: shapes={len(shapes)} -> {svg_path.name} "
        f"({svg_path.stat().st_size} bytes)"
    )


if __name__ == "__main__":
    out = Path(__file__).resolve().parent
    labels = {
        "Mark": "WSMC mark",
        "Abbreviated": "Washington Square Management Consulting",
        "Acronym-Stacked": "WSMC",
        "Full": "Washington Square Management Consulting — NYU Graduate Group",
        "Acronym": "WSMC",
    }
    for name, label in labels.items():
        pdf_to_svg(out / f"{name}.pdf", out / f"{name}.svg", aria_label=label)
