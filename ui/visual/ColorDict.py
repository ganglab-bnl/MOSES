from PyQt6.QtGui import QColor
import random

class ColorDict:
    DEFAULT_COLOR = QColor(200, 200, 200)

    def __init__(self, num_colors=100):
        self.num_colors = num_colors
        self.colordict = self._generate_colors(self.num_colors)

    def get_color(self, index):
        if index is None:
            return self.DEFAULT_COLOR

        if index < 0: # Complementary bonds
            index *= -1
        
        if index >= self.num_colors: # Generate more colors if necessary
            self.update_colors(index + 1)

        return self.colordict.get(index, self.DEFAULT_COLOR)
    

    def _generate_colors(self, num_colors):
        """Use golden ratio to generate visually distinct colors"""
        golden_ratio_conjugate = 0.618033988749895
        h = random.random()
        colors = {0: self.DEFAULT_COLOR}  # snsure index 0 is always DEFAULT_COLOR
        for i in range(1, num_colors):
            h = (h + golden_ratio_conjugate) % 1
            color = QColor.fromHsvF(h, 0.5, 0.8)
            colors[i] = color
        return colors

    def update_colors(self, num_colors):
        self.num_colors = num_colors
        self.colordict = self._generate_colors(self.num_colors)

    def get_all_colors(self):
        return self.colordict