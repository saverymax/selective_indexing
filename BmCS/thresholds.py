"""
Threshold variables.
The voting and CNN thresholds
are only used for testing, 
and not in the production model.

Thresholds are chosen in generate_results.py,
by selecting threshold that generates result
closes to .995 recall, for each model. 
The group thresholds are chosen the same way,
but --group_thresh and --group "group" must be provided
"""

COMBINED_THRESH = .0015
PRECISION_THRESH = .8984
VOTING_THRESH = .034
VOTING_JURISPRUDENCE_THRESH = .185
VOTING_SCIENCE_THRESH = .075
CNN_THRESH = .0237
CNN_JURISPRUDENCE_THRESH = .45
CNN_SCIENCE_THRESH = .15
SCIENCE_THRESH = .0036 #.02
JURISPRUDENCE_THRESH = .075 #Halved from .15 
BIOTECH_THRESH = .0007
CHEMISTRY_THRESH = .0017
