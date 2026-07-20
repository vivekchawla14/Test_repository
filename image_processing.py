import cv2
import numpy as np
import matplotlib.pyplot as plt


class ImageProcessing:
    @staticmethod
    def find_red_cross(image):
        """
        Detects a red cross in the input image.

        Parameters:
            image (numpy.ndarray): The input RGB image.

        Returns:
            tuple: (crosshair_X, crosshair_Y, red_mask) coordinates of the cross center and mask.
        """
        # Convert the image to HSV color space
        image2 = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        hsv_img = cv2.cvtColor(image2, cv2.COLOR_BGR2HSV)

        # Define HSV range for red color
        lower_red1 = np.array([0, 70, 50])  # Lower red range (hue near 0)
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([170, 70, 50])  # Upper red range (hue near 180)
        upper_red2 = np.array([180, 255, 255])

        # Create masks for red color
        mask1 = cv2.inRange(hsv_img, lower_red1, upper_red1)
        mask2 = cv2.inRange(hsv_img, lower_red2, upper_red2)
        red_mask = cv2.bitwise_or(mask1, mask2)

        # Find contours in the red mask
        contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = min(w, h) / max(w, h)
            if 0.8 < aspect_ratio < 1.2 and w > 20 and h > 20:  # Adjust size as needed
                crosshair_X = x + w // 2
                crosshair_Y = y + h // 2
                return crosshair_X, crosshair_Y, red_mask

        return None, None, red_mask

    @staticmethod
    def display_red_cross(image, red_mask, crosshair_coords):
        """
        Displays the input image with the detected red cross highlighted.

        Parameters:
            image (numpy.ndarray): The input RGB image.
            red_mask (numpy.ndarray): The binary mask highlighting red regions.
            crosshair_coords (tuple): (crosshair_X, crosshair_Y) coordinates of the detected cross center.
        """
        # Create a copy of the image for visualization
        result_img = image.copy()

        if crosshair_coords:
            crosshair_X, crosshair_Y = crosshair_coords
            cv2.circle(result_img, (crosshair_X, crosshair_Y), 10, (0, 255, 0), -1)
            cv2.putText(result_img, "Red Cross", (crosshair_X + 10, crosshair_Y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

        # Display results
        plt.figure(figsize=(15, 5))

        plt.subplot(1, 2, 1)
        plt.title("Red Mask")
        plt.imshow(red_mask, cmap="gray")
        plt.axis("off")

        plt.subplot(1, 2, 2)
        plt.title("Detected Red Cross")
        plt.imshow(cv2.cvtColor(result_img, cv2.COLOR_BGR2RGB))
        plt.axis("off")

        plt.show()

    @staticmethod
    def detect_circles_with_contours(image, radius_range, X_scale, Y_scale):
        """
        Detect circles using contour approximation and filtering.

        Parameters:
            image (numpy.ndarray): Input image (grayscale or color).
            radius_range (tuple): Min and max radius of circles in microns.
            X_scale, Y_scale (float): Pixels per micron.

        Returns:
            tuple: List of detected circles as (x, y, radius) in pixels, and list of centers (x, y).
        """
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        # Normalize brightness
        normalized = cv2.normalize(gray, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX)

        # Blur and binarize the image
        blurred = cv2.GaussianBlur(normalized, (5, 5), 0)
        _, binary = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # Find contours
        contours, _ = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        detected_circles = []
        detected_circles_with_radius = []

        min_radius_px = radius_range[0] * X_scale
        max_radius_px = radius_range[1] * Y_scale

        for contour in contours:
            (x, y), radius = cv2.minEnclosingCircle(contour)
            radius_px = int(radius)

            if min_radius_px <= radius_px <= max_radius_px:
                perimeter = cv2.arcLength(contour, True)
                area = cv2.contourArea(contour)
                if area > 0 and (4 * np.pi * area / (perimeter ** 2) > 0.8):
                    detected_circles_with_radius.append((int(x), int(y), radius_px))
                    detected_circles.append((int(x), int(y)))

        return detected_circles, detected_circles_with_radius

    @staticmethod
    def visualize_detected_circles(image, circles_with_radius):
        """
        Visualizes detected circles on the image.

        Parameters:
            image (numpy.ndarray): Input image (grayscale or color).
            circles_with_radius (list): List of detected circles as (x, y, radius).
        """
        output_image = image.copy()
        if len(output_image.shape) == 2:
            output_image = cv2.cvtColor(output_image, cv2.COLOR_GRAY2BGR)

        for (x, y, r) in circles_with_radius:
            cv2.circle(output_image, (x, y), r, (0, 255, 0), 2)
            cv2.circle(output_image, (x, y), 2, (0, 0, 255), 3)

        plt.imshow(cv2.cvtColor(output_image, cv2.COLOR_BGR2RGB))
        plt.title("Detected Circles")
        plt.axis("off")
        plt.show()
