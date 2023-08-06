# python modules
from datetime import datetime, date
import time

# extra modules
import pytz


def tzinfo(request):
	#FIXME: this is hard coded for now. find a better way to do this

	return pytz.timezone('Asia/Jerusalem')


def add_tz_info(dt, tzinfo):
	"""Add timezone info to datetime or date object.

	dt: date or datetime object
	tzinfo: timezone info to add

	>>> from datetime import date, datetime
	>>> tz = tzinfo(None)
	>>> today = date.today()
	>>> now = datetime.now()

	>>> add_tz_info(today, tz) # doctest: +ELLIPSIS
	datetime.datetime(..., ..., ..., 0, 0, tzinfo=<DstTzInfo 'Asia/Jerusalem' JMT+2:21:00 STD>)

	>>> add_tz_info(now, tz) # doctest: +ELLIPSIS
	datetime.datetime(..., ..., ..., ..., ..., tzinfo=<DstTzInfo 'Asia/Jerusalem' JMT+2:21:00 STD>)

	"""

	try: # If we got a datetime object
		return datetime(dt.year, dt.month, dt.day, dt.hour, dt.minute, tzinfo=tzinfo)
	except AttributeError: # If we got a date object
		return datetime(dt.year, dt.month, dt.day, tzinfo=tzinfo)