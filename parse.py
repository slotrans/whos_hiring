import sys
import argparse
import pathlib
import json
import functools

from bs4 import BeautifulSoup


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
            soup = BeautifulSoup(contents, "html.parser")

            for comtr in soup.find_all("tr", class_="comtr"):
                td_ind = comtr.find("td", class_="ind")
                if td_ind["indent"] != "0": # replies have an indent > 0
                    print(f"comment id {comment_id} is a reply, skipping", file=sys.stderr)
                    continue

                commtext_span = comtr.find("span", class_="commtext")
                if commtext_span is None:
                    print(f"comment id {comment_id} has no text, skippping", file=sys.stderr)
                    continue

                comment_id = int(comtr["id"])

                out = {"comment_id":comment_id, "body":commtext_span.text}
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
