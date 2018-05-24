

## XBPM1 and XBPM2 PID parameters (mirrors)
#  Initial values used in feedback manager

class XBPMPIDParams:

    def __init__(self, KP, KI, KD, feedback, position):
        self.KP = KP
        self.KI = KI
        self.KD = KD
        self.feedback = feedback
        self.position = position

