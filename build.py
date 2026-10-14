#!/usr/bin/env python3
"""Static generator for KeepYourSpreadsheet. Run: python3 build.py <base_url>"""
import sys, os, json, html, shutil
BASE = (sys.argv[1] if len(sys.argv) > 1 else "https://example.invalid").rstrip("/")
from urllib.parse import urlparse
PREFIX = urlparse(BASE).path.rstrip("/")  # e.g. /keepyourspreadsheet on GitHub project pages
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "public")
CHECKED = "14 Oct 2026"
NAME = "KeepYourSpreadsheet"

def src(url, label=None):
    return f'<p class="src">Last checked {CHECKED}. Source: <a href="{url}" rel="nofollow noopener">{html.escape(label or url)}</a></p>'

NAV = [("/", "Home"), ("/compare/", "Compare tools"), ("/deadlines/", "Deadlines"), ("/penalties/", "Penalties"),
       ("/does-hmrc-have-a-free-tool/", "Free HMRC tool?"), ("/free-via-bank/", "Free via your bank"), ("/changelog/", "Changelog")]

pages = []  # (path, title, desc, body, faq)

def page(path, title, desc, body, faq=None):
    pages.append((path, title, desc, body, faq or []))

CSS = """:root{--ink:#0b0c0c;--muted:#505a5f;--line:#b1b4b6;--bg:#fff;--soft:#f3f2f1;--acc:#1d70b8;--warn:#ffdd00;--ok:#00703c}
*{box-sizing:border-box}body{margin:0;font:18px/1.55 system-ui,-apple-system,"Segoe UI",Arial,sans-serif;color:var(--ink);background:var(--bg)}
a{color:var(--acc)}a:focus{outline:3px solid var(--warn);background:var(--warn)}
header{background:var(--ink);color:#fff;border-bottom:8px solid var(--acc)}header .w{display:flex;flex-wrap:wrap;gap:.5rem 1.2rem;align-items:center;padding:.8rem 1rem}
header a{color:#fff;text-decoration:none}header .logo{font-weight:700;font-size:1.2rem;margin-right:auto}header nav a{font-size:.95rem}header nav a:hover{text-decoration:underline}
.w{max-width:960px;margin:0 auto;padding:0 1rem}main{padding:1.5rem 0 3rem}h1{font-size:2rem;line-height:1.2;margin:.5rem 0 1rem}h2{margin-top:2rem}
.notice{border-left:6px solid var(--warn);background:var(--soft);padding:.8rem 1rem;margin:1rem 0}
.box{border:2px solid var(--ink);padding:1rem;margin:1rem 0}.count{font-size:2.2rem;font-weight:700}
.src{font-size:.85rem;color:var(--muted)}table{border-collapse:collapse;width:100%;font-size:.95rem}
th,td{border-bottom:1px solid var(--line);text-align:left;padding:.5rem;vertical-align:top}th{background:var(--soft)}
.tw{overflow-x:auto}footer{background:var(--soft);border-top:1px solid var(--line);font-size:.9rem;padding:1.5rem 0;color:var(--muted)}
.tag{display:inline-block;background:var(--ok);color:#fff;padding:0 .4rem;font-size:.8rem;font-weight:700}
.tag.paid{background:var(--muted)}input{font:inherit;padding:.4rem;border:2px solid var(--ink);width:100%;max-width:22rem}
button{font:inherit;background:var(--muted);color:#fff;border:0;padding:.5rem 1rem;margin-top:.5rem}"""

DISCLAIMER = '<div class="notice"><strong>Not tax advice.</strong> This site is general information about software and published HMRC rules. Check GOV.UK or a qualified adviser for your own situation.</div>'

def render(path, title, desc, body, faq):
    nav = " ".join(f'<a href="{p}">{n}</a>' for p, n in NAV)
    ld = []
    if faq:
        ld.append({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]})
        body += "<h2>Questions</h2>" + "".join(f"<h3>{html.escape(q)}</h3><p>{html.escape(a)}</p>" for q, a in faq)
    ldh = "".join(f'<script type="application/ld+json">{json.dumps(x)}</script>' for x in ld)
    out = f"""<!doctype html><html lang="en-GB"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title><meta name="description" content="{html.escape(desc)}"><link rel="canonical" href="{BASE}{path}">
<meta property="og:title" content="{html.escape(title)}"><meta property="og:description" content="{html.escape(desc)}"><meta property="og:type" content="website">
<link rel="stylesheet" href="/style.css">{ldh}</head><body>
<header><div class="w"><a class="logo" href="/">{NAME}</a><nav>{nav}</nav></div></header>
<main><div class="w">{body}</div></main>
<footer><div class="w"><p><strong>Not tax advice.</strong> Independent site, not affiliated with HMRC or any software provider. No affiliate links yet. Facts last checked {CHECKED}; see the <a href="/changelog/">changelog</a>. <a href="/about/">About</a> · <a href="/newsletter/">Newsletter</a></p></div></footer>
</body></html>"""
    return out.replace('href="/', f'href="{PREFIX}/').replace("href='/", f"href='{PREFIX}/")

GOV_GUIDE = "https://www.gov.uk/guidance/use-making-tax-digital-for-income-tax/before-you-use-this-guide"
GOV_SOFT = "https://www.gov.uk/guidance/find-software-thats-compatible-with-making-tax-digital-for-income-tax"
GOV_PEN = "https://www.gov.uk/guidance/penalties-for-income-tax-self-assessment-volunteers"
HMRC_PR = "https://www.mynewsdesk.com/uk/hm-revenue-customs-hmrc/pressreleases/six-months-to-go-sole-traders-and-landlords-earning-more-than-30000-pounds-urged-to-act-now-3470794"

TOOLS = [
 dict(slug="aligned-tax", name="aligned.tax", url="https://aligned.tax/", kind="Bridging", price="Free for individuals filing their own quarterly updates",
      free=True, files="XLSX upload (Google Sheets/Numbers export to XLSX)", yearend="Year-end filing described as 'coming soon'",
      points=["Vendor says filing your own quarterly updates is free 'always', with no card and no time limit.",
              "Needs an .xlsx file; the vendor explains how to export one from Google Sheets, Apple Numbers or LibreOffice.",
              "Vendor says it was recognised by HMRC in July 2026.",
              "Year-end submissions are listed as 'coming soon', so check before relying on it for your tax return.",
              "Its Smart Map feature sends a redacted view of your spreadsheet to an AI model to suggest mappings (vendor's description)."]),
 dict(slug="flonancial", name="flonancial", url="https://www.flonancial.co.uk/", kind="Bridging", price="Free (quarterly updates and year-end return)",
      free=True, files=".xlsx, .xls, .csv, .ods", yearend="Vendor says the year-end tax return is included free",
      points=["Vendor says quarterly updates and the year-end tax return 'will always remain free'.",
              "Designed for straightforward sole traders and UK landlords bringing in less than £90,000 a year before expenses (vendor's wording).",
              "Displays HMRC recognition reference AM3Z8N.",
              "Vendor says your spreadsheet is parsed in your browser and only the submitted totals are stored."]),
 dict(slug="suitesheets", name="suiteSheets", url="https://www.suitesheets.co.uk/", kind="Bridging", price="£20 per tax year (first income source)",
      free=False, files="Free .xlsx template or add their Overview sheet to yours", yearend="End-of-year return 'in development' (£15 when launched)",
      points=["£20 covers all four quarterly updates for one income source for the tax year, paid at your first submission.",
              "Each additional income source is £10 for the year.",
              "End-of-year tax return is in development; the vendor says it will cost a separate £15.",
              "Aimed at sole traders and landlords earning under £90,000 (vendor's wording). No monthly subscription."]),
 dict(slug="my-tax-digital", name="My Tax Digital", url="https://www.mytaxdigital.co.uk/", kind="Bridging + accounting", price="Free",
      free=True, files="Imports figures from spreadsheets (bridging mode)", yearend="Not stated on the homepage — check with the vendor",
      points=["Vendor describes itself as free MTD software for Income Tax and VAT.",
              "Two modes: Bridging (import figures from spreadsheets) and Accounting (keep records in the app).",
              "Covers self-employment (SA103S/F), UK property (SA105) and foreign property (SA106) categories, per the vendor.",
              "Note: the vendor homepage still describes MTD as 'currently voluntary', which is out of date — MTD became mandatory for some from 6 April 2026."]),
 dict(slug="123-sheets", name="123 Sheets", url="https://www.123sheets.com/", kind="Bridging", price="Not verified — see vendor",
      free=False, files="Excel worksheet (also Google Sheets, Numbers, LibreOffice)", yearend="Not verified",
      points=["Spreadsheet bridging software for self-employed, landlords and VAT, per the vendor.",
              "Vendor says it works with Excel and also Google Sheets, Apple Numbers, LibreOffice and OpenOffice.",
              "Vendor says it only reads the summary figures HMRC needs and does not store your underlying data.",
              "We could not find the price on the vendor homepage on 14 Oct 2026, so we have not listed one."]),
 dict(slug="clear-books-free", name="Clear Books Sole Trader Free", url="https://www.clearbooks.co.uk/pricing/", kind="Accounting (free plan)", price="Free; paid Sole Trader plan £5/month + VAT",
      free=True, files="Records kept in the app (not a spreadsheet bridge)", yearend="Year-end filing included on the free plan",
      points=["Sole Trader Free includes MTD Income Tax quarterly updates and year-end filing, per the vendor's pricing page.",
              "No transaction limits and works for CIS subcontractors (vendor's list).",
              "The paid Sole Trader plan (£5/month plus VAT) adds bank feeds, receipt scanning and invoicing.",
              "Property Free covers one property's MTD filings at no cost, per the vendor."]),
]

for t in TOOLS:
    body = f"<h1>{t['name']}: MTD for Income Tax review</h1>{DISCLAIMER}<table><tr><th>Type</th><td>{t['kind']}</td></tr><tr><th>Price</th><td>{t['price']}</td></tr><tr><th>Works with</th><td>{t['files']}</td></tr><tr><th>Year-end return</th><td>{t['yearend']}</td></tr></table><h2>What we verified</h2><ul>" + "".join(f"<li>{html.escape(p)}</li>" for p in t["points"]) + f"</ul>{src(t['url'], t['name'] + ' (vendor page)')}<p>Always confirm a product appears in <a href='{GOV_SOFT}'>HMRC's software finder</a> before signing up.</p><p><a href='/compare/'>← Compare all tools</a></p>"
    page(f"/tools/{t['slug']}/", f"{t['name']} for Making Tax Digital: price & features (checked {CHECKED})",
         f"{t['name']} for MTD Income Tax: {t['price']}. Verified on the vendor's own page {CHECKED}.", body)

rows = "".join(f"<tr><td><a href='/tools/{t['slug']}/'>{t['name']}</a></td><td>{t['kind']}</td><td><span class='tag{'' if t['free'] else ' paid'}'>{'FREE' if t['free'] else 'PAID/?'}</span> {t['price']}</td><td>{t['files']}</td><td>{t['yearend']}</td><td><a href='{t['url']}' rel='nofollow noopener'>vendor page</a></td></tr>" for t in TOOLS)
page("/compare/", "MTD bridging software compared: keep your spreadsheet (Oct 2026)",
     "Side-by-side comparison of spreadsheet bridging tools and free plans for Making Tax Digital for Income Tax. Every price checked on the vendor's page on 14 Oct 2026.",
     f"<h1>Keep your spreadsheet: MTD tools compared</h1>{DISCLAIMER}<p>Bridging software links the spreadsheet you already keep to HMRC. GOV.UK confirms you can keep using spreadsheets if you use software that links to them.</p>{src(GOV_GUIDE,'GOV.UK: Use Making Tax Digital for Income Tax')}<div class='tw'><table><tr><th>Tool</th><th>Type</th><th>Price</th><th>Works with</th><th>Year-end return</th><th>Source</th></tr>{rows}</table></div><p class='src'>All rows last checked {CHECKED} on each vendor's own page. Where we could not verify something, we say so rather than guess.</p>",
     [("Can I keep using a spreadsheet for Making Tax Digital?", "Yes. GOV.UK says you can continue to use spreadsheets, but you need software that links to them (bridging software) to send quarterly updates and your tax return."),
      ("What is bridging software?", "Software that connects your existing records, such as a spreadsheet, to HMRC so you can send quarterly updates without moving to full accounting software.")])

page("/", "Making Tax Digital for sole traders: keep your spreadsheet | KeepYourSpreadsheet",
     "Who must join Making Tax Digital for Income Tax and when, the next quarterly deadline (7 Nov 2026), and verified free or cheap spreadsheet bridging tools.",
     f"""<h1>Making Tax Digital without giving up your spreadsheet</h1>
<div class="box"><p>Next quarterly update deadline: <strong>7 November 2026</strong></p><p class="count" id="cd">—</p><p class="src">Covers 6 April to 5 October 2026 for people already in MTD. {src(GOV_GUIDE,'GOV.UK')}</p></div>
<script>(function(){{var e=document.getElementById('cd'),t=new Date('2026-11-07T23:59:59Z').getTime();function u(){{var d=t-Date.now();if(d<0){{e.textContent='Deadline passed';return}}var days=Math.floor(d/864e5),h=Math.floor(d%864e5/36e5);e.textContent=days+' days '+h+' hours left'}}u();setInterval(u,6e4)}})();</script>
<h2>Who must join, and when</h2>
<table><tr><th>Your Self Assessment return for</th><th>Qualifying income</th><th>You start</th></tr>
<tr><td>2024 to 2025</td><td>more than £50,000</td><td>6 April 2026</td></tr><tr><td>2025 to 2026</td><td>more than £30,000</td><td>6 April 2027</td></tr><tr><td>2026 to 2027</td><td>more than £20,000</td><td>6 April 2028</td></tr></table>
<p>Qualifying income is your total turnover from self-employment and property <strong>before expenses</strong>.</p>{src(GOV_GUIDE,'GOV.UK: Use Making Tax Digital for Income Tax')}
<p>HMRC estimates around 1,077,000 more sole traders and landlords will need to use MTD from 6 April 2027.</p>{src(HMRC_PR,'HMRC press release, 5 Oct 2026')}
<h2>Start here</h2><ul><li><a href="/compare/">Compare spreadsheet bridging tools</a></li><li><a href="/free-via-bank/">Get software free through your bank</a></li><li><a href="/deadlines/">All deadlines</a> · <a href="/penalties/">Penalties</a></li><li><a href="/does-hmrc-have-a-free-tool/">Does HMRC have a free tool?</a></li></ul>{DISCLAIMER}""",
     [("When do I have to start Making Tax Digital for Income Tax?", "It depends on qualifying income on an earlier return: over £50,000 (2024-25 return) from 6 April 2026, over £30,000 (2025-26 return) from 6 April 2027, over £20,000 (2026-27 return) from 6 April 2028, according to GOV.UK."),
      ("Is the threshold based on profit or turnover?", "Turnover. GOV.UK defines qualifying income as total turnover from self-employment and property income before expenses.")])

page("/deadlines/", "MTD for Income Tax deadlines 2026/27: quarterly update dates",
     "Making Tax Digital quarterly update deadlines for 2026/27: 7 Aug 2026, 7 Nov 2026, 7 Feb 2027, 7 May 2027, tax return by 31 Jan 2028. Checked against GOV.UK.",
     f"""<h1>MTD for Income Tax deadlines (2026/27)</h1><table><tr><th>What</th><th>Deadline</th></tr>
<tr><td>First quarterly update</td><td>7 August 2026</td></tr><tr><td>Second quarterly update</td><td>7 November 2026</td></tr><tr><td>Third quarterly update</td><td>7 February 2027</td></tr><tr><td>Fourth quarterly update</td><td>7 May 2027</td></tr><tr><td>Tax return and pay your tax bill</td><td>31 January 2028</td></tr></table>
<p>Quarterly updates are summaries of income and expenses, not tax returns. You send one for each sole trader business and property business.</p>{src(GOV_GUIDE,'GOV.UK: Use Making Tax Digital for Income Tax')}{DISCLAIMER}""",
     [("When is the next MTD quarterly update due?", "The second quarterly update for 2026/27 is due by 7 November 2026, according to GOV.UK."),
      ("Is a quarterly update a tax return?", "No. GOV.UK says quarterly updates are totals of your self-employment and property income and expenses; they are summaries, not tax returns.")])

page("/penalties/", "MTD for Income Tax penalties: points, soft landing and what changes in 2027",
     "How Making Tax Digital late submission penalty points work, the 2026/27 soft landing for quarterly updates, and the 4-point threshold from 2027/28. From GOV.UK.",
     f"""<h1>MTD penalties explained</h1>{DISCLAIMER}
<h2>2026/27: no points for late quarterly updates</h2><p>HMRC will not apply penalty points for late quarterly updates for the 2026 to 2027 tax year. You still need to send them before you can submit your tax return.</p>{src(GOV_GUIDE,'GOV.UK: Use Making Tax Digital for Income Tax')}
<h2>From 2027/28 for people required to use MTD</h2><ul><li>Late submission penalties apply if you miss quarterly update deadlines.</li><li>The penalty point threshold is 4 points.</li></ul>
<h2>How the points system works (as described for volunteers)</h2><ul><li>Late submissions earn a penalty point; reaching the threshold triggers a £200 penalty, and £200 each time you miss another deadline.</li><li>Late payment penalties are separate and depend on how late you pay.</li></ul>{src(GOV_PEN,'GOV.UK: Penalties for MTD for Income Tax volunteers')}
<p>GOV.UK has a separate page for people required to use MTD from April 2026; we link to the volunteers page because that is the one we checked.</p>""",
     [("Will I get a penalty for a late quarterly update in 2026/27?", "GOV.UK says HMRC will not apply penalty points for late quarterly updates for the 2026 to 2027 tax year, though you still need to send them."),
      ("How many penalty points before a fine from 2027/28?", "GOV.UK says for people required to use MTD from 2027 to 2028 onwards, the penalty point threshold is 4 points and late quarterly updates count.")])

page("/does-hmrc-have-a-free-tool/", "Does HMRC have a free Making Tax Digital tool? No — here's what is free",
     "HMRC does not provide its own software for Making Tax Digital for Income Tax. GOV.UK confirms it. Here are verified free third-party options instead.",
     f"""<h1>Does HMRC have a free MTD tool?</h1><p><strong>No.</strong> GOV.UK says: “HMRC does not provide software”. You need third-party software that has been through HMRC's recognition process.</p>{src(GOV_GUIDE,'GOV.UK: Use Making Tax Digital for Income Tax')}
<p>Some websites still say there is an HMRC free tool. That contradicts GOV.UK.</p><p>HMRC also says it “does not recommend any product or software provider”.</p>{src(GOV_SOFT,'GOV.UK: Choose the right software')}
<h2>Free options we verified</h2><ul><li><a href="/tools/aligned-tax/">aligned.tax</a> (quarterly updates)</li><li><a href="/tools/flonancial/">flonancial</a></li><li><a href="/tools/my-tax-digital/">My Tax Digital</a></li><li><a href="/tools/clear-books-free/">Clear Books Sole Trader Free</a></li><li><a href="/free-via-bank/">FreeAgent through NatWest Group banks</a></li></ul>{DISCLAIMER}""",
     [("Does HMRC provide free software for Making Tax Digital for Income Tax?", "No. GOV.UK states that HMRC does not provide software. You must use compatible third-party software, some of which is free."),
      ("Does HMRC recommend any MTD software?", "No. GOV.UK says HMRC does not recommend any product or software provider.")])

page("/free-via-bank/", "Free MTD software through your business bank (FreeAgent via NatWest, Mettle)",
     "How to get FreeAgent free for Making Tax Digital with a NatWest, RBS, Ulster Bank or Mettle business account, and the conditions. Checked on FreeAgent's page 14 Oct 2026.",
     f"""<h1>Free MTD software through your bank</h1>{DISCLAIMER}
<h2>FreeAgent with NatWest, Royal Bank of Scotland, Ulster Bank or Mettle</h2><ul>
<li>NatWest, Royal Bank of Scotland or Ulster Bank business account holders are entitled to a free FreeAgent account for as long as they keep the bank account.</li>
<li>With Mettle, you must make at least one transaction a month from your Mettle account. If you don't, or you close it, a FreeAgent subscription is charged while you keep using it.</li>
<li>FreeAgent says it is HMRC-recognised for MTD for Income Tax and VAT.</li>
<li>FreeAgent is full accounting software, not a spreadsheet bridge; it can import spreadsheet and bank data.</li>
<li>Mettle's eligibility criteria do not support partnerships, per FreeAgent.</li></ul>{src('https://www.freeagent.com/mettle/','FreeAgent: Mettle and FreeAgent')}
<p>Other banks' bundled tools (for example Starling or Monzo) are not listed yet because we have not verified them on the banks' own pages.</p>""",
     [("Is FreeAgent free with Mettle?", "FreeAgent says yes, as long as you make at least one transaction a month from your Mettle account; otherwise a subscription is charged."),
      ("Is FreeAgent free with NatWest?", "FreeAgent says NatWest, Royal Bank of Scotland and Ulster Bank business account holders get a free FreeAgent account for as long as they keep the bank account.")])

page("/newsletter/", "MTD deadline reminders newsletter (coming soon)", "A free email reminder before each Making Tax Digital quarterly deadline. Sign-up is not open yet.",
     """<h1>Deadline reminders (coming soon)</h1><p>We plan a short email before each quarterly deadline, plus any price changes to the tools we track. Sign-up is not open yet, and this form does not collect anything.</p>
<form onsubmit="return false"><label for="em">Email</label><br><input id="em" type="email" disabled placeholder="Sign-up opens soon"><br><button disabled>Not open yet</button></form><p>Meanwhile, the <a href="/deadlines/">deadlines page</a> and <a href="/changelog/">changelog</a> are always up to date.</p>""")

page("/about/", "About KeepYourSpreadsheet and our 'not tax advice' notice", "Who runs KeepYourSpreadsheet, how facts are checked, and why this is not tax advice.",
     f"""<h1>About this site</h1><div class="notice"><strong>Not tax advice.</strong> KeepYourSpreadsheet is an independent information site. It is not affiliated with HMRC or any software provider. Nothing here is tax, legal or financial advice. Rules and prices change; check GOV.UK, the vendor, or a qualified adviser before acting.</div>
<h2>How we check facts</h2><ul><li>Every price and product claim is checked on the vendor's own page, with the date and a link.</li><li>Rules and deadlines come from GOV.UK or HMRC.</li><li>If we can't verify something, we leave it out and say so.</li><li>Every change is logged publicly in the <a href="/changelog/">changelog</a>.</li></ul>
<h2>Money</h2><p>There are no affiliate links or sponsors yet. If that changes, we'll label them clearly and it won't change what we list.</p><p>Spotted an error? Corrections are logged in the changelog. A contact address will be added soon.</p>""")

page("/changelog/", "Changelog: every fact change on KeepYourSpreadsheet", "Public log of every price, rule and deadline check on KeepYourSpreadsheet.",
     f"""<h1>Changelog</h1><h2>14 Oct 2026 — version 1 launched</h2><ul>
<li>Checked on vendor pages: aligned.tax, flonancial, suiteSheets, My Tax Digital, 123 Sheets, Clear Books, FreeAgent (Mettle/NatWest).</li>
<li>Checked on GOV.UK: start dates and thresholds, 2026/27 deadlines, penalties (volunteers page), "HMRC does not provide software".</li>
<li>Not published because we could not verify on the vendor's own page today: 123 Sheets price; Xero, QuickBooks, Sage, Starling, Monzo, Coconut, Zoho, Pandle, QuickFile, VitalTax, Landlord Studio and others.</li>
<li>Noted: My Tax Digital's homepage still calls MTD "currently voluntary" (out of date).</li></ul>""")

# write
if os.path.exists(OUT): shutil.rmtree(OUT)
os.makedirs(OUT)
open(os.path.join(OUT, "style.css"), "w").write(CSS)
for path, title, desc, body, faq in pages:
    d = os.path.join(OUT, path.strip("/"))
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, "index.html"), "w").write(render(path, title, desc, body, faq))
open(os.path.join(OUT, "404.html"), "w").write(render("/404", "Page not found", "Page not found", "<h1>Page not found</h1><p><a href='/'>Go to the home page</a></p>", None))
open(os.path.join(OUT, "sitemap.xml"), "w").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + "".join(f"<url><loc>{BASE}{p[0]}</loc><lastmod>2026-10-14</lastmod></url>" for p in pages) + "</urlset>\n")
open(os.path.join(OUT, "robots.txt"), "w").write(f"User-agent: *\nAllow: /\nSitemap: {BASE}/sitemap.xml\n")
llms = f"# {NAME}\n\n> Independent UK guide to Making Tax Digital for Income Tax for sole traders and landlords who want to keep using a spreadsheet. Facts last checked {CHECKED}. Not tax advice.\n\n## Key facts (from GOV.UK)\n- Start dates: over £50,000 qualifying income from 6 April 2026; over £30,000 from 6 April 2027; over £20,000 from 6 April 2028. Qualifying income is turnover before expenses.\n- 2026/27 quarterly updates due 7 Aug 2026, 7 Nov 2026, 7 Feb 2027, 7 May 2027; tax return by 31 Jan 2028.\n- HMRC does not provide its own MTD software.\n- No penalty points for late quarterly updates in 2026/27.\n\n## Pages\n" + "".join(f"- [{t}]({BASE}{p}): {d}\n" for p, t, d, b, f in pages)
open(os.path.join(OUT, "llms.txt"), "w").write(llms)
print("built", len(pages), "pages ->", OUT)
