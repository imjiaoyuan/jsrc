import os
import cv2
import numpy as np
from PIL import Image
from common import apply_morphology, filter_contours, extract_roi_with_alpha

def cmd_split_fruit(args):
    os.makedirs(args.o, exist_ok=True)
    
    img = cv2.imread(args.i)
    if img is None:
        print(f"Error: Cannot read image {args.i}")
        return
    
    h, w = img.shape[:2]
    scale = args.size / max(h, w)
    new_h, new_w = int(h * scale), int(w * scale)
    img_resized = cv2.resize(img, (new_w, new_h))
    
    hsv = cv2.cvtColor(img_resized, cv2.COLOR_BGR2HSV)
    
    lower = np.array([0, 30, 30])
    upper = np.array([180, 255, 255])
    mask = cv2.inRange(hsv, lower, upper)
    
    mask = apply_morphology(mask, 'close', 15)
    mask = apply_morphology(mask, 'open', 10)
    
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    contours = filter_contours(contours, min_area=500)
    
    for i, cnt in enumerate(contours):
        roi = extract_roi_with_alpha(img_resized, cnt, padding=20)
        
        out_path = os.path.join(args.o, f'fruit_{i:03d}.png')
        Image.fromarray(cv2.cvtColor(roi, cv2.COLOR_BGRA2RGBA)).save(out_path)
    
    print(f"Extracted {len(contours)} fruits to {args.o}")

def cmd_split_fruit_raw(args):
    os.makedirs(args.o, exist_ok=True)
    
    img = cv2.imread(args.i)
    if img is None:
        print(f"Error: Cannot read image {args.i}")
        return
    
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    lower = np.array([0, 30, 30])
    upper = np.array([180, 255, 255])
    mask = cv2.inRange(hsv, lower, upper)
    
    mask = apply_morphology(mask, 'close', 25)
    mask = apply_morphology(mask, 'open', 15)
    
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    contours = filter_contours(contours, min_area=2000)
    
    for i, cnt in enumerate(contours):
        roi = extract_roi_with_alpha(img, cnt, padding=30)
        
        out_path = os.path.join(args.o, f'fruit_raw_{i:03d}.png')
        Image.fromarray(cv2.cvtColor(roi, cv2.COLOR_BGRA2RGBA)).save(out_path)
    
    print(f"Extracted {len(contours)} fruits (original size) to {args.o}")

def cmd_split_leaf(args):
    os.makedirs(args.o, exist_ok=True)
    
    img = cv2.imread(args.i)
    if img is None:
        print(f"Error: Cannot read image {args.i}")
        return
    
    h, w = img.shape[:2]
    scale = args.size / max(h, w)
    new_h, new_w = int(h * scale), int(w * scale)
    img_resized = cv2.resize(img, (new_w, new_h))
    
    hsv = cv2.cvtColor(img_resized, cv2.COLOR_BGR2HSV)
    
    lower = np.array([35, 40, 40])
    upper = np.array([85, 255, 255])
    mask = cv2.inRange(hsv, lower, upper)
    
    mask = apply_morphology(mask, 'close', 12)
    mask = apply_morphology(mask, 'open', 8)
    
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    contours = filter_contours(contours, min_area=400)
    
    for i, cnt in enumerate(contours):
        roi = extract_roi_with_alpha(img_resized, cnt, padding=15)
        
        out_path = os.path.join(args.o, f'leaf_{i:03d}.png')
        Image.fromarray(cv2.cvtColor(roi, cv2.COLOR_BGRA2RGBA)).save(out_path)
    
    print(f"Extracted {len(contours)} leaves to {args.o}")

def cmd_split_leaf_edge(args):
    os.makedirs(args.o, exist_ok=True)
    
    img = cv2.imread(args.i)
    if img is None:
        print(f"Error: Cannot read image {args.i}")
        return
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    edges = cv2.Canny(blurred, 50, 150)
    
    edges = apply_morphology(edges, 'dilate', 3)
    edges = apply_morphology(edges, 'close', 5)
    
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    contours = filter_contours(contours, min_area=500)
    
    for i, cnt in enumerate(contours):
        mask = np.zeros(img.shape[:2], dtype=np.uint8)
        cv2.drawContours(mask, [cnt], -1, 255, 2)
        
        x, y, w, h = cv2.boundingRect(cnt)
        x1, y1 = max(0, x-20), max(0, y-20)
        x2, y2 = min(img.shape[1], x+w+20), min(img.shape[0], y+h+20)
        
        roi_edge = mask[y1:y2, x1:x2]
        roi_img = img[y1:y2, x1:x2]
        
        b, g, r = cv2.split(roi_img)
        rgba = cv2.merge([b, g, r, roi_edge])
        
        out_path = os.path.join(args.o, f'leaf_edge_{i:03d}.png')
        Image.fromarray(cv2.cvtColor(rgba, cv2.COLOR_BGRA2RGBA)).save(out_path)
    
    print(f"Extracted {len(contours)} leaf edges to {args.o}")
