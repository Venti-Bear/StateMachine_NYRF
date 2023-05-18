from lib.finite_state_machine import FiniteStateMachine
from c64_layout import C64Layout

class C64Project(FiniteStateMachine):
   def __init__(self):
        layout = C64Layout()
        super().__init__(layout)
    
def main():
    c64project = C64Project()
    c64project.run()

if __name__ == '__main__':
    quit(main())  