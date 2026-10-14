"""Dated, conservative news classification. Headlines do not establish causation."""
import html
import json
import re
import time
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timedelta
from email.utils import parsedate_to_datetime
from urllib.parse import urlencode,urlparse
from urllib.request import Request,urlopen
from zoneinfo import ZoneInfo

IST=ZoneInfo("Asia/Kolkata")
NSE_RSS="https://nsearchives.nseindia.com/content/RSS/Online_announcements.xml"
BSE_RSS="https://www.bseindia.com/data/xml/announcements.xml"
TYPES=[
 ("Earnings / guidance",r"\b(earnings|profit|revenue|guidance|quarterly results|q[1-4] results|financial results)\b"),
 ("Orders / contracts",r"\b(order|orders|contract|contracts|tender|deal|supply agreement)\b"),
 ("Regulatory / product",r"\b(approval|approved|fda|launch|patent|licen[cs]e)\b"),
 ("M&A / capital / expansion",r"\b(acquisition|acquire|merger|capex|expansion|capacity|fundrais|buyback)\b"),
 ("Policy / sector",r"\b(policy|tariff|duty|gst|ethanol|sugar export|import restriction|sector)\b"),
 ("Corporate action",r"\b(bonus|split|dividend|ex.date|rights issue)\b")]
ROUTINE=r"certificate|trading window|newspaper publication|annual general|\bagm\b|\begm\b|postal ballot|e.voting|investor meet|board meeting intimation|intimation of.*results|schedule.*meeting|spurt in volume|price movement|clarification.*(price|volume)|regulation 74|interest and principal|record date"
SPECULATIVE=r"\b(could|might|may|rumou?r|expected|potential|likely to|plans to)\b"
NEGATIVE=r"\b(falls?|declines?|plunges?|misses?|loss|slump|cuts?|downgrade|cancelled|cancellation|rejects?|denied|denial)\b"
POSITIVE=r"\b(wins?|secured?|bags?|received?|awarded?|approved?|approval|doubles?|triples?|surges?|jumps?|raises?|beats?|record|growth|strong|rallies?|acquire|expands?|launches?)\b"
SPECIFIC=r"\b(won|wins?|secured|bags|bagged|received.*(order|contract)|awarded|approval|approved|profit.*(doubled|tripled|surge|jump|growth)|raises.*guidance|beats.*(estimate|expectation)|launch)\b"


def normalize(s):
    return re.sub(r"[^a-z0-9]","",re.sub(r"\b(limited|ltd|corporation|the)\b","",s.lower()))


def stamp(value):
    try:
        d=parsedate_to_datetime(value)
        return d.replace(tzinfo=IST) if d.tzinfo is None else d.astimezone(IST)
    except (ValueError,TypeError):
        try:return datetime.strptime(value,"%d-%b-%Y %H:%M:%S").replace(tzinfo=IST)
        except ValueError:return None


def read_feed(url,official=False):
    error=None
    for attempt in range(3):
        try:
            with urlopen(Request(url,headers={"User-Agent":"Mozilla/5.0 (NSE-EP-EOD-Dashboard)","Accept":"application/rss+xml, application/xml, text/xml"}),timeout=25) as r:
                root=ET.fromstring(r.read())
            result=[]
            for item in root.findall(".//item"):
                when=stamp(item.findtext("pubDate") or "")
                link=item.findtext("link") or ""
                if when is None or urlparse(link).scheme not in ("http","https"):continue
                desc=re.sub(r"<[^>]+>"," ",html.unescape(item.findtext("description") or ""))
                source=item.findtext("source") or ("NSE filing" if "nseindia" in url else "BSE filing")
                result.append({"title":html.unescape(item.findtext("title") or ""),
                               "summary":" ".join(desc.split())[:1400],"url":link,
                               "published_at":when.isoformat(),"publisher":source,"official":official})
            return result,{"url":url,"ok":True,"items":len(result),"error":None}
        except Exception as e:
            error=f"{type(e).__name__}: {str(e)[:160]}"
            if attempt<2:time.sleep(attempt+1)
    return [],{"url":url,"ok":False,"items":0,"error":error}


def news_query(company,symbol,session,previous_session):
    short=re.sub(r"\b(Limited|Ltd\.?)\b","",company,flags=re.I).strip()
    query=f'{short} after:{previous_session} before:{(datetime.fromisoformat(session)+timedelta(days=1)).date()}'
    url="https://news.google.com/rss/search?"+urlencode({"q":query,"hl":"en-IN","gl":"IN","ceid":"IN:en"})
    items,status=read_feed(url)
    status["symbol"]=symbol
    # Search engines may return out-of-window items. Enforce timestamps ourselves.
    return items,status


def describe(item,company,symbol,start,end,opening):
    when=stamp(item["published_at"])
    if when is None:
        try:when=datetime.fromisoformat(item["published_at"]).astimezone(IST)
        except ValueError:return None
    if not start<when<=end:return None
    title=item["title"]
    text=(title+" "+(item["summary"] if item["official"] else "")).lower()
    if item["official"]:
        if normalize(company) not in normalize(item["title"]) and not re.search(r"/"+re.escape(symbol)+r"[_/]",item["url"],re.I):return None
    else:
        core=re.sub(r"\b(limited|ltd|international|industries|industry|india)\b","",company.lower()).strip()
        tokens=[t for t in re.findall(r"[a-z0-9]+",core) if len(t)>=3]
        identity=bool(re.search(r"\b"+re.escape(symbol.lower())+r"\b",title.lower())) or (tokens and all(t in title.lower() for t in tokens[:2]))
        if not identity:return None
    routine=bool(re.search(ROUTINE,text))
    negative=bool(re.search(NEGATIVE,title.lower()))
    speculative=bool(re.search(SPECULATIVE,title.lower()))
    repost=any(s in item["publisher"].lower() for s in ("linkedin","reddit","facebook","twitter","youtube")) or any(s in title.lower() for s in (" - linkedin"," - reddit"," - facebook"))
    category=next((name for name,pat in TYPES if re.search(pat,text)),"Price / volume commentary")
    real=category not in ("Price / volume commentary","Corporate action") and not routine and not negative and not speculative and not repost and bool(re.search(SPECIFIC,text))
    pre_open=when<=opening
    score=0
    reasons=[]
    if repost:
        reasons=["Social/media repost: original event date and novelty are unverified, not an economic catalyst confirmation."]
    elif speculative:
        reasons=["Speculative or prospective headline, not a completed catalyst event."]
    elif routine:
        reasons=["Routine compliance / scheduling / exchange enquiry is not an economic catalyst."]
    elif negative:
        reasons=["Negative or mixed headline; does not support a bullish catalyst."]
    elif real:
        score=2
        reasons=["Event-specific positive language identified."]
        if item["official"]:
            score+=1; reasons.append("Primary exchange disclosure, not only a media headline.")
        if pre_open and item["official"]:
            score+=1; reasons.append("Disclosure precedes this session's opening.")
        if not item["official"]:
            reasons.append("Headline-only evidence: rating capped at 2/5; materiality and recurrence unverified.")
            reasons.append("First-publication novelty unverified; a newly dated article can repeat an older event.")
        else:
            reasons.append("Business materiality and recurrence still require reading the filing.")
    elif category=="Corporate action":
        score=1;reasons=["Corporate action: check adjustment mechanics, not necessarily economic rerating."]
    else:
        reasons=["Reported price/volume action or non-specific context is not proof of a fresh catalyst."]
    if not pre_open:
        reasons.append("Published after the open: cannot by itself establish the cause of the opening gap.")
        score=min(score,3)
    return {**item,"category":category,"candidate":real,"timing":"Before open" if pre_open else "During session",
            "strength":score,"rating_reasons":reasons,
            "evidence_level":"Exchange feed excerpt" if item["official"] else "Media headline only"}


def collect(rows,names,session,previous_session,archive_path):
    end=datetime.fromisoformat(session).replace(hour=15,minute=30,tzinfo=IST)
    start=datetime.fromisoformat(previous_session).replace(hour=15,minute=30,tzinfo=IST)
    opening=end.replace(hour=9,minute=15)
    archive=json.loads(archive_path.read_text()) if archive_path.exists() else []
    diagnostics=[]
    for url in (NSE_RSS,BSE_RSS):
        fresh,status=read_feed(url,True);archive.extend(fresh);diagnostics.append(status)
    archive=list({(a["url"],a["published_at"]):a for a in archive}.values())
    archive=[a for a in archive if datetime.fromisoformat(a["published_at"])>=end-timedelta(days=14)]
    archive_path.parent.mkdir(parents=True,exist_ok=True)
    archive_path.write_text(json.dumps(archive[-6000:],ensure_ascii=False))
    targets=[r for r in rows if r["mover"] or r["technical_pass"]]
    def work(row):
        symbol=row["symbol"];company=names.get(symbol,symbol)
        media,status=news_query(company,symbol,session,previous_session)
        sources=[]
        for item in archive+media:
            found=describe(item,company,symbol,start,end,opening)
            if found:sources.append(found)
        sources=list({(s["url"],s["published_at"]):s for s in sources}.values())
        sources.sort(key=lambda s:(s["strength"],s["official"],s["timing"]=="Before open",s["published_at"]),reverse=True)
        economic=[s for s in sources if s["candidate"]]
        best=economic[0] if economic else None
        score=best["strength"] if best else None
        row["company"]=company
        row["catalyst"]={"strength":score,"label":{1:"Low",2:"Tentative",3:"Moderate",4:"Strong provisional",5:"Exceptional reviewed"}.get(score,"Unverified"),
                         "category":best["category"] if best else "No evidenced fresh bullish catalyst",
                         "headline":best["title"] if best else "No qualifying event found in the fetched sources",
                         "status":"Exchange-reported event" if best and best["official"] else "Headline candidate" if best else "Unverified",
                         "timing":best["timing"] if best else None,"url":best["url"] if best else None,
                         "rating_reasons":best["rating_reasons"] if best else ["Price/volume alone does not establish a catalyst. No qualifying event in available feeds is not proof that none exists."],
                         "sources":sources[:12],"source_count":len(sources),"fetch_ok":status["ok"],
                         "causality":"Not established"}
        return status
    with ThreadPoolExecutor(max_workers=4) as pool:
        for status in pool.map(work,targets):diagnostics.append(status)
    for r in rows:
        r.setdefault("company",names.get(r["symbol"],r["symbol"]))
        r.setdefault("catalyst",{"strength":None,"label":"Not researched","category":"Outside mover research scope",
                                "headline":"News collection covers all ≥4% movers and technical EP candidates",
                                "sources":[],"rating_reasons":[],"fetch_ok":None,"causality":"Not established"})
    return diagnostics
