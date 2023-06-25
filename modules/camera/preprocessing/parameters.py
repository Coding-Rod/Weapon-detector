import cv2
import numpy as np
import os
import yaml

class Parameters:
    
    def __init__(self,image_params: dict = None, edge_params: dict = None):
        if image_params:
            self.desired_width = image_params["width"] or 800
            self.desired_height = image_params["height"] or 600
            self.alpha = image_params["alpha"] or 1.0
            self.beta = image_params["beta"] or 0
        if edge_params:
            self.clip_limit = edge_params["clip_limit"] or 2.0
            self.tile_grid_size = (edge_params["tile_grid_size"][0] or 8, edge_params["tile_grid_size"][1] or 8)
            self.canny_threshold1, self.canny_threshold2 = edge_params["canny_threshold"][0] or 100, edge_params["canny_threshold"][1] or 200
            self.color = (edge_params["color"][0] or 0, edge_params["color"][1] or 0, edge_params["color"][2] or 0)
            self.lines_threshold, self.lines_min_line_length, self.lines_max_line_gap = edge_params["lines_threshold"] or 100, edge_params["lines_min_line_length"] or 100, edge_params["lines_max_line_gap"] or 10
        
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