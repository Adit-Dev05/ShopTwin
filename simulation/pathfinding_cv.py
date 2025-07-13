import cv2
import numpy as np
import heapq
import logging

# Use a binary aisle mask (white=walkable, black=not) as the walkable grid
# Place your mask at assets/aisle_mask.png, same size as the store map

def load_aisle_mask(mask_path):
    print(f"[DEBUG] Loading aisle mask from: {mask_path}")
    mask = cv2.imread(mask_path)
    if mask is None:
        raise FileNotFoundError(f"Mask image not found or could not be loaded: {mask_path}")
    hsv = cv2.cvtColor(mask, cv2.COLOR_BGR2HSV)
    # Yellow-green (main aisle)
    yellow_lower = np.array([20, 80, 80])
    yellow_upper = np.array([45, 255, 255])
    mask_yellow = cv2.inRange(hsv, yellow_lower, yellow_upper)
    # Purple (secondary aisle)
    purple_lower = np.array([120, 50, 50])
    purple_upper = np.array([160, 255, 255])
    mask_purple = cv2.inRange(hsv, purple_lower, purple_upper)
    # Walkable: yellow or purple
    walkable = ((mask_yellow > 0) | (mask_purple > 0)).astype(np.uint8)
    return walkable, mask

def heuristic(a, b):
    return np.linalg.norm(np.array(a) - np.array(b))

# Modified astar to support different costs for primary/secondary aisles
def astar(grid, start, goal):
    h, w = grid.shape
    open_set = []
    heapq.heappush(open_set, (0 + heuristic(start, goal), 0, start, [start]))
    visited = set()
    while open_set:
        _, cost, current, path = heapq.heappop(open_set)
        if current == goal:
            return path
        if current in visited:
            continue
        visited.add(current)
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(1,1),(-1,1),(1,-1)]:
            ny, nx = current[0]+dy, current[1]+dx
            if 0 <= ny < h and 0 <= nx < w and grid[ny, nx] > 0:
                # Cost: 1 for primary, 2 for secondary
                move_cost = 1 if grid[ny, nx] == 1 else 2
                heapq.heappush(open_set, (cost+move_cost+heuristic((ny,nx), goal), cost+move_cost, (ny,nx), path+[(ny,nx)]))
    logging.error(f"A* failed to find path: {start} -> {goal}")
    return None

# Update snap_to_aisle to snap to any walkable aisle (primary or secondary)
def snap_to_aisle(grid, point, max_radius=50):
    y, x = point
    h, w = grid.shape
    y = min(max(y, 0), h-1)
    x = min(max(x, 0), w-1)
    if grid[y, x] == 1:
        return (y, x)
    # Search in increasing radius
    for r in range(1, max_radius+1):
        for dy in range(-r, r+1):
            for dx in range(-r, r+1):
                ny, nx = y+dy, x+dx
                if 0 <= ny < h and 0 <= nx < w and grid[ny, nx] == 1:
                    return (ny, nx)
    # Fallback: use distance transform to find closest walkable pixel
    import cv2
    walkable = (grid == 1).astype(np.uint8)
    dist_transform = cv2.distanceTransform(1-walkable, cv2.DIST_L2, 5)
    min_idx = np.unravel_index(np.argmin(dist_transform + ((walkable==0)*1e6)), dist_transform.shape)
    logging.warning(f"No walkable pixel found near {point}, fallback to closest {min_idx}")
    return min_idx

# Debug: Overlay mask on map for visual inspection

def overlay_mask_on_map(map_img, mask_img, alpha=0.4):
    """Overlay the binary mask on the map image for debugging alignment."""
    # Ensure both images are the same size
    if map_img.shape[:2] != mask_img.shape[:2]:
        import cv2
        mask_img = cv2.resize(mask_img, (map_img.shape[1], map_img.shape[0]), interpolation=cv2.INTER_NEAREST)
    # Ensure both images are 3 channels
    if len(map_img.shape) == 2:
        map_img = cv2.cvtColor(map_img, cv2.COLOR_GRAY2BGR)
    if len(mask_img.shape) == 2:
        mask_colored = cv2.cvtColor(mask_img, cv2.COLOR_GRAY2BGR)
    elif mask_img.shape[2] == 4:
        mask_colored = cv2.cvtColor(mask_img, cv2.COLOR_BGRA2BGR)
    else:
        mask_colored = mask_img
    overlay = cv2.addWeighted(map_img, 1-alpha, mask_colored, alpha, 0)
    return overlay

def overlay_points_and_paths(img, snapped_stops, path_segments, failed_pairs, dwell_times=None, walkable_mask=None, section_names=None, visit_counts=None):
    walkability = []
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.55
    font_thickness = 1
    outline_thickness = 3
    label_offset = 16
    # Draw entrance and exit with outlined, modern markers
    for idx, pt in enumerate(snapped_stops):
        is_walkable = walkable_mask[pt[0], pt[1]] == 1 if walkable_mask is not None else True
        walkability.append(is_walkable)
        if idx == 0:  # Entrance
            color = (60, 220, 60)  # Softer green
            cv2.circle(img, (pt[1], pt[0]), 13, (255,255,255), -1, lineType=cv2.LINE_AA)
            cv2.circle(img, (pt[1], pt[0]), 10, color, -1, lineType=cv2.LINE_AA)
            cv2.circle(img, (pt[1], pt[0]), 13, color, 2, lineType=cv2.LINE_AA)
            cv2.putText(img, "S", (pt[1]-7, pt[0]+6), font, 0.7, (0,0,0), 2, cv2.LINE_AA)
        elif idx == len(snapped_stops) - 1:  # Exit
            color = (60, 60, 220)  # Softer blue
            cv2.circle(img, (pt[1], pt[0]), 13, (255,255,255), -1, lineType=cv2.LINE_AA)
            cv2.circle(img, (pt[1], pt[0]), 10, color, -1, lineType=cv2.LINE_AA)
            cv2.circle(img, (pt[1], pt[0]), 13, color, 2, lineType=cv2.LINE_AA)
            cv2.putText(img, "E", (pt[1]-7, pt[0]+6), font, 0.7, (0,0,0), 2, cv2.LINE_AA)
        else:  # Regular sections
            color = (255, 180, 60) if is_walkable else (200, 60, 60)
            cv2.circle(img, (pt[1], pt[0]), 9, (255,255,255), -1, lineType=cv2.LINE_AA)
            cv2.circle(img, (pt[1], pt[0]), 7, color, -1, lineType=cv2.LINE_AA)
            cv2.circle(img, (pt[1], pt[0]), 9, color, 1, lineType=cv2.LINE_AA)
        # Minimal, offset label
        if dwell_times and idx < len(dwell_times):
            time_val = dwell_times[idx]
            visits = 1
            if visit_counts and section_names and idx < len(section_names):
                visits = visit_counts.get(section_names[idx], 1)
            label = f"{time_val}m" if visits == 1 else f"{time_val}m({visits}x)"
            label_pos = (pt[1]+label_offset, pt[0]-label_offset)
            cv2.putText(img, label, label_pos, font, font_scale, (255,255,255), outline_thickness, cv2.LINE_AA)
            cv2.putText(img, label, label_pos, font, font_scale, (40,40,40), font_thickness, cv2.LINE_AA)
    # Draw path segments with soft, semi-transparent color and shadow
    overlay = img.copy()
    shadow = img.copy()
    for seg_idx, segment in enumerate(path_segments):
        for i in range(len(segment)-1):
            # Shadow (glow)
            cv2.line(shadow, (segment[i][1], segment[i][0]), (segment[i+1][1], segment[i+1][0]), (80,80,80), 7, lineType=cv2.LINE_AA)
            # Main path
            cv2.line(overlay, (segment[i][1], segment[i][0]), (segment[i+1][1], segment[i+1][0]), (255,80,80), 3, lineType=cv2.LINE_AA)
            # Only draw arrows at the end of each segment
            if i == len(segment) - 2:
                end_pt = (segment[i+1][1], segment[i+1][0])
                start_pt = (segment[i][1], segment[i][0])
                dx = end_pt[0] - start_pt[0]
                dy = end_pt[1] - start_pt[1]
                arrow_length = 13
                angle = np.arctan2(dy, dx)
                arrow_x = int(end_pt[0] - arrow_length * np.cos(angle))
                arrow_y = int(end_pt[1] - arrow_length * np.sin(angle))
                cv2.arrowedLine(overlay, (arrow_x, arrow_y), end_pt, (255, 80, 80), 2, tipLength=0.3, line_type=cv2.LINE_AA)
    # Blend overlays for soft effect
    cv2.addWeighted(shadow, 0.25, img, 0.75, 0, img)
    cv2.addWeighted(overlay, 0.7, img, 0.3, 0, img)
    # Draw failed connections
    for (start, end) in failed_pairs:
        cv2.line(img, (start[1], start[0]), (end[1], end[0]), (0,255,255), 2, lineType=cv2.LINE_AA)
    return img, walkability

def compute_full_path(grid, stops):
    h, w = grid.shape
    full_path = []
    snapped_stops = []
    for pt in stops:
        y, x = pt
        y = min(max(y, 0), h-1)
        x = min(max(x, 0), w-1)
        snapped_stops.append(snap_to_aisle(grid, (y, x)))
    for i in range(len(snapped_stops)-1):
        start, end = snapped_stops[i], snapped_stops[i+1]
        if not (0 <= start[0] < h and 0 <= start[1] < w and 0 <= end[0] < h and 0 <= end[1] < w):
            logging.error(f"Invalid coordinates for astar: {start} -> {end} (grid shape: {h}, {w})")
            continue
        segment = astar(grid, start, end)
        if segment is None:
            logging.error(f"A* failed to find path: {start} -> {end}")
            continue
        if i > 0:
            segment = segment[1:]  # avoid duplicate
        full_path.extend(segment)
    return full_path

def draw_path_on_image(img, path, color=(0,0,255), thickness=3):
    for i in range(len(path)-1):
        cv2.line(img, (path[i][1], path[i][0]), (path[i+1][1], path[i+1][0]), color, thickness)
    return img