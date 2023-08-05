<%inherit file="base.mak"/>

##<h1>Authetication failure</h1>

## TODO: show something more usefull
<p>
  The remote OpenID server denied authentication from this site.  
% if c.fail_msg:
  The message from remove server was <em>"${c.fail_msg}"</em>.
% else:
  The server did not supply an error message.
% endif
</p>

<p>
  You can <a href="/login">try again</a> or <a href="/">continue
  browsing</a> as an anonymous visitor.

</p>