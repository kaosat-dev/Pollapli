from doboz_web.core.components.automation.conditions.condition import Condition

class HumanValidationCondition(Condition):
    def __init__(self):
        Condition.__init__(self)
        #hack
        self.valid=True