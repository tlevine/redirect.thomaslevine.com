Web forward API
=========================

Web forwards, or HTTP redirects, should be easy, but I couldn't find any
service I liked. Problems with existing services:

* The good ones are DNS services that cost like $50 per year. This doesn't
    need to be so expensive.
* I use Gandi's web forwards for the domains I have registered on Gandi, but
    not all registrars provide HTTP redirects.
* Gandi is too complicated. HTTP redirects are stupidly simple to specify;
    I should be able to specify one with a form with one or two fields.
* Setting up my own server took half a day. It shouldn't take this long.

Given all these problems, I figured I'd make a service myself. For now, it's
free. If shit tons of people start using it and I need to get another server
or a bigger server, I'll need figure out how to make it sustainable, but it
would still certainly be cheap.

## What do I mean by "HTTP redirects"?

Here's the most common sort of HTTP redirect: I own thomaslevine.com, I host
a website at www.thomaslevine.com, and I want thomaslevine.com and
www.thomaslevine.com to go to the same place, so I make thomaslevine.com
redirect to www.thomaslevine.com.

More technically, this includes HTTP responses with codes of 301, ..., but it
could include more, like proxying and dynamic DNS. What's really relevant to
this service is that they are tiny things that need a reliable server but don't need a big server.
