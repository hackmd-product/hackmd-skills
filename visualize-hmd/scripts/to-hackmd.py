#!/usr/bin/env python3
"""
to-hackmd.py — Convert a standalone HTML file to HackMD-compatible markup.

Usage:
    python3 to-hackmd.py <input.html> <output.html>

What it does:
  1. Strips <html>, <head>, <body> wrapper tags
  2. Extracts <style> block, dedents CSS to col 0
  3. Prepends Google Fonts @import + .markdown-body override to CSS
  4. Rewrites body/html/a selectors for .viz-root scope
  5. Removes blank lines from HTML body (prevents Type 6 HTML block termination)
  6. Strips leading whitespace from HTML lines (prevents 4-space code-block)
  7. Replaces <main> with <div>
  8. Wraps body in <div class="viz-root">
"""

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
    # Remove html {} rules
    css = re.sub(r'\nhtml\s*\{[^}]*\}', '', css)
    # body {} -> .viz-root {}
    css = re.sub(r'(?m)^body\s*\{', '.viz-root {', css)
    # a {} -> .viz-root a {}  (only bare `a`, not e.g. `.nav a`)
    css = re.sub(r'(?m)^a\s*\{', '.viz-root a {', css)
    return css


def clean_body(html: str) -> str:
    lines = [line.strip() for line in html.split('\n') if line.strip()]
    return '\n'.join(lines)


def replace_main(html: str) -> str:
    html = re.sub(r'<main\b', '<div', html)
    html = html.replace('</main>', '</div>')
    return html


def convert(src: str, dst: str) -> None:
    with open(src, 'r', encoding='utf-8') as f:
        content = f.read()

    # --- Style block ---
    style_match = re.search(r'<style>(.*?)</style>', content, re.DOTALL)
    if not style_match:
        raise ValueError("No <style> block found in input file")
    style_inner = style_match.group(1)
    style_inner = dedent_css(style_inner)
    style_inner = fix_selectors(style_inner)
    css_header = '\n' + FONTS_IMPORT + '\n' + MARKDOWN_BODY_OVERRIDE + '\n'
    style_inner = css_header + style_inner.lstrip('\n')

    # --- Body ---
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

    # Sanity checks
    idx = result.index('</style>')
    body_part = result[idx:]
    blank_count = body_part.count('\n\n') - 1  # -1 for the style/div separator
    main_count = len(re.findall(r'</?main', result))
    body_rules = re.findall(r'(?m)^body\s*\{', result)

    print(f"Output: {dst} ({len(result):,} chars)")
    print(f"Blank lines in body: {blank_count}  (should be 0)")
    print(f"<main> tags remaining: {main_count}  (should be 0)")
    print(f"bare body{{}} rules remaining: {body_rules}  (should be [])")


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <input.html> <output.html>")
        sys.exit(1)
    convert(sys.argv[1], sys.argv[2])
