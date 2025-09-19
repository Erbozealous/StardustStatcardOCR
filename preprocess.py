from typing import List, Tuple
import numpy as np
import cv2
import glob
import os
import json

def crop_img(img, bg_gray=50, debug_path=None):
    # Make sure it's uint8 for cv2
    if img.dtype != np.uint8:
        img = img.astype(np.uint8)
    
    H, W = img.shape
    
    # Start flood fill from the center
    center_y, center_x = H // 2, W // 2
    
    # Create a slightly larger mask for flood fill
    mask = np.zeros((H+2, W+2), np.uint8)
    flood_img = img.copy()

    # Replace a small region around the center with background gray
    block_size = 10  # Size of the gray block (10x10 pixels)
    half_block = block_size // 2
    y1 = max(0, center_y - half_block)
    y2 = min(H, center_y + half_block)
    x1 = max(0, center_x - half_block)
    x2 = min(W, center_x + half_block)
    flood_img[y1:y2, x1:x2] = bg_gray
    
    # Flood fill from center with a value different from bg_gray
    cv2.floodFill(flood_img, mask, (center_x, center_y), (127,), 
                  loDiff=(5,), upDiff=(5,), flags=4)  # flag 4 = 4-connected
    
    # Create binary mask of the flooded region
    flood_mask = (flood_img == 127).astype(np.uint8) * 255
    
    # Find contours of the flood-filled region
    contours, _ = cv2.findContours(flood_mask, cv2.RETR_EXTERNAL, 
                                 cv2.CHAIN_APPROX_SIMPLE)
    
    if not contours:
        return img
    
    # Get the largest contour
    largest_contour = max(contours, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(largest_contour)
    
    # Add size constraints
    min_area_ratio = 0.1  # Minimum area as fraction of total image
    min_area = H * W * min_area_ratio
    if cv2.contourArea(largest_contour) < min_area:
        if debug_path:
            debug_img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
            cv2.putText(debug_img, "Crop failed: Region too small", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)
            cv2.imwrite(f"{debug_path}/debug_crop.png", debug_img)
        return img  # Return original if detected region is too small

    if debug_path:
        debug_img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        cv2.rectangle(debug_img, (x,y),(x+w,y+h),(0,0,255),2)
        cv2.imwrite(f"{debug_path}/debug_crop.png", debug_img)



    return img[y:y+h, x:x+w]





def segment_lines(img, bg_gray=50, sep_threshold=200, min_height=7, verbose=0, debug_path=None) -> Tuple[List[Tuple[int,int]], int, int]:
    """
    Scan horizontally to detect line boxes in a grayscale image.

    Parameters:
        img (np.ndarray): Grayscale image (uint8).
        bg_gray (int): Background gray level (default 50).
        sep_threshold (int): Pixel count threshold to treat a row as a separator.
        min_height (int): Minimum height for a valid line box.
        debug_path (str): Path to save debug image (optional).

    Returns:
        list of tuples: [(y1, y2), ...] line bounding boxes.
    """
    
    H, W = img.shape
    line_boxes = []

    inside_line = False
    y_start = 0

    stat_boundary_left = 0
    stat_boundary_right = 0

    img[:, -3:] = 50

    for y in range(H):
        # Count non-background pixels in this row
        row_foreground = np.count_nonzero(img[y, :] != bg_gray)

        if not inside_line:
            # Look for line start
            if row_foreground > 0 and row_foreground < sep_threshold:
                inside_line = True
                y_start = y
        else:
            # Look for line end
            if row_foreground == 0 or row_foreground >= sep_threshold:
                y_end = y
                if y_start is not None and y_end - y_start >= min_height:
                    line_boxes.append((y_start, y_end))
                inside_line = False
                y_start = None

        if stat_boundary_left == 0 and stat_boundary_right == 0 and row_foreground >= sep_threshold:
            stat_boundary_left = 0
            while stat_boundary_left < W and not np.any(img[y, stat_boundary_left:stat_boundary_left+1] != bg_gray):
                stat_boundary_left += 1
            stat_boundary_right = W
            while stat_boundary_right > 0 and not np.any(img[y, stat_boundary_right:stat_boundary_right+1] != bg_gray):
                stat_boundary_right -= 1
            stat_boundary_right+=1
            if(verbose > 1): print(f"Stat Left:{stat_boundary_left} / Right: {stat_boundary_right}")

    # Handle last line if open at end of image
    if inside_line and y_start is not None:
        line_boxes.append((y_start, H - 1))

    # Debug visualization
    if debug_path:
        debug_img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        for (y1, y2) in line_boxes:
            cv2.rectangle(debug_img, (0, y1), (W - 1, y2), (0, 255, 0), 1)
        cv2.line(debug_img, (stat_boundary_left, 0), (stat_boundary_left, H), (255, 0, 0), 1)
        cv2.line(debug_img, (stat_boundary_right, 0), (stat_boundary_right, H), (255, 0, 0), 1)
        cv2.imwrite(f"{debug_path}/debug_lines.png", debug_img)

    if (verbose > 1): print(f"Detected {len(line_boxes)} lines.")

    return line_boxes, stat_boundary_left, stat_boundary_right


def segment_chars(line_img, bg_gray=50, debug_path=None, line_idx=0, settings=None, centered=False, rules= None, stat_left=0, stat_right=0) -> Tuple[List[Tuple[int,int,int,int]], bool]:
    """
    Segments a line of text into bounding boxes for each character.
    Assumes grayscale (0=black, 255=background).
    """
    if rules is None:
        rules = {
            "8": {
                "Lbracket": { "50": 20, "80": 8, "100": 2, "offset": -2 },
                "L":        { "50": 18, "80": 7, "100": 0, "offset": -1 },
                "F":        { "50": 21, "80": 6, "100": 1, "offset": -1 }
            }
        }

    if settings is None:
        settings = load_default_settings()



    # Custom width override
    if settings.get('custom_width', False):
        width_small = settings.get('width_small', 6)
        width_medium = settings.get('width_medium', 7)
        width_large = settings.get('width_large', 8)
    else:
        width_small = 6
        width_medium = 7
        width_large = 8

    imgH, imgW = line_img.shape

    def has_foreground(region):
        return np.any(region != bg_gray)
    
    # --- Step 1: Classify header vs stat ---
    mid = imgW // 2
    middle_cols = line_img[:, mid-5:mid+5]
    returnCentered = False
    if has_foreground(middle_cols):
        line_type = "HEADER"
        returnCentered = True
    else:
        line_type = "STAT"

    # Double check if the stat is just really long
    x=0
    while x < imgW and not has_foreground(line_img[:, x:x+1]):
            x += 1
    if(stat_left) and line_idx > 2: 
        line_type = "STAT"
        returnCentered = False

    boxes = []

    if(centered): line_type = "STAT"

    # --- Step 2a: Header segmentation ---
    if line_type == "HEADER":

        # The first 2 lines are usually 8-width, the rest are 7-width
        if line_idx < 2:
            char_width = width_large
        else:
            char_width = width_medium

        # Re-segment using fixed width boxes
        empty_thresh = 2
        

        x = 0
        
        # The header is centered, so we increase until the first non-empty pixel
        while x < imgW and not has_foreground(line_img[:, x:x+1]):
            x += 1

        # Offset detection
        exit_offset = False
        if char_width == width_large:
            test_box = line_img[:, x-2:x-2+char_width]   # <--- your test box
            hist = pixel_hist(test_box, bg_gray)
            char_rules = rules.get(str(char_width), {})
            if(settings.get('verbose', 1) > 1): print(f"Offset: {-2} - Hist: {hist}")
            offset = match_rule(hist, char_rules, verbose=settings.get('verbose', 1))
            if offset != 0:
                x += offset
                exit_offset = True

        # if needed, fall back to another test_box variation
        if not exit_offset:
            test_box = line_img[:, x-1:x-1+char_width]
            hist = pixel_hist(test_box, bg_gray)
            char_rules = rules.get(str(char_width), {})
            if(settings.get('verbose', 1) > 1): print(f"Offset: {-1} - Hist: {hist}")
            offset = match_rule(hist, char_rules, verbose=settings.get('verbose', 1))
            if offset != 0:
                x += offset
                exit_offset = True
                print(f"offset: {offset}")

        if(settings.get('verbose', 1) == 2): print(f"Line {line_idx} HEADER: char_width={char_width} offset_applied={exit_offset}")


        empty_count = 0
        while x + char_width <= imgW:
            region = line_img[:, x:x+char_width]
            boxes.append((x, 0, char_width, imgH))
            if has_foreground(region):
                empty_count = 0
            else:
                empty_count += 1
                if empty_count >= empty_thresh:
                    break
            x += char_width

        # Remove trailing empty boxes
        while boxes and not has_foreground(line_img[:, boxes[-1][0]:boxes[-1][0]+boxes[-1][2]]):
            boxes.pop()

    # --- Step 2b: Stat segmentation ---
    else:

        char_width = width_small
        empty_thresh = 2

        stopping_point = (imgW//3)*2 # 2/3 of the way across

        if(centered): stopping_point = imgW
        
        # Left → Right
        x = 0

        if(centered):
            while x < imgW and not has_foreground(line_img[:, x:x+1]):
                x += 1
        else:
            x = stat_left

        # Possible offsets
        exit_offset = False
        if(not exit_offset):
            test_box = line_img[:, x-1:x-1+char_width]
            # [: 24
            # 1: 17
            if np.sum(test_box != bg_gray) == 17 or np.sum(test_box != bg_gray) == 23:
                x -= 1
                exit_offset = True

        if(settings.get('verbose', 1) == 2): print(f"Line {line_idx} STAT: char_width={char_width} offset_applied={exit_offset}")


        empty_count = 0
        while x + char_width <= stopping_point:
            region = line_img[:, x:x+char_width]
            boxes.append((x, 0, char_width, imgH))
            if has_foreground(region):
                empty_count = 0
            else:
                empty_count += 1
                if empty_count >= empty_thresh:
                    break
            x += char_width

        # Remove trailing empty boxes
        while boxes and not has_foreground(line_img[:, boxes[-1][0]:boxes[-1][0]+boxes[-1][2]]):
            boxes.pop()

        # Add one whitespace box at the end for spacing
        if boxes and boxes[-1][0] + boxes[-1][2] < imgW:
            boxes.append((boxes[-1][0] + boxes[-1][2], 0, char_width, imgH))

        if not centered:
            # Right → Left
            x = stat_right
            empty_count = 0
            right_boxes = []

            

            while x - char_width >= mid:
                region = line_img[:, x-char_width:x]
                right_boxes.insert(0, (x-char_width, 0, char_width, imgH))
                if has_foreground(region):
                    empty_count = 0
                else:
                    empty_count += 1
                    if empty_count >= empty_thresh:
                        break
                x -= char_width

            # Remove LEADING empty boxes
            while right_boxes and not has_foreground(line_img[:, right_boxes[0][0]:right_boxes[0][0]+right_boxes[0][2]]):
                right_boxes.pop(0)

            boxes.extend(right_boxes)

    if debug_path:
        debug_img = cv2.cvtColor(line_img, cv2.COLOR_GRAY2BGR)
        for (x, y, w, h) in boxes:
            cv2.rectangle(debug_img, (x, y), (x+w-1, y+h-1), (0,0,255), 1)
        cv2.putText(debug_img, str(line_idx), (0, 10), cv2.FONT_HERSHEY_PLAIN, 1, (255,0,0), 1, 1, False)
        cv2.imwrite(f"{debug_path}/debug_chars_line{line_idx}.png", debug_img)


    # Finally, slice char imgs from the boxes
    char_imgs = [line_img[y:y+h, x:x+w] for (x, y, w, h) in boxes]

    

    return char_imgs, returnCentered


def merge_debug_lines(debug_path, verbose=0):
    images = []
    i = 0
    while True:
        path = os.path.join(debug_path, f"debug_chars_line{i}.png")
        if not os.path.exists(path):
            break
        img = cv2.imread(path)
        images.append(img)
        i += 1

    if not images:
        raise ValueError("No debug line images found.")
    
    max_width = max(img.shape[1] for img in images)
    total_height = sum(img.shape[0] for img in images)
    merged_img = np.zeros((total_height, max_width, 3), dtype=np.uint8)
    y_offset = 0
    for img in images:
        h, w, _ = img.shape
        merged_img[y_offset:y_offset+h, 0:w] = img
        y_offset += h
    # Save merged debug image
    cv2.imwrite(f"{debug_path}/merged_debug_chars.png", merged_img)
    if (verbose == 2): print("Merged debug image saved as debug_chars/merged_debug_chars.png")

    # Delete all individual lines
    files = glob.glob(os.path.join(debug_path, "debug_chars_line*.png"))
    for file_path in files:
        try:
            os.remove(file_path)
        except OSError as e:
            print(f"Error deleting {file_path}: {e.strerror}")

def pixel_hist(region, bg_gray):
    """Return histogram of non-background pixel values inside a region."""
    vals, counts = np.unique(region, return_counts=True)
    hist = {int(v): int(c) for v, c in zip(vals, counts) if v != bg_gray}
    return hist

def match_rule(hist, rules, tolerance=1, verbose=0):
    for char_name, rule in rules.items():
        expected = {int(k): v for k, v in rule.items() if k != "offset"}
        offset = rule["offset"]
        
        # Check expected counts
        ok = True
        for val, exp_count in expected.items():
            if abs(hist.get(val, 0) - exp_count) > tolerance:
                ok = False
                break

        # Check for unexpected values
        for val in hist:
            if val not in expected and hist[val] > tolerance:
                ok = False
                break
        if ok:
            if(verbose > 1): print(f"Testing rule {char_name}: Matched")
            return offset
            
    return 0


def segment_image(img, data_directory="OCR", debug_path=None, settings=None) -> List[List[np.ndarray]]:
    """
    Full OCR segmentation pipeline.
    1. Detect line boxes
    2. Segment each line into character boxes

    Returns list of char images for each line
    """

    if settings is None:
        settings = load_default_settings()


    img = crop_img(img, 50, debug_path)


    H, W = img.shape

    line_boxes, left, right = segment_lines(img, bg_gray=50,sep_threshold=200, debug_path=debug_path, verbose=settings.get('verbose', 0))

    offset_rules = {}
    with open(f"{data_directory}/offset_rules.json", "r") as f:
        offset_rules = json.load(f)

    all_chars = []
    char_boxes = []
    alignList = []
    for line_idx, (y1, y2) in enumerate(line_boxes, start=0):
        line_img = img[y1:y2, :]  # crop line
        char_boxes, align = segment_chars(line_img, bg_gray=50, debug_path=debug_path, settings=settings, line_idx=line_idx, rules=offset_rules, stat_left=left, stat_right=right)
        all_chars.append(char_boxes)
        alignList.append(align)

    # We will now go over alignList. If we detect a chunk of centered values(like 5 True in a row), we will mark those lines as actually stats for a second scan pass.
    i = 0
    while i < len(alignList):
        if alignList[i] and i>5:  # start of a centered region
            # find the extent of this chunk
            start = i
            while i < len(alignList) and alignList[i]:
                i += 1
            end = i - 1

            # mark all lines in the chunk except the first and last as "actuallyCenteredStat"
            for j in range(start, end):
                # rescan line j with actuallyCenteredStat=True
                line_img = img[line_boxes[j][0]:line_boxes[j][1], :]    
                char_boxes, _ = segment_chars(
                    line_img,
                    bg_gray=50,
                    debug_path=debug_path,
                    line_idx=j,
                    settings=settings,
                    centered=True,
                    rules=offset_rules
                )
                all_chars[j] = char_boxes  # replace with corrected boxes
        else:
            i += 1



    if(settings.get('save_images')): merge_debug_lines(debug_path, verbose=settings.get('verbose', 1))

    

    return all_chars

def load_default_settings():
    default_settings = {
            'verbose': 1,
            'custom_width': False,
            'width_small': 6,
            'width_medium': 7,
            'width_large': 8,
            'save_images': False,
            'existing_weapon': True,
            'theme': 'dark',
        }
    return default_settings



if __name__ == "__main__":
    verbose = True
    img_path = "weapon.png"
    debug_path = "debug"
    '''
    if sys.argv[1]:
        img_path = sys.argv[1]'''
    
    default_settings = {
            'verbose': 1,
            'custom_width': False,
            'width_small': 6,
            'width_medium': 7,
            'width_large': 8,
            'save_images': False,
            'existing_weapon': True,
            'theme': 'dark',
        }

    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    segment_image(img, debug_path=debug_path, settings=default_settings)

    
