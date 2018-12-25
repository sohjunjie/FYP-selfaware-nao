from executive_proc import ExecutiveProc
from interpreter import Interpreter
from memory import Memory
from reaction import Reaction


class RobotAwareness():
    def __init__(self, wsApp):
        super().__init__()
        self.exeProc = ExecutiveProc(self)
        self.interpreter = Interpreter(self)
        self.memory = Memory(self)
        self.reaction = Reaction(self, wsApp)

    def interpret_robot_experience(self, robot_exp):
        self.interpreter.perceive(robot_exp)
