# INITIALISATION ET VALIDATION
# ============================
# ROBOT_INSTANTIATION -> ROBOT_INTEGRITY if successful else INSTANTIATION_FAILED -> END
# ROBOT_INTEGRITY -> INTEGRITY SUCCEEDED if successful else INTEGRITY_FAILED -> SHUT_DOWN_ROBOT -> END
# INTEGRITY_SUCCEEDED -> HOME 

# ACCEUIL
# ============================
# HOME - TACHES (TASK_1, TASK_2, TASK_3, ...)

# TACHE
# ============================
# TASK_1 -> HOME
# TASK_2 -> HOME
# ...

from finite_state_machine import FiniteStateMachine
from initialisation_validation import InitializationValidation
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

        layout = InitializationValidation()

        super().__init__(layout)
    
def main():
    c64project = C64Project()
    c64project.run()

if __name__ == '__main__':
    quit(main())