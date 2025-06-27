import cv2
import numpy as np
import matplotlib.pyplot as plt
import os

def region_growing(image, seeds, threshold_val, connectivity=8):
    """
    Performs region growing segmentation iteratively.
    Args:
        image: Input grayscale image.
        seeds: A list of (y, x) tuples for seed points.
        threshold_val: Max absolute intensity difference from the seed average.
        connectivity: 4 or 8 for neighbor connectivity.
    Returns:
        Segmented image (binary mask).
    """
    if image is None: raise ValueError("Input image is None.")
    if not seeds: raise ValueError("Seed points must be provided.")

    height, width = image.shape[:2]
    segmented_mask = np.zeros_like(image, dtype=np.uint8)
    
    # Calculate average intensity of initial seeds
    seed_intensities = [image[y, x] for y, x in seeds if 0 <= y < height and 0 <= x < width]
    if not seed_intensities:
        print("Warning: All seed points are outside image bounds.")
        return segmented_mask
        
    avg_seed_intensity = np.mean(seed_intensities)
    print(f"Average seed intensity: {avg_seed_intensity:.2f}")
    print(f"Intensity difference threshold: {threshold_val}")

    points_to_process = []
    for seed_y, seed_x in seeds:
        if 0 <= seed_y < height and 0 <= seed_x < width:
            if segmented_mask[seed_y, seed_x] == 0:
                points_to_process.append((seed_y, seed_x))
                segmented_mask[seed_y, seed_x] = 255

    # Define neighbors
    if connectivity == 8:
        neighbors = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    elif connectivity == 4:
        neighbors = [(-1, 0), (0, -1), (0, 1), (1, 0)]
    else:
        raise ValueError("Connectivity must be 4 or 8.")

    head = 0
    while head < len(points_to_process):
        curr_y, curr_x = points_to_process[head]
        head += 1

        for dy, dx in neighbors:
            ny, nx = curr_y + dy, curr_x + dx

            if 0 <= ny < height and 0 <= nx < width and segmented_mask[ny, nx] == 0:
                pixel_intensity = image[ny, nx]
                # Compare neighbor's intensity to the average intensity of the initial seeds
                if abs(int(pixel_intensity) - int(avg_seed_intensity)) <= threshold_val:
                    segmented_mask[ny, nx] = 255
                    points_to_process.append((ny, nx))
    
    return segmented_mask

def display_and_save_segmentation(original, segmented, seeds, output_dir, filename_suffix):
    """Displays and saves the segmentation result."""
    os.makedirs(output_dir, exist_ok=True)
    
    # Create an overlay image for visualization
    overlay = cv2.cvtColor(original, cv2.COLOR_GRAY2BGR)
    overlay[segmented == 255] = [0, 0, 255] # Mark segmented area in blue
    for y, x in seeds:
        cv2.circle(overlay, (x, y), 3, (0, 255, 0), -1) # Mark seeds in green

    plt.figure(figsize=(18, 6))
    plt.subplot(1, 3, 1)
    plt.imshow(original, cmap='gray')
    plt.title("Original Test Image")
    plt.axis('off')
    
    plt.subplot(1, 3, 2)
    plt.imshow(segmented, cmap='gray')
    plt.title("Segmented Mask")
    plt.axis('off')

    plt.subplot(1, 3, 3)
    plt.imshow(cv2.cvtColor(overlay, cv2.COLOR_BGR2RGB))
    plt.title("Segmentation Overlay")
    plt.axis('off')

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, f"segmentation_results_{filename_suffix}.png"))
    plt.show()

    # Save individual images
    cv2.imwrite(os.path.join(output_dir, f"segmentation_test_image.png"), original)
    cv2.imwrite(os.path.join(output_dir, f"segmented_mask_{filename_suffix}.png"), segmented)
    cv2.imwrite(os.path.join(output_dir, f"segmentation_overlay_{filename_suffix}.png"), overlay)


if __name__ == "__main__":
    print("--- Task 2: Region Growing Segmentation ---")
    output_directory = "results/task-2"
    
    # Create a test image
    height, width = 300, 300
    test_img = np.full((height, width), 40, dtype=np.uint8) # Background
    # Object 1 (darker)
    cv2.rectangle(test_img, (50, 50), (120, 120), 100, -1)
    # Object 2 (brighter)
    cv2.ellipse(test_img, (200, 200), (60, 40), 0, 0, 360, 180, -1)
    # Add noise
    noise = np.random.normal(0, 8, test_img.shape).astype(np.int16)
    test_img = np.clip(test_img.astype(np.int16) + noise, 0, 255).astype(np.uint8)

    # --- Test Case 1: Segmenting the rectangle ---
    seeds_rect = [(80, 80)]
    threshold_rect = 20 # Max intensity difference allowed
    print(f"\nSegmenting rectangle with seeds: {seeds_rect}")
    segmented_mask_rect = region_growing(test_img.copy(), seeds_rect, threshold_val=threshold_rect)
    display_and_save_segmentation(test_img, segmented_mask_rect, seeds_rect, output_directory, "rectangle")

    # --- Test Case 2: Segmenting the ellipse ---
    seeds_ellipse = [(200, 200)]
    threshold_ellipse = 25 # Threshold might need to be different
    print(f"\nSegmenting ellipse with seeds: {seeds_ellipse}")
    segmented_mask_ellipse = region_growing(test_img.copy(), seeds_ellipse, threshold_val=threshold_ellipse)
    display_and_save_segmentation(test_img, segmented_mask_ellipse, seeds_ellipse, output_directory, "ellipse")

    print("\nTask 2 Completed.")