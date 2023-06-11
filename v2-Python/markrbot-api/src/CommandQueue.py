from __future__ import annotations
from src.KlipperSocket import KlipperSocket
import src.MovementCommands as MC
import src.Constants as Constants

from svg_to_gcode.geometry import Vector
import queue
import gpiozero

class CommandQueue :
    
    __slots__ = ("queue","klipper","servo")

    def __init__(self, klipper_reference:KlipperSocket, servo:gpiozero.AngularServo) :
        self.queue = queue.Queue()
        self.klipper = klipper_reference
        self.servo = servo

    def optomizeMovementCommands(self, commands:set) -> list :
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
                standby = MC.ToolheadStandby()
                standby.setServo(self.servo)
                result_list.append(standby)
                toolhead_state = MC.ToolheadStandby
                result_list.append(MC.LinearMoveCommand(MC.LineSegment(current_position.x,current_position.y,start.x,start.y)))

            if isinstance(command, MC.LinearDrawCommand) and toolhead_state != MC.ToolheadDraw :
                draw = MC.ToolheadDraw()
                draw.setServo(self.servo)
                result_list.append(draw)
                toolhead_state = MC.ToolheadDraw
            elif isinstance(command, MC.LinearEraseCommand) and toolhead_state != MC.ToolheadErase :
                erase = MC.ToolheadErase()
                erase.setServo(self.servo)
                result_list.append(erase)
                toolhead_state = MC.ToolheadErase

            result_list.append(command)
            current_position.x = command.end.x
            current_position.y = command.end.y

        return result_list
    
    def checkForOutOfBoundCommands(self, commands:set) -> None : # could certainly be more elegant

        for command in commands :
            command:(MC.LinearDrawCommand|MC.LinearEraseCommand)

            if command.start.x < Constants.MIN_X : raise Exception(f"command \"{command}\" is out of bounds")
            if command.start.x > Constants.MAX_X : raise Exception(f"command \"{command}\" is out of bounds")

            if command.start.y < Constants.MIN_Y : raise Exception(f"command \"{command}\" is out of bounds")
            if command.start.y > Constants.MAX_Y : raise Exception(f"command \"{command}\" is out of bounds")

            if command.end.x < Constants.MIN_X : raise Exception(f"command \"{command}\" is out of bounds")
            if command.end.x > Constants.MAX_X : raise Exception(f"command \"{command}\" is out of bounds")

            if command.end.y < Constants.MIN_Y : raise Exception(f"command \"{command}\" is out of bounds")
            if command.end.y > Constants.MAX_Y : raise Exception(f"command \"{command}\" is out of bounds")


    def recieveMovementCommands(self, commands:set) -> list :
        #determines and structures order of movement commands, prep fro being sent to robot controller.

        #in my case, my robot is faster at changing toolhead states versus moving a distance.
        #My algorithm takes advangate of that, it is meant to minimize the TOTAL moveCommand distance between draw/erase commands
        self.checkForOutOfBoundCommands(commands)
        ordered_move_commands = self.optomizeMovementCommands(commands)
        for command in ordered_move_commands :
            self.queue.put(command)

        self.executeCommandsWithFluff()
        
        return ordered_move_commands
    
    def executeCommandsWithFluff(self) :
        #home & 0,0
        self.klipper.sendMessage({ "id" : 420, "method" : "gcode/script", "params" : {"script" : f"G28 X0 Y{Constants.BOARD_SIZE_Y}"} })
        self.klipper.sendMessage({ "id" : 421, "method" : "gcode/script", "params" : {"script" : f"G90"} })
        self.klipper.sendMessage({ "id" : 420, "method" : "gcode/script", "params" : {"script" : f"G0 X0 Y0"} })

        self.executeAllCommads()

        standby = MC.ToolheadStandby()
        standby.setServo(self.servo)
        standby.execute()
        self.klipper.sendMessage({ "id" : 420, "method" : "gcode/script", "params" : {"script" : f"G0 X0 Y0"} })
    
    def executeSingleCommand(self) :
        command = self.queue.get()

        if isinstance(command, MC.LineSegment) :
            self.klipper.sendMessage(
                {
                    "id" : 420,
                    "method" : "gcode/script",
                    "params" : {"script" : command.toGcode()[1]}
                }
            )
        elif isinstance(command, MC.ToolheadCommand) :
            command.execute()
    

    def executeAllCommads(self) :
        while not self.queue.empty() :
            self.executeSingleCommand()

        
