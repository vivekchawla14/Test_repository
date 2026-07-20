import numpy as np
import cv2
from scipy.interpolate import griddata
import matplotlib.pyplot as plt


class ContourOverlayAlignerCV:
    def __init__(self, screenshot, selected_data, scale_x, scale_y, Z_var='MODULUS'):
        """
        Initialize the ContourOverlayAligner with the screenshot and test data.

        Parameters:
            screenshot (numpy.ndarray): Screenshot image as a NumPy array.
            selected_data (pandas.DataFrame): DataFrame containing 'X Position', 'Y Position', and Z variable.
            scale_x (float): Pixels per micron for the X-axis.
            scale_y (float): Pixels per micron for the Y-axis.
            Z_var (str): The variable to plot as the Z axis (e.g., 'MODULUS', 'HARDNESS').
        """
        if Z_var not in selected_data.columns:
            raise ValueError(f"{Z_var} is not a valid column in the provided data.")

        self.screenshot = screenshot
        self.selected_data = selected_data
        self.scale_x = scale_x
        self.scale_y = scale_y
        self.Z_var = Z_var

        # Initialize offsets to center the contour plot
        self.offset_x = screenshot.shape[1] // 2
        self.offset_y = screenshot.shape[0] // 2
        self.bottom_right_pixel = None  # Store the bottom-right pixel of the aligned contour
        self.confirmed = False  # Flag to check if alignment is confirmed

        # Extract X, Y, and Z values from the test data
        self.x_microns = selected_data['X Position'].values
        self.y_microns = selected_data['Y Position'].values
        self.z_values = selected_data[Z_var].values

        # Handle NaN values in Z
        valid_mask = ~np.isnan(self.z_values)
        self.x_microns = self.x_microns[valid_mask]
        self.y_microns = self.y_microns[valid_mask]
        self.z_values = self.z_values[valid_mask]

        # Map microns to pixels
        self.x_pixels = self.x_microns * scale_x
        self.y_pixels = self.y_microns * scale_y

        # Create a grid for contour plotting
        self.xi = np.linspace(self.x_pixels.min(), self.x_pixels.max(), 500)
        self.yi = np.linspace(self.y_pixels.min(), self.y_pixels.max(), 500)
        self.xi, self.yi = np.meshgrid(self.xi, self.yi)
        self.zi = griddata((self.x_pixels, self.y_pixels), self.z_values, (self.xi, self.yi), method='cubic')

    def show_contour_plot(self, clim=None):
        """
        Displays the contour plot for user confirmation.

        Parameters:
            clim (tuple, optional): Color limits for the plot as (min, max). If None, use automatic scaling.
        """
        plt.figure(figsize=(8, 6))
        contour = plt.contourf(self.xi, self.yi, self.zi, levels=100, cmap='jet')
        if clim is not None:
            contour.set_clim(*clim)
        plt.colorbar(label=self.Z_var)
        plt.title(f"Contour Plot of {self.Z_var}")
        plt.xlabel("X Pixels")
        plt.ylabel("Y Pixels")
        plt.show()

    def overlay_contour(self):
        """
        Overlay the contour plot on the screenshot using the current offsets.
        """
        # Create a transparent overlay
        overlay = self.screenshot.copy()
        contour_img = np.zeros_like(self.screenshot, dtype=np.uint8)

        # Normalize the Z values for visualization
        min_z, max_z = np.nanmin(self.zi), np.nanmax(self.zi)
        normalized_zi = ((self.zi - min_z) / (max_z - min_z) * 255).astype(np.uint8)

        # Apply a colormap to the normalized Z values
        contour_colored = cv2.applyColorMap(normalized_zi, cv2.COLORMAP_JET)

        # Place the contour plot on the overlay at the current offsets
        for i in range(self.xi.shape[0]):
            for j in range(self.xi.shape[1]):
                x = int(self.xi[i, j] + self.offset_x)
                # Adjust y to flip it vertically for OpenCV's coordinate system
                y = int(self.screenshot.shape[0] - (self.yi[i, j] + self.offset_y))
                if 0 <= x < overlay.shape[1] and 0 <= y < overlay.shape[0]:
                    overlay[y, x] = contour_colored[i, j]

        # Blend the overlay and the screenshot for transparency
        alpha = 0.3  # Adjust transparency (0: fully transparent, 1: fully opaque)
        blended = cv2.addWeighted(overlay, alpha, self.screenshot, 1 - alpha, 0)
        return blended

    def mouse_callback(self, event, x, y, flags, param):
        """
        Mouse callback for dragging the contour plot.
        """
        if event == cv2.EVENT_LBUTTONDOWN:
            self.dragging = True
            self.start_drag_x = x
            self.start_drag_y = y

        elif event == cv2.EVENT_MOUSEMOVE and self.dragging:
            dx = x - self.start_drag_x
            dy = y - self.start_drag_y
            self.offset_x += dx
            self.offset_y += dy
            self.start_drag_x = x
            self.start_drag_y = y

        elif event == cv2.EVENT_LBUTTONUP:
            self.dragging = False

    def start_alignment(self):
        """
        Starts the interactive alignment tool using OpenCV.
        """
        self.dragging = False
        cv2.namedWindow("Align Contour")
        cv2.setMouseCallback("Align Contour", self.mouse_callback)

        while True:
            overlay = self.overlay_contour()
            cv2.imshow("Align Contour", overlay)
            key = cv2.waitKey(1)

            if key == 27:  # ESC key to exit
                break
            elif key == ord('c'):  # Press 'c' to confirm alignment
                self.confirmed = True
                break

        cv2.destroyAllWindows()

        if self.confirmed:
            print("Contour alignment confirmed. Now click on the bottom-right point.")
            # Fix the contour overlay
            overlay = self.overlay_contour()
            cv2.imshow("Align Contour - Select Bottom-Right Point", overlay)

            # Define a callback for capturing the clicked point
            clicked_point = []

            def select_point(event, x, y, flags, param):
                if event == cv2.EVENT_LBUTTONDOWN:
                    clicked_point.append((x, y))
                    print(f"Selected bottom-right pixel: {x}, {y}")
                    cv2.destroyAllWindows()

            # Set the callback for point selection
            cv2.setMouseCallback("Align Contour - Select Bottom-Right Point", select_point)
            cv2.waitKey(0)

            if not clicked_point:
                raise ValueError("No point was selected. Alignment aborted.")

            # Record the selected point as the bottom-right pixel
            contour_bottom_right_x, contour_bottom_right_y = clicked_point[0]
            self.bottom_right_pixel = (contour_bottom_right_x, contour_bottom_right_y)
            print(f"Final bottom-right pixel of the contour plot: {self.bottom_right_pixel}")
        else:
            print("Alignment not confirmed.")
            contour_bottom_right_x, contour_bottom_right_y = None, None

        cv2.destroyAllWindows()
        return contour_bottom_right_x, contour_bottom_right_y
