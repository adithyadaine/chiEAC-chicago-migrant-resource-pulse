"""Shared helpers for reading free public RSS/Atom feeds (no API keys, no scraping of X)."""
import re
import requests
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime
from datetime import datetime, timezone

HEADERS = {'User-Agent': 'Mozilla/5.0 (compatible; ChicagoMigrantResourcePulse research project)'}

# Posts/articles are kept only if they mention one of these topics (whole-word matches).
KEYWORD_RE = re.compile(
    r"\b(migrants?|asylum|newcomers?|new arrivals?|refugees?|immigra\w*|shelters?|homeless\w*|unhoused|"
    r"housing insecurity|food pantr\w+|food banks?|hunger|evictions?|resettle\w*|undocumented|deport\w*)\b"
    r"|\bICE\b",
    re.IGNORECASE,
)

def is_relevant(text):
    text = text or ''
    # "ICE" (immigration enforcement) must be uppercase so "ice" / "Justice" never match
    if KEYWORD_RE.search(text):
        m = [x for x in KEYWORD_RE.finditer(text) if x.group(0).lower() != 'ice' or x.group(0) == 'ICE']
        return bool(m)
    return False

def _strip(tag):
    return tag.split('}', 1)[-1]

def _parse_date(s):
    if not s:
        return None
    s = s.strip()
    try:
        d = parsedate_to_datetime(s)
    except Exception:
        try:
            d = datetime.fromisoformat(s.replace('Z', '+00:00'))
        except Exception:
            return None
    if d.tzinfo is None:
        d = d.replace(tzinfo=timezone.utc)
    return d.astimezone(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

def fetch_feed(url, timeout=30):
    """Return list of dicts: title, link, summary, published (UTC string or None). Raises on HTTP failure."""
    r = requests.get(url, headers=HEADERS, timeout=timeout)
    r.raise_for_status()
    root = ET.fromstring(r.content)
    items = []
    for el in root.iter():
        if _strip(el.tag) not in ('item', 'entry'):
            continue
        d = {'title': '', 'link': '', 'summary': '', 'published': None}
        for ch in el:
            n = _strip(ch.tag)
            if n == 'title':
                d['title'] = (ch.text or '').strip()
            elif n == 'link':
                d['link'] = (ch.get('href') or ch.text or '').strip() or d['link']
            elif n in ('description', 'summary', 'content') and not d['summary']:
                d['summary'] = re.sub(r'<[^>]+>', ' ', ch.text or '')
                d['summary'] = re.sub(r'\s+', ' ', d['summary']).strip()
            elif n in ('pubDate', 'published', 'updated', 'date') and not d['published']:
                d['published'] = _parse_date(ch.text)
        if d['title'] or d['summary']:
            items.append(d)
    return items
