#!/usr/bin/python

__author__ = "ccheever"
__doc__ = """
An example bunny1 server with some common commands that you might want to use.
"""

import urlparse
import subprocess

import bunny1
from bunny1 import cherrypy
from bunny1 import Content
from bunny1 import q
from bunny1 import qp
from bunny1 import expose
from bunny1 import dont_expose
from bunny1 import escape

def is_int(x):
    """tells whether something can be turned into an int or not"""
    try:
        int(x)
        return True
    except ValueError:
        return False

class ExampleCommands(bunny1.Bunny1Commands):

    def lol(self, arg):
        """a random lolcat"""
        return "http://icanhascheezburger.com/?random"

    def hoo(self, arg):
        """a hoogle (haskell + google) search"""
        return "http://haskell.org/hoogle/?q=%s" % q(arg)

    def rickroll(self, arg):
        """You Just Got Rick Roll'd By bunny1!"""
        return "http://tinyurl.com/djddqw"

    def _meta(self, arg):
        """an example of the convention of prefixing meta commands with an underscore"""
        raise Content("if you make a meta command, the convention is to use an underscore at the beginning of the name.")

    def fb(self, arg):
        """search www.facebook.com or go there"""
        if arg:
            return "http://www.facebook.com/s.php?q=%s&init=q" % qp(arg)
        else:
            return "http://www.facebook.com/"

    def fbapp(self, arg):
        """go to a particular Facebook app's default canvas page"""
        return "http://apps.facebook.com/%s" % arg

    # an example involving slightly more complciated logic
    def fbappabout(self, arg):
        """go to the about page for an app given a canvas name, app id, or api key"""
        if is_int(arg):
            return "http://www.facebook.com/apps/application.php?id=%s" % qp(arg)
        else:
            try:
                # check to see if this is a valid API key
                if len(arg) == 32:
                    int(arg, 16)
                    return "http://www.facebook.com/apps/application.php?api_key=%s" % qp(arg)
            except ValueError:
                pass
            return "http://www.facebook.com/app_about.php?app_name=%s" % qp(arg)

    def fbdevforum(self, arg):
        """goes to the developers discussion forum.  still need to add search to this :/"""
        return "http://forum.developers.facebook.com/"

    def jmirc(self, arg):
        """goes to dreiss' version of jmIrc"""
        return "http://www.cdc03.com/jmIrc.jar"

    def fblucky(self, arg):
        """facebook i'm feeling lucky search, i.e. go directly to a person's profile"""
        return "http://www.facebook.com/s.php?jtf&q=" + q(arg)
    fbs = fblucky

    def yt(self, arg):
        """Searches YouTube or goes to it"""
        if arg:
            return "http://www.youtube.com/results?search_query=%s&search_type=&aq=-1&oq=" % qp(arg)
        else:
            return "http://www.youtube.com/"

    def yts(self, arg):
        """goes to your YouTube subscription center"""
        return "http://www.youtube.com/subscription_center"

    def ytd(self, arg):
        """Searches YouTube by date added instead of by relevance, or goes to youtube.com"""
        if arg:
            return "http://www.youtube.com/results?search_query=%s&search_sort=video_date_uploaded" % qp(arg)
        else:
            return "http://www.youtube.com/"

    def bugcongress(self, arg):
        """looks up your senator or congressperson based on a zip code you give it"""
        # similar to the ubiquity command found here:
        # http://people.mozilla.com/~jdicarlo/ubiquity-tutorial-1.mov
        if arg:
            return "http://www.congress.org/congressorg/officials/congress/?lvl=C&azip=%s" % arg
        else:
            return "http://www.congress.org/congressorg/officials/congress/"

    def wikinvest(self, arg):
        """Searches Wikinvest or goes there"""
        if arg:
            return "http://www.wikinvest.com/Special/Search?search=%s" % qp(arg)
        else:
            return "http://www.wikinvest.com/"
    # make wi and wv be aliasses for wikinvest
    wi = wikinvest
    wv = wikinvest

    # unlisted makes it so this command won't show up when listing all
    # commands, but the command can still be used
    @bunny1.unlisted
    def _finger(self, arg):
        """run finger on the host that this is running on"""
        p = subprocess.Popen(["finger", arg], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return PRE("<span style='color: red;'>" + escape(p.stderr.read()) + "</span><hr />" + escape(p.stdout.read()))

    # this is dangerous to expose if you are running a public instance
    # of bunny1, but it might be useful if you are running bunny1 on localhost
    # behind a firewall
    # uncomment "dont_expose" if you want to use it (but only if you are
    # confident that you know what you are doing)
    @dont_expose
    def eval(self, arg):
        try:
            return PRE(eval(arg))
        except Content:
            raise
        except Exception, e:
            return PRE("<span style='color: red;'>" + escape(str(e)) + "</span>")

    def time(self, arg):
        """shows the current time in US time zones"""
        return "http://tycho.usno.navy.mil/cgi-bin/timer.pl"

    def ya(self, arg):
        """searches Yahoo! Answers for an answer to your question"""
        if arg:
            return "http://answers.yahoo.com/search/search_result?p=%s" % qp(arg)
        else:
            return "http://answers.yahoo.com/"

    def tlpd(self, arg):
        """goes to the spoilerless gamelist in the teamliquid programing database"""
        return "http://www.teamliquid.net/tlpd/games/nospoiler"

    def fbpbz(self, arg):
        """goes to Facebook Platform Bugzilla bugs"""
        if arg:
            return "http://bugs.developers.facebook.com/buglist.cgi?quicksearch=%s" % qp(arg)
        else:
            # if no arg, go to the main page of bugzilla
            return "http://bugs.developers.facebook.com/"

    def _author(self, arg):
        """goes to the author of bunny1's homepage"""
        return "http://www.ccheever.com/"""

    # an example of a redirect that goes to a non-HTTP URL
    # also, an example of a command that requires an argument
    def aim(self, arg):
        """use AOL Instant Messenger to IM a given screenname"""
        return "aim:goim?screenname=%s" % qp(arg)

    # an example of showing content instead of redirecting and also
    # using content from the filesystem
    def readme(self, arg):
        """shows the contents of the README file for this software"""
        raise bunny1.PRE(bunny1.bunny1_file("README"))

    @dont_expose
    def _help_html(self, examples=None, name="bunny1"):
        """the help page that gets shown if no command or 'help' is entered"""

        import random

        def bookmarklet(name):
            return """<a href="javascript:bunny1_url='""" + self._base_url() + """?';cmd=prompt('bunny1.  type &quot;help&quot; to get help or &quot;list&quot; to see commands you can use.',window.location);if(cmd){window.location=bunny1_url+escape(cmd);}else{void(0);}">""" + name + """</a>"""

        if not examples:
            examples = [
                    "g phpsh",
                    "fbpbz 1737",
                    "wikinvest 2008 Financial Crisis",
                    "popular",
                    "ya what is the meaning of life?",
                    "list Facebook",
                    "fbs john",
                    "php array_merge",
                    "wp FBML",
                    "fb mark zuckerberg",
                    "gmaps 285 Hamilton Ave, Palo Alto, CA 94301",
                    "gimg bisu",
                    "rickroll",
                    "yt i'm cool sushi654 yeah",
                    "y osteria palo alto",
                    "live james harrison",
                    ]

        return """
<html>
<head>
<title>bunny1</title>
""" + self._opensearch_link() + """
<style>
BODY {
    font-family: Sans-serif;
    width: 800px;
}

code {
    color: darkgreen;
}

A {
    color: #3B5998;
}

H1 {
    width: 800px;
    background: #3B5998;
    color: white;
    padding-left: 10px;
    padding-right: 10px;
    padding-bottom: 3px;
    padding-top: 23px;
    font-weight: bold;
    vertical-align: bottom;
}

small {
    width: 800px;
    text-align: center;
}

.bunny1-logo {
    height: 32px;
    vertical-align: bottom;
    margin-right: 8px;
}

.facebook-logo {
    position: absolute;
    top: 20px;
    left: 660px;
}

.test-query-input {
    width: 400px;
}

</style>
</head>
<body>
<h1><img class="bunny1-logo" src="blobbunny.gif">""" + name + """<img class="facebook-logo" src="http://www.facebook.com/images/facebook.gif" /></h1>

<p>""" + name + """ is a tool that lets you write smart bookmarks in python and then share them across all your browsers and with a group of people or the whole world.  It was developed at <a href="http://www.facebook.com/">Facebook</a> and is widely used there.</p>

<form method="GET">
<p>Type something like """ + " or ".join(["""<a href="#" onclick="return false;"><code onclick="document.getElementById('b1cmd').value = this.innerHTML; return true;">""" + x + "</code></a>" for x in examples]) + """.</p>
<input class="test-query-input" id="b1cmd" type="text" name="___" value=""" + '"' + escape(random.choice(examples)) + '"' + """/><input type="submit" value=" try me "/>
</p>
<p>
<p>Or you can see <a href="?list">a list of shortcuts you can use</a> with this example server.</p>

<h3>Installing on Firefox</h3>
<ul>Type <code>about:config</code> into your location bar in Mozilla.</ul>
<ul>Set the value of keyword.URL to be <code>""" + self._base_url() + """?</code></ul>
<ul>Make sure you include the <code>http://</code> at the beginning and the <code>?</code> at the end.</ul>
<ul>Now, type <code>list</code> or <code>_source</code> into your location bar and hit enter.</ul>
<ul>Also, if you are a Firefox user and find bunny1 useful, you should check out <a href="http://labs.mozilla.com/projects/ubiquity/">Ubiquity</a>.</ul>

<h3>Installing on Safari</h3>
<ul>Drag this bookmarklet [""" + bookmarklet(name) + """] to your bookmarks bar.</ul>
<ul>Now, visit the bookmarklet, and in the box that pops up, type <code>list</code> or <code>_source</code> and hit enter.</ul>
<ul>In Safari, one thing you can do is make the bookmarklet the leftmost bookmark in your bookmarks bar, and then use <code>Command-1</code> to get to it.</ul>
<ul>Alternatively, you can get the location bar behavior of Firefox in Safari 3 by using the <a href="http://purefiction.net/keywurl/">keywurl</a> extension.</ul>

<h3>Installing on Google Chrome</h3>
<ul>Choose <code>Options</code> from the wrench menu to the right of the location bar in Chrome, then under the section <code>Default Search</code>, click the <code>Manage</code> button.  Click the <code>Add</code> button and then fill in the fields name, keyword, and URL with <code>""" + name + """</code>, <code>b1</code>, and <code>""" + self._base_url() + """?</code>.  Hit <code>OK</code> and then select """ + name + """ from the list of search engines and hit the <code>Make Default</code> button to make """ + name + """ your default search engine.</ul>

<h3>Installing on Internet Explorer</h3>
<ul>There aren't any great solutions for installing """ + name + """ on IE, but two OK solutions are:</ul>
<ul>You can use this bookmarklet [""" + bookmarklet(name) + """] by dragging into your bookmarks bar and then clicking on it when you want to use """ + name + """.</ul>
<ul>Or, in IE7+, you can click the down arrow on the search bar to the right of your location bar and choose the starred """ + name + """ option there.  This will install the bunny OpenSearch plugin in your search bar.</ul>

<hr />
<small>bunny1 was originally written by <a href="http://www.facebook.com/people/Charlie-Cheever/1160">Charlie Cheever</a> and is maintained by him, <a href="http://www.facebook.com/people/David-Reiss/626221207">David Reiss</a>, Eugene Letuchy, and <a href="http://www.facebook.com/people/Daniel-Corson/708561">Dan Corson</a>.</small>


</body>
</html>
        """

    # fallback is special method that is called if a command isn't found
    # by default, bunny1 falls back to yubnub.org which has a pretty good
    # database of commands that you would want to use, but you can configure
    # it to point anywhere you'd like.  ex. you could run a personal instance
    # of bunny1 that falls back to a company-wide instance of bunny1 which
    # falls back to yubnub or some other global redirector.  yubnub similarly
    # falls back to doing a google search, which is often what a user wants.

    @dont_expose
    def fallback(self, raw, *a, **k):

        # this code makes it so that if you put a command in angle brackets
        # (so it looks like an HTML tag), then the command will get executed.
        # doing something like this is useful when there is a server on your 
        # LAN with the same name as a command that you want to use without 
        # any arguments.  ex. at facebook, there is an 'svn' command and
        # the svn(.facebook.com) server, so if you type 'svn' into the 
        # location bar of a browser, it goes to the server first even though
        # that's not usually what you want.  this provides a workaround for 
        # that problem.
        if raw.startswith("<") and raw.endswith(">"):
            return self._b1.do_command(raw[1:-1])

        # meta-fallback
        return bunny1.Bunny1Commands.fallback(self, raw, *a, **k)


def rewrite_tld(url, new_tld):
    """changes the last thing after the dot in the netloc in a URL"""
    (scheme, netloc, path, query, fragment) = urlparse.urlsplit(url)
    domain = netloc.split(".")

    # this is just an example so we naievely assume the TLD doesn't
    # include any dots (so this breaks if you try to rewrite .co.jp
    # URLs for example)...
    domain[-1] = new_tld
    new_domain = ".".join(domain)
    return urlparse.urlunsplit((scheme, new_domain, path, query, fragment))

def tld_rewriter(new_tld):
    """returns a function that rewrites the TLD of a URL to be new_tld"""
    return expose(lambda url: rewrite_tld(url, new_tld))


class ExampleDecorators(bunny1.Bunny1Decorators):
    """decorators that show switching between TLDs"""

    # we don't really need to hardcode these since they should get handled
    # by the default case below, but we'll include them just as examples.
    com = tld_rewriter("com")
    net = tld_rewriter("net")
    org = tld_rewriter("org")
    edu = tld_rewriter("edu")

    # make it so that you can do @co.uk -- the default decorator rewrites the TLD
    def __getattr__(self, attr):
        return tld_rewriter(attr)

    @expose
    def archive(self, url):
        """shows a list of older versions of the page using the wayback machine at archive.org"""
        return "http://web.archive.org/web/*/%s" % url

    @expose
    def identity(self, url):
        """a no-op decorator"""
        return url

    @expose
    def tinyurl(self, url):
        """creates a tinyurl of the URL"""
        # we need to leave url raw here since tinyurl will actually
        # break if we send it a quoted url
        return "http://tinyurl.com/create.php?url=%s" % url

class ExampleBunny(bunny1.Bunny1):
    """An example"""
    def __init__(self):
        bunny1.Bunny1.__init__(self, ExampleCommands(), ExampleDecorators())

if __name__ == "__main__":
    bunny1.main(ExampleBunny())


