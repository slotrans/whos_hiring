import sys
import os
import argparse
import pathlib
import time

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://news.ycombinator.com/"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0" # FF 89.0.2


def get_next_page(body: str) -> str:
    soup = BeautifulSoup(body, "html.parser")

    # "More" link looks like <a href="item?id=28719320&amp;p=2" class="morelink" rel="next">More</a>
    # there's only ever 1 or 0 of these in the page
    for link in soup.find_all("a", class_="morelink"):
        return f"{BASE_URL}{link['href']}"

    return None


def main(args) -> int:
    # ensure output directory
    os.makedirs(args.output_dir, exist_ok=True)

    # go get pages and save them
    req_headers = {"User-Agent": USER_AGENT}

    pagenum = 1
    url = args.url
    while(url is not None and pagenum <= args.max_pages):
        if pagenum > 1:
            print("(waiting...)")
            time.sleep(5)
        print(f"requesting page {url}")
        response = requests.get(url, headers=req_headers)
        
        if response.status_code != 200:
            print(f"ERROR: status code {response.status_code}", file=sys.stderr)
            print(response.text, file=sys.stderr)
            return 1

        outpath = pathlib.Path(".") / args.output_dir / f"page{pagenum:0>2}.html"
        if args.clobber or not outpath.exists():
            with outpath.open(mode="wt", encoding="utf-8") as f:
                f.write(response.text)

        url = get_next_page(response.text)
        pagenum += 1

    print("done.")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Hacker News scraper")
    parser.add_argument("--url", required=True, help="Base HN URL to begin scrape from")
    parser.add_argument("--output-dir", required=True, help="Directory to store output in, will be created if it does not exist")
    parser.add_argument("--clobber", required=False, action="store_true", help="If set, overwrite existing files")
    parser.add_argument("--max-pages", required=False, type=int, default=999, help="Exit after retrieving this many pages")
    args = parser.parse_args()

    sys.exit(main(args))
