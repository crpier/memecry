#! /usr/bin/env python

import subprocess
import sys
from pathlib import Path

import httpx

# set some vars
USER = "cristi"
# PASSWORD = "boss"
PASSWORD = "kek"
# BASE_URL = "http://localhost:8000"
BASE_URL = "https://memecry.crpier.me"

# initial validation
DIR_WITH_FILES = Path(sys.argv[1])
if not DIR_WITH_FILES.is_dir():
    print(f"{DIR_WITH_FILES} is not a directory")

login_response = httpx.post(
    f"{BASE_URL}/signin", data={"username": USER, "password": PASSWORD}
)
AUTH_HEADER = {"Cookie": login_response.headers["set-cookie"].split(";")[0]}
print(AUTH_HEADER)

for file in DIR_WITH_FILES.iterdir():
    print(f"Looking at {file}")
    # subproc = subprocess.Popen(["open", file], stderr=subprocess.DEVNULL)
    # title = input("title: ")
    # content = input("content: ")
    # tags = input("tags: ")
    # if title == "<" or content == "<" or tags == "<":
    #     print("skipping")
    #     continue
    # if title == "d" and content == "d" and tags == "d":
    #     print("deleting")
    #     file.unlink()
    #     continue
    # if tags == "":
    #     tags = "no-tags"
    # tag_data = {}
    # for tag in tags.split(", "):
    #     tag_data[tag] = tag

    tag_data = {"off": "off"}
    title = ""
    content = ""
    response = httpx.post(
        f"{BASE_URL}/upload",
        headers=AUTH_HEADER,
        data={"title": title, "searchable_content": content} | tag_data,
        files={"file": open(file, "rb")},
    )
    if response.status_code < 203:
        file.unlink()
    print()
