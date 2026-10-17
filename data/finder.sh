#!/usr/bin/env bash
# Snapshot HMRC MTD IT software finder: bridging list and bridging+free list (sole trader/landlord).
# Usage: data/finder.sh YYYY-MM-DD   (writes data/hmrc-finder-bridging[-free]-DATE.txt, LC_ALL=C sorted)
# HMRC returns 403 without a browser User-Agent and Referer.
set -e; D=$(cd "$(dirname "$0")" && pwd); DATE=${1:-$(date +%F)}; W=$(mktemp -d); cd "$W"
B=https://www.tax.service.gov.uk; P=/find-making-tax-digital-income-tax-software
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0 Safari/537.36"
c(){ curl -s -A "$UA" -c cj -b cj "$@"; }
tok(){ grep -oE 'name="csrfToken" value="[^"]*"' "$1" | sed 's/.*value="//;s/"//'; }
names(){ python3 -c "import re,html,sys;s=open(sys.argv[1]).read();[print(html.unescape(m.strip())) for m in re.findall(r'(?s)software-vendor-list-heading-override\">(.*?)</h3>',s)]" "$1" | LC_ALL=C sort; }
c "$B$P/how-to-find-software" -o a.html
c -e "$B$P/how-to-find-software" -X POST "$B$P/how-to-find-software" --data-urlencode "csrfToken=$(tok a.html)" --data "how-you-find-software=view-all" -o /dev/null
c -e "$B$P/how-to-find-software" "$B$P/about-you" -o b.html
c -e "$B$P/about-you" -X POST "$B$P/about-you" --data-urlencode "csrfToken=$(tok b.html)" --data "type-of-user=sole-trader-or-landlord" -o /dev/null
c -e "$B$P/about-you" "$B$P/software-results" -o r.html
c -e "$B$P/software-results" -X POST "$B$P/software-results" --data-urlencode "csrfToken=$(tok r.html)" --data "filters[]=bridging" -o /dev/null
c -e "$B$P/software-results" "$B$P/software-results" -o br.html
c -e "$B$P/software-results" -X POST "$B$P/software-results" --data-urlencode "csrfToken=$(tok br.html)" --data "filters[]=bridging&filters[]=free-version" -o /dev/null
c -e "$B$P/software-results" "$B$P/software-results" -o brf.html
names br.html > "$D/hmrc-finder-bridging-$DATE.txt"; names brf.html > "$D/hmrc-finder-bridging-free-$DATE.txt"
grep -oiE '[0-9]+ software results' br.html | head -1; grep -oiE '[0-9]+ software results' brf.html | head -1
