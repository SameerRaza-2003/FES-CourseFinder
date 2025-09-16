import requests
import pandas as pd
import time

BASE_URL = "https://tcf-backend.timescoursefinder.com/api/v2/search/courses_v2/"

HEADERS = {
    "User-Agent": "Mozilla/5.0",   # mimic browser
    "Accept": "application/json"
}

# Example: mapping your unis → their slugs (you’ll need to build this once)
target_unis = {
    "Edinburgh Napier University": "edinburgh-napier-university",
    "University of Dundee": "university-of-dundee",
    "Robert Gordon University": "robert-gordon-university",
    "University of South Wales": "university-of-south-wales",
    "University of East Anglia": "university-of-east-anglia",
    "University of Portsmouth": "university-of-portsmouth",
    "Manchester Metropolitan University (MMU), UK": "manchester-metropolitan-university",
    "LJMU": "liverpool-john-moores-university",
    "University of Stirling": "university-of-stirling",
    "Anglia Ruskin University": "anglia-ruskin-university",
    "University of Essex": "university-of-essex",
    "University of Northampton, UK": "university-of-northampton",
    "Nottingham Trent University": "nottingham-trent-university",
    "Sheffield Hallam University (SHU)": "sheffield-hallam-university",
    "University of Westminster": "university-of-westminster",
    "Ulster University, Belfast, UK": "ulster-university",
    "SRUC – Scotland’s Rural College": "sruc-scotlands-rural-college",
    "Prifysgol Aberystwyth University": "aberystwyth-university",
    "Regent College London, UK": "regent-college-london",
    "Middlesex University London": "middlesex-university",
    "Heriot Watt University": "heriot-watt-university",
    "University of Hull (Main Campus)": "university-of-hull-2565",
    "DMU UK": "de-montfort-university",
    "University of Bradford": "university-of-bradford",
    "Kingston University London": "kingston-university",
    "Birmingham City University (BCU), UK": "birmingham-city-university",
    "Swansea University, UK": "swansea-university",
    "Wrexham Glyndwr University": "wrexham-glyndwr-university",
    "Bath Spa University": "bath-spa-university",
    "Cardiff Metropolitan University": "cardiff-metropolitan-university"
}

def fetch_courses(slug):
    all_courses = []
    page = 1
    while True:
        params = {
            "institute": slug,
            "page": page
        }
        resp = requests.get(BASE_URL, headers=HEADERS, params=params, timeout=20)
        if resp.status_code != 200:
            print(f"❌ Failed {slug} page {page}: {resp.status_code}")
            break
        data = resp.json()
        results = data.get("result", [])
        if not results:
            break
        all_courses.extend(results)
        print(f"Fetched {len(results)} from {slug}, page {page}")
        page += 1
        time.sleep(0.1)
    return all_courses

def get_study_level(c):
    if c.get("degreelevel_type"):
        return c["degreelevel_type"].capitalize()
    dl = (c.get("degreelevel_name") or "").lower()
    if any(x in dl for x in ["bachelor", "diploma", "certificate", "foundation", "associate"]):
        return "Undergraduate"
    else:
        return "Postgraduate"

def main():
    records = []
    failed_unis = []
    
    for uni, slug in target_unis.items():
        print(f"\n🔎 Scraping {uni} ({slug})...")
        courses = fetch_courses(slug)
        if not courses:
            print(f"⚠️ No courses found for {uni}")
            failed_unis.append(uni)
            continue
        for c in courses:
            records.append({
                "input_uni": uni,
                "institute_name": c.get("institute_name"),
                "course_id": c.get("course_id"),
                "course_title": c.get("name"),
                "discipline": c.get("discipline_name"),
                "specialization": c.get("specialization_name"),
                "degree": c.get("degreelevel_name"),
                "study_level": get_study_level(c),
                "course_title_short": c.get("coursetitle_name"),
                "language": c.get("course_language"),
                "duration": c.get("duration"),
                "course_fee": c.get("course_fee"),
                "currency": c.get("currency"),
                "rating": c.get("rating"),
                "course_slug": c.get("course_slug"),
                "institute_slug": c.get("institute_slug")
            })
    
    df = pd.DataFrame(records)
    df.to_csv("courses_scraped.csv", index=False, encoding="utf-8")
    
    print(f"\n✅ Done! Total {len(records)} courses saved.")
    if failed_unis:
        print("\n⚠️ Failed to retrieve data for these universities:")
        for u in failed_unis:
            print("-", u)

if __name__ == "__main__":
    main()
