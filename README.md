Web redirects
=========================
## What do I mean by "web redirects"?
They're also called web forwards, HTTP redirects and URL redirects. Here's the
most common sort of HTTP redirect: I own
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

Wikipedia has [further thoughts](http://en.wikipedia.org/wiki/URL_redirection).
More technically, this currently includes HTTP responses with codes of 301
and 303, but it could include more. The relevant part is that these are tiny
things that need a reliable server but don't need a big server.

## Why
I started needing these when I started hosting things on Amazon S3. Amason S3
requires you to point CNAME records to Amazon, so you can't use bare domains.
So I wanted to redirect the domains. I could do this with a proper server, but
I was sure some other service already did this. But I couldn't find any service
I liked. Problems with existing services:

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

## How to use: Set up DNS
First, you need to add a record to your zone file with your DNS provider. If
you don't know what that means, it's probably the the site that you use to
manage all of your web hosting; a lot of hosts package domain registration,
domain name service and web hosting.

Let's say you want to redirect from [thomaslevine.com](http://thomaslevine.com) to [www.thomaslevine.com](http://www.thomaslevine.com).
In this case, you need to add an A record that points "[thomaslevine.com](http://thomaslevine.com)" to
"108.174.51.19". Depending on your provider, you might have to specify it in
one of a few days. Typically, the zone file editor assumes that you are
managing subdomains, so you might need to enter "" (nothing),
"[thomaslevine.com](http://thomaslevine.com)", or "@" in whatever form you're using. If you're editing the
zone file directly, this line should work.

    @ 10800 IN A 108.174.51.19

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
      "status_code": 303
    }

If you request a url that does not correspond to a redirect, you'll get
something like this

    { "error": "That redirect doesn't exist. But feel free to create it."
    }

**Delete** the redirect configuration like so.

    curl -X DELETE http://redirect.thomaslevine.com/v1/sho+ue8ohn,.n237fun

## Architecture
Let's divide it into two parts.

1. ReST API for editing nginx configuration files
2. Nginx

The ReST API (documented above) only reads and edits configuration files; it
doesn't serve redirects. If you **delete** the ReST API and **run** Nginx,
you will **not** be able to edit redirects, and the redirects **will** be served.
If you turn **on** the ReST API and **uninstall** Nginx, your API queries
**will** read and edit the nginx configuration files, and the redirects will
**not** be served.

This is very convenient; because Nginx handles all of the heavy traffic, I
don't need to write an application that can handle substantial load. Also,
if I notice a problem with the API, I can just disable it while I fix it.
(This aspect hasn't been relevant because my code is so awesome.)

### Front-end
Aside from sites that the ReST API creates, Nginx serves the front-end clicky
AJAX form for creating sites. The only interesting part about that is the
selection of identifiers. First, this is what I mean by the "identifier".

    http://redirect.thomaslevine.com/v1/:identifier

The API requires that you select the identifier. It is thus possible for them
to clash, so I just used them as passwords by suggesting that they be made
really long. The front-end does this for you without telling you; it generates
a UUID for the identifier. You can see it by clicking "Show advanced options."

### Scaling
It should be easy to adjust the nginx configuration to handle high load, but
problems could arise if lots of people are editing lots of redirects with the
ReST API. There isn't any particular thing that worries me much, but here are
some ideas of how to approach that.

1. If lots of people are accessing your redirects (not the API), just run
    multiple Nginx boxes with one API box; you can send the configuration file
    directory from the API box to the Nginx boxes every so often.
2. If you want to run multiple API boxes, consider why you need them, as this
    situation would be a bit strange. Naively, I could suggest storing the
    configuration files in GlusterFS and accessing this from all of the Nginx
    and API boxes. But you might be able to make some convenient assumptions
    in such a sitiation that would allow you to do something simpler.
3. Depending on what filesystem you're using, having lots of files could be
    problematic. I don't know whether it would noticeably impact Nginx. It
    shouldn't be a problem for the API because it always looks for one
    particular file. If you are using a stupid filesystem, you might hit
    the limit on the number of files in a directory.
4. If you are going to access the same API endpoint from many different
    computers at similar times, you might want to think about whether there
    are relevant race conditions in this API code. I don't think there are
    any, but I haven't used this API like that.

## Hosting
This runs on a tiny server from ChicagoVPS. The API is a uWSGI application that
runs inside of a tmux because I didn't feel like making a proper ademon. It
edits nginx configuration files; each redirect is a server entry.

### Installing the server
If we're lucky, the entire install process can be run without interactively
logging in to the redirect server; all of the commands below are supposed to be
run from any old computer, rather than the redirect server.

First, make an A record pointing to the server and install Debian on the server.
Then configure the ssh keys. 

    ssh-copy-id root@redirect.thomaslevine.com

Now build the dependencies and copy the files. There's a script for this.

    . activate
    build_redirect_server redirect.thomaslevine.com

All done. Test it out.

    curl http://redirect.thomaslevine.com
    curl -X PUT \ 
    --data from="thomaslevine.com" \ 
    --data to="www.thomaslevine.com" \
    --data status_code=303 \
    http://redirect.thomaslevine.com/v1/sho+ue8ohn,.n237fun

### Running the backups
Run `./bin/backup_redirect_server` to take backups. Set up a cron job to do
this daily or so.

### Integration tests
Run `./bin/runlocal` to run a server on [localhost:9002](http://localhost:9002).
Then you can run `nosetests2 integrationtests.py` from `./application` to run
integration tests locally.

Run `./bin/integration_tests` to run integration tests on the live site. You
could set up a cron job to do this daily or so.

## Wishlist
Here are some things I want.

* I want different views in the front-end should have own URLs
    (fragment identifiers) so that the back button can work and so that I can
    link to places.
* I want API should run in a real daemon, not a tmux, just because.
* I want the configuration files should be prefixed with something later than
    "1-", like maybe "50-", so that I can manually add other sites with higher
    priority.
* I want a system for backing up the nginx configuration with all of the
    redirects to another server so that I can restore the redirects in case of
    problems. A git repository in `/etc/nginx/conf.d/` should be fine for this.
* I sort of want the Javascript on the front end to be less hacky and ugly, but
    I haven't wanted to edit this at all, and it's been working just fine, so
    maybe it's not that important.
