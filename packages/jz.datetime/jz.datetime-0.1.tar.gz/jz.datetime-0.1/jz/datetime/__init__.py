r"""Date and Time helper functions.

"""

# python modules
import time
from datetime import date


def timestamp(dt):
	"""Return timestamp from datetime object.

		>>> import datetime
		>>> d = datetime.datetime(2008, 4, 23, 12, 44, 05)
		>>> timestamp(d)
		1208943845

		>>> timestamp(None)
		0
	"""

	if dt is not None:
		return int(time.mktime(dt.timetuple()))
	return 0


def getFormattedDate(date, request):
	"""Format date according to locale in given request."""

	return request.locale.dates.getFormatter('date', 'short').format(date)


def getFormattedDateTime(datetime, request):

	return request.locale.dates.getFormatter('date', 'short').format(datetime)


def datefromdatetime(dt):
	"""Get date from a datetime object. If None given, returns None.

	>>> from datetime import datetime
	>>> dt = datetime(2007, 10, 30, 15, 33, 49)
	>>> datefromdatetime(dt)
	datetime.date(2007, 10, 30)

	>>> datefromdatetime(None) is None
	True
	"""

	if dt is not None:
		return date.fromtimestamp(time.mktime(dt.timetuple()))
	return None