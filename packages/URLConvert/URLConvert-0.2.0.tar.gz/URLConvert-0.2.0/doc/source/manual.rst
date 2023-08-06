# -*- coding: utf-8 -*-

URLConvert - A simple, modular URL conversion toolkit
+++++++++++++++++++++++++++++++++++++++++++++++++++++

.. contents::

Introduction
============

URLConvert does just one thing and aims to do it well; it converts a URL to a
dictionary of variables and converts a dictionary of variables back to a URL. 

It is designed as a replacement for Routes which aims to:

* be more predictable
* be really simple for all common cases (and even some of the less common ones)
* handle multiple different encodings
* allow variables in any part of the URL
* be modular and extensible for different needs

URLConvert is built on the belief that as your requirements become more complex
the law of diminishing returns kicks in and it becomes more effort to learn how
a framework deals with your particular case than to hand code the solution.
URLConvert therefore also aims to:

* provide APIs designed in such a way that existing configuration will work
  nicely alongside a hard coded solution

URLConvert is targetted specifically at web applications where the paradigm of
treating a URL as nothing more that a dictionary of variables proves very
useful in three areas in particular:

* dispatching requests to specific parts of the application based on the URL
* generating URLs which point to various parts of your application
* storing application state via the URL, removing the need for custom query 
  strings or hidden form variables to maintian state

Unlike other URL parsing systems, URLConvert can extract variables from any
part of a URL including the host, port, scheme and path info. You can also
extract variables from the query string and even from the script name part of a
URL (although as you'll see this isn't recommended since the conversions are
designed to be agnostic of the way the application is deployed).

Because URLConvert is highly modular though it is easy to create your own
converters which have different characteristics from the defaults.

FAQ
---

* How secure are regexs for the URL matching? Actually nothing from the web goes into the regex so we are fine.
* What's the point of the query string code? The script code?

ToDo
----

* Generating domains doesn't work yet
* Change 
* Writing your own rules, caching custom rules, even when getting things from the state

Overview
========

URLConvert is a simple toolkit for converting a URL to a dictionary of
variables and converting a dictionary of variables back to a URL. Converting a
URL to a dictionary of variables is called *matching* in URLConvert
terminology. Converting a dictionary of variables back to a URL is called
*generating*.

Before we go into the detail of how URLConvert works, we'll take a look at how
the these processes work.

Understanding the Matching Process
----------------------------------

When a human wants to work out which variables a particular URL represents they
will compare the current URL to a list of possible patterns they know their
application uses. Consider this URL::

    https://www.example.com/account/signin

A human would instantly recognise the subdomain as ``www``, the domain name as
``example.com`` and that ``account`` and ``signin`` were key variables in the
path info component. If it was imortant in the application the human would also
be able to recognise that this is a secure URL and that the port is implied to
mean port 443 (the port an HTTPS connection uses by default).

In performing this analysis a human would apply different criteria to different
parts of the URL. They know that a domain name contains two names separated by
a ``.`` character and that any other ``.`` characters between the two ``/``
characters represent sub-domain components. On the other hand, when a human
looks at the path info component they know that the key variables are separated
by a ``/`` character.

A web application to serve this URL might need to know all of the information
identified in the first paragraph or it might only need to know the subdomain
and the two key variables in the path info component. URLConvert allows you to
express this with a string which looks like this::

    {*}://{subdomain}.{}.com:{*}/{*}|{controller}/{action}

This syntax allows URLConvert to analse the URL in the same way a human would,
ignoring the domain name, scheme (``http`` or ``https``) and port. It would
then create variables for each of the names you do want to match and it would
assign the text in the URL at the position of that variable to the variable
name so that you would end up with a dictionary looking like this::

    {
        'subdomain': u'www',
        'controller': u'account',
        'action': u'signin',
    }

The variable names ``controller`` and ``action`` don't mean anything special
to URLConvert, you could choose other names if you preferred, but it is a
convention from Ruby on Rails which means that the application controller and
action used to handle the URL will be based on the contents of the
``controller`` and ``action`` variables.

By setting up a series of different rules you can create a ruleset that allows
you to correctly match any URL your application uses.

Although rules represent the easiest way of expressing the vast majority of URL
structures you can also write your own matching and generating converters
directly if you prefer or if you have particularly complex rules.

Rules are always expressed as Unicode strings. This rule tells URLConvert that
the scheme, host, port, script_name and query_string can be ignored but that in
order for the rule to apply the ``path_info`` component should contain exactly
one ``/`` character with characters both before and after it and that the
characters before the ``/`` should be used to set the ``controller`` variable
and the characters afterwards should be used to set the ``action`` variable.

Usually a set of rules are used together as a *ruleset*, notice that the domain
names are different in the two rules:

.. sourcecode :: pycon

    >>> from urlconvert import RuleSet, rule
    >>> from conversionkit.exception import ConversionError
    >>>
    >>> ruleset = RuleSet([
    ...     rule(u'http://example.com:80/{hi}'),
    ...     rule(u'http://example.net:80/{hi}'),
    ... ])

Let's try to match some different URLs against these rules:

.. sourcecode :: pycon

    >>> for url in [
    ...     u'http://example.com/name/2?a=a',
    ...     u'https://example.net/name/2?',
    ...     u'http://example.net/name?a=a',
    ... ]:  
    ...     match = ruleset.match_url(url)
    ...     if match.successful:
    ...         print "Success: %r" % match.result
    ...     else:
    ...         print "Failed: %s" % match.error
    Failed: No rule matched
    Failed: No rule matched
    Success: {u'hi': u'name'}

As you can see, only the third rule matched. The ``match`` object is just a
ConversionKit ``Conversion`` instance for the conversion which takes place for
each URL behind the scenes. This means you can easily inspect it to see why the
rules that failed weren't successful:

.. sourcecode :: pycon

    >>> match.children
    [<conversionkit.Conversion object at 0x...>, <conversionkit.Conversion object at 0x...>]
    >>> match.children[0].error
    'The host field is invalid'
    >>> match.children[0].children['host'].error
    "The host u'example.net' does not match u'example.com' expected by the rule"
    
Now you have an idea of the matching process, let's look at the generating
process.

Understanding the Generating Process
------------------------------------

Once you have an appropriate ruleset your application's URLs are effectively 
just dictionaries of variables. Wouldn't it be useful if you could use those
same variables to generate URLs as well as just match them?

Well you can. If a human had to convert the variables into a URL they'd look at
each rule in turn and see if all the variables were used in that rule.
URLConvert can do exactly the same thing so that when given a dictionary of
variables it can generate a URL which when matched will result in the same set
of variables. 

Suddenly the problems of URL management in your application disappear. Your
URLs are cleanly separated from your application code which means that to
restructure your URLs you simply need to re-write the rules, not the
application. 

Of course, there is a lot to learn to use URLConvert properly so let's get
cracking.

Here's an example using the same ruleset:

.. sourcecode :: pycon

    >>> from urlconvert import build_url
    >>> for vars in [
    ...     {u'hi': u'james'},
    ...     {u'bye': u'fred'},
    ... ]:
    ...     generation = ruleset.generate(vars)
    ...     if generation.successful:
    ...         print "Success: %r" % build_url(** generation.result)
    ...     else:
    ...         print "Failed: %s" % generation.error
    Success: u'http://example.com/james'
    Failed: No rule matched

Notice that the second attempt fails because there is no rule for handling a
variable ``bye``. Again, you can access the errors from the child conversion as
``generation.children``.

URLs, Servers, Proxies and the Environment
==========================================

Before we look at how URLConvert works it is worth spending some time
understanding how the request URL is actually determined is in the context of a
web application and what functionality of URLs is actually useful. 

First of all a URL is any string which matches the definition in `RFC 1738
<http://tools.ietf.org/html/rfc1738>`_. URLs can have the following components:

* ``scheme`` - URL scheme specifier
* ``netloc`` - Network location part (whether representing a host or IP address) including the port
* ``path`` - Hierarchical path
* ``params`` - Parameters for last path element
* ``query`` - Query component
* ``fragment`` 

These corresponds to the general structure of a URL:
``scheme://netloc/path;parameters?query#fragment`` and are the items you would
get if you used the Python ``urlparse`` module to split up a URL.

In reality the ``params`` portion of a URL are virtually never used and in fact
the term "params" usually refers to components of the ``query`` part so we will
ignore them. The ``fragment`` part is also of little use because it is never
submitted to the server, it is only used client side to mark particular anchors
in the HTML so ``params`` and ``fragment`` are totally ignored by URLConvert.

Another part which can usually be ignored is the ``query`` part. If you've
worked with tools which don't have a URL conversion tool you might have used
the query string to store information about the state of the appliction but
when you are using URLConvert you can convert the URL to a dictionary of
variables anyway so there is no need to use the query string. For form
submissions you should use the POST method which sends data as part of the HTTP
request rather than as part of the URL. Although URLConvert supports the query
string, you don't need it.

That leaves the just the following parts:

* ``scheme``
* ``netloc``
* ``path``

For the purposes of web development the port and the host are very important
so URLConvert treats them as separate parts of the URL instead of lumping them
together as the ``netloc``. Another problem web developers face is that
different server administrators might deploy the same application at different
paths. For example one might put it at ``/app`` and the other at
``/internal/app``. The convention for dealing with this is to treat the path in
two parts: a script name and path info. This means URLConvert actually deals
with these parts of a URL:

* ``scheme`` - the scheme (``http`` or ``https``)
* ``host`` - the host or IP address part of the URL
* ``port`` - the port on which the server is running
* ``script`` - the part of the path which depends on where the administrator deploys the app
* ``path`` - the part of the path after the script name
* ``query`` - the query string part of a URL after the ``?`` (not really needed)

Unfortunately the complication doesn't end there. Web developers don't actually
get access to the URL the user entered into their browser, instead the server
exposes certain key variables via the *enviornment* and it is up to the
developer (or a web framework or library) to piece together the parts.

Here are the main keys in the ``environ`` dictionary which are relevant to
URLs. These variables can be used to work out what the URL the user entered
actually was:

``wsgi.url_scheme``
    Whether the browser is using HTTP or HTTPS to contact the server

``SERVER_NAME``
    The full host and domain name or IP address on which the server believes 
    it is running

``SERVER_PORT``
    The port on which the server believes it is running

``SCRIPT_NAME``
    The part of the URL which is dependant on how the app is deployed. It
    occurs after the domain name and before the ``PATH_INFO``.

``PATH_INFO``
    The part of the URL after the ``SCRIPT_NAME``

``QUERY_STRING``
    The part of a URL after the ``?``

From these variables you might think it possible to piece together the URL the
user entered but things are a little more tricky than that. For a start there
might be many different domain names which resolve to the same server; just
because the server things it is running at ``example.com`` doesn't mean the URL
the user entered was ``example.com``. Web browsers set the host the user enterd
as the ``Host`` HTTP header which is added to the ``environ`` dictionary as the
``HTTP_HOST`` key:

``HTTP_HOST``
    The full host and domain name the web browser sent in its ``Host`` header
    to let the server know which host and domain it thought it was accessing. Note;
    you shouldn't necessarily trust this because a malicious user could send an
    incorrect HTTP header.

Another problem is that the person deploying the app might have set up a proxy
server between the browser and the application in which case ``HTTP_HOST`` will
be from the proxy, not the user and the port the server runs on might not be
the same as the port the proxy runs on. In such cases the proxy should be
configured to set some extra HTTP headers which can be accessed via these
variables:

``X_FORWARDED_FOR``
    A defacto standard for specifying the host and domain name of all the
    proxies through which the request passed before it reached the server as well
    as the original host.

``X_FORWARDED_PORT``
    Totally unoffical convention some software uses to specify the ports on
    each of the proxies through which the request passed before it reached the
    server. The reason this isn't used much in reality is that the original 
    port will almost always be 80 or 443 which you can tell from the scheme
    so you don't normally need the client to tell you it. 

As you can see, there are a lot of variables which affect the URL so rather
than making a guess and risking getting it wrong the URLConvert libraries
actually don't deal with URLs at all, they deal with ``scheme``, ``host``,
``port``, ``script``, ``path`` and ``query`` (collectively called the *URL
parts*) and leave you to specify which environment variable should be used for
each part. 

Of course if you want URLConvert to make a best guess it will. Here are some examples:

.. sourcecode :: pycon

    >>> from urlconvert import extract_scheme, extract_host, extract_port, extract_script, extract_path, extract_query

Let's set up a sample environment to demonstrate these functions

.. sourcecode :: pycon

    >>> environ = {
    ...     'wsgi.url_scheme': 'http',
    ...     'SERVER_NAME': 'example.com',
    ...     'SERVER_PORT': '80',
    ...     'PATH_INFO': '/admin/view',
    ...     'SCRIPT_NAME': '/run.py',
    ...     'QUERY_STRING': 'name=james',
    ... }

The URL helpers all work in the basis that you are using a ``flow`` object
(from the Flows framework, just a dictionary of services) so if you are not you
need to create one and attach the environment for the helpers to work
correctly:

.. sourcecode :: pycon

    >>> from bn import AttributeDict
    >>> flow = AttributeDict(wsgi=(AttributeDict(environ=environ)))

Now let's give them a go:

.. sourcecode :: pycon

    >>> scheme = extract_scheme(flow)
    >>> host = extract_host(flow)
    >>> port = extract_port(flow)
    >>> script = extract_script(flow)
    >>> path = extract_path(flow)
    >>> query = extract_query(flow)
    >>> scheme, host, port, script, path, query
    (u'http', u'example.com', u'80', u'run.py', u'admin/view', u'name=james')

Notice the script and path don't start with a ``/`` even though the variables
they are obtained from do. This is for three reasons:

* The WSGI spec requires that ``SCRIPT_NAME`` does not end in ``/`` which means that ``PATH_INFO`` always will. The only confusion is around the case where the root URL is served because the ``SCRIPT_NAME`` in that case is ``''`` which is the same as the script value you'd get if you were serving a URL of ``//``. Since URLConvert doesn't support script or path components with multiple ``/`` characters anyway this is not a problem.
* It is very easy to re-build URLS now becasue a ``/`` character can always be inserted between the script and the path
* It means that the variables make sense when they are written in rules because the ``/`` that appear in the rules don't end up in the variables after they are parsed.

There is also a helper for building a URL from all the *URL parts*"

.. sourcecode :: pycon

    >>> from urlconvert import build_url
    >>> build_url(scheme, host, port, script, path, query)
    u'http://example.com/run.py/admin/view?name=james'

If you just want to build the URL directly from the ``flow`` object in one step
you can use ``extract_url()`` like this. Note that by default,
``extract_url()`` ignores the port, script name and query string by default so
that the the URL is in the correct form to be parsed for use in URL matching.
You want the script name ignored so that your rules will work with any script
name and are independant of how an administrator deploys your application, you
don't usually match on the qurey string so this can be removed too and if the
scheme is http and the port is 80, or the scheme is https and the port is 443,
the port doesn't need to be displayed.

.. sourcecode :: pycon

    >>> from urlconvert import extract_url
    >>> extract_url(flow)
    u'http://example.com/admin/view'

See the API documentation for each of the extraction helpers to find out the
rules they follow.

Encoding and Decoding
---------------------

Another potential pitfall is that there are lots of different ways of writing
the same URL. For example these three URIs are technically equivalent (although
the last format is of very little use).

::

    http://abc.com:80/~smith/home.html
    http://ABC.com/%7Esmith/home.html
    /ABC.com:/%7esmith/home.html

It is important that your application only uses one URL for each page it is
serving so you only need to write rules once, not one for every type of string
which represents the same URL.

URLConvert has tools to convert URLs to a standard internal format which is as 
follows:

* Everything in Unicode
* The scheme and port present, even if they can be calculated from one another
* All script, path and query escapes fully decoded to Unicode characters

It is this format in which URLs are used by URLConvert, but how do you get URLs
to and from this format?

Well here's the process for matching:

#. Get all the URL parts from the environment
#. Decode each of the strings from the format they are stored in the 
   environment (probably UTF-8???) to a Unicode string
#. Run validators to ensure all the parts are valid
#. Decode escapes from all parts which might have them: the script, path and 
   query
#. Pass the parts to URLConvert for matching against the rules

Here's the process for generating:

#. Get the URL parts returned from URLConvert after it has generated
#. Encode them all to the output format eg UTF8 (Yes: this happens before
   the escaping!)
#. Encode the non-ascii characters using an escape sequence and return an
   ASCII string
#. Run the validators
#. Return the data to the template where it might get encoded to UTF-8 or 
   some other encoding to be rendered

There are quite a lot of steps there and lots of URLConversion tools skip over
the steps which is fine 99.9% of the time. 

Here are some sample encoders and decoders for the URL parts:

Let's import some objects we need from ConversionKit:

.. sourcecode :: pycon

    >>> from conversionkit import Conversion, chainConverters

Now here are some sample encoders and decoders for the URL parts. Each of the
decoders and matchers above can also take arguments to affect their behaviour
and to allow you to customise the way they work.

.. sourcecode :: pycon

    >>> from urlconvert import plainDecode, matchScheme, matchHost, matchPort, matchScript, matchPath, matchQuery, decodeScript, decodePath, decodeQuery, makeUnicode
    >>> decode_scheme = chainConverters(makeUnicode(), matchScheme(), plainDecode('utf8'))
    >>> decode_host = chainConverters(makeUnicode(), matchHost(), plainDecode('utf8'))
    >>> decode_port = chainConverters(makeUnicode(), matchPort(), plainDecode('utf8'))
    >>> decode_script = chainConverters(makeUnicode(), matchScript(), decodeScript('utf8'))
    >>> decode_path = chainConverters(makeUnicode(), matchPath(), decodePath('utf8'))
    >>> decode_query = chainConverters(makeUnicode(), matchQuery(), decodeQuery('utf8'))
  
Notice that the decoders for ``script``, ``path`` and ``query`` have an extra
converter to decode the escape sequences starting with a ``%``.

Here is an example:

.. sourcecode :: pycon

    >>> Conversion(u'%7Esmith').perform(decode_path).result
    u'~smith'

The definitions above are actually what the ``extract_*()`` functions use if
you don't specify the converter you want to use. You can import them like this:

.. sourcecode :: pycon

    >>> from urlconvert import decode_scheme, decode_host, decode_port, decode_script, decode_path, decode_query

The encoding side is similar:

.. sourcecode :: pycon

    >>> from urlconvert import plainEncode, encodeScript, encodePath, encodeQuery
    >>> encode_scheme = matchScheme()
    >>> encode_host = matchHost()
    >>> encode_port = matchPort()
    >>> encode_script = chainConverters(matchScript(), encodeScript())
    >>> encode_path = chainConverters(matchPath(), encodePath('utf8'))
    >>> encode_query = chainConverters(matchQuery(), encodeQuery())

Here's an example:

.. sourcecode :: pycon

    >>> Conversion(u'~smith').perform(encode_path).result
    u'%7Esmith'

Putting this alltogether you can do this:

.. sourcecode :: pycon

    >>> hoge = u'\u30c6\u30b9\u30c8'
    >>> ruleset = RuleSet([
    ...     rule(u'{*}://{*}:{*}/'+hoge),
    ... ])
    >>> ruleset.match_url(u'http://www.example.com/'+hoge).result
    {}
    >>> Conversion(hoge).perform(encode_path).result
    u'%E3%83%86%E3%82%B9%E3%83%88'
    >>> Conversion(u'%E3%83%86%E3%82%B9%E3%83%88').perform(decode_path).result
    u'\u30c6\u30b9\u30c8'

As you can see, the idea is that all the % escapes are decoded out by the time
you are matching a URL. Here's the same thing using the information in the
environ instead:

.. sourcecode :: pycon

    >>> from urlconvert import extract_url_parts
    >>> environ = {
    ...     'wsgi.url_scheme': 'http',
    ...     'SERVER_NAME': 'example.com',
    ...     'SERVER_PORT': '80',
    ...     'PATH_INFO': '/%E3%83%86%E3%82%B9%E3%83%88',
    ...     'SCRIPT_NAME': '/run.py',
    ...     'QUERY_STRING': 'name=james',
    ... }
    >>> flow = AttributeDict(wsgi=(AttributeDict(environ=environ)))
    >>> ruleset.match(url_parts=extract_url_parts(flow)).result
    {}

It also works with less extreme characters like the £ sign:

.. sourcecode :: pycon

    >>> pound = u'\xa3'
    >>> Conversion(pound).perform(encode_path).result
    u'%C2%A3'
    >>> ruleset = RuleSet([
    ...     rule(u'{*}://{*}:{*}/'+pound+'?{query}'),
    ... ])
    >>> from urlconvert import extract_url_parts
    >>> environ = {
    ...     'wsgi.url_scheme': 'http',
    ...     'SERVER_NAME': 'example.com',
    ...     'SERVER_PORT': '80',
    ...     'PATH_INFO': '/%C2%A3',
    ...     'SCRIPT_NAME': '/run.py',
    ...     'QUERY_STRING': 'name=james+gardner+%C2%A3',
    ... }
    >>> flow = AttributeDict(wsgi=(AttributeDict(environ=environ)))
    >>> ruleset.match(url_parts=extract_url_parts(flow)).result['query'] == u'name=james gardner '+pound
    True

Splitting Rules and URLs
------------------------

Internally, URLConvert uses tools to split URLs and rules. Here are some examples of how they work:

.. sourcecode :: pycon

    >>> from urlconvert import urlToParts, ruleToParts
    >>>
    >>> Conversion(u'scheme://host:port/path').perform(urlToParts()).result
    {'path': u'path', 'host': u'host', 'scheme': u'scheme', 'port': u'port'}
    >>> Conversion(u'scheme://host:port/path').perform(ruleToParts()).result
    {'script': u'{*}', 'host': u'host', 'query': u'{*}', 'path': u'path', 'scheme': u'scheme', 'port': u'port'}

So far so good. As you can see the first ``/`` is always included in the path.
When splitting a rule, the ``script`` and ``query`` get set to ``u'{*}'`` if
they aren't specified.

In our model, script never starts with a ``/``, the path components never start
with a ``/`` and there is no way to obtain the full path, only parts, no way to
obtain the full domain either. 

.. sourcecode :: pycon

    >>> Conversion(u'scheme://host:port/script|path').perform(ruleToParts()).result
    {'script': u'script', 'host': u'host', 'query': u'{*}', 'path': u'path', 'scheme': u'scheme', 'port': u'port'}
    >>> Conversion(u'scheme://host:port/{*}|path').perform(ruleToParts()).result
    {'script': u'{*}', 'host': u'host', 'query': u'{*}', 'path': u'path', 'scheme': u'scheme', 'port': u'port'}
    >>> Conversion(u'scheme://host:port/script|{*}').perform(ruleToParts()).result
    {'script': u'script', 'host': u'host', 'query': u'{*}', 'path': u'{*}', 'scheme': u'scheme', 'port': u'port'}
    >>> Conversion(u'scheme://host:port/{*}|{*}').perform(ruleToParts()).result
    {'script': u'{*}', 'host': u'host', 'query': u'{*}', 'path': u'{*}', 'scheme': u'scheme', 'port': u'port'}
    >>> Conversion(u'scheme://host:port/{*}').perform(ruleToParts()).result
    {'script': u'{*}', 'host': u'host', 'query': u'{*}', 'path': u'{*}', 'scheme': u'scheme', 'port': u'port'}

As an indication of how these are matched let's test with some URLs:

.. sourcecode :: pycon

    >>> Conversion(u'scheme://host:port/path').perform(urlToParts()).result
    {'path': u'path', 'host': u'host', 'scheme': u'scheme', 'port': u'port'}
    >>> Conversion(u'scheme://host:port/path').perform(ruleToParts()).result
    {'script': u'{*}', 'host': u'host', 'query': u'{*}', 'path': u'path', 'scheme': u'scheme', 'port': u'port'}
    >>> ruleset = RuleSet([rule(u'scheme://host:port/{path}')])
    >>> ruleset.match_url(u'scheme://host:port/one').result
    {u'path': u'one'}

.. sourcecode :: pycon

    >>> ruleset = RuleSet([rule(u'scheme://host:port/{script}|{path}')])
    >>> ruleset.match_url(u'scheme://host:port/', script=u'').error
    'No rule matched'
    >>> ruleset.match_url(u'scheme://host:port/one.cgi/', script=u'one.cgi').children[0].children['path'].error
    "Path u'' not matched against u'{path}'"
    >>> ruleset.match_url(u'scheme://host:port/one.cgi', script=u'one.cgi').children[0].children['path'].error
    "Path u'' not matched against u'{path}'"
    >>> ruleset.match_url(u'scheme://host:port/one.cgi', script=u'').children[0].children['script'].error
    "Script u'' not matched against u'{script}'"
    >>> ruleset.match_url(u'scheme://host:port/one.cgi/two', script=u'one.cgi').result
    {u'path': u'two', u'script': u'one.cgi'}

See also this thread: http://osdir.com/ml/python.web/2007-01/msg00021.html

    I think it's safe to say that WSGI does not permit an application to live
    at a mount point with a trailing '/', unless it is the root of the host.
    ...
    Given the weird effects that result from trying to manage relative names
    and other such complications of the idea, I don't think we should extend
    WSGI to allow applications to live at non-root URLs with trailing
    slashes. They should live at the named location, and optionally get a
    PATH_INFO. It's up to the application to interpret the trailing /, if any.

Matching In Detail
==================

Now you've seen how to correctly extract URL parts from a URL and fully
understand the encoding and decoding issues we can get back to URLConvert and
to understanding how the rules work.

Matching from the environment
-----------------------------

In most situations you won't want to match a URL, but will instead want to
match from the environment. You can use the ``extract_url_parts()`` function to
get the information you need from the environment and perform the necessary
decoding. 

.. note ::

    If you are using an encoding other than UTF-8 you will need to set up
    your own converters to pass as arguments to ``extract_url_parts()``.

Here's the same example environ we will use:

.. sourcecode :: pycon

    >>> environ = {
    ...     'wsgi.url_scheme': 'http',
    ...     'SERVER_NAME': 'example.com',
    ...     'SERVER_PORT': '80',
    ...     'PATH_INFO': '/name',
    ...     'SCRIPT_NAME': '/run.py',
    ...     'QUERY_STRING': 'name=james',
    ... }

Here's an example ``flow`` object which you might use:

.. sourcecode :: pycon

    >>> from bn import AttributeDict
    >>> flow = AttributeDict(wsgi=(AttributeDict(environ=environ)))

Let's create a ruleset:

.. sourcecode :: pycon

    >>> from urlconvert import RuleSet, rule, extract_url_parts
    >>> from conversionkit.exception import ConversionError
    >>>
    >>> ruleset = RuleSet([
    ...     rule(u'http://example.com:80/{hi}'),
    ...     rule(u'http://example.net:80/{hi}'),
    ... ])

Now let's try to match the information in the environment against these rules:

.. sourcecode :: pycon

    >>> url_parts = extract_url_parts(flow)
    >>> url_parts
    {'script': u'run.py', 'host': u'example.com', 'query': u'name=james', 'path': u'name', 'scheme': u'http', 'port': u'80'}
    >>> ruleset.match(url_parts).result
    {u'hi': u'name'}

As you can see, this example works too.

Wildcard Matching
-----------------

So far the rules you've seen haven't been very useful because they will only
work if the application is deployed at ``example.com`` or ``example.net``. If
you are writing an application it is more likely you'll want it to work at any
domain. You have two choices in that case:

* Automatically generate the rules based on the domain at which the application is deployed, perhaps from a config file
* Use unnamed matching

In the first case you could write code like this:

.. sourcecode :: python

    >>> display_host = u'example.com'
    >>> ruleset = RuleSet([
    ...     rule(u'http://'+display_host+u':80/{hi}'),
    ...     rule(u'http://'+display_host+u':80/{hi}'),
    ... ])
    >>> url_parts
    {'script': u'run.py', 'host': u'example.com', 'query': u'name=james', 'path': u'name', 'scheme': u'http', 'port': u'80'}
    >>> ruleset.match(url_parts).result
    {u'hi': u'name'}

Now both rules would match for the ``example.com`` domain but the application
would also work at other domains if the administrator deploying it set the
``flow.config.server.display_host`` option.

Although this works perfectly well it can be a bit cumbersome and is less well
suited to more complex cases. Instead it is better to use unnamed matching to
tell URLConvert that you don't care about a particular part of the URL and any
value should be matched. 

Here's the same example written with unnamed matching:

.. sourcecode :: pycon

    >>> ruleset = RuleSet([
    ...     rule(u'http://{*}:80/{hi}'),
    ...     rule(u'http://{*}:80/{hi}'),
    ... ])

This time, any host or domain would work. Let's check with the current domain
then change the domain to ``example.org`` and try again:

.. sourcecode :: pycon

    >>> url_parts
    {'script': u'run.py', 'host': u'example.com', 'query': u'name=james', 'path': u'name', 'scheme': u'http', 'port': u'80'}
    >>> ruleset.match(url_parts).result
    {u'hi': u'name'}
    >>> url_parts['host'] = u'example.org'
    >>> url_parts
    {'script': u'run.py', 'host': u'example.org', 'query': u'name=james', 'path': u'name', 'scheme': u'http', 'port': u'80'}
    >>> ruleset.match(url_parts).result
    {u'hi': u'name'}

The new domain matches too. Notice that the URL parts must always be Unicode strings.

Wildcard Matching
-----------------

If an unnamed variable is the only part of a domain, script or path, the
*whole* part is matched (including any ``.`` or ``/`` characters. This probably
isn't what you expect but it is what you get!


Each of the parts of the URL can be marked as being a unnamed, just by
replacing their entire content with ``{*}``. As an example, here's a fully
specified rule which will match any URL (although it won't return any 
variables because none are specified:

.. sourcecode :: pycon

    >>> ruleset = RuleSet([rule(u'{*}://{*}:{*}/{*}')])
    >>> ruleset.match_url(u'http://example.com/james').result
    {}
    >>> ruleset = RuleSet([rule(u'{*}://{*}:{*}/')])
    >>> ruleset.match_url(u'http://example.com/').result
    {}
    >>> ruleset = RuleSet([rule(u'{*}://{*}:{}/|')])
    >>> ruleset.match_url(u'http://example.com/', script=u'').result
    {}
    >>> ruleset = RuleSet([rule(u'{*}://{*}:{*}/one.cgi|')])
    >>> ruleset.match_url(u'http://example.com/', script=u'one.cgi').result
    {}



Full Rules: Script name and query string
----------------------------------------

So far the format we've been using for the rules hasn't allowed you to specify
what should happen with the script name or query string. If you want to specify
these you need to use the *full form* of a rule as demonstrated below. Notice
that ``|`` is used as a delimiter between the script name and path info and the
``?`` is used as a delimiter between the path info and query string.

.. sourcecode :: pycon

    >>> url_parts
    {'script': u'run.py', 'host': u'example.org', 'query': u'name=james', 'path': u'name', 'scheme': u'http', 'port': u'80'}
    >>> ruleset = RuleSet([rule(u'{*}://{*}:{*}/run.py|{*}?name=var')])
    >>> ruleset.match(url_parts).children[0].children['query'].error
    "The query u'name=james' does not match u'name=var' expected by the rule"
    >>> url_parts['query'] = u'name=var'
    >>> ruleset.match(url_parts).result 
    {}

For this rule to match the script name must be ``run.py`` and there must be a
query string ``name=var``. The scheme, host, port and path can be anything
though. You can also have the script name and query string assigned to variables:

.. sourcecode :: pycon

    >>> ruleset = RuleSet([rule(u'{*}://{*}:{*}/{script}|{*}?{query}')])
    >>> ruleset.match(url_parts).result
    {u'query': u'name=var', u'script': u'run.py'}

Here the script name would always be mapped to the variable ``script`` and the
query string would always be mapped to ``query``.

In reality it is very unlikely you'd want to match on the query string or path
info so rather than writing out all rules in full, the short form is usually
used. You can always specify a unnamed part for the script, query or both if
you want to use the full form but don't want them to contribute to the matching
process:

Using the controller and action pattern
---------------------------------------

One common pattern employed by frameworks such as Ruby on Rails and Pylons is
to have your URL always result in two variables: one named ``action`` and one
named ``controller``. The action defines the name of a function or method to
call to handle the URL and the controller defines what file it is in.

You can use this pattern with URLConvert too.

.. sourcecode :: pycon

    >>> ruleset = RuleSet([rule(u'{*}://{*}:{*}/{controller}/{action}')])
    >>> ruleset.match_url(u'http://example.com/account/signin').result
    {u'action': u'signin', u'controller': u'account'}

Additional Variables
--------------------

Sometimes you might want a particular URL to have a special meaning. For
example it might be that the URL http://www.example.com/signin should also
result in the  ``signin()`` action of the ``account`` controller being called.
If you think about how to you would write this using the rule syntax above you
will realise that you can't because there is only one path info component but
that you need to assign two variables. For this reason URLConvert has a feature
for adding variables if the rest of the rule matches. Here's one way it could
be handled:
    
.. sourcecode :: pycon

    >>> ruleset = RuleSet([rule(u'{*}://{*}:{*}/{action}', add={u'controller': u'account'})])
    >>> ruleset.match_url(u'http://example.com/signin').result
    {u'action': u'signin', u'controller': u'account'}

This rule would mean that any URL which had just one component in the path info
would be treated as an action of the ``account`` controller. Effectively the
``action`` variable would be matched from the URL and the ``controller``
variable would be added from the dictionary specified so that the resulting
dictionary of variables is the same and would therefore result in the same
``signin()`` action of the ``account`` controller being called.

Static Text
-----------

If you only wanted URLConvert to add the ``controller`` variable with a value
of ``account`` for this URL, and not for others with just one path info
component you would have to do something slightly differently. Rather than
specifying the variable ``action`` in the URL you would add the *static text*
``signin`` and put the ``action`` variable in the add dictionary like this:

.. sourcecode :: pycon

    >>> ruleset = RuleSet([rule(u'{*}://{*}:{*}/signin', add={u'action': u'signin', u'controller': u'account'})])
    >>> ruleset.match_url(u'http://www.example.com/signin').result
    {u'action': u'signin', u'controller': u'account'}

Unlike the previous example, this URL would not match http://www.example.com/signout:

.. sourcecode :: pycon

    >>> ruleset.match_url(u'http://www.example.com/signout').error
    'No rule matched'

Matching Subdomains
-------------------

You can match subdomains just as easily as paths:

.. sourcecode :: pycon

    >>> ruleset = RuleSet([rule(u'{*}://{subdomain}.example.com:{*}/{action}', add={u'controller': u'account'})])
    >>> ruleset.match_url(u'http://www.example.com/signin').result
    {u'action': u'signin', u'controller': u'account', u'subdomain': u'www'}

Matching on Scheme and Port
---------------------------

You can also match on scheme and port too. Unlike subdomains and paths though,
you can't mix and match static text *and* variables in these URL parts, you
just choose one or the other.

.. sourcecode :: pycon

    >>> ruleset = RuleSet([rule(u'{scheme}://{subdomain}.example.com:{port}/{action}', add={u'controller': u'account'})])
    >>> ruleset.match_url(u'http://www.example.com/signin').result
    {u'action': u'signin', u'scheme': u'http', u'controller': u'account', u'subdomain': u'www', u'port': u'80'}

Here we've called the variables ``scheme`` and ``port`` but you could have
called them something else too.

Rule Order
----------

Your application could conceivably have quite a few rules. It is important you
specify the rules with the most specific ones first, otherwise there is a
chance that more specific rules won't be matched because the more generic ones
will be matched first. For example, consider this URL::

    http://www.example.com/signin

and these two rules:

.. sourcecode :: pycon

    >>> ruleset = RuleSet([
    ...     rule(u'{*}://{*}:{*}/{controller}', add={u'action': u'index'}),
    ...     rule(u'{*}://{*}:{*}/signin', add={u'controller': u'account', u'action': u'signin'}),
    ... ])

In this situation you might intend for the URL to be matched by the second rule
and result in the ``signin()`` action being called. Instead the first rule
matches and ``signin`` is treated as the value for the ``controller`` variable.

.. sourcecode :: pycon

    >>> ruleset.match_url(u'http://www.example.com/signin').result
    {u'action': u'index', u'controller': u'signin'}

Instead specify them like this:

.. sourcecode :: pycon

    >>> ruleset = RuleSet([
    ...     rule(u'{*}://{*}:{*}/signin', add={u'controller': u'account', u'action': u'signin'}),
    ...     rule(u'{*}://{*}:{*}/{controller}', add={u'action': u'index'}),
    ... ])
    >>> ruleset.match_url(u'http://www.example.com/signin').result
    {u'action': u'signin', u'controller': u'account'}

Trailing Forward Slashes
------------------------

Servers such as Apache and URL routing systems like Routes sometimes treat these as the same URL::

    http://www.example.com/signin
    http://www.example.com/signin/

The trailing ``/`` at the end makes these completely different URLs so it is
generally a bad idea to pretend they are the same. URLConvert is explicit about
treating theses as **different** URLs. If you want both URLs to generate the
same variables dictionary you need to add two rules, one for each URL:

.. sourcecode :: pycon

    >>> ruleset = RuleSet([
    ...     rule(u'{*}://{*}:{*}/signin', add={u'controller': u'account', u'action': u'signin'}),
    ...     rule(u'{*}://{*}:{*}/signin/', add={u'controller': u'account', u'action': u'signin'}),
    ... ])
    >>> ruleset.match_url(u'http://www.example.com/signin').result
    {u'action': u'signin', u'controller': u'account'}
    >>> ruleset.match_url(u'http://www.example.com/signin/').result
    {u'action': u'signin', u'controller': u'account'}

A little more typing early on will make things much simpler later.

Duplicate Variables
-------------------

One thing you can't do is have a variable which is specified in the URL also
specified in the add dictionary. If you think about it this wouldn't make sense
because URLConvert wouldn't know which to use. You can't therefore do this:

.. sourcecode :: pycon

    >>> rule(u'{*}://{*}:{*}/{controller}', add={u'controller': u'account'})
    Traceback (most recent call last):
      File ...
    URLConvertError: The 'add' dictionary cannot contain the same key u'controller' as a routing variable defined in the rule

You can however specify the same name twice in the same rule. Doing so means
that the variable must take the same value in both places for the rule to
match. For example, the following rule:

.. sourcecode :: pycon

    >>> ruleset = RuleSet([
    ...     rule(u'{*}://{subdomain}.{}.{}:{*}/{subdomain}', add={u'controller': u'account', u'action': u'signin'}),
    ... ])

Would match for these URLs:

.. sourcecode :: pycon

    >>> ruleset.match_url(u'http://www.example.com/www').result
    {u'action': u'signin', u'controller': u'account', u'subdomain': u'www'}
    >>> ruleset.match_url(u'http://signin.example.com/signin').result
    {u'action': u'signin', u'controller': u'account', u'subdomain': u'signin'}

But not for this URL:

.. sourcecode :: pycon

    >>> ruleset.match_url(u'http://www.example.com/signin').error
    'No rule matched'

That's really all there is to know about URL matching. Everything is very
simple and very explicit. Now let's look at URL generation.

Generating URLs
===============

If you pass the same variables obtained from matching, back to the rule that
matched them you'll get back a URL will match the rule again. That's the idea
behind the generation side of URLConvert.

URLConvert can't automatically generate URLs for rules which have either
wildcard or unnamed parts when they match because the rule doesn't contain any
information about what to add in. In these circumstances you need to supply a
dictionary of URL parts to use as defaults. These can either be based on the
current URL, or from config file settings or elsewhere.

Here's an example:

.. sourcecode :: pycon

    >>> from urlconvert import build_url
    >>> ruleset = RuleSet([
    ...     rule(u'{*}://{*}:{*}/blog/{year}/{month}/{day}', add={u'controller': u'blog', u'action': u'view'}),
    ... ])
    >>> vars = {u'action': u'view', u'controller': u'blog', u'year': u'2009', u'day': u'18', u'month': u'08'}
    >>> ruleset.generate_url(vars, default_url_parts=dict(scheme=u'http', host='example.com', port=u'80'))
    u'http://example.com/blog/2009/08/18'

Here's an example which also matched part of the domain:

.. sourcecode :: pycon

    >>> from urlconvert import build_url
    >>> ruleset = RuleSet([
    ...     rule(u'{*}://example.{tld}:{*}/blog/{year}/{month}/{day}', add={u'controller': u'blog', u'action': u'view'}),
    ... ])
    >>> vars = {u'action': u'view', u'controller': u'blog', u'year': u'2009', u'day': u'18', u'month': u'08', 'tld': u'net'}
    >>> ruleset.generate_url(vars, default_url_parts=dict(scheme=u'http', host='example.com', port=u'80'))
    u'http://example.net/blog/2009/08/18'

Notice that this time, the default host part wasn't needed because all the
information could be determined from the rule and the vars. As a result, the
host and domain is ``example.net``, not ``example.com``.

Extending URLConvert
====================

URLConvert is specifically desgined to be *predictable*. That means it always
provides detailed error structures you can inspect to see why rules didn't
match and it avoids fancy features in favour of forcing you to be slightly more
verbose. Since it is predictable, matching and generation can be cached which
means it is very fast in practice for all but the uncommon URL cases.

It also avoids any filtering or matching so **all routing variables are always
Unicode strings**. If you want to do more specific conversions you can pass the
routing variables through a normal ConversionKit converter. Since the
``rule()`` function simply returns two normal ConversionKit converters you can
either chain them with your new converter or write your own completely. Let's
start by chaining the rules with another converter. Here's the classic blog
example:


.. sourcecode :: pycon

    >>> ruleset = RuleSet([
    ...     rule(u'{*}://{*}:{*}/blog/{year}/{month}/{day}', add={u'controller': u'blog', u'action': u'view'}),
    ... ])
    >>> ruleset.match_url(u'http://www.example.com/blog/2009/08/18').result
    {u'action': u'view', u'controller': u'blog', u'year': u'2009', u'day': u'18', u'month': u'08'}

At the moment this would also match this, which isn't a valid URL:

.. sourcecode :: pycon

    >>> ruleset.match_url(u'http://www.example.com/blog/not/valid/url').result
    {u'action': u'view', u'controller': u'blog', u'year': u'not', u'day': u'url', u'month': u'valid'}

Other frameworks solve this with regular expressions or with their own DSL
(domain specific languages) but at this point I think it is easier and more
predictable to drop into Python code.

Let's modify the rule:

.. sourcecode :: pycon

    >>> from stringconvert import toUnicode, unicodeToInteger
    >>> from conversionkit import chainConverters, toDictionary, noConversion
    >>> 
    >>> r = rule(u'{*}://{*}:{*}/blog/{year}/{month}/{day}', add={u'controller': u'blog', u'action': u'view'})
    >>> new_to_vars = chainConverters(
    ...     r.to_vars,
    ...     toDictionary(
    ...         converters = dict(
    ...             year = unicodeToInteger(min=2000, max=2100), 
    ...             month = unicodeToInteger(min=1, max=12), 
    ...             day = unicodeToInteger(min=1, max=31),
    ...         ),
    ...         # Leave the other routing variables in there:
    ...         filter_extra_fields = False
    ...     ),
    ... )
    >>> new_to_url = chainConverters(
    ...     toDictionary(
    ...         converters = dict(
    ...             # We don't want to do anything with the 'current' dictionary
    ...             current = noConversion(),
    ...             vars = toDictionary(
    ...                 converters = dict(
    ...                     year = chainConverters(toUnicode(), unicodeToInteger(min=2000, max=2100), toUnicode()),
    ...                     month = chainConverters(toUnicode(), unicodeToInteger(min=1, max=12), toUnicode()), 
    ...                     day = chainConverters(toUnicode(), unicodeToInteger(min=1, max=31), toUnicode()),
    ...                 ),
    ...                 # Leave the other routing variables in there:
    ...                 filter_extra_fields = False
    ...             ),
    ...         ),
    ...     ),
    ...     r.to_url,
    ... )

Let's create a new ruleset using the new converters for matching and generating:

.. sourcecode :: pycon

    >>> ruleset = RuleSet([
    ...     AttributeDict(to_vars=new_to_vars, to_url=new_to_url),
    ... ])
    >>> vars = ruleset.match_url(u'http://www.example.com/blog/2009/08/18').result
    >>> vars
    {u'action': u'view', u'controller': u'blog', u'month': 8, u'day': 18, u'year': 2009}
    >>> ruleset.generate_url(vars, dict(host=u'www.example.com', scheme=u'http', port=u'80'))
    u'http://www.example.com/blog/2009/8/18'

             

