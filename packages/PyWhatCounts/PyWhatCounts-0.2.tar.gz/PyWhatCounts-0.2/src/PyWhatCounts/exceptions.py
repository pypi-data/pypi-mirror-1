"""A few custom exceptions to delineate the difference between a bad value being
passed to WC and an unexpected response from WC."""

class WCAuthError(EnvironmentError):
	"""Used only in instances where realm or api key seem to be invalid"""

class WCUserError(EnvironmentError):
	"""Used to describe an error with info going into WC (usually indicated by
	a message returned by WC starting with FAILURE:"""

class WCSystemError(EnvironmentError):
	"""Used to indicate an unexpected response from WC"""
