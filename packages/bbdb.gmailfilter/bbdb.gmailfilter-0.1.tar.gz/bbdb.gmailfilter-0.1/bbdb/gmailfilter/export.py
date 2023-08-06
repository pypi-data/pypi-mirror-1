import optparse
import time
import datetime
import rfc822

from zope.pagetemplate import pagetemplatefile

parser = optparse.OptionParser()

def dateToID(date):
    return'%s%s' % (
        int(time.mktime(date.timetuple())), str(date.microsecond)[:3])

def parseFilters(filters):
    for filter_ in filters:
        stamp, name, label, addresses = filter_.split(',', 3)
        date = datetime.datetime(
            *time.strptime(stamp, '%Y-%m-%d')[:3])
        yield {'date': date,
               'id': dateToID(datetime.datetime.now()),
               'label': label,
               'name': name,
               'value': ' OR '.join(
                   [i[1] for i in rfc822.AddressList(addresses)])}

def main(args=None):
    options, args = parser.parse_args(args=args)
    author, email = args[:2]
    filters = list(parseFilters(args[2:]))
    ids = ','.join(filter_['id'] for filter_ in filters)
    now = datetime.datetime.now()

    template = pagetemplatefile.PageTemplateFile('gmail-filter.pt')
    print template(
        now=now, ids=ids, author=author, email=email,
        filters=filters)
