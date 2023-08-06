# -*- coding: utf-8 -*-

import datetime
import rfc822 # A very versatile date/time parser.
import responses
import time


__all__ = ['responses', 'parse_date', 'format_date']


def parse_date(date_string):
    """Parse an RFC822 timestamp string into a datetime object."""
    
    return datetime.datetime(*rfc822.parsedate(date_string)[:7])


time_tuple_types = tuple
if hasattr(time, 'struct_time'):
    time_tuple_types = (tuple, time.struct_time)

def format_date(timestamp):
    """Format a datetime object as an RFC822 timestamp string."""
    
    if isinstance(timestamp, datetime.datetime):
        timestamp = time.mktime(timestamp.utctimetuple())
    elif isinstance(timestamp, time_tuple_types):
        timestamp = time.mktime(timestamp)
    
    return rfc822.formatdate(timestamp)
