"""NUMBER CHECK (NewIdeas, Mon 9 Nov): are the digits in a built PDF the same as in its Markdown source?
Extracts every number token from the .md (markdown markup dropped) and from the PDF's text (pdftotext), normalises typography
(unicode minus / dashes, multiplication sign, thin and no-break spaces, ligatures, soft hyphens), and compares the two
multisets of numbers. Prints the counts and every number that appears a different number of times, with a little context.
usage: /usr/bin/python3 -I pdf_digits.py <paper.md> <paper.pdf> [--html]   (--html: the second file is an HTML page)"""
import collections, re, subprocess, sys, html

NUM = re.compile(r"(?<![\w.])[-+]?\d[\d,]*(?:\.\d+)?(?![\w])")


def norm(t):
    t = t.replace("−", "-").replace("–", "-").replace("—", "-").replace("×", "x")
    t = t.replace(" ", " ").replace(" ", " ").replace(" ", " ").replace("­", "")
    t = t.replace("ﬁ", "fi").replace("ﬂ", "fl")
    t = re.sub(r"(?<![A-Za-z])x(?=\d)", "x ", t)            # ratios: "x1.08" -> "x 1.08"
    return t


def md_text(p):
    t = open(p, encoding="utf-8").read()
    t = re.sub(r"<!--.*?-->", " ", t, flags=re.S)          # comments
    t = re.sub(r"`([^`]*)`", r"\1", t)                      # inline code: keep its text
    t = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", t)          # links: keep the label, drop the URL
    t = re.sub(r"[*_#>|]", " ", t)                          # emphasis, headings, quotes, table bars
    return norm(t)


def pdf_text(p):
    return norm(subprocess.run(["pdftotext", "-enc", "UTF-8", p, "-"], capture_output=True, text=True, check=True).stdout)


def html_text(p):
    t = open(p, encoding="utf-8").read()
    t = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", t)
    t = re.sub(r"<[^>]+>", " ", t)
    return norm(html.unescape(t))


def nums(t):
    # join numbers a line break split inside a token (e.g. "1,2\n34" is rare; "12.\n5" never joined) - keep simple
    return [m.group(0).lstrip("+") for m in NUM.finditer(t)]


md, other = sys.argv[1], sys.argv[2]
a_t = md_text(md)
b_t = html_text(other) if "--html" in sys.argv else pdf_text(other)
A, B = collections.Counter(nums(a_t)), collections.Counter(nums(b_t))
diff = sorted(set(A) | set(B), key=lambda k: (-(abs(A[k] - B[k])), k))
bad = [(k, A[k], B[k]) for k in diff if A[k] != B[k]]
only_build = [b for b in bad if b[2] > b[1]]
bad.sort(key=lambda b: (b[2] <= b[1], -abs(b[1] - b[2])))   # build-only (changed digits?) first
print(f"{md} -> {other}: numbers in source {sum(A.values())} ({len(A)} distinct), in build {sum(B.values())} ({len(B)} distinct); "
      f"{len(bad)} distinct numbers differ in count; {len(only_build)} appear more often in the BUILD (changed digits?)")
for k, x, y in bad[:60]:
    i = a_t.find(k) if x > y else b_t.find(k)
    src = a_t if x > y else b_t
    ctx = src[max(0, i - 50):i + 50].replace("\n", " ") if i >= 0 else ""
    print(f"  {k!r}: source {x}, build {y}   ... {ctx} ...")
