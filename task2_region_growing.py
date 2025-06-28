import cv2
import numpy as np
import matplotlib.pyplot as plt
import os

def region_growing(image, seeds, threshold_val, connectivity=8):

    if image is None: raise ValueError("Input image is None.")
    if not seeds: raise ValueError("Seed points must be provided.")

    height, width = image.shape[:2]
    segmented_mask = np.zeros_like(image, dtype=np.uint8)
    
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
                if abs(int(pixel_intensity) - int(avg_seed_intensity)) <= threshold_val:
                    segmented_mask[ny, nx] = 255
                    points_to_process.append((ny, nx))
    
    return segmented_mask

def display_and_save_segmentation(original, segmented, seeds, output_dir, filename_suffix):
    os.makedirs(output_dir, exist_ok=True)
    
    overlay = cv2.cvtColor(original, cv2.COLOR_GRAY2BGR)
    overlay[segmented == 255] = [0, 0, 255] # Mark segmented area in red
    for y, x in seeds:
        cv2.circle(overlay, (x, y), 3, (0, 255, 0), -1) # Mark seeds in green

    plt.figure(figsize=(18, 6))
    plt.subplot(1, 3, 1)
    plt.imshow(original, cmap='gray')
    plt.title("Original Brain MRI")
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

    cv2.imwrite(os.path.join(output_dir, f"brain_mri_original.png"), original)
    cv2.imwrite(os.path.join(output_dir, f"segmented_mask_{filename_suffix}.png"), segmented)
    cv2.imwrite(os.path.join(output_dir, f"segmentation_overlay_{filename_suffix}.png"), overlay)


if __name__ == "__main__":
    output_directory = "results/task-2"
    image_path = "input/brain_image.jpg"

    try:
        brain_img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if brain_img is None:
            raise FileNotFoundError(f"Image not found at path: {image_path}")
    except FileNotFoundError as e:
        print(e)
        exit()
    except Exception as e:
        print(f"An error occurred while loading the image: {e}")
        exit()

    # Test Case 1: Segmenting White Matter
    seeds_white_matter = [(215, 225)]
    threshold_white_matter = 15
    
    print(f"\nSegmenting White Matter with seeds: {seeds_white_matter}")
    segmented_mask_wm = region_growing(brain_img.copy(), seeds_white_matter, threshold_val=threshold_white_matter)
    display_and_save_segmentation(brain_img, segmented_mask_wm, seeds_white_matter, output_directory, "white_matter")

    # Test Case 2: Segmenting Gray Matter
    seeds_gray_matter = [(150, 150)]
    threshold_gray_matter = 15
    
    print(f"\nSegmenting Gray Matter with seeds: {seeds_gray_matter}")
    segmented_mask_gm = region_growing(brain_img.copy(), seeds_gray_matter, threshold_val=threshold_gray_matter)
    display_and_save_segmentation(brain_img, segmented_mask_gm, seeds_gray_matter, output_directory, "gray_matter")
