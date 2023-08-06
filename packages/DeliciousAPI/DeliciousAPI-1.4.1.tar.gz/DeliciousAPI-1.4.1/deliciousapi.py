"""
    Unofficial Python API for retrieving data from del.icio.us.

    This module provides the following features plus some more:

    * getting a url's full history with
        * users who bookmarked the url including tags used for such bookmarks
      	  and the creation time of the bookmark in YYYY-MM format
        * common tags (up to a maximum of 25) including weight (0...5)
    * getting a user's full bookmark collection including private bookmarks
      IF you know username AND password
    * getting a user's most recent public bookmarks if you do not know the
      password
    * getting a user's full tagging vocabulary, i.e. tags and tag counts,
      in case you do not know the password
    * HTTP proxy support

    The official del.icio.us API does not provide all the functionality mentioned
    above, and in such cases this module will query the del.icio.us *website*
    directly and extract the required information by parsing the HTML code of the
    resulting web pages (a kind of poor man's web mining). The module is able to
    detect IP throttling, which is employed by del.icio.us to temporarily block
    abusive HTTP request behavior, and will raise a custom Python error to
    indicate that. Please be a nice netizen and do not stress the del.icio.us
    service more than necessary.

    It is strongly advised that you read the del.icio.us Terms of Use
    before using this Python module. In particular, read section 5
    'Intellectual Property'.

    The code is licensed to you under version 2 of the GNU General Public
    License.

    More information about this module can be found at
    http://www.michael-noll.com/wiki/Del.icio.us_Python_API

    Copyright 2006-2008 Michael G. Noll <http://www.michael-noll.com/>

"""

__version__ = "1.4.1"

import base64
import cgi
import datetime
import httplib
import md5
import re
import socket
import time
import xml.dom.minidom

try:
    from BeautifulSoup import BeautifulSoup
except:
    print "ERROR: could not import BeautifulSoup Python module"
    print ""
    print "Since version 1.2, DeliciousAPI requires the BeautifulSoup module ()."
    print "You can download BeautifulSoup from the Python Cheese Shop at"
    print "http://cheeseshop.python.org/pypi/BeautifulSoup/"
    print "or directly from http://www.crummy.com/software/BeautifulSoup/"
    print ""
    raise

try:
    import feedparser
except:
    print "ERROR: could not import Universal Feed Parser module"
    print
    print "You can download Universal Feed Parser from the Python Cheese Shop at"
    print "http://pypi.python.org/pypi/FeedParser"
    print
    raise


class DeliciousUser(object):
    """This class wraps all available information about a user into one object.

    Variables:
        bookmarks:
            A list of (user, tags, title, notes, timestamp) tuples representing
            a user's bookmark collection.

            url is a 'unicode'
            tags is a 'list' of 'unicode'
            title is a 'unicode'
            notes is a 'unicode'
            timestamp is a 'datetime.datetime'

        tags (read-only property):
            A list of (tag, tag_count) tuples, aggregated over all a user's
            retrieved bookmarks. The tags represent a user's tagging vocabulary.

        username:
            The del.icio.us account name of the user.

    """

    def __init__(self, username, bookmarks=None):
        assert username
        self.username = username
        self.bookmarks = bookmarks or []

    def __str__(self):
        total_tag_count = 0
        total_tags = set()
        for url, tags, title, notes, timestamp in self.bookmarks:
            total_tag_count += len(tags)
            for tag in tags:
                total_tags.add(tag)
        return "[%s] %d bookmarks, %d tags (%d unique)" % \
                    (self.username, len(self.bookmarks), total_tag_count, len(total_tags))

    def __repr__(self):
        return self.username

    def get_tags(self):
        """Returns a dictionary mapping tags to their tag count.

        For example, if the tag count of tag 'foo' is 23, then
        23 bookmarks were annotated with 'foo'. A different way
        to put it is that 23 users used the tag 'foo' when
        bookmarking the URL.

        """

        total_tags = {}
        for url, tags, title, notes, timestamp in self.bookmarks:
            for tag in tags:
                total_tags[tag] = total_tags.get(tag, 0) + 1 
        return total_tags
    tags = property(fget=get_tags, doc="Returns a dictionary mapping tags to their tag count")


class DeliciousURL(object):
    """This class wraps all available information about a web document into one object.

    Variables:
        bookmarks:
            A list of (user, tags, timestamp tuples), representing a document's
            bookmark history.

            user is a 'str', tags is a 'list', timestamp is a 'str' in
            'YYYY-MM' format

        tags (read-only property):
            A list of (tag, tag_count) tuples, aggregated over all a document's
            retrieved bookmarks.

        common_tags:
            A list of (tag, tag_weight) tuples, representing a document's so-called
            "common tags", i.e. the up to 25 most popular tags for this document.

        url:
            The URL of the document.

    """

    def __init__(self, url, common_tags=None, bookmarks=None):
        assert url
        self.url = url
        self.common_tags = common_tags or []
        self.bookmarks = bookmarks or []

    def __str__(self):
        total_tag_count = 0
        total_tags = set()
        for user, tags, timestamp in self.bookmarks:
            total_tag_count += len(tags)
            for tag in tags:
                total_tags.add(tag)
        return "[%s] %d bookmarks (= users), %d tags (%d unique), %d out of 25 max 'common' tags" % \
                    (self.url, len(self.bookmarks), total_tag_count, \
                    len(total_tags), len(self.common_tags))

    def __repr__(self):
        return self.url

    def get_tags(self):
        """Returns a dictionary mapping tags to their tag count.

        For example, if the tag count of tag 'foo' is 23, then
        23 bookmarks were annotated with 'foo'. A different way
        to put it is that 23 users used the tag 'foo' when
        bookmarking the URL.

        """
        total_tags = {}
        for user, tags, timestamp in self.bookmarks:
            for tag in tags:
                total_tags[tag] = total_tags.get(tag, 0) + 1
        return total_tags
    tags = property(fget=get_tags, doc="Returns a dictionary mapping tags to their tag count")

class DeliciousAPI(object):
    """This class provides a custom, unofficial API to the del.icio.us service.

    Instead of querying the official del.icio.us API (which has limited
    functionality), this class retrieves information from the del.icio.us
    website directly and extracts data from the web pages.

    Note that del.icio.us will block clients with too many queries in a
    certain timeframe (similar to their API throttling). So be a nice citizen
    and don't stress their website.

    """

    def __init__(self,
                    http_proxy="",
                    tries=3,
                    wait_seconds=3,
                    user_agent="DeliciousAPI/%s \
                        (+http://www.michael-noll.com/wiki/Del.icio.us_Python_API)" % __version__,
                    timeout=30,
        ):
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

            timeout (optional, default: 30):
                Set network timeout. timeout must be >= 0.

        """
        assert tries >= 1
        assert wait_seconds >= 0
        assert timeout >= 0
        self.http_proxy = http_proxy
        self.tries = tries
        self.wait_seconds = wait_seconds
        self.user_agent = user_agent
        self.timeout = timeout
        socket.setdefaulttimeout(self.timeout)


    def _query(self, path, host="del.icio.us", user=None, password=None, use_ssl=False):
        """Queries delicious for information, specified by (query) path.

        Returns None on errors (i.e. on all HTTP status other than 200).
        On success, returns the content of the HTML response.

        """

        # compose delicious query
        method = "GET"
        headers = { 'User-agent' : self.user_agent }
        # add HTTP Basic authentication if available
        if user and password:
            encodedCredentials = base64.encodestring('%s:%s' % (user, password))[:-1]
            headers["Authorization"] = "Basic %s" % encodedCredentials

        body = None

        conn = None
        if use_ssl:
            port = 443
        else:
            port = 80
        if self.http_proxy:
            host, port = self.http_proxy.split(":")
        if use_ssl:
            conn = httplib.HTTPSConnection(host, port)
        else:
            conn = httplib.HTTPConnection(host, port)

        data = None

        tries = self.tries
        if use_ssl:
            protocol = "https"
        else:
            protocol = "http"
        while tries > 0:
            try:
                conn.request(method, "".join([protocol, "://", host, path]), body, headers)
                # read response from server
                response = conn.getresponse()

                if response.status == 200:
                    data = response.read()
                elif response.status == 302:
                    raise DeliciousMovedTemporarilyWarning, "del.icio.us status %s - url moved temporarily" % response.status
                elif response.status == 401:
                    raise DeliciousUnauthorizedError, "del.icio.us error %s - unauthorized (authentication failed?)" % response.status
                elif response.status == 404:
                    raise DeliciousNotFoundError, "del.icio.us error %s - url not found" % response.status
                elif response.status == 500:
                    raise Delicious500Error, "del.icio.us error %s - server problem" % response.status
                elif response.status == 999:
                    # [Excerpt from corresponding HTML error page]
                    # Unfortunately we are unable to process your request at this time.
                    # This error is usually temporary. Please try again later.
                    # 
                    # If you continue to experience this error, it may be caused by one
                    # of the following:
                    # 
                    #   * You may want to scan your system for spyware and viruses,
                    #     as they may interfere with your ability to connect to Yahoo!.
                    #     For detailed information on spyware and virus protection,
                    #     please visit the Yahoo! Security Center.
                    #
                    #   * This problem may be due to unusual network activity coming
                    #     from your Internet Service Provider. We recommend that you
                    #     report this problem to them. 
                    # 
                    # While this error is usually temporary, if it continues and the above
                    # solutions don't resolve your problem, please let us know.
                    # 
                    conn.close()
                    raise DeliciousThrottleError, "del.icio.us error %s - unable to process request (your IP address has been throttled/blocked)" % response.status
                else:
                    conn.close()
                    raise DeliciousUnknownError, "del.icio.us error %s - unknown error" % response.status
                break
            except httplib.BadStatusLine:
                # wait a bit and then try again
                time.sleep(self.wait_seconds)
            except socket.error, msg:
                # sometimes we get a "Connection Refused" error
                # wait a bit and then try again
                time.sleep(self.wait_seconds)
            tries -= 1

        conn.close()
        return data

    def get_url(self, url):
        """Returns a DeliciousURL instance representing the del.icio.us history of url.

        Generally, this method is what you want for getting bookmark, tag, and
        user information about a URL.

        """
        document = DeliciousURL(url)

        m = md5.new(url)
        hash = m.hexdigest()

        path = "".join(["/url/", hash, "?all"])
        data = self._query(path)
        if data:
            document.bookmarks = self._extract_bookmarks_from_url_history(data)
            document.common_tags = self._extract_common_tags_from_url_history(data)
        return document

    def _extract_bookmarks_from_url_history(self, data):
        bookmarks = []
        soup = BeautifulSoup(data)
        elements = soup.findAll(lambda tag:
                   (tag.name == "ul" and tag.attrs and 'class' in tag.attrs[0] and tag['class'] == 'historylist')
                or (tag.name == "h5" and tag.attrs and 'class' in tag.attrs[0] and tag['class'] == 'datehead')
        )
        timestamp = None
        for element in elements:
            # try to extract date information (the history page of a url
            # aggregates bookmarks into months, so we don't get a more
            # detailed view on date/time without analyzing each user's
            # bookmark collection (and this would hardly scale well in practice)
            #
            # Example:
            #   <h5 class="datehead">Aug &lsquo;07</h5>
            #   <ul class="historylist">
            #       <li><p>
            #           by <a class="who" href="/jsmith">jsmith</a>
            #           to <a href="/jsmith/foo">foo</a> <a href="/jsmith/bar">bar</a>
            #       </p></li>
            #   </ul>
            if element.name == 'h5':
                month_string = element.string
                timestamp = datetime.datetime.strptime(month_string, '%b &lsquo;%y')
            else:
                lis = element.findAll("li")
                for li in lis:
                    p = li.find("p")
                    links = p.findAll("a")
                    if links:
                        user_tags = []
                        user_a = links[0]
                        user = user_a.contents[0]
                        user_tags_a = links[1:]
                        for user_tag_a in user_tags_a:
                            if user_tag_a.contents:
                                user_tags.append(user_tag_a.contents[0])
                        timestamp_string = ""
                        if timestamp:
                            timestamp_string = timestamp.strftime('%Y-%m')
                        bookmarks.append( (user, user_tags, timestamp_string) )
        # put old bookmarks to the beginning, and new to the end
        bookmarks.reverse()
        return bookmarks

    def get_common_tags_of_url(self, url):
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

    def _extract_common_tags_from_url_history(self, data):
        common_tags = []
        soup = BeautifulSoup(data)
        div = soup.find("div", "alphacloud")
        if div:
            links = div.findAll("a")
            for link in links:
                tag = link.string
                cssClass = link['class']
                weight = 0
                if cssClass and len(cssClass) > 1:
                    try:
                        weight = int(cssClass[1:])
                    except ValueError:
                        pass
                common_tags.append( (tag, weight) )
        return common_tags

    def get_user(self, username, password=None):
        """Retrieves a user's bookmarks from del.icio.us.

        If a correct username AND password are supplied, a user's *full*
        bookmark collection (which also includes private bookmarks) is
        retrieved. Data communication is encrypted using SSL in this case.

        If no password is supplied, only the most recent public bookmarks
        of the user are extracted from his/her RSS feed (about 30 bookmarks
        if any). Note that if you want to get the *full* tagging vocabulary
        of the user even if you don't know the password, you can call
        get_tags_of_user() instead.

        This function can be used to backup all of a user's bookmarks if
        called with a username and password.

        Returns a DeliciousUser instance.

        """
        assert username
        user = DeliciousUser(username)
        bookmarks = []
        if password:
            # We have username AND password, so we call
            # the official del.ici.us API.
            path = "/v1/posts/all"
            data = self._query(path, host="api.del.icio.us", use_ssl=True, user=username, password=password)
            if data:
                soup = BeautifulSoup(data)
                elements = soup.findAll("post")
                for element in elements:
                    url = element["href"]
                    title = element["description"] or u""
                    notes = element["extended"] or u""
                    tags = None
                    if element["tag"]:
                        tags = element["tag"].split()
                    timestamp = datetime.datetime.strptime(element["time"], "%Y-%m-%dT%H:%M:%SZ")
                    bookmarks.append( (url, tags, title, notes, timestamp) )
            user.bookmarks = bookmarks
        else:
            # We have only the username, so we extract data from
            # the user's RSS feed. However, the feed is restricted
            # to the most recent public bookmarks of the user (about 30
            # if any)
            path = "/rss/%s" % username
            data = self._query(path, host="feeds.delicious.com", user=username)
            if data:
                f = feedparser.parse(data)
                for entry in f.entries:
                    url = entry.link
                    tags = []
                    if entry.tags and "term" in entry.tags[0]:
                        tags = entry.tags[0].term.split()
                    else:
                        tags.append(u"system:unfiled")
                    title = entry.title
                    notes = entry.summary
                    timestamp = datetime.datetime.strptime(entry.updated, "%Y-%m-%dT%H:%M:%SZ")
                    bookmarks.append( (url, tags, title, notes, timestamp) )
                user.bookmarks = bookmarks
        return user

    def get_tags_of_user(self, username):
        """
        Retrieves user's tags and their tag counts from del.icio.us.
        The tags represent a user's full tagging vocabulary.

        IF you know the user's password, then get_user() provides
        even more information.

        Returns a dictionary mapping tags to their tag counts.

        """
        tags = {}
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
        return dict(tags_counts)

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

class DeliciousWarning(Exception):
    """Used to indicate a warning when trying to access del.icio.us via its API.

    Warnings are raised when it is useful to alert the user of some condition
    where that condition doesn't warrant raising an exception and terminating
    the program. For example, we issue a warning when del.icio.us returns a
    HTTP status code for redirections (3xx).
    """

class DeliciousThrottleError(DeliciousError):
    """Used to indicate that the client computer (i.e. its IP address) has been temporarily blocked by del.icio.us."""
    pass

class DeliciousUnknownError(DeliciousError):
    """Used to indicate that del.icio.us returned an (HTTP) error which we don't know how to handle yet."""
    pass

class DeliciousUnauthorizedError(DeliciousError):
    """Used to indicate that del.icio.us returned a 401 Unauthorized error.

    Most of the time, the user credentials for acessing restricted (official)
    del.icio.us API functions are incorrect.

    """
    pass

class DeliciousNotFoundError(DeliciousError):
    """Used to indicate that del.icio.us returned a 404 Not Found error.

    Most of the time, retrying some seconds later fixes the problem
    (because we only query existing pages with this API).

    """
    pass

class Delicious500Error(DeliciousError):
    """Used to indicate that del.icio.us returned a 500 error.

    Most of the time, retrying some seconds later fixes the problem
    (because we only query existing pages with this API).

    """
    pass

class DeliciousMovedTemporarilyWarning(DeliciousWarning):
    """Used to indicate that del.icio.us returned a 302 Found (Moved Temporarily) redirection."""
    pass

__all__ = ['DeliciousAPI', 'DeliciousURL', 'DeliciousError', 'DeliciousThrottleError', 'DeliciousUnauthorizedError', 'DeliciousUnknownError', 'DeliciousNotFoundError' , 'Delicious500Error', 'DeliciousMovedTemporarilyWarning']

if __name__ == "__main__":
    d = DeliciousAPI()
    url = 'http://www.michael-noll.com/'
    print "Retrieving del.icio.us data for url '%s'" % url
    print "Note: This might take some time..."
    print "========================================================="
    document = d.get_url(url)
    print document
