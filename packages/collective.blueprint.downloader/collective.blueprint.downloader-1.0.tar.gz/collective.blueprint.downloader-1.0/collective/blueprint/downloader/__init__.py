import os
import string
import urllib2

from urllibcache import build_opener

from collective.transmogrifier.interfaces import ISectionBlueprint
from collective.transmogrifier.interfaces import ISection
from zope.interface import classProvides
from zope.interface import implements


def normalize_path(path):
    return os.path.expanduser(string.Template(path).safe_substitute(os.environ))


class Downloader(object):
    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.previous = previous
        if options.get('cache', True):
            if 'cache_path' in options:
                cache_path = options.get('cache_path')
            else:
                cache_path = os.path.join('$CLIENT_HOME', 'urllibcache')
            cache_path = normalize_path(cache_path)
            if not os.path.exists(cache_path):
                os.mkdir(cache_path)
            self.opener = build_opener(cache_path)
        else:
            self.opener = urllib2.build_opener()
        self.keys = [x.strip() for x in options['keys'].split('\n')]
        ignored_errors = options.get('ignored_errors', '')
        self.ignored_errors = [int(x) for x in ignored_errors.split(',')]

    def __iter__(self):
        for item in self.previous:
            for key in self.keys:
                if key in item:
                    if not item[key]:
                        del item[key]
                        continue
                    try:
                        item[key] = self.opener.open(item[key])
                    except urllib2.HTTPError, e:
                        if e.code not in self.ignored_errors:
                            raise
                        del item[key]
            yield item
