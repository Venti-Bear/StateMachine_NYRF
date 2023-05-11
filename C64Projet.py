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

from c64_layout import C64Layout

from finite_state_machine import FiniteStateMachine
from layout import Layout

class C64Project(FiniteStateMachine):
   def __init__(self):
        layout = C64Layout()
        super().__init__(layout)
    
def main():
    c64project = C64Project()
    c64project.run()

if __name__ == '__main__':
    quit(main())