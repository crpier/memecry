import re
from collections import defaultdict
from functools import lru_cache
from itertools import product
from pathlib import Path
from pprint import pprint

import cv2  # type: ignore
import matplotlib.pyplot as plt  # type: ignore
import numpy as np
import pytesseract  # type: ignore
from PIL import Image

INDEXABLE_SUFFIXES = [".png", ".jpg", ".jpeg"]


def _get_image_text(image_path: Path, debug=False, threshold=240, psm=11):
    im = np.array(Image.open(image_path))
    im = cv2.bilateralFilter(im, 5, 55, 60)  # type: ignore
    im = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)  # type: ignore
    _, im = cv2.threshold(im, threshold, 255, 1)  # type: ignore
    if debug:
        _save_intermediate_image(im)  # type: ignore
    custom_config = rf"--oem 3 --psm {psm}"
    return pytesseract.image_to_string(im, config=custom_config, lang="eng")


def _save_intermediate_image(im: Image.Image):
    plt.figure(figsize=(10, 10))
    plt.title("Edited Image")
    plt.imshow(im, cmap="gray")
    plt.xticks([])
    plt.yticks([])
    plt.savefig("edited.png", bbox_inches="tight")


def _cleanup_text(text: str):
    text = text.lower()
    text = text.replace("\n", " ")
    text = re.sub(r"[^a-zA-Z0-9 ]", "", text)
    while text.find("  ") != -1:
        text = text.replace("  ", " ")
    return text


@lru_cache
def _get_wordlist(source: Path = Path("static/wordlist.txt")):
    with open(source, "r") as f:
        return list(map(lambda x: x.lower(), f.read().split("\n")))


def _get_real_word_count(text: str):
    word_counter = 0
    wordlist = _get_wordlist()
    for word in text.split(" "):
        word = word.lower()
        if word.isdigit() or word in wordlist:
            word_counter += 1
    return word_counter


def get_text_from_image(image_path: Path, debug=False) -> str:
    if image_path.suffix not in INDEXABLE_SUFFIXES:
        return ""
    threshold_options = [240, 150]
    psm_options = [6, 11]
    results: dict[int, str] = defaultdict(str)
    for threshold_option, psm_option in product(threshold_options, psm_options):
        text = _cleanup_text(
            _get_image_text(
                image_path, threshold=threshold_option, psm=psm_option, debug=debug
            )
        )
        word_counter = _get_real_word_count(text)
        results[word_counter] += f" {text}"

    if debug:
        pprint(results)
    # I'd rather have all the options available
    return " ".join(results.values())


# print(get_text_from_image(Path("media/37.jpg")))
