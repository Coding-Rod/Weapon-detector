import cv2
import numpy as np
from dotenv import load_dotenv
import os

class Parameters:
    load_dotenv()
    desired_width = int(os.getenv("DESIRED_WIDTH"))
    desired_height = int(os.getenv("DESIRED_HEIGHT"))
    clip_limit = float(os.getenv("CLIP_LIMIT"))
    tile_grid_size = tuple(map(int, os.getenv("TILE_GRID_SIZE").split(",")))
    canny_threshold1, canny_threshold2 = tuple(map(int, os.getenv("CANNY_THRESHOLD").split(",")))
    color = tuple(map(int, os.getenv("COLOR").split(",")))
    lines_threshold, lines_min_line_length, lines_max_line_gap = tuple(map(int, os.getenv("LINES").split(",")))
    alpha = float(os.getenv("ALPHA"))
    beta = float(os.getenv("BETA"))
    
    def set_desired_width(self, value):
        self.desired_width = value # Min: 0, Max: 1000
        
    def set_desired_height(self, value):
        self.desired_height = value # Min: 0, Max: 1000
        
    def set_clip_limit(self, value):
        self.clip_limit = value/100 # Min: 0, Max: 1
        
    def set_tile_grid_size_width(self, value):
        self.tile_grid_size_width = value # Min: 0, Max: 128
    
    def set_tile_grid_size_height(self, value):
        self.tile_grid_size_height = value # Min: 0, Max: 128
        
    def set_canny_threshold1(self, value):
        self.canny_threshold1 = value # Min: 0, Max: 255
        
    def set_canny_threshold2(self, value):
        self.canny_threshold2 = value # Min: 0, Max: 255
        
    def set_blue_color(self, value):
        self.color = (value, self.color[1], self.color[2])
        
    def set_green_color(self, value):
        self.color = (self.color[0], value, self.color[2])
        
    def set_red_color(self, value):
        self.color = (self.color[0], self.color[1], value)
        
    def set_lines_threshold(self, value):
        self.lines_threshold = value
        
    def set_lines_min_line_length(self, value):
        self.lines_min_line_length = value
        
    def set_lines_max_line_gap(self, value):
        self.lines_max_line_gap = value
        
    def set_alpha(self, value):
        self.alpha = value/100
    
    def set_beta(self, value):
        self.beta = value/100