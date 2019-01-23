from executive_proc import ExecutiveProc
from perception import Perception
from memory import Memory
from reaction import Reaction


class RobotAwareness():
    def __init__(self, wsApp):

        self.memory = Memory(self)
        self.exeProc = ExecutiveProc(self)
        self.perception = Perception(self)
        self.reaction = Reaction(self, wsApp)

    def interpret_robot_experience(self, robot_exp):
        self.perception.perceive(robot_exp)
