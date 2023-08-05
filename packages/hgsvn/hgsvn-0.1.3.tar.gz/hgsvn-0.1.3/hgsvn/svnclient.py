
from hgsvn.common import run_svn
from hgsvn.errors import EmptySVNLog

import os
import time
import calendar
import operator

try:
    from xml.etree import cElementTree as ET
except ImportError:
    try:
        from xml.etree import ElementTree as ET
    except ImportError:
        try:
            import cElementTree as ET
        except ImportError:
            from elementtree import ElementTree as ET


svn_log_args = ['log', '--xml', '-v']
svn_info_args = ['info', '--xml']
svn_checkout_args = ['checkout', '-q']
svn_status_args = ['status', '--xml', '-v', '--ignore-externals']


def svn_date_to_timestamp(svn_date):
    """
    Parse an SVN date as read from the XML output and return the corresponding
    timestamp.
    """
    # Strip microseconds and timezone (always UTC, hopefully)
    # XXX there are various ISO datetime parsing routines out there,
    # cf. http://seehuhn.de/comp/pdate
    date = svn_date.split('.', 2)[0]
    time_tuple = time.strptime(date, "%Y-%m-%dT%H:%M:%S")
    return calendar.timegm(time_tuple)

def parse_svn_info_xml(xml_string):
    """
    Parse the XML output from an "svn info" command and extract useful information
    as a dict.
    """
    d = {}
    tree = ET.fromstring(xml_string)
    entry = tree.find('.//entry')
    d['url'] = entry.find('url').text
    d['revision'] = int(entry.get('revision'))
    d['repos_url'] = tree.find('.//repository/root').text
    d['last_changed_rev'] = int(tree.find('.//commit').get('revision'))
    return d

def parse_svn_log_xml(xml_string):
    """
    Parse the XML output from an "svn log" command and extract useful information
    as a list of dicts (one per log changeset).
    """
    l = []
    tree = ET.fromstring(xml_string)
    for entry in tree.findall('logentry'):
        d = {}
        d['revision'] = int(entry.get('revision'))
        author = entry.find('author')
        # Some revisions don't have authors, most notably the first revision
        # in a repository.
        d['author'] = author is not None and author.text or None
        d['date'] = svn_date_to_timestamp(entry.find('date').text)
        d['message'] = entry.find('msg').text or ""
        paths = d['changed_paths'] = []
        for path in entry.findall('.//path'):
            copyfrom_rev = path.get('copyfrom-rev')
            if copyfrom_rev:
                copyfrom_rev = int(copyfrom_rev)
            paths.append({
                'path': path.text,
                'action': path.get('action'),
                'copyfrom_path': path.get('copyfrom-path'),
                'copyfrom_revision': copyfrom_rev,
            })
        l.append(d)
    return l

def parse_svn_status_xml(xml_string, base_dir=None):
    """
    Parse the XML output from an "svn status" command and extract useful info
    as a list of dicts (one per status entry).
    """
    l = []
    tree = ET.fromstring(xml_string)
    for entry in tree.findall('.//entry'):
        d = {}
        path = entry.get('path')
        if base_dir is not None:
            assert path.startswith(base_dir)
            path = path[len(base_dir):].lstrip('/\\')
        d['path'] = path
        wc_status = entry.find('wc-status')
        if wc_status.get('item') == 'external':
            d['type'] = 'external'
        elif wc_status.get('revision') is not None:
            d['type'] = 'normal'
        else:
            d['type'] = 'unversioned'
        l.append(d)
    return l

def get_svn_info(svn_url_or_wc, rev_number=None):
    """
    Get SVN information for the given URL or working copy, with an optionally
    specified revision number.
    Returns a dict as created by parse_svn_info_xml().
    """
    if rev_number is not None:
        args = ['-r', rev_number]
    else:
        args = []
    xml_string = run_svn(svn_info_args + args + [svn_url_or_wc],
        fail_if_stderr=True)
    return parse_svn_info_xml(xml_string)

def svn_checkout(svn_url, checkout_dir, rev_number=None):
    """
    Checkout the given URL at an optional revision number.
    """
    args = []
    if rev_number is not None:
        args += ['-r', rev_number]
    args += [svn_url, checkout_dir]
    return run_svn(svn_checkout_args + args)

def run_svn_log(svn_url_or_wc, rev_start, rev_end, limit, stop_on_copy=False):
    """
    Fetch up to 'limit' SVN log entries between the given revisions.
    """
    if stop_on_copy:
        args = ['--stop-on-copy']
    else:
        args = []
    args += ['-r', '%s:%s' % (rev_start, rev_end), '--limit', limit, svn_url_or_wc]
    xml_string = run_svn(svn_log_args + args)
    return parse_svn_log_xml(xml_string)

def get_svn_status(svn_wc):
    """
    Get SVN status information about the given working copy.
    """
    # Ensure proper stripping by canonicalizing the path
    svn_wc = os.path.abspath(svn_wc)
    args = [svn_wc]
    xml_string = run_svn(svn_status_args + args)
    return parse_svn_status_xml(xml_string, svn_wc)

def get_one_svn_log_entry(svn_url, rev_start, rev_end, stop_on_copy=False):
    """
    Get the first SVN log entry in the requested revision range.
    """
    entries = run_svn_log(svn_url, rev_start, rev_end, 1, stop_on_copy)
    if entries:
        return entries[0]

    # XXX performance optimization disabled because it disturbs --stop-on-copy

    #sign = rev_start <= rev_end and 1 or -1
    #cmp_func = rev_start <= rev_end and operator.le or operator.ge
    #interval = 1
    #while cmp_func(rev_start, rev_end):
        #rev_stop = rev_start + interval * sign
        #if cmp_func(rev_end, rev_stop):
            #rev_stop = rev_end
        #try:
            #entries = run_svn_log(svn_url, rev_start, rev_stop, 1, stop_on_copy)
        #except RuntimeError:
            ## It's likely this happens because the specific branch doesn't exist
            ## in the request revision range, so increase the latter big time.
            #rev_start = rev_stop + sign
            #interval *= 50
            #continue
        #if entries:
            #return entries[0]
        #rev_start = rev_stop + sign
        #interval *= 8
        #entries = run_svn_log(svn_url, rev_start, rev_stop, 1, stop_on_copy)

    raise EmptySVNLog("No SVN log for %s between revisions %s and %s" %
        (svn_url, rev_start, rev_end))


def get_first_svn_log_entry(svn_url, rev_start, rev_end):
    """
    Get the first log entry after (or at) the given revision number in an SVN branch.
    By default the revision number is set to 0, which will give you the log
    entry corresponding to the branch creaction.

    NOTE: to know whether the branch creation corresponds to an SVN import or
    a copy from another branch, inspect elements of the 'changed_paths' entry
    in the returned dictionary.
    """
    return get_one_svn_log_entry(svn_url, rev_start, rev_end, stop_on_copy=True)

def get_last_svn_log_entry(svn_url, rev_start, rev_end):
    """
    Get the last log entry before (or at) the given revision number in an SVN branch.
    By default the revision number is set to HEAD, which will give you the log
    entry corresponding to the latest commit in branch.
    """
    return get_one_svn_log_entry(svn_url, rev_end, rev_start, stop_on_copy=True)


log_duration_threshold = 10.0
log_min_chunk_length = 10

def iter_svn_log_entries(svn_url, first_rev, last_rev):
    """
    Iterate over SVN log entries between first_rev and last_rev.

    This function features chunked log fetching so that it isn't too nasty
    to the SVN server if many entries are requested.
    """
    cur_rev = first_rev
    chunk_length = log_min_chunk_length
    chunk_interval_factor = 1.0
    while last_rev == "HEAD" or cur_rev <= last_rev:
        start_t = time.time()
        stop_rev = min(last_rev, cur_rev + int(chunk_length * chunk_interval_factor))
        entries = run_svn_log(svn_url, cur_rev, stop_rev, chunk_length)
        duration = time.time() - start_t
        if not entries:
            if stop_rev == last_rev:
                break
            cur_rev = stop_rev + 1
            chunk_interval_factor *= 2.0
            continue
        for e in entries:
            yield e
        cur_rev = e['revision'] + 1
        # Adapt chunk length based on measured request duration
        if duration < log_duration_threshold:
            chunk_length = int(chunk_length * 2.0)
        elif duration > log_duration_threshold * 2:
            chunk_length = max(log_min_chunk_length, int(chunk_length / 2.0))


