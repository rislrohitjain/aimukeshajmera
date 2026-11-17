import os
import json
import logging
import urllib.request
import urllib.error

INDEXNOW_KEY = os.environ.get("INDEXNOW_KEY", "e4f05ba18384a6870ed8dfea1122335a")
HOST = "aimukeshajmera.vercel.app"

def notify_indexnow(urls):
    """
    Submits updated URLs to the official IndexNow API (supporting Bing, Yandex, etc.)
    using standard Python library to avoid external dependency issues.
    """
    if isinstance(urls, str):
        urls = [urls]

    payload = {
        "host": HOST,
        "key": INDEXNOW_KEY,
        "keyLocation": f"https://{HOST}/{INDEXNOW_KEY}.txt",
        "urlList": urls
    }

    req = urllib.request.Request(
        "https://api.indexnow.org/indexnow",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.status in (200, 202)
    except urllib.error.HTTPError as e:
        logging.warning(f"IndexNow HTTP response {e.code}: {e.reason}")
        return e.code in (200, 202)
    except Exception as e:
        logging.error(f"IndexNow notification failed: {e}")
        return False

def submit_core_pages_to_indexnow():
    core_urls = [
        f"https://{HOST}/",
        f"https://{HOST}/about-mukesh-ajmera",
        f"https://{HOST}/lic-services-sarwar",
        f"https://{HOST}/post-office-schemes",
        f"https://{HOST}/contact",
        f"https://{HOST}/blogs",
        f"https://{HOST}/sitemap.xml"
    ]
    return notify_indexnow(core_urls)
