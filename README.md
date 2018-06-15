# dls_feedback_manager
Python soft ioc for running feedback loop on XBPMs.

This IOC is based around a BLFeedback EPICS module which receives Readback PV data and apply feedback accordingly to Control PVs. An AUTOCALC PV acts as an On/Off setting which monitors other PVs in order to switch the feedback
on or off. The purpose of the dls_feedback_manager is to provide PVs that get monitored and set conditions for whether or not the feedback runs.
The IOC is divided into two different managers; the range manager and feedback manager.

XBPM_range_manager imports records of the readback values and creates PVs which define normalised beam position and size, as well as a threshold percentage.
The mean readback values and DRV range PVs are used to switch between TetrAMM gain modes, 120nA for lower currents and 120uA for higher currents.
The users are able to set the threshold value of the beam position to ensure it is within a certain distance from the centre of the XBPM. This gets flagged by GDA which writes to the POSITION_OK PV, setting it to 0 or 1,
also depending on the normalised positions and threshold before allowing data collection to restart.
A vertical scale factor can also be set on an XBPM if required. The position scale PV associated with the DCM energy is monitored and then set to a value using an undulator beam size calculation. 

XBPM_feedback_manager creates PVs for enabling the feedback. The FB_RUN PV is set to 0, 1 or 2 corresponding to stop, start or pausing the feedback respectively, depending on the beamline conditions.
FB_MODE allows users to run the feedback on 1 or more XBPMs at the same time depending on what each beamline has. Currently, the modes are 0, 1 and 2, corresponding to XBPM1 only, XBPM1 and XBPM2 or XBPM2 
(more can be added if needed). 
A GUI screen is available for users to set the mode and stop and start the feedback, involving the FB_ENABLE PV, where a logging message is displayed on the console to give the current status of the feedback.
The FB_PAUSE PV pauses the feedback when told to by GDA during energy changes/attenuation, setting this PVs value to 0 (paused) and the FB_RUN PV to 2 (paused). Once GDA has completed its task, it writes to the pause PV again
changing its value back to 1, which in turn sets the run PV back to 1 so the feedback is able to run again.
Each beamline can define its required values for the PID parameters (in XBPM manager control). These are used to create a dictionary of PID PVs where the values are assigned to the pitch and roll features of each XBPM.
When it comes to the feedback resetting these PID to the initial desired state, it reads these PVs and sets them back to the original values.

XBPM_pid_params stores a class containing pid variables that are used by XBPM_feedback_manager.

XBPM_manager_control contains the parameters specific to each beamline e.g. PV name prefixes, KP, KI, KD values, current limits and position thresholds.
All components of this file needs to be instantiated for each XBPM. 
