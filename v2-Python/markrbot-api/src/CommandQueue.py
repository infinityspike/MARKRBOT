# from __future__ import annotations
# from src.KlipperSocket import KlipperSocket
# import src.MovementCommands as MC
# import src.Constants as Constants

# from svg_to_gcode.geometry import Vector
# import queue
# import gpiozero

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

        draw = MC.ToolheadDraw()
        draw.setServo(self.servo)

        standby = MC.ToolheadStandby()
        standby.setServo(self.servo)

        erase = MC.ToolheadErase()
        erase.setServo(self.servo)

        while commands :
            command:(MC.LinearDrawCommand|MC.LinearEraseCommand) = commands.pop()

            start, _ = command.toGcode()
            # if current_position.x != start.x and current_position.y != start.y :
            #     standby = MC.ToolheadStandby()
            #     standby.setServo(self.servo)
            #     result_list.append(standby)
            #     toolhead_state = MC.ToolheadStandby
            #     result_list.append(MC.LinearMoveCommand(MC.LineSegment(current_position.x,current_position.y,start.x,start.y)))
            result_list.append(standby)
            toolhead_state = MC.ToolheadStandby
            result_list.append(MC.LinearMoveCommand(MC.LineSegment(0,0,start.x,start.y)))
                                                    
            if isinstance(command, MC.LinearDrawCommand) and toolhead_state != MC.ToolheadDraw :
                toolhead_state = MC.ToolheadDraw
                result_list.append(draw)
            elif isinstance(command, MC.LinearEraseCommand) and toolhead_state != MC.ToolheadErase :
                toolhead_state = MC.ToolheadErase
                result_list.append(erase)

            result_list.append(command)
            # current_position.x = command.end.x
            # current_position.y = command.end.y
            result_list.append(standby)
            toolhead_state = MC.ToolheadStandby
            result_list.append(MC.LinearMoveCommand(MC.LineSegment(command.end.x,command.end.y,0,0)))



        return result_list
    
    def groupMovementCommands(self, starts:dict, ends:dict) -> list[list] :
        """
        starts "start Vector : [LineSegment]"
        ends "LineSegment : end Vector"
        return " [[line1,line3,line2], [line6,line4], [line5]]
        
        """
        all_line_chains:list[list] = list()
        current_line_chain = list()

        while ends :
            #start weith a random command
            current_command, current_end = ends.popitem()
            current_line_chain.append(current_command)

            # if another command has the same start point as that commands end point, add it and repeat process
            # if there are multiple commands that have the same start point, choose one arbitrarily
            next_possible_commands:list = starts[current_end]
            next_command = next_possible_commands.pop()
            # if the command selected is the last command in the list, pop the list from the dict
            if not next_possible_commands : starts.pop(current_end)

            while next_command :
                # if the command that was chosen next is already in a chain, add the current chain to the start of the found chain
                for line_chain in all_line_chains :
                    if next_command == line_chain[0] :
                        line_chain = current_line_chain.extend(line_chain)
                        found_extendable_chain = True
                        break
                if found_extendable_chain : break

                current_line_chain.append(next_command)

                next_command_end = ends.pop(next_command)
                next_commands:list = starts[next_command_end]
                next_command = next_commands.pop()
                if not next_commands : starts.pop(current_end)
            # once that line chain is broken(last commands end has no other commands start), start again with a new random command
            all_line_chains.append(current_line_chain)
            current_line_chain.clear()

                

        return
    

    def collectMovementCommands(self, commands:set) -> dict :
        start_dict = dict()
        end_dict = dict()

        for command in commands :
            if start_dict[command.start] :
                start_dict[command.start].append(command)
            else :
                start_dict[command.start] = [command]
            end_dict[command] = command.end

        return self.groupMovementCommands(start_dict, end_dict)
    

    def optomizeMovementCommands(self, commands:set) -> list :
        dict_commands = self.collectMovementCommands(commands) 

        return

    

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
        self.klipper.sendMessage({ "id" : 420, "method" : "gcode/script", "params" : {"script" : f"G0 X0 Y0 F2000"} })

        self.executeAllCommads()

        standby = MC.ToolheadStandby()
        standby.setServo(self.servo)
        standby.execute()
        self.klipper.sendMessage({ "id" : 420, "method" : "gcode/script", "params" : {"script" : f"G0 X0 Y0 F2000"} })
    
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

if __name__ == '__main__' :
    test_queue = CommandQueue(None, None)

    test_set = {
        MC.LineSegment(0,0, 1,0),
        MC.LineSegment(1,0, 1,1),
        MC.LineSegment(1,0, 1,-1),
        MC.LineSegment(1,-1, 2,-1),
        MC.LineSegment(2,-1, 2,0),
        MC.LineSegment(2,-1, 2,-2)
    }

    print(test_queue.collectMovementCommands(test_set))

        
