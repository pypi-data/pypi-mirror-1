
from _test import *

from hgsvn import svnclient

import time


def eq_utc_timestamp(timestamp, time_tuple):
    eq_(time.gmtime(timestamp)[:6], time_tuple)


class TestSVNDate(object):
    def test_parse(self):
        svn_date = "2007-05-01T18:33:32.749605Z"
        timestamp = svnclient.svn_date_to_timestamp(svn_date)
        eq_(timestamp, 1178044412)
        eq_utc_timestamp(timestamp, (2007, 5, 1, 18, 33, 32))


svn_info_xml = """<?xml version="1.0"?>
<info>
<entry
   kind="dir"
   path="trunk"
   revision="20191">
<url>svn://svn.twistedmatrix.com/svn/Twisted/trunk</url>
<repository>
<root>svn://svn.twistedmatrix.com/svn/Twisted</root>
<uuid>bbbe8e31-12d6-0310-92fd-ac37d47ddeeb</uuid>
</repository>
<commit
   revision="20185">
<author>ralphm</author>
<date>2007-05-04T10:47:32.843908Z</date>
</commit>
</entry>
</info>
"""

class TestSVNInfo(object):
    def test_parse(self):
        d = svnclient.parse_svn_info_xml(svn_info_xml)
        eq_(d['url'], 'svn://svn.twistedmatrix.com/svn/Twisted/trunk')
        eq_(d['repos_url'], 'svn://svn.twistedmatrix.com/svn/Twisted')
        eq_(d['revision'], 20191)
        eq_(d['last_changed_rev'], 20185)


svn_log_xml = """<?xml version="1.0"?>
<log>
<logentry
   revision="1777">
<author>apitrou</author>
<date>2007-03-29T09:37:56.023608Z</date>
<paths>
<path
   copyfrom-path="/scripts"
   copyfrom-rev="1776"
   action="A">/hgsvn</path>
<path
   action="D">/scripts</path>
</paths>
<msg>move dir to better-named location

</msg>
</logentry>
<logentry
   revision="1776">
<author>apitrou</author>
<date>2007-03-28T16:51:15.339713Z</date>
<paths>
<path
   action="M">/scripts/hgimportsvn.py</path>
</paths>
<msg>automatically detect a parent hg repo tracking the parent SVN branch,
and pull from it.

</msg>
</logentry>
</log>
"""

class TestSVNLog(object):
    def test_parse(self):
        entries = svnclient.parse_svn_log_xml(svn_log_xml)
        eq_(len(entries), 2)
        e = entries[0]
        eq_(e['author'], 'apitrou')
        eq_(e['revision'], 1777)
        eq_utc_timestamp(e['date'], (2007, 3, 29, 9, 37, 56))
        eq_(e['message'], "move dir to better-named location\n\n")
        paths = e['changed_paths']
        eq_(len(paths), 2)
        p = paths[0]
        eq_(p, {
            'path': '/hgsvn',
            'action': 'A',
            'copyfrom_path': '/scripts',
            'copyfrom_revision': 1776,
        })
        p = paths[1]
        eq_(p, {
            'path': '/scripts',
            'action': 'D',
            'copyfrom_path': None,
            'copyfrom_revision': None,
        })
        e = entries[1]
        eq_(e['author'], 'apitrou')
        eq_(e['revision'], 1776)
        eq_utc_timestamp(e['date'], (2007, 3, 28, 16, 51, 15))
        eq_(len(e['changed_paths']), 1)


svn_status_xml = """<?xml version="1.0"?>
<status>
<entry
   path="_doc.html">
<wc-status
   props="none"
   item="unversioned">
</wc-status>
</entry>
<entry
   path="ez_setup">
<wc-status
   props="none"
   item="external">
</wc-status>
</entry>
<entry
   path="hgcreatesvn.py">
<wc-status
   props="normal"
   item="normal"
   revision="1962">
<commit
   revision="1774">
<author>apitrou</author>
<date>2007-03-28T15:22:22.975800Z</date>
</commit>
</wc-status>
</entry>
<entry
   path="hgsvn/svnclient.py">
<wc-status
   props="none"
   item="modified"
   revision="1962">
<commit
   revision="1962">
<author>apitrou</author>
<date>2007-05-04T19:59:06.567367Z</date>
</commit>
</wc-status>
</entry>
</status>
"""

svn_status_xml_with_base_dir = """<?xml version="1.0"?>
<status>
<target
   path="/home/antoine/hgsvn">
<entry
   path="/home/antoine/hgsvn/build">
<wc-status
   props="none"
   item="unversioned">
</wc-status>
</entry>
</target>
</status>
"""

class TestSVNStatus(object):
    def test_parse(self):
        entries = svnclient.parse_svn_status_xml(svn_status_xml)
        eq_(len(entries), 4)
        e = entries[0]
        eq_(e['path'], '_doc.html')
        eq_(e['type'], 'unversioned')
        e = entries[1]
        eq_(e['path'], 'ez_setup')
        eq_(e['type'], 'external')
        e = entries[2]
        eq_(e['path'], 'hgcreatesvn.py')
        eq_(e['type'], 'normal')
        e = entries[3]
        eq_(e['path'], 'hgsvn/svnclient.py')
        eq_(e['type'], 'normal')

    def test_parse_with_base_dir(self):
        entries = svnclient.parse_svn_status_xml(
            svn_status_xml_with_base_dir, '/home/antoine/hgsvn')
        eq_(len(entries), 1)
        e = entries[0]
        eq_(e['path'], 'build')
        eq_(e['type'], 'unversioned')
