# -*- coding: UTF-8 -*-

# Copyright (c) 2007 Felix Schwarz <felix.schwarz@oss.schwarz.eu>
#
# This code is placed under the MIT license:
#
# Permission is hereby granted, free of charge, to any person obtaining a copy 
# of this software and associated documentation files (the "Software"), to deal 
# in the Software without restriction, including without limitation the rights 
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell 
# copies of the Software, and to permit persons to whom the Software is 
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in 
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, 
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE 
# SOFTWARE.

import time

import turbogears


class TimeoutException(Exception):
	"A timeout occured!"
	pass


def get_received_mail(sink):
	"""Return the first mail received (which is removed from the TurboMail
	queue) in the following format {'client': ...., 'from': ..., 
	'recipients': ..., 'mail': ...}. Blocks the caller until a message was 
	received but no longer than 10 seconds (in this case, a TimeoutException
	is thrown)."""
	for i in range(10 * 10):
		if not sink.has_message():
			time.sleep(0.1)
		else:
			break
	if not sink.has_message():
		raise TimeoutException()
	return sink.pop(index=0)


def save_config(keys):
	"""Return a dictionary with the original configuration for the specified
	keys."""
	original_config = {}
	for key in keys:
		original_config[key] = turbogears.config.get(key)
	return original_config


