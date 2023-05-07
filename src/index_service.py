from pathlib import Path
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import cv2
import pytesseract


def get_image_text(image_path: Path, debug=False):
    im = np.array(Image.open(image_path))
    im = cv2.bilateralFilter(im, 5, 55, 60)  # type: ignore
    im = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)  # type: ignore
    _, im = cv2.threshold(im, 150, 255, 1)  # type: ignore

    if debug:
        plt.figure(figsize=(10, 10))
        plt.title("IMMAGINE BINARIA")
        plt.imshow(im, cmap="gray")
        plt.xticks([])
        plt.yticks([])
        plt.savefig("edited.png", bbox_inches="tight")

    custom_config = r"--oem 3 --psm 11"
    text = pytesseract.image_to_string(im, config=custom_config, lang="eng")
    print(text)
