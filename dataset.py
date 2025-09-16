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
    # add more: check the site for exact slugs
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
        time.sleep(0.5)
    return all_courses

def main():
    records = []
    for uni, slug in target_unis.items():
        print(f"\n🔎 Scraping {uni} ({slug})...")
        courses = fetch_courses(slug)
        if not courses:
            print(f"⚠️ No courses found for {uni}")
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
                "course_title_short": c.get("coursetitle_name"),
                "language": c.get("course_language"),
                "duration": c.get("duration"),
                "course_fee": c.get("course_fee"),
                "currency": c.get("currency"),
                "rating": c.get("rating"),
                "course_slug": c.get("course_slug"),
                "institute_slug": c.get("institute_slug"),
                "logo": c.get("logo")
            })
    df = pd.DataFrame(records)
    df.to_csv("courses_scraped.csv", index=False, encoding="utf-8")
    print(f"\n✅ Done! Total {len(records)} courses saved.")

if __name__ == "__main__":
    main()
