import cv2
import numpy as np


def get_channel_image(img: np.ndarray, channel: str) -> np.ndarray:
    if channel == "gray":
        return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    if channel in {"a", "b"}:
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2Lab)
        _, a_channel, b_channel = cv2.split(lab)
        return a_channel if channel == "a" else b_channel
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    _, s_channel, v_channel = cv2.split(hsv)
    return s_channel if channel == "s" else v_channel


def ensure_odd(value: int) -> int:
    if value < 1:
        return 1
    return value if value % 2 == 1 else value + 1
