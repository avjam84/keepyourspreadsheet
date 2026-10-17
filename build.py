#!/usr/bin/env python3
"""Static generator for KeepYourSpreadsheet. Run: python3 build.py <base_url>"""
import sys, os, json, html, shutil
BASE = (sys.argv[1] if len(sys.argv) > 1 else "https://example.invalid").rstrip("/")
from urllib.parse import urlparse
PREFIX = urlparse(BASE).path.rstrip("/")  # e.g. /keepyourspreadsheet on GitHub project pages
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "public")
CHECKED = "17 Oct 2026"
NAME = "KeepYourSpreadsheet"

def src(url, label=None):
    return f'<p class="src">Last checked {CHECKED}. Source: <a href="{url}" rel="nofollow noopener">{html.escape(label or url)}</a></p>'

NAV = [("/", "Home"), ("/compare/", "Compare tools"), ("/deadlines/", "Deadlines"), ("/quarterly-updates/", "Quarterly updates"), ("/penalties/", "Penalties"),
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

GOV_GUIDE = "https://www.gov.uk/guidance/use-making-tax-digital-for-income-tax/using-making-tax-digital-for-income-tax-for-the-first-time"
GOV_SEND = "https://www.gov.uk/guidance/use-making-tax-digital-for-income-tax/send-quarterly-updates"
GOV_SOFT = "https://www.gov.uk/guidance/choose-the-right-software-for-making-tax-digital-for-income-tax"
GOV_FINDER = "https://www.tax.service.gov.uk/find-making-tax-digital-income-tax-software/"
GOV_PEN_REQ = "https://www.gov.uk/guidance/penalties-for-making-tax-digital-for-income-tax"
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
              f"We could not find the price on the vendor homepage (last looked {CHECKED}), so we have not listed one."]),
 dict(slug="clear-books-free", name="Clear Books Sole Trader Free", url="https://www.clearbooks.co.uk/pricing/", kind="Accounting (free plan)", price="Free; paid Sole Trader plan £5/month + VAT",
      free=True, files="Records kept in the app (not a spreadsheet bridge)", yearend="Year-end filing included on the free plan",
      points=["Sole Trader Free includes MTD Income Tax quarterly updates and year-end filing, per the vendor's pricing page.",
              "No transaction limits and works for CIS subcontractors (vendor's list).",
              "The paid Sole Trader plan (£5/month plus VAT) adds bank feeds, receipt scanning and invoicing.",
              "Property Free covers one property's MTD filings at no cost, per the vendor."]),
 dict(slug="taxupdates", name="TaxUpdates", url="https://taxupdates.co.uk/", kind="Bridging", price="Free for individuals doing their own tax; agents free up to 10 clients",
      free=True, files="CSV upload (adapt your own spreadsheet or use their free Google Sheets templates)", yearend="Vendor says year-end filing is included; HMRC's finder lists tax returns as 'Ready now'",
      extra=("https://taxupdates.co.uk/guide/index", "TaxUpdates: How to use this site"),
      points=["Vendor says the site is free to use as an individual dealing with your own tax. Tax agents can manage up to 10 clients free, and more with a subscription.",
              "Vendor says it files quarterly business updates and year-end information, including other income and gains.",
              "Uploads must be in CSV format. You can paste HMRC's category names into a new sheet in your existing spreadsheet, or use one of the vendor's free Google Sheets templates (self-employment, UK property, foreign property).",
              "Vendor's guide says each quarterly update is cumulative, so you submit year-to-date totals each time.",
              "You can also record transactions inside TaxUpdates instead of uploading, up to 1,200 transactions per business per tax year (vendor's limit).",
              "The vendor says the earliest tax year with full functionality is 2026-27, and your Government Gateway account must be signed up for MTD first (it can take around 72 hours to update).",
              "HMRC's software finder lists it as bridging software with a free version, covering sole trader, UK property and foreign property income."]),
]

for t in TOOLS:
    body = f"<h1>{t['name']}: MTD for Income Tax review</h1>{DISCLAIMER}<table><tr><th>Type</th><td>{t['kind']}</td></tr><tr><th>Price</th><td>{t['price']}</td></tr><tr><th>Works with</th><td>{t['files']}</td></tr><tr><th>Year-end return</th><td>{t['yearend']}</td></tr></table><h2>What we verified</h2><ul>" + "".join(f"<li>{html.escape(p)}</li>" for p in t["points"]) + f"</ul>{src(t['url'], t['name'] + ' (vendor page)')}{src(*t['extra']) if t.get('extra') else ''}<p>Always confirm a product appears in <a href='{GOV_FINDER}'>HMRC's software finder</a> before signing up.</p><p><a href='/compare/'>← Compare all tools</a></p>"
    page(f"/tools/{t['slug']}/", f"{t['name']} for Making Tax Digital: price & features (checked {CHECKED})",
         f"{t['name']} for MTD Income Tax: {t['price']}. Verified on the vendor's own page {CHECKED}.", body)

rows = "".join(f"<tr><td><a href='/tools/{t['slug']}/'>{t['name']}</a></td><td>{t['kind']}</td><td><span class='tag{'' if t['free'] else ' paid'}'>{'FREE' if t['free'] else 'PAID/?'}</span> {t['price']}</td><td>{t['files']}</td><td>{t['yearend']}</td><td><a href='{t['url']}' rel='nofollow noopener'>vendor page</a></td></tr>" for t in TOOLS)
page("/compare/", "MTD bridging software compared: keep your spreadsheet (Oct 2026)",
     f"Side-by-side comparison of spreadsheet bridging tools and free plans for Making Tax Digital for Income Tax. Every price checked on the vendor's page on {CHECKED}.",
     f"<h1>Keep your spreadsheet: MTD tools compared</h1>{DISCLAIMER}<p>Bridging software links the spreadsheet you already keep to HMRC. GOV.UK confirms you can keep using spreadsheets if you use software that links to them.</p>{src(GOV_GUIDE,'GOV.UK: Use Making Tax Digital for Income Tax')}<div class='tw'><table><tr><th>Tool</th><th>Type</th><th>Price</th><th>Works with</th><th>Year-end return</th><th>Source</th></tr>{rows}</table></div><p class='src'>All rows last checked {CHECKED} on each vendor's own page. Where we could not verify something, we say so rather than guess.</p><h2>How many bridging tools does HMRC list?</h2><p>On 17 Oct 2026, HMRC's software finder showed <strong>78</strong> products under \"Bridging software that connects to records\" for sole traders and landlords, and <strong>22</strong> of those when also filtered to \"Free version\". HMRC shows results in random order and does not recommend any of them. We add tools to the table above only after checking the vendor's own page.</p>{src(GOV_FINDER,'HMRC: Find software that works with Making Tax Digital for Income Tax')}",
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
<h2>Start here</h2><ul><li><a href="/compare/">Compare spreadsheet bridging tools</a></li><li><a href="/free-via-bank/">Get software free through your bank</a></li><li><a href="/quarterly-updates/">How to send a quarterly update</a></li><li><a href="/deadlines/">All deadlines</a> · <a href="/penalties/">Penalties</a></li><li><a href="/does-hmrc-have-a-free-tool/">Does HMRC have a free tool?</a></li></ul>{DISCLAIMER}""",
     [("When do I have to start Making Tax Digital for Income Tax?", "It depends on qualifying income on an earlier return: over £50,000 (2024-25 return) from 6 April 2026, over £30,000 (2025-26 return) from 6 April 2027, over £20,000 (2026-27 return) from 6 April 2028, according to GOV.UK."),
      ("Is the threshold based on profit or turnover?", "Turnover. GOV.UK defines qualifying income as total turnover from self-employment and property income before expenses.")])

page("/deadlines/", "MTD for Income Tax deadlines 2026/27: quarterly update dates",
     "Making Tax Digital quarterly update deadlines for 2026/27: 7 Aug 2026, 7 Nov 2026, 7 Feb 2027, 7 May 2027, tax return by 31 Jan 2028. Checked against GOV.UK.",
     f"""<h1>MTD for Income Tax deadlines (2026/27)</h1><table><tr><th>What</th><th>Deadline</th></tr>
<tr><td>First quarterly update</td><td>7 August 2026</td></tr><tr><td>Second quarterly update</td><td>7 November 2026</td></tr><tr><td>Third quarterly update</td><td>7 February 2027</td></tr><tr><td>Fourth quarterly update</td><td>7 May 2027</td></tr><tr><td>Tax return and pay your tax bill</td><td>31 January 2028</td></tr></table>
<p>Quarterly updates are summaries of income and expenses, not tax returns. You send one for each sole trader business and property business.</p><p>If your accounts run 1 April to 31 March, you can use calendar update periods instead, with the same deadlines. See <a href="/quarterly-updates/">how quarterly updates work</a>.</p>{src(GOV_GUIDE,'GOV.UK: Use Making Tax Digital for Income Tax')}{DISCLAIMER}""",
     [("When is the next MTD quarterly update due?", "The second quarterly update for 2026/27 is due by 7 November 2026, according to GOV.UK."),
      ("Is a quarterly update a tax return?", "No. GOV.UK says quarterly updates are totals of your self-employment and property income and expenses; they are summaries, not tax returns.")])

page("/quarterly-updates/", "How to send an MTD quarterly update: standard vs calendar update periods",
     "How Making Tax Digital quarterly updates work, from GOV.UK: year-to-date totals, standard (6 April) vs calendar (1 April) update periods, when you can send, nil updates and what happens after.",
     f"""<h1>How MTD quarterly updates work</h1>{DISCLAIMER}
<p>A quarterly update is a set of totals of your self-employment and property income and expenses. Your software adds up your digital records every 3 months and you send the totals to HMRC for each self-employment and property business you have. They are summaries, not tax returns, and you do not need to make any accounting or tax adjustments before sending one.</p>
<h2>What HMRC receives</h2><ul><li>Totals for each income and expense category you used in your records. MTD uses the same categories as Self Assessment.</li><li>HMRC does not receive details of individual receipts or invoices.</li><li>If you use a spreadsheet, <a href="/compare/">bridging software</a> reads these totals from it and sends them.</li></ul>
<h2>Each update covers the tax year so far</h2><p>Every quarterly update runs from the start of the tax year to the end of the update period, so your third update covers 6 April to 5 January (standard periods). This lets you correct your records, and the correction is picked up in your next update. If you had no income or expenses in a period, you must still send the update.</p>
<h2>Standard or calendar update periods</h2><p>Your software uses standard update periods by default, which follow the tax year. If your accounting period runs from 1 April to 31 March, GOV.UK says you should use calendar update periods. The deadlines are the same either way.</p>
<div class="tw"><table><tr><th>Standard period</th><th>Calendar period</th><th>Deadline</th></tr>
<tr><td>6 April to 5 July</td><td>1 April to 30 June</td><td>7 August</td></tr>
<tr><td>6 April to 5 October</td><td>1 April to 30 September</td><td>7 November</td></tr>
<tr><td>6 April to 5 January</td><td>1 April to 31 December</td><td>7 February</td></tr>
<tr><td>6 April to 5 April</td><td>1 April to 31 March</td><td>7 May (the following tax year)</td></tr></table></div>
<div class="notice"><strong>Choose before your first update.</strong> To switch to calendar update periods you need to select this in your software before you send your first quarterly update. After you send an update you cannot change your update periods for the rest of the tax year.</div>
<h2>When you can send</h2><ul><li>Any time after the end of the update period, up to and including the deadline day.</li><li>Up to 10 days before the end of the period, if you do not expect to record any more transactions (for example, you are going on holiday).</li><li>More often if you like: most software lets you send on any day, but each update must still cover the full period from 6 April. For example, three updates covering 6 April to 5 May, 6 April to 5 June and 6 April to 5 July instead of one.</li></ul>
<h2>After you send an update</h2><ul><li>The recent activity in your HMRC online account will say "You sent a quarterly update". Sign in with the details you used when you signed up for MTD.</li><li>You can see an estimate of your tax bill for the year so far in your software and your HMRC online account. HMRC adds information it already has, such as a student loan plan. It will be less accurate if you have other income HMRC does not know about yet, or if your accounting period does not match the tax year.</li><li>Some software lets you add other income, such as savings interest, during the year. It is not part of your quarterly updates but improves the estimate.</li></ul>
<h2>Jointly let property</h2><p>For jointly let properties you can include either income and expenses, or income only. If you leave the expenses out, you must report them after the tax year by resending your fourth quarterly update before you submit your tax return. Properties you own alone need both income and expenses in every update.</p>
<h2>Late updates</h2><p>HMRC will not apply penalty points for late quarterly updates in the 2026 to 2027 tax year, but you must send them before you can submit your tax return. From the following year, each missed deadline gets a point. See <a href="/penalties/">MTD penalties</a>.</p>
<h2>Fixing mistakes after the fourth update</h2><p>You may need to resend your fourth quarterly update to correct an error, add expenses for jointly let property, or record Rent-a-Room income if you decide to claim the relief after the tax year ends. Do this before making any tax adjustments.</p>
{src(GOV_SEND,'GOV.UK: Send quarterly updates (updated 16 Oct 2026)')}<p>Next deadline: <strong>7 November 2026</strong>. See <a href="/deadlines/">all deadlines</a>.</p>""",
     [("What are calendar update periods for MTD?", "Quarterly periods that run from 1 April (ending 30 June, 30 September, 31 December and 31 March) instead of 6 April. GOV.UK says to use them if your accounting period is 1 April to 31 March. The deadlines are the same as standard periods."),
      ("Can I change from standard to calendar update periods?", "Only before your first quarterly update of the tax year. GOV.UK says you select it in your software, and once you have sent an update you cannot change your update periods for the rest of that tax year."),
      ("Do I have to send a quarterly update if I had no income?", "Yes. GOV.UK says that if you received no income and had no expenses in an update period, you must still send your quarterly update."),
      ("Can I send an MTD quarterly update early?", "Yes, up to 10 days before the end of the update period if you do not expect to record any more transactions, according to GOV.UK."),
      ("How do I know my quarterly update was received?", "GOV.UK says the recent activity in your HMRC online account will show 'You sent a quarterly update'.")])

page("/penalties/", "MTD for Income Tax penalties 2026/27: points, £200 fines and late payment %",
     "Making Tax Digital penalties from GOV.UK: no penalties for late quarterly updates in 2026/27, a 4-point threshold with £200 fines, and late payment penalties of 3% or 4% plus 10% a year.",
     f"""<h1>MTD for Income Tax penalties explained</h1>{DISCLAIMER}
<p>This page covers people <strong>required</strong> to use Making Tax Digital for Income Tax from April 2026. Volunteers have slightly different rules (see the end of this page).</p>
<h2>When the new penalties start</h2><ul><li>The new late submission and late payment penalties replace the old Self Assessment ones from the tax year you join MTD.</li><li>Earlier years keep the old penalties. For example, if you join on 6 April 2026, the old penalties still apply to your 2025 to 2026 tax return due 31 January 2027.</li><li>They do not apply to partnership, trust or estate, or non-resident company returns. How late payment interest works does not change.</li></ul>
<h2>2026/27: no penalties for late quarterly updates</h2><p>There are no penalties for missing a quarterly update deadline in the 2026 to 2027 tax year. You still need to keep digital records and send your quarterly updates before you can submit your tax return. The tax return deadline still counts.</p>
<h2>Late submission: penalty points</h2><ul><li>You get one penalty point for each missed tax return deadline, and, for tax years after 2026 to 2027, each missed quarterly update deadline.</li><li>The threshold is <strong>4 points</strong>. When you reach it you get a <strong>£200 penalty</strong>, and another £200 each time you miss a further submission deadline.</li><li>You only get one point per deadline, even if you have more than one business and send more than one update late.</li><li>MTD for Income Tax points are separate from any VAT penalty points.</li></ul>
<h2>Late payment penalties</h2><div class="tw"><table><tr><th>How late you pay</th><th>For 2026 to 2027</th><th>For 2027 to 2028</th></tr>
<tr><td>Up to 15 days</td><td>No penalty</td><td>No penalty</td></tr>
<tr><td>16 to 30 days</td><td>3% of the tax owed at day 15, or no penalty if it's your first year</td><td>4% of the tax owed at day 15, or no penalty if it's your first year</td></tr>
<tr><td>31 days or more</td><td>3% at day 15 and 3% at day 30, plus 10% a year on the outstanding amount, charged daily from day 31 until paid (up to 2 years)</td><td>4% at day 15 and 4% at day 30, plus 10% a year on the outstanding amount, charged daily from day 31 until paid (up to 2 years)</td></tr></table></div>
<ul><li>In your first year of the new penalties you have 30 days from the due date to pay in full or contact HMRC to set up a payment plan. After that it drops to 15 days, and you only get the 30-day period once.</li><li>Late payment penalties do not apply to payments on account. Late payment interest is charged from the first day you are late.</li><li>If HMRC agrees a payment plan and you stick to it, penalties are paused from the date you contacted them.</li></ul>
<h2>Getting points removed</h2><ul><li>Below 4 points, each point is removed automatically 24 months after the missed deadline.</li><li>At 4 points, they are only removed once you have sent your updates and tax return on time for 12 months and sent anything outstanding from the previous 24 months.</li></ul>
{src(GOV_PEN_REQ,'GOV.UK: Penalties for Making Tax Digital for Income Tax')}
<h2>If you volunteered for MTD</h2><p>For volunteers, the penalty point threshold is 2 points, with a £200 penalty at the threshold and for each further missed deadline. If you are later required to use MTD, late quarterly updates start to count and your threshold rises from 2 points to 4.</p>{src(GOV_PEN,'GOV.UK: Penalties for MTD for Income Tax volunteers')}""",
     [("Will I get a penalty for a late quarterly update in 2026/27?", "No. GOV.UK says there are no penalties for missing a quarterly update deadline for the 2026 to 2027 tax year, but you still need to send your quarterly updates before you can submit your tax return."),
      ("How many penalty points before a fine under MTD for Income Tax?", "GOV.UK says the threshold is 4 points for people required to use MTD. Reaching it means a £200 penalty, and £200 for each further missed submission deadline."),
      ("What is the MTD late payment penalty?", "According to GOV.UK, nothing if you pay within 15 days. For 2026/27 tax it is 3% of the tax owed at day 15 and 3% at day 30, plus 10% a year from day 31; for 2027/28 those rise to 4%. In your first year you get 30 days before penalties start."),
      ("Do I get a penalty point for each business?", "No. GOV.UK says you only get one penalty point per deadline, even if you have more than one business and send more than one quarterly update late.")])

page("/does-hmrc-have-a-free-tool/", "Does HMRC have a free Making Tax Digital tool? No — here's what is free",
     "HMRC does not provide its own software for Making Tax Digital for Income Tax. GOV.UK confirms it. Here are verified free third-party options instead.",
     f"""<h1>Does HMRC have a free MTD tool?</h1><p><strong>No.</strong> GOV.UK says: “HMRC does not provide software”. You need third-party software that has been through HMRC's recognition process.</p>{src(GOV_GUIDE,'GOV.UK: Use Making Tax Digital for Income Tax')}
<p>Some websites still say there is an HMRC free tool. That contradicts GOV.UK.</p><p>HMRC also says it “does not recommend any product or software provider”.</p>{src(GOV_SOFT,'GOV.UK: Choose the right software')}
<h2>Free options we verified</h2><ul><li><a href="/tools/aligned-tax/">aligned.tax</a> (quarterly updates)</li><li><a href="/tools/flonancial/">flonancial</a></li><li><a href="/tools/my-tax-digital/">My Tax Digital</a></li><li><a href="/tools/taxupdates/">TaxUpdates</a> (quarterly updates and year-end, CSV upload)</li><li><a href="/tools/clear-books-free/">Clear Books Sole Trader Free</a></li><li><a href="/free-via-bank/">FreeAgent through NatWest Group banks</a></li></ul>{DISCLAIMER}""",
     [("Does HMRC provide free software for Making Tax Digital for Income Tax?", "No. GOV.UK states that HMRC does not provide software. You must use compatible third-party software, some of which is free."),
      ("Does HMRC recommend any MTD software?", "No. GOV.UK says HMRC does not recommend any product or software provider.")])

page("/free-via-bank/", "Free MTD software through your business bank (FreeAgent via NatWest, Mettle)",
     f"How to get FreeAgent free for Making Tax Digital with a NatWest, RBS, Ulster Bank or Mettle business account, and the conditions. Checked on FreeAgent's page {CHECKED}.",
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
     f"""<h1>Changelog</h1><h2>17 Oct 2026: daily check</h2><ul>
<li>GOV.UK updated its "Send quarterly updates" guidance on 16 Oct 2026, adding what happens after you send an update and how to change your update period. New page: <a href="/quarterly-updates/">how MTD quarterly updates work</a>, covering standard and calendar update periods, when you can send, and what HMRC receives. The deadlines page now mentions calendar update periods.</li>
<li>Our main GOV.UK guide link now points straight to the current "Using Making Tax Digital for Income Tax for the first time" page (the old address redirected there).</li>
<li>Re-checked on vendor pages, no changes found: aligned.tax, flonancial, suiteSheets, My Tax Digital, 123 Sheets (still no price on homepage), Clear Books, TaxUpdates, FreeAgent (Mettle/NatWest).</li>
<li>Re-checked GOV.UK: no changes to the software guidance or either penalties page.</li>
<li>HMRC's software finder still lists 78 bridging products for sole traders and landlords, 22 with a free version. No newly listed bridging tools since 16 Oct.</li></ul><h2>16 Oct 2026: daily check</h2><ul>
<li>Added <a href="/tools/taxupdates/">TaxUpdates</a>, a free bridging tool listed in HMRC's software finder, after checking its own homepage and guide: free for individuals doing their own tax, CSV upload, quarterly updates and year-end filing.</li>
<li>Re-checked on vendor pages, no changes found: aligned.tax, flonancial, suiteSheets (year-end return still in development at £15), My Tax Digital (homepage still says "currently voluntary"), 123 Sheets (still no price on homepage), Clear Books, FreeAgent (Mettle/NatWest).</li>
<li>Re-checked GOV.UK: no new updates to the MTD for Income Tax guide, the software guidance, or either penalties page since our last check.</li>
<li>HMRC's software finder still lists 78 bridging products for sole traders and landlords, 22 with a free version. No newly listed bridging tools since 15 Oct.</li></ul><h2>15 Oct 2026: daily check</h2><ul>
<li>Re-checked on vendor pages, no changes found: aligned.tax, flonancial, suiteSheets (year-end return still "coming soon" at £15), My Tax Digital (homepage still says "currently voluntary"), 123 Sheets (still no price on homepage), Clear Books, FreeAgent (Mettle/NatWest).</li>
<li>Re-checked on GOV.UK, no changes found: start dates and thresholds, 2026/27 deadlines, "HMRC does not provide software", "HMRC does not recommend any product".</li>
<li>Penalties page rewritten from GOV.UK's page for people required to use MTD (it previously relied on the volunteers page): 4-point threshold, one point per deadline, late payment penalty rates for 2026/27 and 2027/28, the 30-day first-year period, and how points are removed.</li>
<li>Compare page: added the number of bridging products in HMRC's software finder (78, of which 22 have a free version, on 15 Oct 2026).</li>
<li>Updated the "Choose the right software" GOV.UK link to its current address, and tool pages now link straight to HMRC's software finder.</li></ul><h2>14 Oct 2026 — version 1 launched</h2><ul>
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
open(os.path.join(OUT, "sitemap.xml"), "w").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + "".join(f"<url><loc>{BASE}{p[0]}</loc><lastmod>2026-10-17</lastmod></url>" for p in pages) + "</urlset>\n")
open(os.path.join(OUT, "robots.txt"), "w").write(f"User-agent: *\nAllow: /\nSitemap: {BASE}/sitemap.xml\n")
llms = f"# {NAME}\n\n> Independent UK guide to Making Tax Digital for Income Tax for sole traders and landlords who want to keep using a spreadsheet. Facts last checked {CHECKED}. Not tax advice.\n\n## Key facts (from GOV.UK)\n- Start dates: over £50,000 qualifying income from 6 April 2026; over £30,000 from 6 April 2027; over £20,000 from 6 April 2028. Qualifying income is turnover before expenses.\n- 2026/27 quarterly updates due 7 Aug 2026, 7 Nov 2026, 7 Feb 2027, 7 May 2027; tax return by 31 Jan 2028.\n- HMRC does not provide its own MTD software.\n- No penalties for late quarterly updates in 2026/27. From then, the penalty point threshold is 4 points (£200 penalty) for people required to use MTD.\n\n## Pages\n" + "".join(f"- [{t}]({BASE}{p}): {d}\n" for p, t, d, b, f in pages)
open(os.path.join(OUT, "llms.txt"), "w").write(llms)
print("built", len(pages), "pages ->", OUT)
