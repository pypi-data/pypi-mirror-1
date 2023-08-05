##############################################################################
#
# Copyright (c) 2002-2006 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""PostgreSQL Database Adapter for Zope 3

$Id: adapter.py 84319 2008-02-27 07:51:06Z srichter $
"""
import datetime
import psycopg
import re
import sys
import zope.interface
import zope.rdb
from zope.datetime import tzinfo
from zope.interface import implements

from zope.rdb.interfaces import DatabaseException, IZopeConnection
from zope.publisher.interfaces import Retry


# These OIDs are taken from include/server/pg_type.h from PostgreSQL headers.
# Unfortunatelly psycopg does not export them as constants, and
# we cannot use psycopg.FOO.values because they overlap.
DATE_OID        = 1082
TIME_OID        = 1083
TIMETZ_OID      = 1266
TIMESTAMP_OID   = 1114
TIMESTAMPTZ_OID = 1184
INTERVAL_OID    = 1186

CHAR_OID = 18
TEXT_OID = 25
BPCHAR_OID = 1042
VARCHAR_OID = 1043

# The following ones are obsolete and we don't handle them
#ABSTIME_OID     = 702
#RELTIME_OID     = 703
#TINTERVAL_OID   = 704

# Date/time parsing functions

_dateFmt = re.compile(r"^(\d\d\d\d)-?([01]\d)-?([0-3]\d)$")

def parse_date(s):
    """Parses ISO-8601 compliant dates and returns a tuple (year, month,
    day).

    The following formats are accepted:
        YYYY-MM-DD  (extended format)
        YYYYMMDD    (basic format)
    """
    m = _dateFmt.match(s)
    if m is None:
        raise ValueError, 'invalid date string: %s' % s
    year, month, day = m.groups()
    return int(year), int(month), int(day)


_timeFmt = re.compile(
    r"^([0-2]\d)(?::?([0-5]\d)(?::?([0-5]\d)(?:[.,](\d+))?)?)?$")

def parse_time(s):
    """Parses ISO-8601 compliant times and returns a tuple (hour, minute,
    second).

    The following formats are accepted:
        HH:MM:SS.ssss or HHMMSS.ssss
        HH:MM:SS,ssss or HHMMSS,ssss
        HH:MM:SS      or HHMMSS
        HH:MM         or HHMM
        HH
    """
    m = _timeFmt.match(s)
    if m is None:
        raise ValueError, 'invalid time string: %s' % s
    hr, mn, sc, msc = m.groups(0)
    if msc != 0:
        sc = float("%s.%s" % (sc, msc))
    else:
        sc = int(sc)
    return int(hr), int(mn), sc


_tzFmt = re.compile(r"^([+-])([0-2]\d)(?::?([0-5]\d))?$")

def parse_tz(s):
    """Parses ISO-8601 timezones and returns the offset east of UTC in
    minutes.

    The following formats are accepted:
        +/-HH:MM
        +/-HHMM
        +/-HH
        Z           (equivalent to +0000)
    """
    if s == 'Z':
        return 0
    m = _tzFmt.match(s)
    if m is None:
        raise ValueError, 'invalid time zone: %s' % s
    d, hoff, moff = m.groups(0)
    if d == "-":
        return - int(hoff) * 60 - int(moff)
    return int(hoff) * 60 + int(moff)


_tzPos = re.compile(r"[Z+-]")

def parse_timetz(s):
    """Parses ISO-8601 compliant times that may include timezone information
    and returns a tuple (hour, minute, second, tzoffset).

    tzoffset is the offset east of UTC in minutes.  It will be None if s does
    not include time zone information.

    Formats accepted are those listed in the descriptions of parse_time() and
    parse_tz().  Time zone should immediatelly follow time without intervening
    spaces.
    """
    m = _tzPos.search(s)
    if m is None:
        return parse_time(s) + (None,)
    pos = m.start()
    return parse_time(s[:pos]) + (parse_tz(s[pos:]),)


_datetimeFmt = re.compile(r"[T ]")

def _split_datetime(s):
    """Split date and time parts of ISO-8601 compliant timestamp and
    return a tuple (date, time).

    ' ' or 'T' used to separate date and time parts.
    """
    m = _datetimeFmt.search(s)
    if m is None:
        raise ValueError, 'time part of datetime missing: %s' % s
    pos = m.start()
    return s[:pos], s[pos + 1:]


def parse_datetime(s):
    """Parses ISO-8601 compliant timestamp and returns a tuple (year, month,
    day, hour, minute, second).

    Formats accepted are those listed in the descriptions of parse_date() and
    parse_time() with ' ' or 'T' used to separate date and time parts.
    """
    dt, tm = _split_datetime(s)
    return parse_date(dt) + parse_time(tm)


def parse_datetimetz(s):
    """Parses ISO-8601 compliant timestamp that may include timezone
    information and returns a tuple (year, month, day, hour, minute, second,
    tzoffset).

    tzoffset is the offset east of UTC in minutes.  It will be None if s does
    not include time zone information.

    Formats accepted are those listed in the descriptions of parse_date() and
    parse_timetz() with ' ' or 'T' used to separate date and time parts.
    """
    dt, tm = _split_datetime(s)
    return parse_date(dt) + parse_timetz(tm)


def parse_interval(s):
    """Parses PostgreSQL interval notation and returns a tuple (years, months,
    days, hours, minutes, seconds).

    Values accepted:
        interval  ::= date
                   |  time
                   |  date time
        date      ::= date_comp
                   |  date date_comp
        date_comp ::= 1 'day'
                   |  number 'days'
                   |  1 'month'
\                   |  1 'mon'
                   |  number 'months'
                   |  number 'mons'
                   |  1 'year'
                   |  number 'years'
        time      ::= number ':' number
                   |  number ':' number ':' number
                   |  number ':' number ':' number '.' fraction
    """
    years = months = days = 0
    hours = minutes = seconds = 0
    elements = s.split()
    # Tests with 7.4.6 on Ubuntu 5.4 interval output returns 'mon' and 'mons'
    # and not 'month' or 'months' as expected. I've fixed this and left
    # the original matches there too in case this is dependant on
    # OS or PostgreSQL release.
    for i in range(0, len(elements) - 1, 2):
        count, unit = elements[i:i+2]
        if unit == 'day' and count == '1':
            days += 1
        elif unit == 'days':
            days += int(count)
        elif unit == 'month' and count == '1':
            months += 1
        elif unit == 'mon' and count == '1':
            months += 1
        elif unit == 'months':
            months += int(count)
        elif unit == 'mons':
            months += int(count)
        elif unit == 'year' and count == '1':
            years += 1
        elif unit == 'years':
            years += int(count)
        else:
            raise ValueError, 'unknown time interval %s %s' % (count, unit)
    if len(elements) % 2 == 1:
        hours, minutes, seconds = parse_time(elements[-1])
    return (years, months, days, hours, minutes, seconds)


# Type conversions
def _conv_date(s):
    if s:
        return datetime.date(*parse_date(s))

def _conv_time(s):
    if s:
        hr, mn, sc = parse_time(s)
        sc, micro = divmod(sc, 1.0)
        micro = round(micro * 1000000)
        return datetime.time(hr, mn, int(sc), int(micro))

def _conv_timetz(s):
    if s:
        hr, mn, sc, tz = parse_timetz(s)
        sc, micro = divmod(sc, 1.0)
        micro = round(micro * 1000000)
        if tz:
            tz = tzinfo(tz)
        return datetime.time(hr, mn, int(sc), int(micro), tz)

def _conv_timestamp(s):
    if s:
        y, m, d, hr, mn, sc = parse_datetime(s)
        sc, micro = divmod(sc, 1.0)
        micro = round(micro * 1000000)
        return datetime.datetime(y, m, d, hr, mn, int(sc), int(micro))

def _conv_timestamptz(s):
    if s:
        y, m, d, hr, mn, sc, tz = parse_datetimetz(s)
        sc, micro = divmod(sc, 1.0)
        micro = round(micro * 1000000)
        if tz:
            tz = tzinfo(tz)
        return datetime.datetime(y, m, d, hr, mn, int(sc), int(micro), tz)

def _conv_interval(s):
    if s:
        y, m, d, hr, mn, sc = parse_interval(s)
        if (y, m) != (0, 0):
            # XXX: Currently there's no way to represent years and months as
            # timedeltas
            return s
        else:
            return datetime.timedelta(days=d, hours=hr, minutes=mn, seconds=sc)

def _get_string_conv(encoding):
    def _conv_string(s):
        if s is not None:
            s = s.decode(encoding)
        return s
    return _conv_string

# User-defined types
DATE = psycopg.new_type((DATE_OID,), "ZDATE", _conv_date)
TIME = psycopg.new_type((TIME_OID,), "ZTIME", _conv_time)
TIMETZ = psycopg.new_type((TIMETZ_OID,), "ZTIMETZ", _conv_timetz)
TIMESTAMP = psycopg.new_type((TIMESTAMP_OID,), "ZTIMESTAMP", _conv_timestamp)
TIMESTAMPTZ = psycopg.new_type((TIMESTAMPTZ_OID,), "ZTIMESTAMPTZ",
                                _conv_timestamptz)
INTERVAL = psycopg.new_type((INTERVAL_OID,), "ZINTERVAL", _conv_interval)


dsn2option_mapping = {'host': 'host',
                      'port': 'port',
                      'dbname': 'dbname',
                      'username': 'user',
                      'password': 'password'}

def registerTypes(encoding):
    """Register type conversions for psycopg"""
    psycopg.register_type(DATE)
    psycopg.register_type(TIME)
    psycopg.register_type(TIMETZ)
    psycopg.register_type(TIMESTAMP)
    psycopg.register_type(TIMESTAMPTZ)
    psycopg.register_type(INTERVAL)
    STRING = psycopg.new_type((CHAR_OID, TEXT_OID, BPCHAR_OID, VARCHAR_OID),
                              "ZSTRING", _get_string_conv(encoding))
    psycopg.register_type(STRING)

class PsycopgAdapter(zope.rdb.ZopeDatabaseAdapter):
    """A PsycoPG adapter for Zope3.

    The following type conversions are performed:

        DATE -> datetime.date
        TIME -> datetime.time
        TIMETZ -> datetime.time
        TIMESTAMP -> datetime.datetime
        TIMESTAMPTZ -> datetime.datetime

    XXX: INTERVAL cannot be represented exactly as datetime.timedelta since
    it might be something like '1 month', which is a variable number of days.
    """

    def connect(self):
        if not self.isConnected():
            try:
                self._v_connection = PsycopgConnection(
                        self._connection_factory(), self
                        )
            except psycopg.Error, error:
                raise DatabaseException, str(error)

    def registerTypes(self):
        registerTypes(self.getEncoding())

    def _connection_factory(self):
        """Create a Psycopg DBI connection based on the DSN"""
        self.registerTypes()
        conn_info = zope.rdb.parseDSN(self.dsn)
        conn_list = []
        for dsnname, optname in dsn2option_mapping.iteritems():
            if conn_info[dsnname]:
                conn_list.append('%s=%s' % (optname, conn_info[dsnname]))
        conn_str = ' '.join(conn_list)
        connection = psycopg.connect(conn_str)

        # Ensure we are in SERIALIZABLE transaction isolation level.
        # This is the default under psycopg1, but changed to READ COMMITTED
        # under psycopg2. This should become an option if anyone wants
        # different isolation levels.
        connection.set_isolation_level(3)

        return connection


def _handle_psycopg_exception(error):
    """Called from a exception handler for psycopg.Error.

    If we have a serialization exception or a deadlock, we should retry the
    transaction by raising a Retry exception. Otherwise, we reraise.
    """
    if not error.args:
        raise
    msg = error.args[0]
    # These messages are from PostgreSQL 8.0. They may change between
    # PostgreSQL releases - if so, the different messages should be added
    # rather than the existing ones changed so this logic works with
    # different versions.
    if msg.startswith(
            'ERROR:  could not serialize access due to concurrent update'
            ):
        raise Retry(sys.exc_info())
    if msg.startswith('ERROR:  deadlock detected'):
        raise Retry(sys.exc_info())
    raise


class IPsycopgZopeConnection(IZopeConnection):
    """A marker interface stating that this connection uses PostgreSQL."""


class PsycopgConnection(zope.rdb.ZopeConnection):
    zope.interface.implements(IPsycopgZopeConnection)

    def cursor(self):
        """See IZopeConnection"""
        return PsycopgCursor(self.conn.cursor(), self)

    def commit(self):
        try:
            zope.rdb.ZopeConnection.commit(self)
        except psycopg.Error, error:
            _handle_psycopg_exception(error)


class PsycopgCursor(zope.rdb.ZopeCursor):

    def execute(self, operation, parameters=None):
        """See IZopeCursor"""
        try:
            return zope.rdb.ZopeCursor.execute(self, operation, parameters)
        except psycopg.Error, error:
            _handle_psycopg_exception(error)

    def executemany(operation, seq_of_parameters=None):
        """See IZopeCursor"""
        raise RuntimeError, 'Oos'
        try:
            return zope.rdb.ZopeCursor.execute(
                self, operation, seq_of_parameters)
        except psycopg.Error, error:
            _handle_psycopg_exception(error)
