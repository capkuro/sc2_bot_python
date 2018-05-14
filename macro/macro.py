import random
import math
import time

import numpy as np
import pandas as pd

from pysc2.lib import actions
from pysc2.lib import features

from absl import app
from absl import flags

class Macro(object):
    def __init__(self, id_mac = -1, name = None, desc = None,):
        print("MACRO")
        self.id = id_mac
        self.name = name
        self.desc = desc
        self.state = 0 # -1: Error, 0: Inicializando, 1: En Progreso, 2: Done
        self.runs = 0
        self.internal_step = 0
        self.steps = {}
        self.maxsteps = 0

    def _complete_macro(self):
        self.state = 2
        self.runs += 1
        self.internal_step = 0

    def reset(self):
        self.state = None
        self.runs = 0

    def add_step_func(self,fun):
        self.steps[self.maxsteps] = fun
        self.maxsteps +=  1

    def run(self):
        self.state = 1
        res = self.execute_func(self.internal_step)
        if res is None:
            self.state = -1
        else:
            self.internal_step +=1
            if self.internal_step == self.maxsteps:
                self._complete_macro()
        return res


    def execute_func(self,step = None):
        if step <= self.maxsteps:
            return self.steps[step]()
        else:
            print("Invalid step")
            return None

    def is_macro_done(self):
        return self.state == 2

    def restart_done_state(self):
        self.state = 0


    def __str__(self):
        text = """===== Macro {0}
Id: {1}
Description: {2}
====
State:{3}
Runs:{4}
Steps:{5}""".format(self.name,self.id,self.desc,self.state,self.runs,self.maxsteps)
        return text

def _main(unused_argv):
    description = """ 
    Multi line description for macro agent
    This is line 2"""
    mac = Macro(id_mac=0, name="Test", desc=description)



    def func1():
        print("function 1")
        return "function 1"
    def func2():
        print("function 2")
        return"function 2"
    def func3():
        print("function 3")
        return "function 3"



    mac.add_step_func(func1)
    mac.add_step_func(func2)
    mac.add_step_func(func3)
    print("running macro")
    while not(mac.is_macro_done()):
        mac.run()
    mac.restart_done_state()
    while not(mac.is_macro_done()):
        mac.run()
    mac.restart_done_state()
    while not(mac.is_macro_done()):
        mac.run()

    print(mac)

if __name__ == "__main__":
  app.run(_main)
