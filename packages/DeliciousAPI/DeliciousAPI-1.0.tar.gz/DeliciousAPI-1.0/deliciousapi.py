"""
    Unofficial Python API for retrieving data from del.icio.us.

    This module provides the following features:

    * getting a user's tags including tag counts, i.e. her tagging vocabulary
    * getting a url's so-called 'common tags', i.e. the most popular tags
      assigned to user bookmarks of said url, if any (number between 0 and 25)
    * getting the total number of bookmarks for a url, i.e. the number of
      users who have bookmarked the url
    * HTTP proxy support

    Note: Only public del.icio.us data will be mined (read below). This means
    that this API does not (yet) provide means to access your private bookmark
    data.

    The official del.icio.us API does not provide the functionality mentioned
    above, so this module will query the del.icio.us website directly and
    extract the required information by parsing the HTML code of the resulting
    web pages (a kind of poor man's web mining). The module is able to detect
    IP throttling, which is employed by del.icio.us to temporarily block
    abusive HTTP request behavior, and will raise a custom Python error to
    indicate that. Please be a nice netizen and do not stress the del.icio.us
    service more than necessary.

    It is strongly advised that you read the del.icio.us Terms of Use
    before using this Python module. In particular, read section 5
    'Intellectual Property'.

    The code is licensed to you under version 2 of the GNU General Public
    License.

    More information about this module can be found at
    http://www.michael-noll.com/2006/12/18/delicious-python-api/

    (c) 2006-2007 Michael G. Noll <http://www.michael-noll.com/>
"""
import cgi
import httplib
import md5
import re
import time
import xml.dom.minidom

class DeliciousAPI(object):
    """This class provides a custom, unofficial API to the del.icio.us service.

    Instead of querying the official del.icio.us API (which has limited
    functionality), this class retrieves information from the del.icio.us
    website directly and extracts data from the web pages.

    Note that del.icio.us will block clients with too many queries in a
    certain timeframe (similar to their API throttling). So be a nice citizen
    and don't stress their website.

    """

    def __init__(self, http_proxy="", tries=3, wait_seconds=3, user_agent="Mozilla/4.0 (compatible; research)"):
        """Set up the API module.

        Parameters:
            http_proxy (optional)
                Use an HTTP proxy for HTTP connections.
                Format: "hostname:port" (e.g., "localhost:8080")

            tries (optional, default: 3):
                Try the specified number of times when downloading a
                monitored document fails. tries must be >= 1.
                See also wait_seconds.

            wait_seconds (optional, default: 3):
                Wait the specified number of seconds before re-trying to
                download a monitored document. wait_seconds must be >= 0.
                See also tries.

            user_agent (optional, default: "Mozilla/4.0 (compatible; research)")
                Set the User-Agent HTTP Header.

        """
        self.http_proxy = http_proxy
        self.tries = tries
        assert self.tries >= 1
        self.wait_seconds = wait_seconds
        assert self.wait_seconds >= 0
        self.user_agent = user_agent


    def _query(self, path):
        """Queries delicious for information, specified by (query) path.

        Returns None on errors (i.e. on all HTTP status other than 200).
        On success, returns the content of the HTML response.
        """

        # compose delicious query
        method = "GET"
        headers = { 'User-agent' : self.user_agent }
        body = None

        conn = None
        if self.http_proxy:
            host, port = self.http_proxy.split(":")
            conn = httplib.HTTPConnection(host, port)
        else:
            conn = httplib.HTTPConnection("del.icio.us")
        conn.request(method, "".join(["http://del.icio.us", path]), body, headers)

        data = None

        tries = self.tries
        while tries > 0:
            try:
                # read response from server
                response = conn.getresponse()

                if response.status == 200:
                    data = response.read()
                elif response.status == 999:
                    # [Excerpt from corresponding HTML error page]
                    # Sorry, Unable to process request at this time -- error 999
                    # 
                    # Sorry, you've been temporarily blocked for accessing del.icio.us
                    # too rapidly. This could be the result of using a buggy, misconfigured,
                    # or malicious program. It could also be accidental on our part. Please
                    # hold off for a few minutes and try again later, in a gentler fashion.
                    #
                    # If you think we've wrongly blocked you and it continues to happen,
                    # let us know. This link will bring you to a Yahoo website. When filling
                    # out this report, please ignore the Yahoo ID field.
                    #
                    # - the del.icio.us staff
                    conn.close()
                    raise DeliciousThrottleError, "del.icio.us error %s - unable to process request (your IP address has been throttled/blocked)" % response.status
                else:
                    conn.close()
                    raise DeliciousUnknownError, "del.icio.us error %s - unknown error" % response.status
                break
            except httplib.BadStatusLine:
                # wait a bit and then try again
                time.sleep(self.wait_seconds)
            tries -= 1

        conn.close()
        return data


    def get_tags(self, username):
        """Returns user's tags from del.icio.us (his tagging 'vocabulary', as used in displaying the tag cloud)."""
        tags = []

        path = "".join(["/", username, "?setminposts=1&setbundleview=hide"])
        data = self._query(path)
        if data:
            tags = self._extract_tags_from_user_page(data)
        return tags

    def _extract_tags_from_user_page(self, data):
        tags_counts = []

        # remove newlines so the regex does work correctly
        data = data.replace('\n', '')

        # find the user's list of tags
        regex_tagcloud = re.compile(r'<li.*?class="bundle fold".*?><h3.*?>.*?</h3>(?P<tags>.*)</li>[\s]*<li.*?class="bundle fold options">')

        div_tagcloud = regex_tagcloud.search(data)
        if div_tagcloud:
            tags_content = div_tagcloud.group('tags')
            # we need an enclosing DOM element or minidom parsing will break
            tags_content = "".join(["<tags>", tags_content, "</tags>"])

            dom = xml.dom.minidom.parseString(tags_content)

            counts = []
            tags = []
            # format: <li><span>4</span> <a href="/USERNAME/TAG">TAG</a></li>
            for span in dom.getElementsByTagName('span'):
                counts.append(int(span.firstChild.nodeValue));
            for link in dom.getElementsByTagName('a'):
                link_name = self._html_escape(link.firstChild.nodeValue)
                tags.append(link_name.lower())

            assert len(counts) == len(tags)
            tags_counts = zip(tags, counts)
        return tags_counts

    def get_number_of_users(self, url):
        """Returns the number of users who have rated this url at del.icio.us."""
        number_of_users = 0

        m = md5.new()
        m.update(url)
        hash = m.hexdigest()

        path = "".join(["/url/", hash])
        data = self._query(path)
        if data:
            number_of_users = self._extract_number_of_users(data)
        return number_of_users

    def get_common_tags(self, url):
        """Returns the list of "common tags" of url from del.icio.us."""
        tags = []

        m = md5.new()
        m.update(url)
        hash = m.hexdigest()

        path = "".join(["/url/", hash])
        data = self._query(path)
        if data:
            tags = self._extract_common_tags_from_url_history(data)
        return tags

    def _extract_number_of_users(self, data):
        number_of_users = 0

        # remove newlines so the regex does work correctly
        data = data.replace('\n', '')

        # find number of users who have rated a url in a url detail page on del.icio.us
        regex_users = re.compile(r'<h4.*?class="smaller nom".*?>(?P<number_of_users>.*?)</h4>')
        regex_usercount = re.compile(r'this url has been saved by (?P<usercount>[0-9]*?) (people|person).')

        div_users = regex_users.search(data)
        if div_users:
            content = div_users.group('number_of_users')
            result = regex_usercount.search(content)
            if result:
                number_of_users = result.group('usercount')
        return number_of_users

    def _extract_common_tags_from_url_history(self, data):
        tags = []

        # remove newlines so the regex does work correctly
        data = data.replace('\n', '')

        # find "common tags" in a url detail page on del.icio.us
        regex_tagcloud = re.compile(r'<div.*?class="alphacloud".*?>(?P<tags>.*?)</div>')

        div_tagcloud = regex_tagcloud.search(data)
        if div_tagcloud:
            tags_content = div_tagcloud.group('tags')

            # we need an enclosing DOM element or minidom parsing will break
            tags_content = "".join(["<tags>", tags_content, "</tags>"])

            dom = xml.dom.minidom.parseString(tags_content)
            for tag in dom.getElementsByTagName('a'):
                tag_name = self._html_escape(tag.firstChild.nodeValue)
                count = 0
                tag_class = tag.getAttribute("class")
                if tag_class and len(tag_class) > 1:
                    count = int(tag_class[1:])
                tags.append((tag_name.lower(), count))
        return tags

    def _html_escape(self, s):
        """HTML-escape a string or object.

        This converts any non-string objects passed into it to strings
        (actually, using ``unicode()``).  All values returned are
        non-unicode strings (using ``&#num;`` entities for all non-ASCII
        characters).

        None is treated specially, and returns the empty string.
        """
        if s is None:
            return ''
        if not isinstance(s, basestring):
            if hasattr(s, '__unicode__'):
                s = unicode(s)
            else:
                s = str(s)
        s = cgi.escape(s, True)
        if isinstance(s, unicode):
            s = s.encode('ascii', 'xmlcharrefreplace')
        return s


class DeliciousError(Exception):
    """Used to indicate that an error occurred when trying to access del.icio.us via its API."""

class DeliciousThrottleError(DeliciousError):
    """Used to indicate that the client computer (i.e. its IP address) has been temporarily blocked by del.icio.us."""

class DeliciousUnknownError(DeliciousError):
    """Used to indicate that del.icio.us returned an (HTTP) error which we don't know how to handle yet."""

