import sys
import argparse
import pathlib
import json

from bs4 import BeautifulSoup


def main(args) -> int:
    input_path = pathlib.Path(args.input_dir)
    for infile in input_path.iterdir():
        if not infile.name.endswith(".html"):
            print(f"skipping {infile.name}", file=sys.stderr)
            continue

        print(f"parsing {infile.name}", file=sys.stderr)
        contents = infile.open(mode="rt", encoding="utf-8").read()
        soup = BeautifulSoup(contents, "html.parser")

        for comtr in soup.find_all("tr", class_="comtr"):
            comment_id = int(comtr["id"])

            commtext_span = comtr.find("span", class_="commtext")
            if commtext_span is None:
                print(f"comment id {comment_id} has no text, skippping", file=sys.stderr)
            else:
                #safe_body = commtext_span.text.replace("\t", " ") # unlikely, but be safe
                #safe_body = safe_body.replace("\n", " ") # annoying
                #print(f"{comment_id}\t{safe_body}")
                out = {"comment_id":comment_id, "body":commtext_span.text}
                print(f"{json.dumps(out)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Hacker News scraper")
    parser.add_argument("--input-dir", required=True, help="Directory to read scraped HTML files from")
    #parser.add_argument("--output-file", required=False, help="Output file name (STDOUT if not set)")
    args = parser.parse_args()

    sys.exit(main(args))
