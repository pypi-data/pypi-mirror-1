"""
Implementation of a ``mod_rewrite`` compatible URL rewriter.

This WSGI middleware implements an URL rewriter that uses the same
syntax as the famous ``mod_rewrite`` module for Apache. Most of
``mod_rewrite`` features are supported, including redirecting with
a specific status code, proxying, conditional rules based on
environment variables and chained rules.

"""

import re
import os.path
from datetime import datetime, timedelta
import urllib
import urlparse

from paste import httpexceptions
from paste.proxy import Proxy


__author__ = "Roberto De Almeida <roberto@dealmeida.net>"
__license__ = "MIT"
__version__ = (0,1,0)


def make_filter(app, global_conf, rulesets=None, config=None):
    """
    Entry point for Paste Deploy.

    To create a WSGI filter middleware add the following line to
    the deployment file::

        [pipeline:main]
        pipeline = wsgirewrite myapp

        [filter:wsgirewrite]
        use = egg:WSGIRewrite
        config = /path/to/htaccess

        [app:myapp]
        ...

    Where ``config`` specifies a file with the rewriting rules
    following ``mod_rewrite``'s syntax::

        RewriteCond  %{HTTP_USER_AGENT}  ^Mozilla.*
        RewriteRule  ^/$                 /homepage.max.html  [L]

        RewriteCond  %{HTTP_USER_AGENT}  ^Lynx.*
        RewriteRule  ^/$                 /homepage.min.html  [L]

        RewriteRule  ^/$                 /homepage.std.html  [L]

    Optionally, you can also specify rules directly on the INI file
    using the ``rulesets`` variable::

        [filter:wsgirewrite]
        use = egg:WSGIRewrite
        rulesets = feed blocked

        [wsgirewrite:feed]
        # redirect /atom.xml to real feed location
        rule1 = ^/atom.xml$ /index.php?format=Atom1.0

        [wsgirewrite:blocked]
        # block host1.example.com and host2.example.com
        # this could be done by matching ``host(1|2)``; I'm
        # using these rules just to demonstrate the ``OR``
        # flag functionality.
        cond1 = %{REMOTE_HOST} ^host1\.example\.com$ [OR]
        cond2 = %{REMOTE_HOST} ^host2\.example\.com$
        # no redirection (-), Forbidden
        rule1 = ^.*$ - F

    In case both ``config`` and ``rulesets`` are specified, the
    latter are evaluated first.

    """
    rs = []

    # Parse rules from deployment file.
    if rulesets is not None:
        rs.extend(parse_ini(global_conf['__file__'], rulesets))

    # Parse config file.
    if config is not None and os.path.exists(config):
        rs.extend(parse_htaccess(config))

    return RewriteMiddleware(app, rs)


def parse_ini(path, names):
    """
    Parse the deployment file.

    This function parses the deployment file, searching for sections
    that specify rulesets; these sections should have the name
    ``wsgirewrite:``, followed by the name of the ruleset. Eg::

        [wsgirewrite:blocked]
        cond1 = %{REMOTE_HOST} !^.*example.com$
        rule1 = ^.*$ - F

    The ruleset aboved is called "blocked", and will be applied if
    it is in the parameter ``names``. Condition and rules are sorted
    by their names, which should start with ``cond`` and ``rule``,
    respectively.

    """
    from ConfigParser import ConfigParser

    # Read the deployment file.
    config = ConfigParser()
    config.read(path)
    names = names.split()

    # Get relevant sections.
    sections = [section for section in config.sections() if
            section.startswith('wsgirewrite:') and
            section.split(':')[1] in names]

    rulesets = []
    for section in sections:
        conditions = []
        directives = []

        # Parse config.
        conds = [option for option in config.options(section)
                if option.startswith('cond')]
        conds.sort()
        rules = [option for option in config.options(section)
                if option.startswith('rule')]
        rules.sort()
        for cond in conds:
            line = config.get(section, cond)
            conditions.append(parse_line(line))
        for rule in rules:
            line = config.get(section, rule)
            directives.append(parse_line(line))

        rulesets.append((conditions, directives))
    return rulesets


def parse_htaccess(path):
    """
    Parse configuration from a ``.htaccess`` like file.

    This function parses the configuration from a file specifying
    the rulesets using ``mod_rewrite``'s syntax.

    """
    config = open(path)
    rulesets = []
    conds = []
    directives = []
    state = 0  # 1 is reading conds, 2 is reading directives
    for line in config:
        line = line.strip()
        if line.startswith('RewriteCond') or not line:
            if state == 2:
                rulesets.append((conds, directives))
                conds = []
                directives = []
            state = 1
            if line:
                # Remove ``RewriteCond`` from the line.
                line = line[11:]
                conds.append(parse_line(line))
        elif line.startswith('RewriteRule'):
            state = 2
            # Remove ``RewriteRule`` from the line.
            line = line[11:]
            directives.append(parse_line(line))
    rulesets.append((conds, directives))
    return rulesets


def parse_line(line):
    """
    Parse a configuration line into tokens.

    This function converts a line to the necessary tokens::

        >>> parse_line("^/$  /homepage.max.html  [L]")
        ('^/$', '/homepage.max.html', ['L'])
        >>> parse_line("^/$  /homepage.max.html")
        ('^/$', '/homepage.max.html', [])

    """
    tokens = re.split('\s+', line.strip())
    if len(tokens) < 2: raise Exception("Bogus line: %s" % line)
    if len(tokens) == 2:
        tokens.append([])
    else:
        tokens[2] = tokens[2][1:-1].split(',')
    return tuple(tokens)


class RewriteMiddleware(object):
    """
    WSGI middleware for rewriting URLs.

    This middleware rewrites URLs according to Apache's ``mod_rewrite``
    syntax. To redirect the user from page ``/page.html`` to
    ``new_page.html`` just give it the following ruleset::

        >>> app = RewriteMiddleware(some_app, [
        ...     ([], # conditions (none, in this case)
        ...      [   # rules
        ...          ("^/page.html$", "/new_page.html", []),
        ...      ]
        ...     )
        ... ])

    """

    def __init__(self, app, rulesets):
        """
        Create the middleware.

        To instantiate the middleware, pass a WSGI app ``app`` to
        be filtered, and a group of rulesets. The parameter
        ``rulesets`` should be a list of tuples, each tuple consisting
        of a list of conditions and a list of directives (rewrites)
        to be applied.

        """
        self.app = app
        self.rulesets = rulesets

    def __call__(self, environ, start_response):
        """
        Process the request.

        The middleware follows the algorithm used by ``mod_rewrite``,
        where first the path is checked and, in case of a match,
        the conditions are checked to see if the replacement should
        be done.

        This method will return either the original app with
        ``PATH_INFO`` modified (and possibly ``QUERY_STRING``), a
        Proxy object proxying a request to another location, or an
        ``httpexception`` middleware for redirects or Forbidden/Gone
        pages.

        """
        # Update the environ with additional variables.
        environ = update_environ(environ)

        # Modified start_response with additional headers for
        # setting cookies and overriding the content-type.
        additional_headers = []

        def new_start_response(status, headers, exc_info=None):
            """Modified start response with additional headers."""
            headers = headers + additional_headers
            start_response(status, headers, exc_info)

        # Process each ruleset.
        for conds, directives in self.rulesets:

            # Apply replacements.
            cskip = False
            nskip = 0
            for pattern, repl, flags in directives:
                path_info = environ['PATH_INFO']
                # Skip rules. This can be used to make pseudo if-then-else
                # constructs.
                if nskip > 0:
                    nskip -= 1
                    continue

                # Skip chained rules if a previous rule has failed;
                # in this case, skip will be True. If this is the last
                # chained rule (no "C" flag) we unset the skip boolean.
                if cskip:
                    if "C" not in flags and "chain" not in flags:
                        cskip = False
                    continue

                # Skip internal requests. We detect internal requests
                # that were made using the ``paste.recursive``
                # middleware. We also set the ``IS_SUBREQ`` flag in
                # the environ, since mod_rewrite allows it.
                internal = path_info in environ.get(
                        'paste.recursive.old_path_info', [])
                environ['IS_SUBREQ'] = ["false", "true"][internal]
                if (internal and
                        "nosubreq" in flags or
                        "NS" in flags):
                    break

                # Check for an inverted match.
                if pattern.startswith('!'):
                    pattern = pattern[1:]
                    invert = True
                else:
                    invert = False

                # Compile the pattern to match the path and check
                # if it matches.
                if "NC" in flags or "nocase" in flags:
                    pattern = re.compile(pattern, re.IGNORECASE)
                else:
                    pattern = re.compile(pattern)
                match = pattern.search(path_info)
                if invert: match = not match

                if match:
                    # Check conditions. We need to check the path
                    # before the conditions because mod_rewrite
                    # allows the conditions to use back references
                    # based on the matched path, and that's why here
                    # we pass ``match.groups()`` to the function
                    # that will do the checking.
                    path_pattern = (hasattr(match, "groups")
                            and match.groups() or ())
                    cond_pattern = self.check(conds, environ, path_pattern)
                    if cond_pattern is False: continue  # skip this rule

                    # Set cookies.
                    cookies = [flag for flag in flags if
                            flag.startswith('CO') or
                            flag.startswith('cookie')]
                    for cookie in cookies:
                        additional_headers.append(cookie_header(cookie))

                    # Add variables to environment. Should we let
                    # the environment to be overriden?
                    envs = [flag for flag in flags if
                            flag.startswith('E') or
                            flag.startswith('env')]
                    for env in envs:
                        m = re.match("(?:E|env)=(.*)", env)
                        k, v = m.group(1).split(':', 1)
                        # Expand backreferences from the RewriteRule ($N)
                        # and from the CondRule (%N).
                        v = re.sub(r"(?<!\\)\$(\d)",
                                lambda m: path_pattern[int(m.group(1)) - 1],
                                v)
                        v = v.replace(r'\$', '$')
                        v = re.sub(r"(?<!\\)%(\d)",
                                lambda m: cond_pattern[int(m.group(1)) - 1],
                                v)
                        v = v.replace(r'\%', '%')
                        environ.setdefault(k, v)

                    # Force the MIME type of the target.
                    mimes = [flag for flag in flags if
                            flag.startswith('T') or
                            flag.startswith('type')]
                    if mimes:
                        mime = re.match("(?:T|type)=(.*)",
                                mimes[-1]).group(1)
                        h = ("Content-type", mime)
                        additional_headers.append(h)

                    # Handle flags "G" and "F". These are easy, we just
                    # block the access.
                    if "F" in flags or "forbidden" in flags:
                        e = httpexceptions.HTTPForbidden()
                        return e.wsgi_application(environ, new_start_response)
                    if "G" in flags or "gone" in flags:
                        e = httpexceptions.HTTPGone()
                        return e.wsgi_application(environ, new_start_response)

                    # Replace path_info with the new value, expading back
                    new_path_info = pattern.sub(repl, path_info)
                    new_path_info = re.sub(r"(?<!\\)\$(\d)",
                            lambda m: path_pattern[int(m.group(1)) - 1],
                            new_path_info)
                    # Apply any back references from the cond pattern.
                    new_path_info = re.sub(r"(?<!\\)%(\d)",
                            lambda m: cond_pattern[int(m.group(1)) - 1],
                            new_path_info)
                    new_path_info = new_path_info.replace(r'\%', '%')

                    # Should we escape new path?
                    if "noescape" in flags or "NE" in flags:
                        new_path_info = urllib.unquote(new_path_info)

                    # Move query string parameters from new PATH_INFO
                    # to QUERY_STRING.
                    old_qs = environ.get('QUERY_STRING', "")
                    new_qs = urlparse.urlsplit(new_path_info)[3]
                    new_path_info = new_path_info.split('?', 1)[0]
                    if "QSA" in flags or "qsappend" in flags:
                        # Pass QUERY_STRING from the original path to the
                        # new one.
                        if old_qs: new_qs = old_qs + '&' + new_qs
                    environ['QUERY_STRING'] = new_qs

                    # The "P" flag is final and makes a proxied request. This
                    # can be easily handled by Paste's proxy class.
                    if "P" in flags or "proxy" in flags:
                        proxy = Proxy(new_path_info)
                        return proxy(environ, new_start_response)

                    # The "R" flags calls a redirect, which we make using the
                    # httpexception module from Paste.
                    redir = [flag for flag in flags if
                            flag.startswith('R') or
                            flag.startswith('redirect')]
                    if redir:
                        status = re.match("(?:R|redirect)(?:=(\d+))?",
                                redir[-1]).group(1) or '302'
                        exception = status_code_to_exception(status)
                        e = exception(new_path_info)
                        return e.wsgi_application(environ, new_start_response)

                    # Replace PATH_INFO for current app.
                    if repl != '-': environ['PATH_INFO'] = new_path_info

                    # Re-run the whold process.
                    if "N" in flags: return self(environ, new_start_response)

                    # Skip next rules?
                    skip = [flag for flag in flags if
                            flag.startswith('S') or
                            flag.startswith('skip')]
                    if skip:
                        nskip = int(re.match("(?:S|skip)=(\d+)",
                                skip[-1]).group(1))

                    # Last rule? Break.
                    if "L" in flags: break

                # Rule fails and is chained. In this case we set the
                # skip flag, making rules to be skipped until a non-
                # chained rule appears.
                elif ("C" in flags or "chain" in flags):
                    cskip = True

        return self.app(environ, new_start_response)

    def check(self, conds, environ, path_pattern):
        """
        Check if conditions apply.

        This method checks the conditions in the rulesets to see
        if the replacement should be performed. The conditions take
        the form::

            TestString CondPattern [optional-flags]

        And usually expand variables from the environment for the
        checks. Not all forms of expansion from ``mod_rewrite`` are
        supported, though.

        """
        out = True
        skip = False
        for string, pattern, flags in conds:
            # Skip rule if we found an "OR" group of
            # rules and one of them matched.
            if skip:
                # If this is the last rule in the "OR"
                # group, stop skipping rules.
                if "OR" not in flags:
                    skip = False
                continue

            # Replace variables in the string using
            # the environment.
            string = re.sub(r"(?<!\\)%{(.*?)}",
                    lambda m: environ.get(m.group(1), ""),
                    string)
            string = string.replace(r'\%', '%')
            # Replacements from path match.
            string = re.sub(r"(?<!\\)\$(\d)",
                    lambda m: path_pattern[int(m.group(1)) - 1],
                    string)
            string = string.replace(r'\$', '$')

            # Check for inverted match.
            if pattern.startswith('!'):
                pattern = pattern[1:]
                invert = True
            else:
                invert = False

            # Do the test. In addition to regexp search, we also
            # allow for lexicographical comparisons.
            if pattern.startswith(">"):
                m = string > m[1:]
            elif pattern.startswith("<"):
                m = string < m[1:]
            elif pattern.startswith("="):
                m = string == m[1:]
            elif "NC" in flags:
                m = re.search(pattern, string, re.IGNORECASE)
            else:
                m = re.search(pattern, string)
            if invert: m = not m

            # If any condition fails we return false.
            if not m:
                if "OR" not in flags:
                    return False
                else:
                    out = False
            elif m:
                out = hasattr(m, "groups") and m.groups() or ()
                if "OR" in flags:
                    skip = True

        # Return the last captured group.
        return out


def update_environ(environ):
    """
    Update environ with ``mod_rewrite`` specific values.

    """
    environ.setdefault('PATH_INFO', "/")

    now = datetime.now()
    environ['TIME_YEAR'] = now.year
    environ['TIME_MON'] = now.month
    environ['TIME_DAY'] = now.day
    environ['TIME_HOUR'] = now.hour
    environ['TIME_MIN'] = now.minute
    environ['TIME_SEC'] = now.second
    environ['TIME_WDAY'] = now.weekday()
    environ['TIME'] = now.strftime("%Y%m%d%H%M%S")
    environ['API_VERSION'] = '.'.join(str(_) for _ in __version__)
    environ['THE_REQUEST'] = "%s %s%s %s" % (
            environ['REQUEST_METHOD'],
            environ.get('SCRIPT_PATH', ''),
            environ['PATH_INFO'],
            environ['SERVER_PROTOCOL'])
    environ['REQUEST_URI'] = "%s%s" % (
            environ.get('SCRIPT_PATH', ''),
            environ['PATH_INFO'])
    environ['REQUEST_FILENAME'] = environ['SCRIPT_FILENAME'] = 'Not supported'
    environ['HTTPS'] = ["off", "on"][environ['wsgi.url_scheme'] == 'https']
    return environ


def status_code_to_exception(status):
    """
    Retrieve an ``httpexceptions`` app from a given status code.

    """
    exception = {"300": httpexceptions.HTTPMultipleChoices,
                 "301": httpexceptions.HTTPMovedPermanently,
                 "permanent": httpexceptions.HTTPMovedPermanently,
                 "302": httpexceptions.HTTPFound,
                 "temp": httpexceptions.HTTPFound,
                 "303": httpexceptions.HTTPSeeOther,
                 "seeother": httpexceptions.HTTPSeeOther,
                 "304": httpexceptions.HTTPNotModified,
                 "305": httpexceptions.HTTPUseProxy,
                 "307": httpexceptions.HTTPTemporaryRedirect}[status]
    return exception


def cookie_header(cookie):
    """
    Build a cookie header from the ``CO|cookie`` flag.

    """
    m = re.match("(?:CO|cookie)=(.*)", cookie)

    # Cookie should be NAME:VAL:domain[:lifetime[:path]]
    c = m.group(1).split(':')
    if len(c) >= 4:
        expires = datetime.utcnow() + timedelta(minutes=int(c[3]))
        c[3] = expires.strftime("%a, %d-%b-%Y %H:%M:%S GMT")

    # Create Set-Cookie header.
    k = [c[0], "domain", "expires", "path"]
    v = c[1:]
    h = ("Set-Cookie", "; ".join("%s=%s" % pair for pair in zip(k, v)))
    return h
