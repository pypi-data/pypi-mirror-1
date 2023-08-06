# Copyright 2009, Red Hat, Inc
# Copyright 2009, Yaakov Nemoy
#
# This software may be freely redistributed under the terms of the GNU
# general public license, version 2 or higher.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
from __future__ import with_statement

import datetime
import dateutil.parser
import gzip
import itertools
import mailbox

from configobj import ConfigObj
from dateutil.relativedelta import relativedelta
from os import makedirs
from os.path import join
from urllib import urlopen, urlretrieve

from sqlalchemy import *
from sqlalchemy.exceptions import InvalidRequestError

import model
import util

from model import *

config = ConfigObj('settings.ini')


def domain_counts_for_source(source):
    counts = session.query(func.count(Fact.sender_domain),
                         Fact.sender_domain)\
        .filter_by(source=source)\
        .group_by(Fact.sender_domain)\
        .order_by(func.count(Fact.sender_domain).desc())\
        .all()
    to_return = dict()
    for count, domain in counts:
        to_return[domain] = count
    return to_return
        

def sources_in_order_for_stream(stream):
    return session.query(Source)\
        .filter_by(stream=stream)\
        .order_by(Source.month)

def month_w_count(stream):
    for source in sources_in_order_for_stream(stream):
        yield (source.month, domain_counts_for_source(source))

def do_streams():
    for stream in session.query(Stream).all():
        pass

def do_month(month, year):
    for source in session.query(Source)\
            .filter_by(month=dateutil.parser.parse("%s %s" % (month, year))\
                           .replace(day=1))\
            .all():
        print domain_counts_for_source(source)

def periodic_totals(months, predicate):
    ytd = dict()
    first_month = None
    for month, counts in months:
        if not first_month:
            first_month = start_year_of(month)
        if predicate(month):
            if ytd == dict():
                pass
            else:
                yield (first_month, ytd)
                ytd = dict()
                first_month = month
        for domain, count in counts.iteritems():
            try:
                ytd[domain] += count
            except KeyError:
                ytd[domain] = count
    if first_month:
        yield (first_month, ytd)
    else:
        raise StopIteration

def start_year_of(date):
    if is_start_year(date):
        return date
    else:
        new_month = date.month - 1
        new_year = date.year if new_month else date.year - 1
        new_month = new_month if new_month else 12
        return start_year_of(date.replace(month=new_month, year=new_year))

def is_start_year(date):
    return date.month == int(config['new_years_month'])

def is_start_quarter(date):
    return date.month % 3 == int(config['new_years_month']) % 3

def yearly_totals(months):
    return periodic_totals(months, is_start_year)

def quarterly_totals(months):
    return periodic_totals(months, is_start_quarter)

def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = itertools.tee(iterable)
    try:
        b.next()
    except StopIteration:
        pass
    return itertools.izip(a, b)

def delta_counts(periods):
    for previous, current in pairwise(periods):
        prev_month, prev_counts = previous
        cur_month, cur_counts = current

        domains = set(prev_counts.keys()).union(cur_counts.keys())

        deltas = dict()
        for domain in domains:
            prev_count = prev_counts.get(domain, 0)
            cur_count = cur_counts.get(domain, 0)
            deltas[domain] = cur_count - prev_count
        yield prev_month, cur_month, deltas


def pairshift(i, j):
    i = iter(i)
    j = iter(j)
    yield i.next(), None
    for x in itertools.izip(i, j):
        yield x

#TODO: this is the wrong way to do strings
# I have a fine library for spitting out html that needs to be packaged in fedora first
def generate_period_table(mm, periods, deltas):
    yield "<table border=2>"
    yield "<tr><th>period</th><th>posts by domain</th><th>deltas since last period</th></tr>"
    for period, delta in pairshift(periods, deltas):
        to_yield = "<tr><td>" + period[0].strftime('%B %Y') + "</td><td><ul>"
        counts = period[1]
        if delta:
            delta_counts = delta[2]
        keys = sorted(counts, key=counts.get, reverse=True)
        for key in keys:
            to_yield += '<li>' + key + ' : ' + str(counts[key]) + '</li>'
        to_yield += '</ul></td><td><ul>'
        if delta:
            for key in keys:
                to_yield += '<li>' + key + ' : ' + str(delta_counts[key]) + '</li>'
            to_yield += '</ul></td></tr>'
        yield to_yield
    yield '</table>'

def generate_page(*iters):
    yield '<html><body>'
    for iter in iters:
        for i in iter:
            yield i
    yield '</body></html>'

def generate_mm_table(mm):
    month_periods = list(month_w_count(mm))
    month_deltas = list(delta_counts(month_periods))

    quarter_periods = list(quarterly_totals(month_periods))
    quarterly_deltas = list(delta_counts(quarter_periods))

    yearly_periods = list(yearly_totals(month_periods))
    yearly_deltas = list(delta_counts(yearly_periods))

    print 'mm'
    print mm.name, mm.type
    print

    print 'month'
    print month_periods
    print month_deltas
    print

    print 'quarter'
    print quarter_periods
    print quarterly_deltas
    print

    print 'year'
    print yearly_periods
    print yearly_deltas

    yield '<h1>' + mm.name + ' of type ' + mm.type + '</h1>'
    yield '<h2>monthly</h2>'
    for line in generate_period_table(mm, month_periods, month_deltas):
        yield line
        
    yield '<h2>quarterly</h2>'
    for line in generate_period_table(mm, quarter_periods, quarterly_deltas):
        yield line
        
    yield '<h2>yearly</h2>'
    for line in generate_period_table(mm, yearly_periods, yearly_deltas):
        yield line

def generate_all_tables():
    for mm in session.query(Stream).all():
        for line in generate_mm_table(mm):
            yield line

def generate_all_tables_page():
    for line in generate_page(generate_all_tables()):
        yield line
    

def write_graph_page(num):
    with file('graph.test.%s.html' % num, 'w') as f: 
        for line in generate_all_tables_page():
            f.write(line)

__all__ = ['domain_counts_for_source', 'sources_in_order_for_stream',
           'month_w_count', 'do_streams', 'do_month', 'periodic_totals',
           'start_year_of', 'is_start_year', 'is_start_quarter', 'yearly_totals',
           'quarterly_totals', 'pairwise', 'delta_counts', 'pairshift',
           'generate_page', 'generate_mm_table', 'generate_all_tables_page',
           'generate_all_tables', 'write_graph_page']
