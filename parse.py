import sys
import argparse
import pathlib
import json
import functools

from bs4 import BeautifulSoup
from bs4.element import NavigableString, Tag


def format_comment(commtext) -> str:
    out_parts = []
    for element in commtext.contents:
        if isinstance(element, NavigableString):
            out_parts.append(element.string)
        elif isinstance(element, Tag):
            if element.name == "a":
                out_parts.append(element.text)
            elif element.name == "p":
                out_parts.append("\n\n")
                out_parts.append(element.text)
            elif element.name == "pre":
                out_parts.append(element.text)
            elif element.name == "div" and "reply" in element["class"]:
                pass
            else:
                print(f"unexpected child tag '{element.name}': {element}", file=sys.stderr)

    return "".join(out_parts)


def main(args) -> int:
    if args.output_file:
        outfile_fd = pathlib.Path(args.output_file).open(mode="wt", encoding="utf-8")
        to_output = functools.partial(print, file=outfile_fd)
    else:
        to_output = functools.partial(print, file=sys.stdout)

    try:
        input_path = pathlib.Path(args.input_dir)
        for infile in input_path.iterdir():
            if not infile.name.endswith(".html"):
                print(f"skipping {infile.name}", file=sys.stderr)
                continue

            print(f"parsing {infile.name}", file=sys.stderr)
            contents = infile.open(mode="rt", encoding="utf-8").read()
            soup = BeautifulSoup(contents, "html5lib")

            for comtr in soup.find_all("tr", class_="comtr"):
                td_ind = comtr.find("td", class_="ind")
                if td_ind["indent"] != "0": # replies have an indent > 0
                    print(f"comment id {comment_id} is a reply, skipping", file=sys.stderr)
                    continue

                commtext_span = comtr.find("span", class_="commtext")
                if commtext_span is None:
                    print(f"comment id {comment_id} has no text, skipping", file=sys.stderr)
                    continue

                comment_id = int(comtr["id"])
                body = format_comment(commtext_span)
                
                out = {"comment_id":comment_id, "body":body}
                to_output(f"{json.dumps(out)}")

    finally:
        if args.output_file:
            outfile_fd.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Hacker News scraper")
    parser.add_argument("--input-dir", required=True, help="Directory to read scraped HTML files from")
    parser.add_argument("--output-file", required=False, help="Output file name (STDOUT if not set)")
    args = parser.parse_args()

    sys.exit(main(args))
