# -*- coding: utf-8 -*-
import re
from datetime import time

from srtexc import InvalidTimeString


class Comparable(object):
    """
    Some builtin types like datetime.time don't use the __cmp__ interface.
    This class map "rich comparison" methods to __cmp__
    http://docs.python.org/reference/datamodel.html#object.__ge__
    """

    def __build_comparator(*values):
        return lambda self, other: self.__cmp__(other) in values

    __eq__ = __build_comparator(0)
    __ne__ = __build_comparator(-1, 1)
    __lt__ = __build_comparator(-1)
    __le__ = __build_comparator(-1, 0)
    __gt__ = __build_comparator(1)
    __ge__ = __build_comparator(0, 1)


class TimeItemDescriptor(object):

    def __init__(self, ratio, super_ratio=0):
        self.ratio = int(ratio)
        self.super_ratio = int(super_ratio)

    def _get_ordinal(self, instance):
        if self.super_ratio:
            return instance.ordinal % self.super_ratio
        return instance.ordinal

    def __get__(self, instance, klass):
        if instance is None:
            raise AttributeError
        return self._get_ordinal(instance) / self.ratio

    def __set__(self, instance, value):
        part = self._get_ordinal(instance) - instance.ordinal % self.ratio
        instance.ordinal += value * self.ratio - part


class SubRipTime(Comparable):
    TIME_PATTERN = '%02d:%02d:%02d,%03d'
    TIME_REPR = 'SubRipTime(%d, %d, %d, %d)'
    RE_TIME = re.compile(r'(?P<hours>\d{2}):(?P<minutes>\d{2}):'
                         r'(?P<seconds>\d{2}),(?P<milliseconds>\d{3})')
    SECONDS_RATIO = 1000
    MINUTES_RATIO = SECONDS_RATIO * 60
    HOURS_RATIO = MINUTES_RATIO * 60

    hours = TimeItemDescriptor(HOURS_RATIO)
    minutes = TimeItemDescriptor(MINUTES_RATIO, HOURS_RATIO)
    seconds = TimeItemDescriptor(SECONDS_RATIO, MINUTES_RATIO)
    milliseconds = TimeItemDescriptor(1, SECONDS_RATIO)

    def __init__(self, hours=0, minutes=0, seconds=0, milliseconds=0):
        """
        SubRipTime(hours, minutes, seconds, milliseconds)

        All arguments are optional and have a default value of 0.
        """
        self.ordinal = hours * self.HOURS_RATIO \
                     + minutes * self.MINUTES_RATIO \
                     + seconds * self.SECONDS_RATIO \
                     + milliseconds

    def __repr__(self):
        return self.TIME_REPR % tuple(self)

    def __unicode__(self):
        return unicode(str(self))

    def __str__(self):
        return self.TIME_PATTERN % tuple(self)

    def __cmp__(self, other):
        return cmp(self.ordinal, self._coerce(other).ordinal)

    def __add__(self, other):
        return self.from_ordinal(self.ordinal + self._coerce(other).ordinal)

    def __iadd__(self, other):
        self.ordinal += self._coerce(other).ordinal
        return self

    def __sub__(self, other):
        return self.from_ordinal(self.ordinal - self._coerce(other).ordinal)

    def __isub__(self, other):
        self.ordinal -= self._coerce(other).ordinal
        return self

    @classmethod
    def _coerce(cls, other):
        if isinstance(other, SubRipTime):
            return other
        elif isinstance(other, basestring):
            return cls.from_string(other)
        elif isinstance(other, (int, long)):
            return cls.from_ordinal(other)
        elif isinstance(other, time):
            return cls.from_time(other)
        try:
            return cls(**other)
        except TypeError:
            return cls(*other)

    def __iter__(self):
        yield self.hours
        yield self.minutes
        yield self.seconds
        yield self.milliseconds

    def shift(self, *args, **kwargs):
        """
        shift(hours, minutes, seconds, milliseconds)

        All arguments are optional and have a default value of 0.
        """
        self += self.__class__(*args, **kwargs)

    @classmethod
    def from_ordinal(cls, ordinal):
        return cls(milliseconds=int(ordinal))

    @classmethod
    def from_string(cls, source):
        match = cls.RE_TIME.match(source)
        if not match:
            raise InvalidTimeString
        items = dict((k, int(v)) for k, v in match.groupdict().items())
        return cls(**items)

    @classmethod
    def from_time(cls, time):
        return cls(hours=time.hour, minutes=time.minute, seconds=time.second,
                   milliseconds=time.microsecond / 1000)

    def to_time(self):
        return time(self.hours, self.minutes, self.seconds,
                    self.milliseconds * 1000)
