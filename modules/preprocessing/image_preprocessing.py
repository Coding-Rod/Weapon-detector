import cv2
from .parameters import Parameters

class ImagePreprocessor(Parameters):
    
    def __init__(self, params: dict = None):
        super().__init__(image_params=params)
    
    def resize_image(self, image):
        return cv2.resize(image, (self.desired_width, self.desired_height), interpolation=cv2.INTER_AREA)
    
    def flip_image(self, image):
        return cv2.flip(image, 0)
    
    def change_contrast_and_brightness(self, image):
        return cv2.convertScaleAbs(image, alpha=self.alpha, beta=self.beta)
    
    def apply_rgb_clahe(self, image):
        b, g, r = cv2.split(image)
        clahe = cv2.createCLAHE(clipLimit=self.clip_limit, tileGridSize=(self.tile_grid_size, self.tile_grid_size))
        b = clahe.apply(b)
        g = clahe.apply(g)
        r = clahe.apply(r)
        return cv2.merge((b, g, r))
    
    def pipeline(self, img, *args):
        self.image = img

        for preprocessing_method in args:
            self.image = preprocessing_method(self.image)

        return self.image
    
    def get_preprocessed_image(self):
        """ 
        Returns the preprocessed image with the original image, multiplying both images
        """
        return self.image
    def get_params(self):
        return super().get_params()['image']