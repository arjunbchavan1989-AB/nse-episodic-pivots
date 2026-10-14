"""Evidence-qualified narrative EPs, separated from earnings/strict gap EPs."""
import json,re
from datetime import datetime,timedelta
from pathlib import Path
from catalysts import IST,ROUTINE,NEGATIVE,SPECULATIVE

CATALOG=[
 ("Defence / aerospace",r"\b(defen[cs]e|aerospace|artillery|military|missile|drone)\b"),
 ("AI / data-centre infrastructure",r"\b(ai|artificial intelligence|data cent(re|er)|gpu|hyperscale)\b"),
 ("Semiconductors / electronics",r"\b(semiconductor|chip fab|electronics manufacturing)\b"),
 ("Renewables / green energy",r"\b(renewable|green energy|solar|wind power|green hydrogen|battery storage)\b"),
 ("Railways / infrastructure",r"\b(railway|metro rail|rail infrastructure|highway)\b"),
 ("Sugar / ethanol",r"\b(sugar|ethanol|sugarcane)\b"),
 ("Pharma / regulatory opportunity",r"\b(usfda|fda|anda|drug approval)\b")]
REPUTABLE=("economic times","cnbc","mint","business standard","business-standard","reuters","bloomberg","moneycontrol","financial express")


def apply_themes(rows,session,review_path=None):
    end=datetime.fromisoformat(session).replace(hour=15,minute=30,tzinfo=IST)
    path=Path(review_path) if review_path else Path(__file__).with_name("story_reviews.json")
    reviewed=json.loads(path.read_text()) if path.exists() else []
    active=[]
    for review in reviewed:
        available=datetime.fromisoformat(review["evidence_available_at"])
        if not available<=end<=available+timedelta(days=review.get("valid_days",30)):continue
        if any(datetime.fromisoformat(s["published_at"])>end for s in review["sources"]):continue
        active.append(review)
    for row in rows:
        sources=row["catalyst"]["sources"]
        stories=[]
        invalidation=any(re.search(r"\b(cancel|cancelled|withdraw|withdrawn|abandon|abandoned|terminated|rejected)\b",s["title"].lower()) for s in sources)
        for review in active:
            if review["symbol"]!=row["symbol"] or invalidation:continue
            stories.append({"name":review["name"],"status":"Reviewed primary evidence","valid":True,
                            "thesis":review["thesis"],"risks":review["risks"],"sources":review["sources"],
                            "evidence_available_at":review["evidence_available_at"],"reviewed_at":review["reviewed_at"],
                            "expires_at":(datetime.fromisoformat(review["evidence_available_at"])+timedelta(days=review.get("valid_days",30))).isoformat()})
            # A same-session reviewed primary event may enrich the catalyst card.
            if datetime.fromisoformat(review["evidence_available_at"]).date()==end.date():
                c=row["catalyst"]
                c.update({"strength":3,"label":"Moderate provisional","status":"Primary filing reviewed",
                          "category":"M&A / restructuring","headline":review["thesis"],"url":review["sources"][0]["url"],
                          "timing":"During session","rating_reasons":["Primary filing and two dated media reports support the event and company exposure.",
                           "In-principle approval, not a completed merger; detailed terms and financial implications remain unresolved.",
                           "Disclosure was during the session, so it does not explain an opening gap. Causality and earnings materiality are not established."]})
                c["sources"]=list({s["url"]:s for s in review["sources"]+c["sources"]}.values())[:12]
                c["source_count"]=len(c["sources"])
        if not invalidation:
            for name,pattern in CATALOG:
                matched=[s for s in sources if re.search(pattern,s["title"]+" "+s.get("summary",""),re.I) and s.get("candidate")]
                primary=[s for s in matched if s["official"]]
                media=[s for s in matched if not s["official"] and any(p in s["publisher"].lower() for p in REPUTABLE)]
                publishers={s["publisher"].lower() for s in media}
                if not matched:continue
                valid=bool(primary) and len(publishers)>=2
                if any(name in s["name"] for s in stories):continue
                stories.append({"name":name,"status":"Primary + two media publishers" if valid else "Narrative candidate, unverified",
                                "valid":valid,"thesis":matched[0]["title"],
                                "risks":["Company-matched primary exposure is required; a sector label alone is insufficient.",
                                         "Feed/headline corroboration is not independent financial verification or proof of causal benefit."],
                                "sources":(primary+media)[:6] if valid else matched[:6],
                                "evidence_available_at":max(s["published_at"] for s in matched)})
        valid=any(s["valid"] for s in stories)
        tape=row["mover"] and row["gates"]["rvol"] and row["gates"]["close_position"] and row["gates"]["positive_session"] and row["neglect_pass"]
        row["stories"]=stories
        row["story_valid"]=valid
        row["story_ep"]=bool(valid and tape)
        row["story_label"]=next((s["name"] for s in stories if s["valid"]),stories[0]["name"] if stories else "No validated story")
    return [{"symbol":r["symbol"],"name":s["name"],"status":s["status"]} for r in rows for s in r["stories"] if s["valid"]]
