======================
 Products.JRedirector
======================

.. contents:

The JRedirector package provides an object that is capable of 
redirecting web requests in a controlled fashion and keeping logs 
about it.

I wrote it so that when I move pieces of my sites around I have 
a way of specifying where users will go if they navigate to the old 
obsolete location. This is helpful if your site is linked from 
other sites and you have no control over the accuracy of these 
outside links.

The administrator can add mappings from old path to new path where 
the user will be redirected to when he tries to visit the old path. 
The HTTP header sent along with this redirect can be specified, 
available choices are "301" (moved permanently) or "302" (moved 
temporarily).

The object will keep an internal log of all web requests that are 
referred to it and presents it on a logging output page.


Usage
=====
The administrator creates a JRedirector object in a given 
location in site. Invoking the redirection capabilities must happen 
explicitly, for example from standard_error_message, by calling 
the JRedirector object and passing REQUEST.

As an example, here is the snippet of my standard_html_error that 
invokes the JRedirector object::

  <dtml-if expr="error_type == 'NotFound'">
    <dtml-call expr="redirector_object(REQUEST)">
  </dtml-if>

This will fire whenever a "NotFound" error occurs. If the path 
the user attempted to go to is not in the explicitly mapped 
list of paths defined by the administrator in the JRedirector
object "Mappings" tab then nothing will happen and the 
standard_error_message will continue to render normally. If the
looked-for path is explicitly mapped then the user will be 
redirected and will never see standard_error_message.
  

Requirements
============
This package requires Zope 2.8 and up.


HTTP Status Codes related to redirecting requests
=================================================
The following is taken from RFC 2616 which describes the HTTP/1.1
specification. The RFCs can be found in various locations on the
Internet, I found it here::

  ftp://ftp.isi.edu/in-notes/rfc2616.txt

Not all status codes are understood by all browsers. If you are worried
about older browsers you should restrict your usage to status codes
301 for permanently moved pages and 302 for temporary moves.

301 Moved Permanently
---------------------
The requested resource has been assigned a new permanent URI and any
future references to this resource SHOULD use one of the returned
URIs.  Clients with link editing capabilities ought to automatically
re-link references to the Request-URI to one or more of the new
references returned by the server, where possible. This response is
cacheable unless indicated otherwise.

The new permanent URI SHOULD be given by the Location field in the
response. Unless the request method was HEAD, the entity of the
response SHOULD contain a short hypertext note with a hyperlink to
the new URI(s).

If the 301 status code is received in response to a request other
than GET or HEAD, the user agent MUST NOT automatically redirect the
request unless it can be confirmed by the user, since this might
change the conditions under which the request was issued.

Note: When automatically redirecting a POST request after
receiving a 301 status code, some existing HTTP/1.0 user agents
will erroneously change it into a GET request.

302 Found
---------
The requested resource resides temporarily under a different URI.
Since the redirection might be altered on occasion, the client SHOULD
continue to use the Request-URI for future requests.  This response
is only cacheable if indicated by a Cache-Control or Expires header
field.

The temporary URI SHOULD be given by the Location field in the
response. Unless the request method was HEAD, the entity of the
response SHOULD contain a short hypertext note with a hyperlink to
the new URI(s).

If the 302 status code is received in response to a request other
than GET or HEAD, the user agent MUST NOT automatically redirect the
request unless it can be confirmed by the user, since this might
change the conditions under which the request was issued.

Note: RFC 1945 and RFC 2068 specify that the client is not allowed
to change the method on the redirected request.  However, most
existing user agent implementations treat 302 as if it were a 303
response, performing a GET on the Location field-value regardless
of the original request method. The status codes 303 and 307 have
been added for servers that wish to make unambiguously clear which
kind of reaction is expected of the client.

303 See Other
-------------
The response to the request can be found under a different URI and
SHOULD be retrieved using a GET method on that resource. This method
exists primarily to allow the output of a POST-activated script to
redirect the user agent to a selected resource. The new URI is not a
substitute reference for the originally requested resource. The 303
response MUST NOT be cached, but the response to the second
(redirected) request might be cacheable.

The different URI SHOULD be given by the Location field in the
response. Unless the request method was HEAD, the entity of the
response SHOULD contain a short hypertext note with a hyperlink to
the new URI(s).

Note: Many pre-HTTP/1.1 user agents do not understand the 303
status. When interoperability with such clients is a concern, the
302 status code may be used instead, since most user agents react
to a 302 response as described here for 303.

307 Temporary Redirect
----------------------
The requested resource resides temporarily under a different URI.
Since the redirection MAY be altered on occasion, the client SHOULD
continue to use the Request-URI for future requests.  This response
is only cacheable if indicated by a Cache-Control or Expires header
field.

The temporary URI SHOULD be given by the Location field in the
response. Unless the request method was HEAD, the entity of the
response SHOULD contain a short hypertext note with a hyperlink to
the new URI(s) , since many pre-HTTP/1.1 user agents do not
understand the 307 status. Therefore, the note SHOULD contain the
information necessary for a user to repeat the original request on
the new URI.

If the 307 status code is received in response to a request other
than GET or HEAD, the user agent MUST NOT automatically redirect the
request unless it can be confirmed by the user, since this might
change the conditions under which the request was issued.

Bug tracker
===========
If you have suggestions, bug reports or requests please use the issue
tracker at http://www.dataflake.org/tracker/

SVN version
===========
You can retrieve the latest code from Subversion using setuptools or
zc.buildout via this URL:

http://svn.dataflake.org/svn/Products.JRedirector/trunk#egg=Products.JRedirector

