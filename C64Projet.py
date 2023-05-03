from finite_state_machine import FiniteStateMachine
from layout import Layout

class C64Project(FiniteStateMachine):
   def __init__(self):
        self.__G_TO_Y = 4.0
        self.__Y_TO_R = 1.0
        self.__R_TO_G = 5.0

        # Créer les states
        # Ajouter les actions aux states

        # Créer les transitions

        # Ajouter les transitions aux states

        layout = Layout()
        # layout.add_states({GREEN, YELLOW, RED})
        # layout.initial_state = GREEN

        super().__init__(layout)
    
def main():
    c64project = C64Project()
    c64project.run()

if __name__ == '__main__':
    quit(main())