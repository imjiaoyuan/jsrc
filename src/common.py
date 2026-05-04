import re
import os
import shutil
from typing import Dict, List, Tuple, Optional
import cv2
import numpy as np

def parse_gff_attributes(attr_string: str) -> Dict[str, str]:
    attrs = {}
    for item in attr_string.strip().strip(';').split(';'):
        if '=' in item:
            key, value = item.strip().split('=', 1)
            attrs[key] = value.strip('"')
        elif ' ' in item:
            parts = item.strip().split(None, 1)
            if len(parts) == 2:
                attrs[parts[0]] = parts[1].strip('"')
    return attrs

def get_gene_structure(gff_file: str, gene_ids: List[str], 
                       feature_types: Optional[List[str]] = None) -> Dict:
    if feature_types is None:
        feature_types = ['CDS', 'exon']
    
    target_set = set(gene_ids)
    valid_mrna = {}
    coords = {tid: [] for tid in gene_ids}
    
    with open(gff_file, 'r') as f:
        for line in f:
            if line.startswith('#'):
                continue
            parts = line.strip().split('\t')
            if len(parts) < 9:
                continue
            
            ftype = parts[2]
            attr = parse_gff_attributes(parts[8])
            
            if ftype == 'mRNA':
                pid = attr.get('Parent')
                mid = attr.get('ID')
                if pid in target_set:
                    valid_mrna[mid] = pid
            
            elif ftype in feature_types:
                pid = attr.get('Parent')
                if pid in valid_mrna:
                    gid = valid_mrna[pid]
                    coords[gid].append((int(parts[3]), int(parts[4])))
                elif pid in target_set:
                    coords[pid].append((int(parts[3]), int(parts[4])))
    
    return coords

def read_fasta_ids(fasta_file: str) -> List[str]:
    ids = []
    with open(fasta_file, 'r') as f:
        for line in f:
            if line.startswith('>'):
                ids.append(line[1:].split()[0])
    return ids

def sanitize_fasta_ids(input_file: str, output_file: str) -> Dict[str, str]:
    mapping = {}
    with open(input_file, 'r') as fin, open(output_file, 'w') as fout:
        for line in fin:
            if line.startswith('>'):
                old_id = line[1:].strip().split()[0]
                new_id = re.sub(r'[^A-Za-z0-9_-]', '_', old_id)
                mapping[new_id] = old_id
                fout.write(f'>{new_id}\n')
            else:
                fout.write(line)
    return mapping

def setup_matplotlib():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    return plt

def natural_sort_key(s):
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r'(\d+)', s)]

def check_external_tool(tool_name: str, install_hint: str = None):
    if not shutil.which(tool_name):
        msg = f"Error: {tool_name} not found in PATH"
        if install_hint:
            msg += f"\nInstall with: {install_hint}"
        raise RuntimeError(msg)

def apply_morphology(mask, operation='close', kernel_size=5):
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
    if operation == 'close':
        return cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    elif operation == 'open':
        return cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    elif operation == 'dilate':
        return cv2.dilate(mask, kernel)
    elif operation == 'erode':
        return cv2.erode(mask, kernel)
    return mask

def filter_contours(contours, min_area=100, max_area=None):
    filtered = []
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < min_area:
            continue
        if max_area and area > max_area:
            continue
        filtered.append(cnt)
    return filtered

def extract_roi_with_alpha(image, contour, padding=10):
    x, y, w, h = cv2.boundingRect(contour)
    x1 = max(0, x - padding)
    y1 = max(0, y - padding)
    x2 = min(image.shape[1], x + w + padding)
    y2 = min(image.shape[0], y + h + padding)
    
    roi = image[y1:y2, x1:x2].copy()
    mask = np.zeros((y2-y1, x2-x1), dtype=np.uint8)
    
    shifted_contour = contour - np.array([[x1, y1]])
    cv2.drawContours(mask, [shifted_contour], -1, 255, -1)
    
    if len(roi.shape) == 2:
        roi = cv2.cvtColor(roi, cv2.COLOR_GRAY2BGR)
    
    b, g, r = cv2.split(roi)
    rgba = cv2.merge([b, g, r, mask])
    
    return rgba
