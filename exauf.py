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
STYLE_SOURCE_PATH = "./source/style.css"
STYLE_BUILD_PATH = "./build/style.css"


def serve():
    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory="./build", **kwargs)

    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print("serving at port", PORT)
        httpd.serve_forever()


def build():
    with open(TEMPLATE_PATH) as f:
        TEMPLATE = f.read()

    shutil.rmtree("./build", ignore_errors=True)
    os.mkdir("./build")
    os.mkdir("./build/e")

    ex_paths = Path("./source/ex").glob("*.html")
    n_exs = 0
    for ex_path in ex_paths:
        uid = ex_path.stem
        with open(ex_path) as f:
            content = f.read()
            header, content = content.split("\n", 1)
        print(header)
        html = TEMPLATE.replace(CONTENT_BLOCK, content)
        html = html.replace(TITLE_BLOCK, uid)
        with open(f"./build/e/{uid}.html", "w") as f:
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
