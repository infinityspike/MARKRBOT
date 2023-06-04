from src.CommandQueue import CommandQueue
from src.Widget import Widget
import src.MovementCommands as MC

import xml.etree.ElementTree as ET
import ziafont
ziafont.config.svg2 = False

class StateController :

    __slots__ = ("working", "snapshot", "delete", "command_queue")

    def __init__(self, queue:CommandQueue) :
        self.snapshot = set() #if persistent database is implemented, snapshot would query db for current board state
        self.working = dict.fromkeys(self.snapshot)
        self.delete = set() # a way to remember to remove a widget from the snapshot if it has been completely erased
        self.command_queue = queue

    def addWidget(self, new:Widget) :
        new_commands = new.parseMovementCommands()
        draw_commands = set()
        for command in new_commands :
            draw_commands.add(MC.LinearDrawCommand(command))

        self.working[new] = draw_commands

    def editWidget(self, old:Widget, new:Widget) :
        #check if old exists in snapshot or working, if it doesn't dont do anything
        in_working = None
        for key in self.working :
            if old == key : in_working = key
        if in_working == None : return 

        in_snapshot = None
        for key in self.snapshot :
            if old == key : in_snapshot = key
        if in_snapshot == None : return 

        # if its already on the board
        if (not in_snapshot == None) :
            old_commands = old.parseMovementCommands()
            new_commands = new.parseMovementCommands()
            draw_commands = set()
            erase_commands = set()
            #if command is in both, its already on the board so do nothing
            #if command is only in new, its not on board yet so draw it
            new_commands.difference_update(old_commands)
            for command in new_commands :
                draw_commands.add(MC.LinearDrawCommand(command))
            #if command is only in old, its on the board but shouldn't be so erase it
            old_commands.difference_update(new_commands)
            for command in old_commands :
                erase_commands.add(MC.LinearEraseCommand(command))

            self.working.pop(in_working)
            self.working[new] = draw_commands.union(erase_commands)
        
        #if its only in working and not written on board yet, remove and replace
        elif (not in_working == None) :
            self.working.pop(in_working)
            self.addWidget(new)

    def deleteWidget(self, old:Widget) :
        #check if old exists in working, if it doesn't dont do anything
        in_working = None
        for key in self.working :
            if old == key : in_working = key
        if in_working == None : return

        #if its only in working and not written on board yet, simply remove it
        in_snapshot = None
        for key in self.snapshot :
            if old == key : in_snapshot = key
        if in_snapshot == None : 
            self.working.pop(in_working)
        else :
            #if its already on the board, erase it
            old_commands = old.parseMovementCommands()
            erase_commands = set()
            for command in old_commands :
                erase_commands.add(MC.LinearEraseCommand(command))
        
            self.working.pop(in_working)
            self.working[old] = erase_commands
            self.delete.add(old)
        
    def revert(self) :
        self.working.clear()
        self.working = dict.fromkeys(list(self.snapshot))

    def syncronize(self) -> list :
        result_set = set()
        for key in self.working :
            if self.working[key] : result_set.update(self.working[key])

        #create new snapshot, remembering to remove completely deleted widgets
        self.snapshot.clear()
        self.snapshot.update(self.working.keys())
        self.snapshot.difference_update(self.delete)

        #create new working dict from snapshot
        self.revert()

        return self.command_queue.recieveMovementCommands(result_set)
    
if __name__ == '__main__' :
    controller = StateController(None)

    drawing = Widget(0,0,ET.parse("./proof_of_concept/test-svgs/drawing.svg").getroot())

    square = Widget(0,0,ET.fromstring('<svg width="100" height="100" xmlns="http://www.w3.org/2000/svg"><path d="M 10 10 H 90 V 90 H 10 L 10 10"/></svg>'))

    square2 = Widget(10,10,ET.fromstring('<svg width="100" height="100" xmlns="http://www.w3.org/2000/svg"><path d="M 10 10 H 90 V 90 H 10 L 10 10"/></svg>'))

    controller.addWidget(square)
    controller.addWidget(square2)
    print(controller.syncronize())
    # controller.editWidget(square,square2)
    # controller.syncronize()
    # controller.deleteWidget(square2)
    # controller.syncronize()