from abc import ABC, abstractmethod
from svgwrite import Drawing

class Widget(ABC) :

    position_x:int
    position_y:int
    size:int
    SVG:Drawing

    def __init__(self, pos_x:int, pos_y:int, size:int) :
        self.position_x = pos_x
        self.position_y = pos_y
        self.size = size

    @abstractmethod
    def toSVG(self) :
        raise NotImplementedError("toSVG not implemented")