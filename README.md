Web forwards
=========================
Web forwards, or HTTP redirects, should be easy, but I couldn't find any
service I liked. Problems with existing services:

* The good ones are [DNS](http://freedns.afraid.org/) [hosting](http://dyn.com)
    that costs like $50 per year. Redirects don't need to be so expensive.
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
Here's the most common sort of HTTP redirect: I own
[thomaslevine.com](http://thomaslevine.com),
I host a website at
[www.thomaslevine.com](http://www.thomaslevine.com),
and I want
[thomaslevine.com](http://thomaslevine.com) and
[www.thomaslevine.com](http://www.thomaslevine.com)
to go to the same place, so I make
[thomaslevine.com](http://thomaslevine.com)
redirect to
[www.thomaslevine.com](http://www.thomaslevine.com).

More technically, this currently includes HTTP responses with codes of 301
and 303, but it could include more. The relevant part is that these are tiny
things that need a reliable server but don't need a big server.

## How to use: Set up DNS
First, you need to add a record to your zone file with your DNS provider. If
you don't know what that means, it's probably the the site that you use to
manage all of your web hosting; a lot of hosts package domain registration,
domain name service and web hosting.

Let's say you want to redirect from [thomaslevine.com](http://thomaslevine.com) to [www.thomaslevine.com](http://www.thomaslevine.com).
In this case, you need to add an A record that points "[thomaslevine.com](http://thomaslevine.com)" to
"37.247.48.207". Depending on your provider, you might have to specify it in
one of a few days. Typically, the zone file editor assumes that you are
managing subdomains, so you might need to enter "" (nothing),
"[thomaslevine.com](http://thomaslevine.com)", or "@" in whatever form you're using. If you're editing the
zone file directly, this line should work.

    @ 10800 IN A 217.70.184.38

You'll have to wait some time, between a few minutes and a few days, for the
change to be propogated to the world's DNS servers. Once that happens, you can
go to the domain that you are redirecting from ([thomaslevine.com](http://thomaslevine.com) in this
example) and set up the redirection. Alternatively, you can go to
[redirect.thomaslevine.com](http://redirect.thomaslevine.com) before then and
set it up, but it won't work until the change gets propogated through the
world's caches. Either way, follow

## How to use: Set up the redirect
You can set up the redirect with a web page that works like you expect. If
you want something fancier or more automatic, use the the API. The form calls
the API, in case you're curious.

### Via the GUI
Go to [redirect.thomaslevine.com](http://redirect.thomaslevine.com), and fill
out the form. It contains two fields

1. **from** is the site that people type in to their URL bar; it's the thing
    you added an A record to the zone file (see above) for.
2. **to** is the place where they should land; it's where you are already
    hosting the site.

You will land at another page. **Save that page's URL**; The identifier at the
end is like a password, so you'll need it if you ever want to change the
redirect.

### Via the API
Choose an identifier for your redirect. This acts as a password, so you should
choose something that other people won't guess or choose accidentally. Bad
identifiers include "website" and "thomaslevine.com". Good ones include
"UDSkS9XH8w07Fq98Jue3aU" and "thomaslevine.com-dear badly pain blanket". You
can find more good identifiers
[here](http://preshing.com/20110811/xkcd-password-generator).
Now that you've chosen an identifier, this is the URL that should concern you

    http://redirect.thomaslevine.com/v1/<identifier>

You can **create**, **edit**, **read** and **delete** the redirect by making
HTTP requests to this URL. Examples follow.

#### Create
Create a redirect from
"[thomaslevine.com](http://thomaslevine.com)" to
"[www.thomaslevine.com](http://www.thomaslevine.com)"
like so.

    curl -X PUT\ 
    --data from=<from address, like "thomaslevine.com"> \ 
    --data to=<to address, like "www.thomaslevine.com"> \
    http://redirect.thomaslevine.com/v1/sho+ue8ohn,.n237fun

You may also specify an HTTP status code and email address for the redirect.

    curl -X PUT\ 
    --data from="thomaslevine.com" \ 
    --data to="www.thomaslevine.com" \
    --data status_code=301 \
    --data email=occurrence@example.com \
    http://redirect.thomaslevine.com/v1/sho+ue8ohn,.n237fun

Regardless of whether you provide an **email address**, I might contact you to
figure out how I can make this better. If you provide an email address, this
will be easier. Also, I'll be more able to inform you of outages and whatnot.

The default is **status code** is 303, which functions as a temporary redirect.
If 303 is specified, the redirect server will be called every time a browser
tries to go to your website. You may also specify 301, which is a permanent
redirect. In this cose, the redirect will be cached within the browser, so
the server will only be called once on each computer; this will make your site
ever-so-slightly faster, reduce my load ever-so-slightly, and make your site
ever-so-slightly more robust in case of outages of my server. It would be
reasonable to use 303 for testing and 301 once it seems to work. And tell me
if you want options for other status codes.

#### Edit
You can edit a redirect by making a PUT request just like you created it.

    # This would remove the email address if one was already listed.
    curl -X PUT \ 
    --data from="thomaslevine.com" \ 
    --data to="www.thomaslevine.com" \
    --data status_code=303 \
    http://redirect.thomaslevine.com/v1/sho+ue8ohn,.n237fun

If you would like to edit just one field, you can also use a POST instead.

    # This would not remove the email address if one was already listed.
    curl -X POST \ 
    --data from="thomaslevine.com" \ 
    --data to="www.thomaslevine.com" \
    --data status_code=303 \
    http://redirect.thomaslevine.com/v1/sho+ue8ohn,.n237fun

    # This is valid.
    curl -X POST \ 
    --data status_code=303 \
    http://redirect.thomaslevine.com/v1/sho+ue8ohn,.n237fun

    # This is not valid.
    curl -X PUT \ 
    --data status_code=303 \
    http://redirect.thomaslevine.com/v1/sho+ue8ohn,.n237fun

#### Read
Run something like this to read the redirect configuration of the redirect.

    curl http://redirect.thomaslevine.com/v1/sho+ue8ohn,.n237fun

You'll get something like this.

    { "from": "thomaslevine.com",
      "to": "www.thomaslevine.com",
      "email": "occurrence@example.com",
      "created": "2012-08-03 03:56",
      "status_code": 303
    }

If you request a url that does not correspond to a redirect, you'll get
something like this

    { "error": "That redirect doesn't exist. But feel free to create it."
    }

**Delete** the redirect configuration like so.

    curl -X DELETE http://redirect.thomaslevine.com/v1/sho+ue8ohn,.n237fun

## Technical details
This runs on a tiny server from Prometeus. The API is a CGI script that runs
with fcgiwrap on nginx and edits nginx sites; each redirect is a site.
