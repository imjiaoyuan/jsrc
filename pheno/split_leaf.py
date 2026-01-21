import os
import argparse
import cv2
import numpy as np

def process_segmentation(input_path, output_dir):
    img = cv2.imread(input_path)
    if img is None:
        return

    blurred = cv2.GaussianBlur(img, (5, 5), 0)
    
    lab = cv2.cvtColor(blurred, cv2.COLOR_BGR2Lab)
    l_channel, a_channel, b_channel = cv2.split(lab)
    
    _, binary = cv2.threshold(a_channel, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel, iterations=2)
    binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel, iterations=2)
    
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    h_img, w_img = binary.shape
    total_area = h_img * w_img
    
    valid_cnts = []
    
    for cnt in contours:
        area = cv2.contourArea(cnt)
        
        if area < total_area * 0.0005:
            continue
        if area > total_area * 0.20:
            continue
            
        x, y, w, h = cv2.boundingRect(cnt)
        rect_area = w * h
        extent = float(area) / rect_area
        
        hull = cv2.convexHull(cnt)
        hull_area = cv2.contourArea(hull)
        solidity = float(area) / hull_area if hull_area > 0 else 0
        
        aspect_ratio = float(w) / h
        
        if extent > 0.90 and solidity > 0.95:
            continue
            
        if aspect_ratio > 5.0 or aspect_ratio < 0.2:
            continue

        valid_cnts.append(cnt)
        
    if valid_cnts:
        bboxes = [cv2.boundingRect(c) for c in valid_cnts]
        valid_cnts = [c for _, c in sorted(zip(bboxes, valid_cnts), key=lambda b: b[0][1])]

    base_name = os.path.splitext(os.path.basename(input_path))[0]
    
    for i, cnt in enumerate(valid_cnts):
        x, y, w, h = cv2.boundingRect(cnt)
        
        roi_bgr = img[y:y+h, x:x+w]
        
        mask = np.zeros((h, w), dtype=np.uint8)
        cnt_shifted = cnt.copy()
        cnt_shifted[:, :, 0] -= x
        cnt_shifted[:, :, 1] -= y
        
        cv2.drawContours(mask, [cnt_shifted], -1, 255, -1)
        
        b, g, r = cv2.split(roi_bgr)
        rgba = cv2.merge([b, g, r, mask])
        
        cv2.imwrite(os.path.join(output_dir, f"{base_name}_{i+1}_cutout.png"), rgba)
        np.save(os.path.join(output_dir, f"{base_name}_{i+1}.npy"), cnt)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', required=True)
    parser.add_argument('-o', '--output', required=True)
    args = parser.parse_args()
    
    if not os.path.exists(args.output):
        os.makedirs(args.output)
        
    process_segmentation(args.input, args.output)