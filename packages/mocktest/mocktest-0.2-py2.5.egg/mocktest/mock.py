__all__ = (
	'raw_mock',
	'mock_wrapper',
	'mock_on',
	'expect',
)

import sys
from mockmatcher import MockMatcher
from silentmock import SilentMock, raw_mock
from mockwrapper import MockWrapper, mock_wrapper
from mockanchor import MockAnchor, mock_on

def _setup():
	MockWrapper._setup()

def _teardown():
	MockWrapper._teardown()
	MockAnchor._reset_all()

def expect(wrapper_or_mock):
	if isinstance(wrapper_or_mock, SilentMock):
		wrapper = mock_wrapper(wrapper_or_mock)
	else:
		if not isinstance(wrapper, MockWrapper):
			raise TypeError("Expected %s or %s, got %s" % (MockWrapper.__name__, SilentMock.__name__, mock_wrapper.__class__.__name__))
		wrapper = wrapper_or_mock
	return wrapper.is_expected


