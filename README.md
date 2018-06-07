# dls_feedback_manager
Python soft ioc module for running feedback loop on XBPMs.

XBPM_manager_control is where parameters specific to each beamline should be set e.g. PV prefixes, KP, KI, KD values, current limits and position thresholds.

XBPM range manager imports records of readback values, creates PVs for normalised beam position and size. It monitors currents and swaps between TetrAMM ranges. A vertical scale factor can be set if required.
XBPM feedback manager creates PVs for the feedback enable button options to start, stop and pause XBPM feedback, switch between different modes i.e. running multiple XBPM feedbacks together or individually.
