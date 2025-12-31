import re
import time
import requests
from bs4 import BeautifulSoup
from ddgs import DDGS

MAX_RESULTS = 50
SLEEP_SEARCH = 2
SLEEP_PAGE = 1

phone_regex = re.compile(r'(\+?\d[\d\s\-\(\)]{7,}\d)')


def normalize_phone(phone):
    phone = phone.strip()
    phone = re.sub(r'[^\d+]', '', phone)

    plus = phone.startswith('+')
    digits = re.sub(r'\D', '', phone)

    if len(digits) < 8 or len(digits) > 15:
        return None

    if len(set(digits)) == 1:
        return None

    if plus and digits.startswith('0'):
        return None

    if digits in ("123456789", "0123456789"):
        return None

    if len(digits) == 8 and not plus:
        return None

    return f"+{digits}" if plus else digits


def is_valid_phone(phone):
    digits = re.sub(r'\D', '', phone)

    if not 8 <= len(digits) <= 15:
        return False

    if len(set(digits)) == 1:
        return False

    # reject obvious price/commodity IDs
    if len(digits) >= 10 and digits[:3] in (
        "200", "300", "400", "500",
        "600", "700", "800", "900"
    ):
        return False

    return True


BAD_CONTEXT = [
    "price", "usd", "market", "commodity",
    "ton", "mt", "steel price", "rate"
]


def extract_phones_from_url(url):
    phones_found = set()

    try:
        r = requests.get(
            url,
            timeout=15,
            headers={"User-Agent": "Mozilla/5.0"}
        )

        soup = BeautifulSoup(r.text, "html.parser")
        text = soup.get_text(" ", strip=True).lower()

        if any(w in text for w in BAD_CONTEXT):
            return []

        raw_phones = re.findall(phone_regex, text)

        for ph in raw_phones:
            clean = normalize_phone(ph)
            if clean and is_valid_phone(clean):
                phones_found.add(clean)

    except:
        pass

    return list(phones_found)


SOCIAL_MEDIA_SITES = [
    "linkedin.com",
    "facebook.com",
    "instagram.com",
    "twitter.com",
    "t.me",
    "wa.me"
]


def is_social_media(url):
    return any(site in url for site in SOCIAL_MEDIA_SITES)


def search_and_extract(keyword):

    keyword_query = f"{keyword} contact phone whatsapp"
    results_set = set()

    with DDGS() as ddgs:
        for result in ddgs.text(keyword_query, max_results=MAX_RESULTS):
            url = result.get("href") or result.get("url")
            if not url:
                continue

            phones = extract_phones_from_url(url)

            if not phones and not is_social_media(url):
                contact_url = url.rstrip("/") + "/contact"
                phones = extract_phones_from_url(contact_url)

            for ph in phones:
                results_set.add((ph, url))

            time.sleep(SLEEP_PAGE)

    time.sleep(SLEEP_SEARCH)

    return list(results_set)
