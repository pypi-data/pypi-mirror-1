<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" 
	  "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
##<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
##    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" lang="en" xml:lang="en">
<head>
  <meta http-equiv="content-type" 
	content="text/html; charset=us-ascii" />
  <link rel="stylesheet" 
	type="text/css" 
	media="screen,projection"
	href="/css/simple.css" />

  <title>${c.title and c.title + " -"} Gazest</title>
</head>

<body>

  <div id="page-container">
    
    <%include file="nav1.mak" />

    <div class="img-header">
      <img class="img-header" src="/img/top-banner.jpg" alt="" />
    </div>

    <%include file="nav2.mak" />
    
    ## actually, a spacer
    <div class="buffer"></div>

    <%include file="msgs.mak" />

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
	  Copyright &copy; 2007 Yannick Gingras &lt;<a
	    href="mailto:ygingras@ygingras.net">ygingras@ygingras.net</a>>
	</b>
      </p>
    </div>

  </div>

</body>
</html>
