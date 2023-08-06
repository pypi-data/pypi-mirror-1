# Copyright (c) 2009, Nokia Corp.
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of Nokia nor the names of its contributors may be
#       used to endorse or promote products derived from this software without
#       specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED THE COPYRIGHT HOLDERS AND CONTRIBUTORS ''AS IS''
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

__author__ = 'eemeli.kantola@iki.fi (Eemeli Kantola)'

from datetime import datetime

class XSDateTime(datetime):
    '''Extends the standard datetime.datetime to enable easy conversions between
    xs:datetime (ISO 8601 formatted strings) and Python datetimes. Ignores
    microseconds when converting to string, so you can for example get the current
    date properly formatted with str(XSDateTime.now()).
    '''
    
    @staticmethod
    def _convert(dt):
        return XSDateTime(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
    
    @staticmethod
    def parse(value, raise_on_error=False):
        '''Parses an ISO 8601 formatted string into an XSDateTime.
        
        >>> XSDateTime.parse('2009-09-09T10:30:55Z')
        XSDateTime(2009, 9, 9, 10, 30, 55)
        >>> XSDateTime.parse('some rubbish', raise_on_error=True)
        Traceback (most recent call last):
          ...
        ValueError: time data 'some rubbish' does not match format '%Y-%m-%dT%H:%M:%SZ'
        >>> XSDateTime.parse('some rubbish') is None
        True
        >>> XSDateTime.parse(None) is None
        True
        '''
        if raise_on_error:
            parsed = XSDateTime._parse(value)
        else:
            try:
                parsed = XSDateTime._parse(value) if value else None
            except ValueError:
                parsed = None
        
        return parsed

    @staticmethod
    def _parse(value):
        return XSDateTime.strptime(value, '%Y-%m-%dT%H:%M:%SZ')

    def __str__(self):
        '''Returns a string representation of the datetime in ISO 8601 format.
        
        >>> str(XSDateTime(2009, 9, 9, 10, 30, 55))
        '2009-09-09T10:30:55Z'
        >>> str(XSDateTime(2009, 9, 21))
        '2009-09-21T00:00:00Z'
        >>> str(XSDateTime(2009, 9, 9, 10, 30, 55, 123456))
        '2009-09-09T10:30:55Z'
        '''
        if not hasattr(self, '_cache__str__'):
            self._cache__str__ = self.replace(microsecond=0).isoformat() + 'Z'
        return self._cache__str__

    def __add__(self, other):
        '''x.__add__(y) <==> x+y
        
        >>> from datetime import timedelta
        >>> XSDateTime(2009, 9, 9, 13, 44, 5) + timedelta(hours=3)
        XSDateTime(2009, 9, 9, 16, 44, 5)
        '''
        return XSDateTime._convert(datetime.__add__(self, other))

    def __sub__(self, other):
        '''x.__add__(y) <==> x+y
        
        >>> from datetime import timedelta
        >>> XSDateTime(2009, 9, 9, 13, 44, 5) - timedelta(hours=3)
        XSDateTime(2009, 9, 9, 10, 44, 5)
        '''
        return XSDateTime._convert(datetime.__sub__(self, other))
