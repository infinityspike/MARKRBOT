import warnings
import math
import MovementCommands

from svg_to_gcode import formulas
from svg_to_gcode.compiler.interfaces import Interface
from svg_to_gcode.geometry import Vector
from svg_to_gcode import TOLERANCES

verbose = False


class MovementCommandCompiler(Interface):

    def __init__(self):
        self.position = Vector(0,0)
        self._next_speed = None
        self._current_speed = None

        # Round outputs to the same number of significant figures as the operational tolerance.
        self.precision = abs(round(math.log(TOLERANCES["operation"], 10)))

    def set_movement_speed(self, speed):
        self._next_speed = speed
        return None

    def linear_move(self, x=None, y=None, z=None):

        # Don't do anything if linear move was called without passing a value.
        if x is None and y is None and z is None:
            warnings.warn("linear_move command invoked without arguments.")
            return None
        
        if x is None:
            x = self.position.x
        if y is None :
            y = self.position.y

        MoveCommand = MovementCommands.LinearMovementCommand(round(self.position.x, self.precision), round(self.position.y,self.precision), round(x,self.precision), round(y, self.precision) )


        if self.position is not None or (x is not None and y is not None):
            if x is None:
                x = self.position.x

            if y is None:
                y = self.position.y

            self.position = Vector(x, y)

        if verbose:
            print(f"Move to {x}, {y}, {z}")

        return MoveCommand

    def laser_off(self):
        return MovementCommands.MoveCommand()

    def set_laser_power(self, power):
        return MovementCommands.DrawCommand()

    def set_absolute_coordinates(self):
        return None

    def set_relative_coordinates(self):
        return None

    def dwell(self, milliseconds) -> str:
        return None

    def set_origin_at_position(self) -> str:
        return None

    def set_unit(self, unit):
        return None

    def home_axes(self):
        return None