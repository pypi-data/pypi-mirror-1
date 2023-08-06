#!/usr/bin/env python

# $Id: error.py 800 2009-02-11 18:30:04Z jaraco $

import ctypes
import ctypes.wintypes

def format_system_message(value):
	"""
	Call FormatMessage with a system error number to retrieve
	the descriptive error message.
	"""
	# first some flags used by FormatMessageW
	ALLOCATE_BUFFER = 0x100
	ARGUMENT_ARRAY = 0x2000
	FROM_HMODULE = 0x800
	FROM_STRING = 0x400
	FROM_SYSTEM = 0x1000
	IGNORE_INSERTS = 0x200
	
	# Let FormatMessageW allocate the buffer (we'll free it below)
	# Also, let it know we want a system error message.
	flags = ALLOCATE_BUFFER | FROM_SYSTEM
	source = None
	message_id = value
	language_id = 0
	result_buffer = ctypes.wintypes.LPWSTR()
	buffer_size = 0
	arguments = None
	bytes = ctypes.windll.kernel32.FormatMessageW(
		flags,
		source,
		message_id,
		language_id,
		ctypes.byref(result_buffer),
		buffer_size,
		arguments,
		)
	# note the following will cause an infinite loop if GetLastError
	#  repeatedly returns an error that cannot be formatted, although
	#  this should not happen.
	handle_nonzero_success(bytes)
	message = result_buffer.value
	ctypes.windll.kernel32.LocalFree(result_buffer)
	return message


class WindowsError(Exception):
	"more info about errors at http://msdn.microsoft.com/en-us/library/ms681381(VS.85).aspx"

	def __init__(self, value=None):
		if value is None:
			value = ctypes.windll.kernel32.GetLastError()
		self.value = value

	@property
	def message(self):
		return format_system_message(self.value)
	
	def __str__(self):
		return self.message

def handle_nonzero_success(result):
	if result == 0:
		raise WindowsError()
