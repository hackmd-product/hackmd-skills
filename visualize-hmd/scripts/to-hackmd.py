#!/usr/bin/env python3
"""
to-hackmd.py — Convert a standalone HTML file to HackMD-compatible markup.

Usage:
    python3 to-hackmd.py [--strict] <input.html> <output.html>

What it does:
  1. Strips <html>, <head>, <body> wrapper tags
  2. Extracts <style> block, dedents CSS to col 0
  3. Prepends Google Fonts @import + .markdown-body override to CSS
  4. Rewrites body/html/a selectors for .viz-root scope
  5. Removes blank lines from HTML body (prevents Type 6 HTML block termination)
  6. Strips leading whitespace from HTML lines (prevents 4-space code-block)
  7. Replaces <main> with <div>
  8. Wraps body in <div class="viz-root">

With --strict: exit 1 if sanity checks fail after conversion.
"""

from __future__ import annotations

import argparse
import re
import sys

FONTS_IMPORT = "@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Noto+Sans+TC:wght@400;500;600;700;800&display=swap');\n"
MARKDOWN_BODY_OVERRIDE = ".markdown-body { max-width: none !important; padding: 0 !important; }\n"


def dedent_css(css: str) -> str:
    lines = []
    for line in css.split('\n'):
        l = line.rstrip()
        for prefix in ('      ', '    ', '  '):
            if l.startswith(prefix):
                l = l[len(prefix):]
                break
        lines.append(l)
    return '\n'.join(lines)


def fix_selectors(css: str) -> str:
    css = re.sub(r'\nhtml\s*\{[^}]*\}', '', css)
    css = re.sub(r'(?m)^body\s*\{', '.viz-root {', css)
    css = re.sub(r'(?m)^a\s*\{', '.viz-root a {', css)
    return css


def clean_body(html: str) -> str:
    lines = [line.strip() for line in html.split('\n') if line.strip()]
    return '\n'.join(lines)


def replace_main(html: str) -> str:
    html = re.sub(r'<main\b', '<div', html)
    html = html.replace('</main>', '</div>')
    return html


def sanity_check(result: str) -> list[str]:
    idx = result.index('</style>')
    body_part = result[idx:]
    issues: list[str] = []
    blank_count = body_part.count('\n\n') - 1
    if blank_count > 0:
        issues.append(f"blank lines in body: {blank_count}")
    if re.search(r'</?main\b', result):
        issues.append("<main> tags remain")
    if re.findall(r'(?m)^body\s*\{', result):
        issues.append("bare body{} rules remain")
    return issues


def convert(src: str, dst: str, strict: bool = False) -> None:
    with open(src, 'r', encoding='utf-8') as f:
        content = f.read()

    style_match = re.search(r'<style>(.*?)</style>', content, re.DOTALL)
    if not style_match:
        raise ValueError("No <style> block found in input file")
    style_inner = style_match.group(1)
    style_inner = dedent_css(style_inner)
    style_inner = fix_selectors(style_inner)
    css_header = '\n' + FONTS_IMPORT + '\n' + MARKDOWN_BODY_OVERRIDE + '\n'
    style_inner = css_header + style_inner.lstrip('\n')

    body_match = re.search(r'<body>(.*?)</body>', content, re.DOTALL)
    if not body_match:
        raise ValueError("No <body> block found in input file")
    body_inner = body_match.group(1)
    body_inner = clean_body(body_inner)
    body_inner = replace_main(body_inner)
    body_wrapped = '<div class="viz-root">\n' + body_inner + '\n</div>'

    result = f'<style>{style_inner}</style>\n\n{body_wrapped}'

    with open(dst, 'w', encoding='utf-8') as f:
        f.write(result)

    issues = sanity_check(result)
    print(f"Output: {dst} ({len(result):,} chars)")
    for issue in issues:
        print(f"  FAIL: {issue}")
    if not issues:
        print("  Sanity: OK")

    if strict and issues:
        sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert standalone HTML to HackMD markup")
    parser.add_argument("input", help="Source standalone HTML")
    parser.add_argument("output", help="Destination HackMD markup")
    parser.add_argument("--strict", action="store_true", help="Exit 1 if sanity checks fail")
    args = parser.parse_args()
    convert(args.input, args.output, strict=args.strict)


if __name__ == '__main__':
    main()
