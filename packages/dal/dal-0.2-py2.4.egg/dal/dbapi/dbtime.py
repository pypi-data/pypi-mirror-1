"""Provides datetime conversion functionality for dball database module
wrapper.  Also useful by itself.

LICENSE
=======

Copyright (c) 2004, Randall Smith
All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

    * Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
    * Neither the name of the <ORGANIZATION> nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""

__revision__ = '0.1'

import math
import copy

try:
    import mx.DateTime
    have_mxDateTime = True
except ImportError:
    have_mxDateTime = False

try:
    import datetime
    have_datetime = True
except ImportError:
    have_datetime = False

# mx.DateTime to Python datetime conversion functions

def mx2pydatetime(mxdt):
    """Converts mx.DateTime.DateTimeType to Python datetime.datetime."""
    year = mxdt.year
    month = mxdt.month
    day = mxdt.day
    hour = mxdt.hour
    minute = mxdt.minute
    decsec = math.modf(mxdt.second)
    sec = int(decsec[1])
    # floating points can be tricky
    # we are rounding
    msec = int(round(decsec[0] * 1000000))
    pytd = datetime.datetime(year, month, day, hour, minute, sec, msec)
    return pytd

def mx2pytime(mxtd):
    """Converts mx.DateTime.DateTimeDeltaType to Python datetime.time.
    
    mx.DateTime uses same class for time and datetime deltas.  This is the
    version with 0 day.
    """ 
    hour = mxtd.hour
    minute = mxtd.minute
    decsec = math.modf(mxtd.second)
    sec = int(decsec[1])
    msec = int(round(decsec[0] * 1000000))
    pydt = datetime.time(hour, minute, sec, msec)
    return pydt

def mx2pydtdelta(mxdtd):
    """Converts mx.DateTime.DateTimeDeltaType to Python datetime.time.
    
    mx.DateTime uses same class for time and datetime deltas.  This is the
    version with 0 day.
    """ 
    day = mxdtd.day
    hour = mxdtd.hour
    minute = mxdtd.minute
    decsec = math.modf(mxdtd.second)
    sec = int(decsec[1])
    msec = int(round(decsec[0] * 1000000))
    # recalc second
    sec = sec + hour * 3600 + minute * 60
    pydtd = datetime.timedelta(day, sec, msec)
    return pydtd

def mx2pydt(mxdt):
    """Executes correct mx2py conversion function."""
    if type(mxdt) == mx.DateTime.DateTimeType:
        return mx2pydatetime(mxdt)
    elif type(mxdt) == mx.DateTime.DateTimeDeltaType:
        # there is not a good way to determine if it is a time or delta
        # object. Unless obvious, assume it is a time.
        if mxdt.day == 0:
            return mx2pytime(mxdt)
        else:   
            return mx2pydtdelta(mxdt)
    else:
        raise Exception, 'Not a mx datetime type.'

# Python datetime to mx.DateTime conversion functions

def py2mxdatetime(pydt):
    """Converts Python datetime.datetime. to mx.DateTime.DateTimeType"""
    year = pydt.year
    month = pydt.month
    day = pydt.day
    hour, minute, sec = 0, 0, 0
    if isinstance(pydt, datetime.datetime):
        hour = pydt.hour
        minute = pydt.minute
        sec = pydt.second
        msec = pydt.microsecond
        sec = sec + msec / 1000000.0
    mxdt = mx.DateTime.DateTime(year, month, day, hour, minute, sec)
    return mxdt

def py2mxtime(pytd):
    """Converts Python datetime.time to mx.DateTime.DateTimeDeltaType
    
    Same as py2mxdtdelta, but without a day.
    """
    hour = pytd.hour
    minute = pytd.minute
    sec = pytd.second
    msec = pytd.microsecond
    sec = sec + msec / 1000000.0
    mxtd = mx.DateTime.TimeDelta(hour, minute, sec)
    return mxtd

def py2mxdtdelta(pydtd):
    """Converts Python datetime.time to mx.DateTime.DateTimeDeltaType"""
    day = pydtd.days
    sec = pydtd.seconds
    msec = pydtd.microseconds
    sec = sec + msec / 1000000.0
    mxdtd = mx.DateTime.DateTimeDelta(day, 0, 0, sec)
    return mxdtd

def py2mxdt(pydt):
    """Determines type and executes correct conversion."""
    if type(pydt) in (datetime.datetime, datetime.date):
        return py2mxdatetime(pydt)
    elif type(pydt) == datetime.time:
        return py2mxtime(pydt)
    elif type(pydt) == datetime.timedelta:
        return py2mxdtdelta(pydt)
    else:
        raise Exception, 'Not a Python datetime type.'

# Date and Time constructors

def construct_date(dtpref, year, month, day):
    """Creates date object for preferred type."""
    if dtpref == 'py':
        return datetime.date(year, month, day)
    elif dtpref == 'mx':
        return mx.DateTime.Date(year, month, day)
    else:
        # what exception should be raised here?
        raise Exception, 'Improper DATETIME set.'

def construct_time(dtpref, hour, minute, second):
    """Creates time object for preferred type."""
    if dtpref == 'py':
        return datetime.time(hour, minute, second)
    elif dtpref == 'mx':
        return mx.DateTime.Time(hour, minute, second)
    else:
        # what exception should be raised here?
        raise Exception, 'Improper DATETIME set.'

def construct_timestamp(dtpref, year, month, day, hour, minute, second):
    """Creates timestamp object for preferred type."""
    if dtpref == 'py':
        return datetime.datetime(year, month, day, hour, minute, second)
    elif dtpref == 'mx':
        return mx.DateTime.DateTime(year, month, day, hour, minute, second)
    else:
        # what exception should be raised here?
        raise Exception, 'Improper DATETIME set.'

def construct_datefromticks(dtpref, ticks):
    """Creates date object for preferred type and ticks."""
    if dtpref == 'py':
        return datetime.date.fromtimestamp(ticks)
    elif dtpref == 'mx':
        return mx.DateTime.DateFromTicks(ticks)
    else:
        # what exception should be raised here?
        raise Exception, 'Improper DATETIME set.'

def construct_timefromticks(dtpref, ticks):
    """Creates time object for preferred type and ticks."""
    if dtpref == 'py':
        return datetime.datetime.fromtimestamp(ticks).time()
    elif dtpref == 'mx':
        return mx.DateTime.TimeFromTicks(ticks)
    else:
        # what exception should be raised here?
        raise Exception, 'Improper DATETIME set.'

def construct_timestampfromticks(dtpref, ticks):
    """Creates timestamp object for preferred type and ticks."""
    if dtpref == 'py':
        return datetime.datetime.fromtimestamp(ticks)
    elif dtpref == 'mx':
        return mx.DateTime.localtime(ticks)
    else:
        # what exception should be raised here?
        raise Exception, 'Improper DATETIME set.'

# Other functions

def dtsubnative(dtpref, dbmod, params):
    """identfies datetime types and subs in driver objects
    
    Usually occurs before paramater conversion
    Will call either Date, Time, or Timestamp
    """
    # Don't change the original params.
    params = copy.copy(params)
    # params could be a list, dictionary, or list of dictionaries.
    def convertdt(param):
        nparam = param
        if dtpref == 'py':
            if type(param) == datetime.time:
                nparam = dbmod.Time(param.hour, param.minute, param.second)
            elif type(param) == datetime.datetime:
                nparam = dbmod.Timestamp(param.year, param.month, param.day,
                                       param.hour, param.minute, param.second)
            elif type(param) == datetime.date:
                nparam = dbmod.Date(param.year, param.month, param.day)
            else:
                # not a datetime field
                pass
        elif dtpref == 'mx':
            if type(param) == mx.DateTime.DateTimeDeltaType:
                sec = int(math.modf(param.second)[0])
                nparam = dbmod.Time(param.hour, param.minute, sec)
            elif type(param) == mx.DateTime.DateTimeType:
                sec = int(math.modf(param.second)[0])
                nparam = dbmod.Timestamp(param.year, param.month, param.day,
                                       param.hour, param.minute, sec)
            else:
                # not a datetime field
                pass
        else:
            raise ValueError, 'dbpref value not known.'
        return nparam

    def convert_dparams(dparams):
        # Convert dictionary of parameters.
        for key, value in dparams.items():
            dparams[key] = convertdt(value)
        return dparams

    if type(params) == dict:
        params = convert_dparams(params)
    elif type(params) == list:
        for key in xrange(len(params)):
            if type(params[key]) == dict:
                params[key] = convert_dparams(params[key])
            else:
                params[key] = convertdt(params[key])
    else:
        raise ValueError, 'params should be list or dict.'
    return params

def native2pref(nativedt, pref, dt_type=None, conv_func=None):
    """Converts a datetime returned by db to preferred datetime object type."""

    def convert2pref(dto, dto_class, pref):
        """Executes correct conversion based on preference and dto type."""
        if dto_class == pref:
            return dto
        elif dto_class == 'py' and pref == 'mx':
            return py2mxdt(dto)
        elif dto_class == 'mx' and pref == 'py':
            return mx2pydt(dto)
        else:
            raise Exception, 'unknown dto_class/pref combination'
    # what type of object is this?
    nativedt_class = dtclass(nativedt)
    if nativedt == None:
        prefdt = None
    elif conv_func != None:
        new_dto = conv_func(nativedt, pref, dt_type)
        # may return preferred object type or Python datetime
        # if latter, we must convert to preferred type
        new_dto_class = dtclass(new_dto)
        if new_dto_class == pref:
            prefdt = new_dto
        else:
            prefdt = convert2pref(new_dto, new_dto_class, pref)
    elif nativedt_class == pref:
        prefdt = nativedt
    elif nativedt_class == None:
        # we do not know what it is
        # try string conversion
        if have_mxDateTime:
            dto = dtfromstr(nativedt)
            prefdt = convert2pref(dto, 'mx', pref)
    else:
        # convert
        prefdt = convert2pref(nativedt, nativedt_class, pref)
    return prefdt

def dtclass(dto):
    """Determines what general type of object a datetime object is."""
    dto_type = None # default
    if dto_type == None and have_datetime:
        clist = [datetime.datetime, datetime.date, datetime.time]
        clist.append(datetime.timedelta)
        if type(dto) in clist:
            dto_type = 'py'
    if dto_type == None and have_mxDateTime:
        clist = [mx.DateTime.DateTimeType, mx.DateTime.DateTimeDeltaType]
        if type(dto) in clist:
            dto_type = 'mx'
    return dto_type

def dtfromstr(dt_thing, which_type=None):
    """Attemts to transform something (string or object) to datetime
    
    Uses mx's string parser
    """
    assert which_type in ['datetime', 'date', 'time', None]
    dt_str = str(dt_thing)

    def try2parse(type_guess):
        """Attempts to parse db_str based on type_guess
        
        Returns either the parsed result (mx type) or None if could not parse.
        """
        date_formats = mx.DateTime.Parser._date_formats[:-1]
        pfuncs = {}
        pfuncs['datetime'] = mx.DateTime.Parser.DateTimeFromString
        pfuncs['date'] = mx.DateTime.Parser.DateFromString
        pfuncs['time'] = mx.DateTime.Parser.TimeFromString
        try:
            if type_guess == 'time':
                parsed_dt = pfuncs[type_guess](dt_str)
            else:
                parsed_dt = pfuncs[type_guess](dt_str, date_formats)
        except ValueError:
            parsed_dt = None
        if type_guess == 'time':
            # time does not throw an exception
            # 0 value means no match
            if parsed_dt == 0:
                parsed_dt = None
        return parsed_dt
           
    if which_type == None:
        # go through all possible options
        for type_guess in ['datetime', 'date', 'time']:
            parsed_dt = try2parse(type_guess)
            if parsed_dt != None:
                break
    else:
        parsed_dt = try2parse(which_type)
    if parsed_dt == None:
        return dt_thing
    else:
        return parsed_dt

def main():
    """Just some tests."""
    # test mx2py
    mxdt = mx.DateTime.now()
    pydt = mx2pydatetime(mxdt)
    assert mxdt.year == pydt.year
    assert mxdt.month == pydt.month
    assert mxdt.day == pydt.day
    assert mxdt.hour == pydt.hour
    assert mxdt.minute == pydt.minute
    assert math.floor(mxdt.second) == pydt.second
    assert round(math.modf(mxdt.second)[0] * 1000000) == pydt.microsecond

    # test py2mx
    pydt = datetime.datetime.now()
    mxdt = py2mxdatetime(pydt)
    assert pydt.year == mxdt.year
    assert pydt.month == mxdt.month
    assert pydt.day == mxdt.day
    assert pydt.hour == mxdt.hour
    assert pydt.minute == mxdt.minute
    assert pydt.second == math.floor(mxdt.second)
    # use round becuase math.modf returns floating point approximation
    # 123456 may look like 123455.999999999999
    # int would misrepresent it
    assert pydt.microsecond == int(round(math.modf(mxdt.second)[0] * 1000000))

    # test py2mxtime
    pytime = datetime.datetime.now().time()
    mxtime = py2mxtime(pytime) 
    assert mxtime.hour == pytime.hour
    assert mxtime.minute == pytime.minute
    assert math.floor(mxtime.second) == pytime.second
    mxtime_msec = int(round(math.modf(mxtime.second)[0] * 1000000))
    assert mxtime_msec == pytime.microsecond

    # test mx2pydtdelta
    mxdt = mx.DateTime.now()
    mxdtd = mx.DateTime.DateTimeDelta(0, mxdt.hour, mxdt.minute, mxdt.second)
    pydtd = mx2pydtdelta(mxdtd)
    assert mxdtd.day == pydtd.days
    mxdtd_sec = int(math.modf(mxdtd.seconds)[1])
    assert mxdtd_sec == pydtd.seconds
    mxdtd_msec = int(round(math.modf(mxdtd.seconds)[0] * 1000000))
    assert mxdtd_msec == pydtd.microseconds

    # test py2mxdtdelta
    pydt = datetime.datetime.now()
    pydtd = datetime.timedelta(0, pydt.second, pydt.microsecond, 0,
                               pydt.minute, pydt.hour)
    mxdtd = py2mxdtdelta(pydtd)
    assert pydtd.days == mxdtd.day
    assert pydtd.seconds == int(math.modf(mxdtd.seconds)[1])
    mxdtd_msec = int(round(math.modf(mxdtd.seconds)[0] * 1000000))
    assert pydtd.microseconds == mxdtd_msec

if __name__ == '__main__':
    for i in xrange(1000):
        main()
