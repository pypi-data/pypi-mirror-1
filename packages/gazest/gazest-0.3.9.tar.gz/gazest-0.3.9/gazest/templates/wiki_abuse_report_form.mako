<%inherit file="wiki_form_base.mako"/>


<h1>Report abusive behavior</h1>

<h2>Offending edit</h2>

${h.diff_highlight(c.rev.parents()[-1], c.rev)}

<hr/>

<h2>Your report</h2>

<form action="${h.url_for(action='abuse_report_action')}" method="post">

  <p>
    
    <label>
      <input type="radio" name="problem" value="spam" /> 
	Spam      
    </label>

    <br />

    <label>
      <input type="radio" name="problem" value="vandalism" checked="checked" /> 
	Valdalism      
    </label>

    <br />

    <label>
      <input type="radio" name="problem" value="offtopic" /> 
	Off-topic content
    </label>

    <br />

    <label>
      <input type="radio" name="problem" value="other" />  
	Other (describe in the comment)
    </label>

  </p>

  <p>

    <label>
      
      Comment:<br/>

      <input type="text" name="comment" size="70" value=""/>

    </label>

  </p>


  <p>
    <input type="submit" name="report" value="Report"/>
  </p>
  
</form>
