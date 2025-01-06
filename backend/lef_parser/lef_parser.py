"""
Lef Parser
Author: Tri Cao
Email: tricao@utdallas.edu
Date: August 2016
"""
from .lef_util import *

SCALE = 2000

class LefDscp():
    """
    LefParser object will parse the LEF file and store information about the
    cell library.
    """
    def __init__(self):
        self.macros = {}
        self.layers = {}
        self.vias = {}

        self.stack = []
        self.statements = []
        self.cell_height = -1

    def get_cell_height(self):
        """
        Get the general cell height in the library
        :return: void
        """
        for macro in self.macros:
            self.cell_height = self.macros[macro].info["SIZE"][1]
            break

    def parse(self, lef_file):
        """Parse input lef file"""
        with open(lef_file, "r") as f:
            for line in f:
                info = str_to_list(line)
                if len(info) != 0:
                    # if info is a blank line, then move to next line
                    # check if the program is processing a statement
                    #print (info)
                    if len(self.stack) != 0:
                        curState = self.stack[len(self.stack) - 1]
                        nextState = curState.parse_next(info)
                    else:
                        curState = Statement()
                        nextState = curState.parse_next(info)
                    # check the status return from parse_next function
                    if nextState == 0:
                        # continue as normal
                        pass
                    elif nextState == 1:
                        # remove the done statement from stack, and add it to the statements
                        # list
                        if len(self.stack) != 0:
                            # add the done statement to a dictionary
                            done_obj = self.stack.pop()
                            if isinstance(done_obj, Macro):
                                self.macros[done_obj.name] = done_obj
                            elif isinstance(done_obj, Layer):
                                self.layers[done_obj.name] = done_obj
                            elif isinstance(done_obj, Via):
                                self.vias[done_obj.name] = done_obj
                            self.statements.append(done_obj)
                    elif nextState == -1:
                        pass
                    else:
                        self.stack.append(nextState)
            self.get_cell_height()


def parse_lef_file(lef_file):
    lef_dscp = LefDscp()
    lef_dscp.parse(lef_file)
    return lef_dscp