

## XBPM1 and XBPM2 PID parameters (mirrors)
#  Initial values used in feedback manager

class XBPMPIDParamsClass:

    def __init__(self, KP, KI, KD, feedback, position):
        self.KP = KP
        self.KI = KI
        self.KD = KD
        self.feedback = feedback
        self.position = position

    def validate_params(self):
        assert type(self.KP) is int
        assert type(self.KI) is int
        assert type(self.KP) is int
        assert type(self.feedback) is str and len(self.feedback) > 0
        assert type(self.position) is str and len(self.position) > 0
