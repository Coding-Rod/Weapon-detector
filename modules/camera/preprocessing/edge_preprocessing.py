import cv2
import numpy as np

from .parameters import Parameters

class EdgePreprocessor(Parameters):

    def resize_image(self, image):
        return cv2.resize(image, (self.desired_width, self.desired_height))

    def convert_to_grayscale(self, image):
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    def perform_histogram_equalization(self, image):
        return cv2.equalizeHist(image)

    def apply_gaussian_blur(self, image):
        return cv2.GaussianBlur(image, (5, 5), 0)

    def apply_clahe(self, image):
        clahe = cv2.createCLAHE(clipLimit=self.clip_limit, tileGridSize=self.tile_grid_size)
        return clahe.apply(image)

    def normalize_image(self, image):
        return image / 255.0

    def detect_edges(self, image):
        edges = cv2.Canny(image, self.canny_threshold1, self.canny_threshold2)
        return edges

    def merge_with_original(self, original, edges):
        merged_image = cv2.bitwise_or(original, cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR))
        return merged_image

    def invert_image(self, image):
        return cv2.bitwise_not(image)

    def detect_lines(self, image):
        lines = cv2.HoughLinesP(
                    image, # Input edge image
                    1, # Distance resolution in pixels
                    np.pi/180, # Angle resolution in radians
                    threshold=self.lines_threshold, # Min number of votes for valid line
                    minLineLength=self.lines_min_line_length, # Min allowed length of line
                    maxLineGap=self.lines_max_line_gap # Max allowed gap between line for joining them
                    )
        
        # Iterate over points
        try:
            for points in lines:
                # Extracted points nested in the list
                x1,y1,x2,y2=points[0]
                # Draw the lines joing the points
                # On the original image
                cv2.line(image,(x1,y1),(x2,y2),(255,255,255),2)
        except TypeError:
            pass
            
        return image

    def dilate_image(self, image):
        return cv2.dilate(image, np.ones((2, 2), np.uint8), iterations=1)
    
    def pipeline(self, img, *args):
        self.edges = img

        for preprocessing_method in args:
            self.edges = preprocessing_method(self.edges)

        return self.get_preprocessed_image(img) + self.change_edges_color()

    def get_edges(self):
        return self.edges
    
    def get_preprocessed_image(self, image):
        """ Returns the preprocessed image with the original image, multiplying both images

        Args:
            image (np.ndarray): The original image (RGB) to be merged with the preprocessed image (grayscale)

        Raises:
            IOError: If the image is not in RGB format
        """
        if image.shape[2] != 3:
            raise IOError("The image must be in RGB format")

        edges = self.get_edges()
        # print(edges)
        # Use edges as mask to multiply the original image
        return cv2.bitwise_and(self.resize_image(image), cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB))

    def change_edges_color(self):
        """ Changes the color of the edges

        Args:
            color (tuple): The color to be applied to the edges 
        """
        edges = self.get_edges() # binary image
        # Convert the binary image to RGB
        bw_rgb = cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)
        
        # Invert the color of the edges
        bw = cv2.bitwise_not(bw_rgb)
        
        # Apply the color to the edges        
        return np.where(bw == (255, 255, 255), self.color, bw).astype(np.uint8)
