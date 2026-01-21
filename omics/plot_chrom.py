import argparse
import re
import math
from PIL import Image, ImageDraw, ImageFont
import matplotlib.cm as cm
import matplotlib.colors as mcolors

def natural_sort_key(s):
    return [int(text) if text.isdigit() else text.lower() for text in re.split('([0-9]+)', s)]

def get_font(size):
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf",
        "arial.ttf",
        "Arial.ttf"
    ]
    for path in font_paths:
        try:
            return ImageFont.truetype(path, size)
        except IOError:
            continue
    return ImageFont.load_default()

def get_font_normal(size):
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans.ttf",
        "/usr/share/fonts/dejavu/DejaVuSans.ttf",
        "arial.ttf",
        "Arial.ttf"
    ]
    for path in font_paths:
        try:
            return ImageFont.truetype(path, size)
        except IOError:
            continue
    return ImageFont.load_default()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-ids', required=True)
    parser.add_argument('-gff', required=True)
    parser.add_argument('-fmt', default='transcript_id')
    parser.add_argument('-o', default='chrom_map_pil.png')
    args = parser.parse_args()

    target_ids = set()
    with open(args.ids, 'r') as f:
        for line in f:
            if line.strip():
                target_ids.add(line.strip())

    chrom_sizes = {}
    unique_gene_map = {}
    chrom_density = {}
    bin_size = 500000 

    with open(args.gff, 'r') as f:
        for line in f:
            if line.startswith('#'):
                continue
            parts = line.strip().split('\t')
            if len(parts) < 9:
                continue

            chrom = parts[0]
            try:
                start = int(parts[3])
                end = int(parts[4])
            except ValueError:
                continue
            
            attributes = parts[8]

            if chrom not in chrom_sizes:
                chrom_sizes[chrom] = 0
            if end > chrom_sizes[chrom]:
                chrom_sizes[chrom] = end

            bin_idx = start // bin_size
            if chrom not in chrom_density:
                chrom_density[chrom] = {}
            if bin_idx not in chrom_density[chrom]:
                chrom_density[chrom][bin_idx] = 0
            chrom_density[chrom][bin_idx] += 1

            pattern = args.fmt + r'\s+"?([^";]+)"?'
            match = re.search(pattern, attributes)
            
            if not match and '=' in attributes:
                pattern_gff = args.fmt + r'=([^;]+)'
                match = re.search(pattern_gff, attributes)

            if match:
                tid = match.group(1)
                if tid in target_ids:
                    key = (chrom, tid)
                    if key not in unique_gene_map:
                        unique_gene_map[key] = start
                    else:
                        if start < unique_gene_map[key]:
                            unique_gene_map[key] = start

    final_gene_map = {}
    for (chrom, tid), start in unique_gene_map.items():
        if chrom not in final_gene_map:
            final_gene_map[chrom] = []
        final_gene_map[chrom].append((start, tid))

    sorted_chroms = sorted(chrom_sizes.items(), key=lambda x: x[1], reverse=True)
    if not sorted_chroms:
        return

    max_len = sorted_chroms[0][1]
    main_chroms = []
    for chrom, size in sorted_chroms:
        if size > max_len * 0.05:
            main_chroms.append(chrom)
    
    main_chroms = sorted(main_chroms, key=natural_sort_key)

    all_counts = []
    for chrom in chrom_density:
        for b_idx in chrom_density[chrom]:
            all_counts.append(chrom_density[chrom][b_idx])
    
    max_density = max(all_counts) if all_counts else 1
    cmap = cm.YlGnBu
    norm = mcolors.Normalize(vmin=0, vmax=max_density)

    img_width = 4200
    img_height = 2600
    background_color = (255, 255, 255)
    image = Image.new('RGB', (img_width, img_height), background_color)
    draw = ImageDraw.Draw(image)

    margin_top = 100
    margin_bottom = 150
    margin_left = 350 
    margin_right = 600  
    
    available_height = img_height - margin_top - margin_bottom
    
    chrom_width_px = 100
    gap_px = 400

    scale_factor = available_height / max_len

    font_label = get_font(40)
    font_gene = get_font_normal(32)
    font_axis = get_font_normal(36)

    axis_line_x = 220
    tick_start_x = 220
    tick_end_x = 205
    text_end_x = 195
    
    draw.line([(axis_line_x, margin_top), (axis_line_x, margin_top + max_len * scale_factor)], fill=(0,0,0), width=4)
    
    num_ticks = 8
    tick_step = max_len / num_ticks
    for i in range(num_ticks + 1):
        bp_val = i * tick_step
        y_pos = margin_top + bp_val * scale_factor
        draw.line([(tick_end_x, y_pos), (tick_start_x, y_pos)], fill=(0,0,0), width=4)
        
        label_text = f"{bp_val / 1e6:.1f}"
        bbox = draw.textbbox((0, 0), label_text, font=font_axis)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        draw.text((text_end_x - text_w, y_pos - text_h/2), label_text, fill=(0,0,0), font=font_axis)

    axis_title = "Position (Mb)"
    bbox = draw.textbbox((0, 0), axis_title, font=font_label)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    
    txt_img = Image.new('RGBA', (w + 20, h + 20), (255, 255, 255, 0))
    d_txt = ImageDraw.Draw(txt_img)
    d_txt.text((0, 0), axis_title, fill=(0, 0, 0), font=font_label)
    txt_img = txt_img.rotate(90, expand=True)
    image.paste(txt_img, (30, int(margin_top + (max_len * scale_factor)/2 - w/2)), txt_img)

    for i, chrom in enumerate(main_chroms):
        x_start = margin_left + i * (chrom_width_px + gap_px)
        chrom_len_px = chrom_sizes[chrom] * scale_factor
        
        chr_img = Image.new('RGBA', (int(chrom_width_px), int(chrom_len_px)), (0,0,0,0))
        chr_draw = ImageDraw.Draw(chr_img)
        
        num_bins = math.ceil(chrom_sizes[chrom] / bin_size)
        current_density = chrom_density.get(chrom, {})
        
        for b in range(num_bins):
            bin_start_px = (b * bin_size) * scale_factor
            bin_end_px = min(((b + 1) * bin_size) * scale_factor, chrom_len_px)
            
            count = current_density.get(b, 0)
            rgba = cmap(norm(count))
            color_tuple = (int(rgba[0]*255), int(rgba[1]*255), int(rgba[2]*255))
            
            chr_draw.rectangle([0, bin_start_px, chrom_width_px, bin_end_px], fill=color_tuple)

        mask = Image.new('L', (int(chrom_width_px), int(chrom_len_px)), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.rounded_rectangle([0, 0, chrom_width_px, chrom_len_px], radius=25, fill=255)
        
        final_chr = Image.new('RGB', (int(chrom_width_px), int(chrom_len_px)), (255,255,255))
        final_chr.paste(chr_img, (0,0), mask)
        
        border_layer = Image.new('RGBA', (int(chrom_width_px), int(chrom_len_px)), (0,0,0,0))
        border_draw = ImageDraw.Draw(border_layer)
        border_draw.rounded_rectangle([0, 0, chrom_width_px-1, chrom_len_px-1], radius=25, outline=(100,100,100), width=3)
        
        image.paste(final_chr, (int(x_start), int(margin_top)))
        image.paste(border_layer, (int(x_start), int(margin_top)), border_layer)

        c_name = f"Chr {i+1}"
        bbox = draw.textbbox((0, 0), c_name, font=font_label)
        cw = bbox[2] - bbox[0]
        ch = bbox[3] - bbox[1]
        
        name_img = Image.new('RGBA', (cw + 20, ch + 20), (255,255,255,0))
        dn = ImageDraw.Draw(name_img)
        dn.text((0,0), c_name, fill=(50,50,50), font=font_label)
        name_img = name_img.rotate(90, expand=True)
        
        image.paste(name_img, (int(x_start - ch - 35), int(margin_top + chrom_len_px/2 - cw/2)), name_img)

    for i, chrom in enumerate(main_chroms):
        if chrom not in final_gene_map:
            continue
            
        x_start = margin_left + i * (chrom_width_px + gap_px)
        
        genes = sorted(final_gene_map[chrom], key=lambda x: x[0])
        label_step_px = 42 
        current_label_y_px = -10000
        
        for g_pos, g_id in genes:
            y_px = margin_top + g_pos * scale_factor
            draw.line([(x_start, y_px), (x_start + chrom_width_px, y_px)], fill=(255,0,0), width=5)
            
            label_y = max(y_px, current_label_y_px + label_step_px)
            current_label_y_px = label_y
            
            l_start_x = x_start + chrom_width_px + 2
            l_mid_x = x_start + chrom_width_px + 20
            l_end_x = x_start + chrom_width_px + 50
            
            draw.line([(l_start_x, y_px), (l_mid_x, label_y), (l_end_x, label_y)], fill=(80,80,80), width=3)
            draw.text((l_end_x + 10, label_y - 18), g_id, fill=(0,0,0), font=font_gene)

    image.save(args.o, dpi=(300, 300))

if __name__ == "__main__":
    main()