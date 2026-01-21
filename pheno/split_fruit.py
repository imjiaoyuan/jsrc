import os
import argparse
import cv2
import numpy as np

def generate_filenames(base_name, count):
    parts = base_name.split('_')

    if len(parts) >= count:
        names = []

        first_part = parts[0]
        names.append(first_part)

        if '-' in first_part:
            prefix = first_part.rsplit('-', 1)[0] + '-'
        else:
            prefix = first_part + '-'

        for i in range(1, count):
            p = parts[i]
            names.append(prefix + p)
            
        return names
    else:
        return [f"{base_name}_{i+1}" for i in range(count)]

def process_fruit_cropped(input_path, output_dir, save_npy):
    img = cv2.imread(input_path)
    if img is None:
        return

    blurred = cv2.GaussianBlur(img, (5, 5), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
    
    mask_brightness = cv2.inRange(hsv, np.array([0, 0, 30]), np.array([180, 255, 255]))
    mask_saturation = cv2.inRange(hsv, np.array([0, 40, 0]), np.array([180, 255, 255]))
    
    mask_raw = cv2.bitwise_and(mask_brightness, mask_saturation)
    
    kernel_tiny = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    mask_fine = cv2.morphologyEx(mask_raw, cv2.MORPH_OPEN, kernel_tiny, iterations=1)
    
    kernel_close = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (20, 20))
    mask_coarse = cv2.morphologyEx(mask_fine, cv2.MORPH_CLOSE, kernel_close, iterations=2)
    
    kernel_open = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    mask_coarse = cv2.morphologyEx(mask_coarse, cv2.MORPH_OPEN, kernel_open, iterations=1)
    
    contours, _ = cv2.findContours(mask_coarse, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    h_img, w_img = mask_coarse.shape
    total_area = h_img * w_img
    
    valid_cnts = []
    
    for cnt in contours:
        area = cv2.contourArea(cnt)
        
        if area < total_area * 0.002:
            continue
            
        x, y, w, h = cv2.boundingRect(cnt)
        rect_area = w * h
        extent = float(area) / rect_area
        
        hull = cv2.convexHull(cnt)
        hull_area = cv2.contourArea(hull)
        solidity = float(area) / hull_area if hull_area > 0 else 0
        
        if solidity > 0.92 and extent > 0.85:
            continue
            
        roi_hsv = hsv[y:y+h, x:x+w]
        
        cnt_mask = np.zeros((h, w), dtype=np.uint8)
        cnt_shifted = cnt.copy()
        cnt_shifted[:, :, 0] -= x
        cnt_shifted[:, :, 1] -= y
        cv2.drawContours(cnt_mask, [cnt_shifted], -1, 255, -1)
        
        lower_blue_purple = np.array([100, 50, 50])
        upper_blue_purple = np.array([165, 255, 255])
        
        mask_artificial = cv2.inRange(roi_hsv, lower_blue_purple, upper_blue_purple)
        mask_check = cv2.bitwise_and(mask_artificial, mask_artificial, mask=cnt_mask)
        artificial_pixel_count = cv2.countNonZero(mask_check)
        
        if artificial_pixel_count > 100:
            continue
            
        aspect_ratio = float(w) / h
        if aspect_ratio < 0.1 or aspect_ratio > 10.0:
            continue

        valid_cnts.append(cnt)
        
    if valid_cnts:
        bboxes = [cv2.boundingRect(c) for c in valid_cnts]
        valid_cnts = [c for _, c in sorted(zip(bboxes, valid_cnts), key=lambda b: b[0][0])]

    base_name = os.path.splitext(os.path.basename(input_path))[0]
    final_names = generate_filenames(base_name, len(valid_cnts))
    
    for i, cnt in enumerate(valid_cnts):
        x, y, w, h = cv2.boundingRect(cnt)
        
        roi_bgr = img[y:y+h, x:x+w]
        
        mask_solid_roi = np.zeros((h, w), dtype=np.uint8)
        cnt_shifted = cnt.copy()
        cnt_shifted[:, :, 0] -= x
        cnt_shifted[:, :, 1] -= y
        cv2.drawContours(mask_solid_roi, [cnt_shifted], -1, 255, -1)
        
        mask_fine_roi = mask_fine[y:y+h, x:x+w]
        
        final_alpha = cv2.bitwise_and(mask_solid_roi, mask_fine_roi)
        
        b, g, r = cv2.split(roi_bgr)
        rgba = cv2.merge([b, g, r, final_alpha])
        
        current_name = final_names[i]
        
        cv2.imwrite(os.path.join(output_dir, f"{current_name}.png"), rgba)
        
        if save_npy:
            np.save(os.path.join(output_dir, f"{current_name}.npy"), cnt)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', required=True)
    parser.add_argument('-o', '--output', required=True)
    parser.add_argument('--save_npy', action='store_true')
    args = parser.parse_args()
    
    if not os.path.exists(args.output):
        os.makedirs(args.output)
        
    process_fruit_cropped(args.input, args.output, args.save_npy)