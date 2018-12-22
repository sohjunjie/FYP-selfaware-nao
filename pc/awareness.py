from threading import Thread
from executive_proc import ExecutiveProc
from interpreter import Interpreter
from memory import Memory
from reaction import Reaction
import time


class RobotAwareness():
    def __init__(self, wsApp):
        super().__init__()
        self.exeProc = ExecutiveProc(self)
        self.interpreter = Interpreter(self)
        self.memory = Memory(self)
        self.reaction = Reaction(self, wsApp)

        self.exeProc.daemon = True
        self.interpreter.daemon = True
        self.memory.daemon = True
        self.reaction.daemon = True

        self.exeProc.start()
        self.interpreter.start()
        self.memory.start()
        self.reaction.start()

    def interpret_robot_experience(self, robot_exp):
        self.interpreter.perceive(robot_exp)

#     def start(self):
#         self.running = True
#         super().start()

#     def run(self):
#         self.idle()

#     def stop(self):
#         self.running = False

#     def idle(self):
#         while(self.running):
#             time.sleep(0.2)


# if __name__ == "__main__":
#     aw = RobotAwareness()
#     aw.daemon = True
#     aw.start()

#     while 1:
#         time.sleep(1)
