from __future__ import annotations
from src.KlipperSocket import KlipperSocket
import src.MovementCommands as MC
from svg_to_gcode.geometry import Vector


import queue
import gpiozero

def optomizeMovementCommands(commands:set) -> list :
    #extremely basic optomization. 
    # CURRENTLY BROKEN -- Will not move to the correct starting position for new command after another command
    # pick a random command from the set
    # move from current position to the starting spot
    # execute command 
    # repeat
    result_list = list()
    current_position = Vector(0,0)
    toolhead_state = None

    while commands :
        command:(MC.LinearDrawCommand|MC.LinearEraseCommand) = commands.pop()

        start, _ = command.toGcode()
        if current_position.x != start.x and current_position.y != start.y :
            result_list.append(MC.MoveCommand())
            toolhead_state = MC.MoveCommand
            result_list.append(MC.LinearMoveCommand(MC.LinearMovementCommand(current_position.x,current_position.y,start.x,start.y)))

        if isinstance(command, MC.LinearDrawCommand) and toolhead_state != MC.DrawCommand :
            result_list.append(MC.DrawCommand())
            toolhead_state = MC.DrawCommand
        elif isinstance(command, MC.LinearEraseCommand) and toolhead_state != MC.EraseCommand :
            result_list.append(MC.EraseCommand())
            toolhead_state = MC.EraseCommand

        result_list.append(command)
        current_position.x = command.end.x
        current_position.y = command.end.y

    return result_list


class CommandQueue :
    
    __slots__ = ("queue","klipper","servo")

    def __init__(self, klipper_reference:KlipperSocket, servo:gpiozero.AngularServo) :
        self.queue = queue.Queue()
        self.klipper = klipper_reference
        self.servo = servo

    def recieveMovementCommands(self, commands:set) -> list :
        #determines and structures order of movement commands, prep fro being sent to robot controller.

        #in my case, my robot is faster at changing toolhead states versus moving a distance.
        #My algorithm takes advangate of that, it is meant to minimize the TOTAL moveCommand distance between draw/erase commands
        ordered_move_commands = optomizeMovementCommands(commands)
        for command in ordered_move_commands :
            self.queue.put(command)

        return ordered_move_commands