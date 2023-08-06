# -*- coding: utf-8 -*-
__all__ = ['SubRipFile', 'SubRipItem', 'SubRipTime']
import re
import sys
from os import path
from UserList import UserList
try:
    from cStringIO import cStringIO as StringIO
except ImportError:
    from StringIO import StringIO


def str_keys(dic):
    return dict((str(k), v) for k, v in dic.iteritems())


class InvalidItem(Exception):
    pass


class TimeItemDescriptor(object):

    def __init__(self, ratio, super_ratio=None):
        self.ratio = int(ratio)
        self.super_ratio = int(super_ratio) if super_ratio else None

    def __get__(self, instance, klass):
        if instance is None:
            raise AttributeError
        if self.super_ratio:
            return (instance.ordinal % self.super_ratio) / self.ratio
        return instance.ordinal / self.ratio

    def __set__(self, instance, value):
        base_ord = instance.ordinal
        if self.super_ratio:
            base_ord %= self.super_ratio
        current_part = base_ord - instance.ordinal % self.ratio
        instance.ordinal += value * self.ratio - current_part


class SubRipTime(object):
    STRING_FORMAT = '%02d:%02d:%02d,%03d'
    RE_TIME = re.compile(r'''(?P<hours>\d{2}):
                             (?P<minutes>\d{2}):
                             (?P<seconds>\d{2}),
                             (?P<micro_seconds>\d{3})''',
                             re.VERBOSE)
    SECONDS_RATIO = 1000
    MINUTES_RATIO = SECONDS_RATIO * 60
    HOURS_RATIO = MINUTES_RATIO * 60

    hours = TimeItemDescriptor(HOURS_RATIO)
    minutes = TimeItemDescriptor(MINUTES_RATIO, HOURS_RATIO)
    seconds = TimeItemDescriptor(SECONDS_RATIO, MINUTES_RATIO)
    micro_seconds = TimeItemDescriptor(1, SECONDS_RATIO)

    def __init__(self, hours=0, minutes=0, seconds=0, micro_seconds=0):
        """SubRipTime(hours, minutes, seconds, micro_seconds)

        All arguments are optional and have a default value of 0.
        """
        self.ordinal = hours * self.HOURS_RATIO \
                     + minutes * self.MINUTES_RATIO \
                     + seconds * self.SECONDS_RATIO \
                     + micro_seconds

    def __unicode__(self):
        return unicode(self.STRING_FORMAT) % (self.hours,
            self.minutes, self.seconds, self.micro_seconds)

    def shift(self, *args, **kwargs):
        """shift(hours, minutes, seconds, micro_seconds)

        All arguments are optional and have a default value of 0.
        """
        self.ordinal += self.__class__(*args, **kwargs).ordinal

    @classmethod
    def from_ordinal(self, ordinal):
        new_time = cls()
        new_time.ordinal = int(ordinal)
        return new_time

    @classmethod
    def from_string(cls, source):
        match = re.match(cls.RE_TIME, source)
        if not match:
            raise InvalidItem
        items = dict((k, int(v)) for k, v in match.groupdict().items())
        return cls(**items)


class SubRipItem(object):
    RE_ITEM = ur'''(?P<id>\d+)
(?P<start>\d{2}:\d{2}:\d{2},\d{3}) --> (?P<end>\d{2}:\d{2}:\d{2},\d{3})
(?P<sub_title>.*)'''

    def __init__(self, id=0, start=None, end=None, sub_title=''):
        self. id = int(id)
        self.start = start or SubRipTime()
        self.end = end or SubRipTime()
        self.sub_title = unicode(sub_title)

    def __unicode__(self):
        return u'%s\n%s --> %s\n%s\n\n' % (self.id,
            self.start, self.end, self.sub_title)

    def shift(self, *args, **kwargs):
        """shift(hours, minutes, seconds, micro_seconds)

        All arguments are optional and have a default value of 0.
        """
        self.start.shift(*args, **kwargs)
        self.end.shift(*args, **kwargs)

    @classmethod
    def from_string(cls, source):
        match = re.match(cls.RE_ITEM, source, re.MULTILINE)
        if not match:
            raise InvalidItem
        datas = dict(match.groupdict())
        datas['start'] = SubRipTime.from_string(datas['start'])
        datas['end'] = SubRipTime.from_string(datas['end'])
        return cls(**str_keys(datas))


class SubRipFile(object, UserList):

    def __init__(self, source_path='', encoding='utf-8'):
        """SubRipFile([source_path, [encoding]])
        """
        UserList.__init__(self)
        if path:
            if path.exists(source_path) and path.isfile(source_path):
                f = open(source_path, 'rU')
            else:
                f = StringIO(source_path)
            string_buffer = StringIO()
            for line in f:
                if line.strip():
                    string_buffer.write(line)
                else:
                    string_buffer.seek(0)
                    source = unicode(string_buffer.read(), encoding)
                    new_item = SubRipItem.from_string(source)
                    self.data.append(new_item)
                    string_buffer.truncate(0)
            f.close()

    def shift(self, *args, **kwargs):
        """shift(hours, minutes, seconds, micro_seconds)

        All arguments are optional and have a default value of 0.
        """
        for item in self:
            item.shift(*args, **kwargs)

    def save(self, path, encoding='utf-8'):
        f = open(path, 'w+')
        for item in self:
            f.write(unicode(item).encode(encoding))
        f.close()
