import optparse
import time
import datetime
import rfc822

from zope.pagetemplate import pagetemplatefile

parser = optparse.OptionParser()

def dateToID(date):
    return'%s%s' % (
        int(time.mktime(date.timetuple())), str(date.microsecond)[:3])

ids = set()
def parseFilters(filters, ids=ids, max_=1500):
    props = {'to': {}, 'from': {}}
    for filter_ in filters:
        stamp, prop, label, addresses = filter_.split(',', 3)
        date = datetime.datetime(
            *time.strptime(stamp, '%Y-%m-%d')[:3])
        item = props[prop].setdefault(label, [date, set()])
        item[0] = max(item[0], date)
        item[1].update(
            addr[1] or addr[0]
            for addr in rfc822.AddressList(addresses))

    for prop, labels in props.iteritems():
        for label, (date, addresses) in labels.iteritems():
            while addresses:

                new = addr = ''
                value = '"%s"' % addresses.pop()
                while len(value)+len(new) < max_:
                    value += new
                    if not addresses:
                        break
                    addr = addresses.pop()
                    new = ' OR "%s"' % addr
                else:
                    # addr made it too long
                    # put it back in for the next filter
                    addresses.add(addr)

                int_id = int(time.mktime(date.timetuple())*1000)
                idx = 0
                id_ = str(int_id+idx)
                while id_ in ids:
                    idx += 1
                    assert idx < 86400*1000, (
                        'Could not find a unique ID within the date '
                        'specified: %s' % stamp)
                    id_ = str(int_id+idx)
                ids.add(id_)

                yield {'date': date,
                       'id': id_, 
                       'label': label.replace('.', '/'),
                       'name': prop,
                       'value': value}

def main(args=None):
    options, args = parser.parse_args(args=args)
    author, email = args[:2]
    ids = set()
    filters = tuple(parseFilters(args[2:], ids=ids))
    now = datetime.datetime.now()

    template = pagetemplatefile.PageTemplateFile('gmail-filter.pt')
    print template(now=now, ids=','.join(ids), author=author,
                   email=email, filters=filters)
