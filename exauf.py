import shutil
import os
import http.server
import socketserver
import argparse

from pathlib import Path


PORT = 8000
TEMPLATE_PATH = "./source/template.html"
CONTENT_BLOCK = "{{ content }}"
TITLE_BLOCK = "{{ title }}"
HEADER_BLOCK = "{{ header }}"
STYLE_SOURCE_PATH = "./source/style.css"
STYLE_BUILD_PATH = "./docs/style.css"
KATEX_HEADER_PATH = "./source/katex_header.html"


def serve():
    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory="./docs", **kwargs)

    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"serving at http://localhost:{PORT}")
        httpd.serve_forever()


def build():
    with open(TEMPLATE_PATH) as f:
        TEMPLATE = f.read()
    with open(KATEX_HEADER_PATH) as f:
        KATEX_HEADER = f.read()

    shutil.rmtree("./docs", ignore_errors=True)
    os.mkdir("./docs")
    os.mkdir("./docs/e")

    ex_paths = Path("./source/e").glob("*.html")
    n_exs = 0
    for ex_path in ex_paths:
        uid = ex_path.stem
        html = ""
        is_meta = True
        meta = {}
        with open(ex_path) as f:
            for line in f.readlines():
                if line[0] != "\n" and is_meta:
                    line = line.replace("\n", "")
                    line = line.split(":")
                    assert len(line) == 2, "Syntax Error in meta"
                    key, values = line
                    values = [value.strip() for value in values.split(",")]
                    meta[key] = values
                else:
                    is_meta = False
                    html += line

        html = TEMPLATE.replace(CONTENT_BLOCK, html)
        html = html.replace(TITLE_BLOCK, uid)
        header = []
        if "dep" in meta:
            for dep in meta["dep"]:
                if dep == "math":
                    header.append(KATEX_HEADER)
        header = "".join(header)
        html = html.replace(HEADER_BLOCK, header)

        with open(f"./docs/e/{uid}.html", "w") as f:
            f.write(html)
        n_exs += 1

    print(f"INFO: Found {n_exs} excercises")

    shutil.copyfile(STYLE_SOURCE_PATH, STYLE_BUILD_PATH)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["build", "serve"])
    args = parser.parse_args()
    if args.mode == "build":
        build()
    elif args.mode == "serve":
        serve()
