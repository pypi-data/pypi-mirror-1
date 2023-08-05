<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" 
	  "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
##<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
##    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" lang="en" xml:lang="en">
<head>
  <meta http-equiv="content-type" 
	content="text/html; charset=us-ascii" />
% if c.noindex:
  <meta name="robots" content="noindex,nofollow">
% endif

## Main distribution CSS
  <link rel="stylesheet" 
	type="text/css" 
	media="screen,projection"
	href="/css/simple.css" />

## Sites should be able to make most constumizations in this one to
## make upgrading as painless as possible.
  <link rel="stylesheet" 
	type="text/css" 
	media="screen,projection"
	href="/css/site.css" />

  <link rel="shortcut icon" href="/favicon.ico" />
  <title>${c.title and c.title + " -"} Gazest</title>

  <%namespace file="common_defs.mako" import="*" 
              name="common" inheritable="True"/>

  ## Default is not to warn.  Pages leading write action should
  ## override this
  <%def name="readonly_msg()"></%def>

</head>
<body>

  <div id="page-container">
    
    <%include file="nav1.mako" />

    <div class="img-header">
      <img class="img-header" src="/img/top-banner.jpg" alt="" />
    </div>

    <%include file="nav2.mako" />
    
    ## actually, a spacer
    <div class="buffer"></div>

    % if c.site_readonly:
      ${self.readonly_msg()}
    % endif

    <%include file="msgs.mako" />

% if c.sidebars:

    <div id="contentwrapper">
      
  % for bar in c.sidebars:
      <div class="sidebar">
         ${bar}
      </div>
  % endfor

      <div class="content-left">

	<div class="inner-pad">
	  
	  ## Two col is still a bit bugy

	  ${next.body()}
	  
	</div>

      </div>

    </div>
% else:
    <div class="inner-pad">

      ${next.body()}

    </div>
% endif

    <div class="footer">
      <p>
	<b>
	  Copyright &copy; 
	  ${c.copyright_years}
	  ${c.copyright_owner} 
	  &lt;<a href="mailto:${c.copyright_owner_email}"
	         >${c.copyright_owner_email}</a>&gt;
	  <br/>
	  Running <a href="http://ygingras.net/gazest">Gazest</a> 
	  ${c.version}
	</b>
      </p>
    </div>

  </div>

</body>
</html>
