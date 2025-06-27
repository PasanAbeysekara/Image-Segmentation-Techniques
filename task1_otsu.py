import cv2
import numpy as np
import matplotlib.pyplot as plt
import os

def create_synthetic_image(height=300, width=400, val_bg=60, val_obj1=140, val_obj2=220):
    image = np.full((height, width), val_bg, dtype=np.uint8)
    cv2.rectangle(image, (width//8, height//8), (width//2, height//2), val_obj1, -1)
    cv2.circle(image, (width*3//4, height*3//4), width//10, val_obj2, -1)
    return image

def add_gaussian_noise(image, mean=0, sigma=30):
    row, col = image.shape
    gauss = np.random.normal(mean, sigma, (row, col))
    noisy_image = image.astype(np.float32) + gauss
    noisy_image = np.clip(noisy_image, 0, 255)
    return noisy_image.astype(np.uint8)

def display_and_save_results(original, noisy, otsu_img, otsu_thresh_val, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    
    plt.figure(figsize=(18, 6))

    plt.subplot(1, 3, 1)
    plt.imshow(original, cmap='gray', vmin=0, vmax=255)
    plt.title("Original Synthetic Image")
    plt.axis('off')

    plt.subplot(1, 3, 2)
    plt.imshow(noisy, cmap='gray', vmin=0, vmax=255)
    plt.title("Image with Gaussian Noise")
    plt.axis('off')

    plt.subplot(1, 3, 3)
    plt.imshow(otsu_img, cmap='gray', vmin=0, vmax=255)
    plt.title(f"Otsu's Thresholding (Thresh = {otsu_thresh_val:.2f})")
    plt.axis('off')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "task1_comparison.png"))
    plt.show()

    cv2.imwrite(os.path.join(output_dir, "synthetic_original.png"), original)
    cv2.imwrite(os.path.join(output_dir, "synthetic_noisy.png"), noisy)
    cv2.imwrite(os.path.join(output_dir, "synthetic_otsu_thresholded.png"), otsu_img)
    
    plt.figure(figsize=(7, 5))
    plt.hist(noisy.ravel(), 256, [0, 256])
    plt.title("Histogram of Noisy Image")
    plt.xlabel("Pixel Intensity")
    plt.ylabel("Frequency")
    plt.axvline(x=otsu_thresh_val, color='r', linestyle='dashed', linewidth=2, label=f"Otsu's Threshold = {otsu_thresh_val:.2f}")
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.savefig(os.path.join(output_dir, "synthetic_noisy_histogram.png"))
    plt.show()


if __name__ == "__main__":
    output_directory = "results/task-1"
    synthetic_img = create_synthetic_image()
    noisy_img = add_gaussian_noise(synthetic_img.copy(), sigma=30)
    threshold_value, otsu_thresholded_img = cv2.threshold(
        noisy_img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )
    print(f"Optimal threshold value determined by Otsu's method: {threshold_value}") # in my case 104.00
    display_and_save_results(
        synthetic_img, noisy_img, otsu_thresholded_img, threshold_value, output_directory
    )