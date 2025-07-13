#!/usr/bin/env python3
"""
Script to resize the new aisle mask to match the store layout dimensions
"""

import cv2
import numpy as np
import json
import os

def resize_aisle_mask():
    """Resize the new aisle mask to match the store layout dimensions"""
    
    # Load store layout dimensions
    with open("data/store_layout.json", "r") as f:
        store_data = json.load(f)
    
    target_width = store_data["image_size"]["width"]  # 828
    target_height = store_data["image_size"]["height"]  # 646
    
    print(f"Target dimensions: {target_width}x{target_height}")
    
    # Load the new aisle mask
    mask_path = "assets/aisle_mask.png"
    if not os.path.exists(mask_path):
        print(f"Error: {mask_path} not found!")
        return False
    
    # Read the mask image
    mask = cv2.imread(mask_path)
    if mask is None:
        print(f"Error: Could not load {mask_path}")
        return False
    
    original_height, original_width = mask.shape[:2]
    print(f"Original mask dimensions: {original_width}x{original_height}")
    
    # Resize the mask to match the store layout
    resized_mask = cv2.resize(mask, (target_width, target_height), interpolation=cv2.INTER_NEAREST)
    
    # Save the resized mask
    output_path = "assets/aisle_mask_resized.png"
    success = cv2.imwrite(output_path, resized_mask)
    
    if success:
        print(f"Successfully resized and saved to {output_path}")
        print(f"New dimensions: {target_width}x{target_height}")
        
        # Verify the mask can be loaded by the pathfinding system
        try:
            from simulation.pathfinding_cv import load_aisle_mask
            walkable, _ = load_aisle_mask(output_path)
            print(f"Mask loaded successfully. Walkable area: {np.sum(walkable)} pixels")
            return True
        except Exception as e:
            print(f"Warning: Mask loaded but pathfinding test failed: {e}")
            return True
    else:
        print(f"Error: Failed to save resized mask to {output_path}")
        return False

if __name__ == "__main__":
    resize_aisle_mask() 