import cv2
import matplotlib.pyplot as plt


class MicroMacroAlignment:
    def __init__(self, macro_image_path, macro_scale_x, macro_scale_y, micro_scale_x=5.89052520107227, micro_scale_y=5.5226654358700005):
        """
        Initialize the MicroMacroAlignment object with the macro image and scaling factors.

        Parameters:
            macro_image_path (str): Path to the macro image.
            macro_scale_x (float): Pixels per micron in the macro image (X direction).
            macro_scale_y (float): Pixels per micron in the macro image (Y direction).
            micro_scale_x (float, optional): Pixels per micron in the micro image (X direction). Default is 5.89052520107227.
            micro_scale_y (float, optional): Pixels per micron in the micro image (Y direction). Default is 5.5226654358700005.
        """
        self.macro_image_path = macro_image_path
        self.macro_scale_x = macro_scale_x
        self.macro_scale_y = macro_scale_y
        self.micro_scale_x = micro_scale_x
        self.micro_scale_y = micro_scale_y

        self.macro_image = None
        self.reference_points = []

    def load_macro_image(self):
        """
        Loads the macro image from the specified path.
        """
        self.macro_image = cv2.imread(self.macro_image_path, cv2.IMREAD_COLOR)
        if self.macro_image is None:
            raise FileNotFoundError(f"Macro image not found at {self.macro_image_path}")
        print(f"Macro image loaded: {self.macro_image_path}")

    def click_reference_points(self):
        """
        Allows the user to click on two reference points in the macro image.
        Opens the macro image in a separate window.
        """
        if self.macro_image is None:
            raise ValueError("Macro image not loaded. Call 'load_macro_image' first.")

        def click_event(event, x, y, flags, param):
            if event == cv2.EVENT_LBUTTONDOWN:
                # Store the reference point
                self.reference_points.append((x, y))
                print(f"Reference point {len(self.reference_points)}: ({x}, {y})")

                # Draw a small circle on the clicked point
                cv2.circle(self.macro_image, (x, y), 5, (0, 255, 0), -1)
                cv2.imshow("Macro Image - Select Two Reference Points", self.macro_image)

                # Stop after two points
                if len(self.reference_points) == 2:
                    print("Two reference points selected.")
                    cv2.destroyAllWindows()

        try:
            # Display the macro image in a separate window
            cv2.namedWindow("Macro Image - Select Two Reference Points", cv2.WINDOW_NORMAL)
            cv2.imshow("Macro Image - Select Two Reference Points", self.macro_image)
            cv2.setMouseCallback("Macro Image - Select Two Reference Points", click_event)
            cv2.waitKey(0)  # Wait until two points are selected
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            # Ensure all OpenCV windows are closed
            cv2.destroyAllWindows()

    def get_reference_points(self):
        """
        Returns the reference points selected by the user.

        Returns:
            list of tuple: List of two reference points as (x, y).
        """
        if len(self.reference_points) != 2:
            raise ValueError("Two reference points must be selected.")
        return self.reference_points

    def calculate_distance_in_microns(self):
        """
        Calculates the X and Y distances between the two reference points in microns.
        The first point is considered as the origin.

        Returns:
            tuple: (distance_x, distance_y) in microns.
        """
        if len(self.reference_points) != 2:
            raise ValueError("Two reference points must be selected before calculating distances.")

        # Get the two reference points
        point1 = self.reference_points[0]
        point2 = self.reference_points[1]

        # Calculate pixel distances
        distance_x_pixels = point2[0] - point1[0]
        distance_y_pixels = point2[1] - point1[1]

        # Convert pixel distances to microns using the macro scales
        distance_x_microns = distance_x_pixels / self.macro_scale_x
        distance_y_microns = distance_y_pixels / self.macro_scale_y

        return distance_x_microns, distance_y_microns
