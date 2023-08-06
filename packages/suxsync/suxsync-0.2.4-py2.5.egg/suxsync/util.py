"""
Utility functions
"""

SECONDS_PER_DAY = 60 * 60 * 24
MILLISECONDS_PER_SECOND = 1000.0

def timeDeltaToSeconds( aTimeDelta ):
    seconds = aTimeDelta.days * SECONDS_PER_DAY
    seconds = seconds + aTimeDelta.seconds
    
    return float(seconds)
    
    