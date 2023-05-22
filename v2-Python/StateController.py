from CommandQueue import CommandQueue
from Widget import Widget
import MovementCommands as MC

import xml.etree.ElementTree as ET
import ziafont
ziafont.config.svg2 = False

class StateController :

    __slots__ = ("working", "snapshot","delete")

    def __init__(self) :
        self.snapshot = set() #if persistent database is implemented, snapshot would query db for current board state

        self.working = dict.fromkeys(self.snapshot)

        self.delete = set() # a way to remember to remove a widget from the snapshot if it has been completely erased

    def addWidget(self, new:Widget) :
        new_commands = new.parseMovementCommands()
        draw_commands = set()
        for command in new_commands :
            draw_commands.add(MC.LinearDrawCommand(command))

        self.working[new] = draw_commands

    def editWidget(self, old:Widget, new:Widget) :
        #check if old exists in snapshot or working, if it doesn't dont do anything
        if old not in self.working and old not in self.snapshot : return

        #if its only in working and not written on board yet, remove and replace
        if old in self.working and old not in self.snapshot :
            self.working.pop(old)
            self.addWidget(new)

        # if its already on the board
        elif old in self.snapshot :
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

            self.working.pop(old)
            self.working[new] = draw_commands.union(erase_commands)

    def deleteWidget(self, old:Widget) :
        #check if old exists in snapshot or working, if it doesn't dont do anything
        if old not in self.working and old not in self.snapshot : return

        #if its only in working and not written on board yet, simply remove it
        if old in self.working and old not in self.snapshot :
            self.working.pop(old)

        #if its already on the board, erase it
        if old in self.snapshot :
            old_commands = old.parseMovementCommands()
            erase_commands = set()
            for command in old_commands :
                erase_commands.add(MC.LinearEraseCommand(command))
        
            self.working[old] = erase_commands
            self.delete.add(old)
        
    def revert(self) :
        self.working.clear()
        self.working = dict.fromkeys(list(self.snapshot))

    def syncronize(self) -> set[set] :
        result_set = set.union(*self.working.values())

        #create new snapshot, remembering to remove completely deleted widgets
        self.snapshot.clear()
        self.snapshot.update(self.working.keys())
        self.snapshot.difference_update(self.delete)

        #create new working dict from snapshot
        self.revert()

        return result_set
    
if __name__ == '__main__' :
    controller = StateController()

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