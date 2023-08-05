<%inherit file="form_base.mako"/>


<h1>IP Addres Blocking</h1>

<form action="${h.url_for(controller='/admin', action='boycott_action')}" 
      method="post">

  <p>

    <label>
      
      IP Range (in <a
      href="http://en.wikipedia.org/wiki/Classless_Inter-Domain_Routing"
      >CIDR</a> notation):<br/>

      <input type="text" name="range_cidr" size="20" 
	     value="${c.range_cidr}"/>

    </label>

  </p>


  <p>

    <label>
      
      Duration (in days)<br/>

      <input type="text" name="nb_days" size="20" 
	     value="${c.nb_days}"/>

    </label>

  </p>


  <p>

    <label>
      
      Reason:<br/>

      <input type="text" name="reason" size="70" value=""/>

    </label>

  </p>


  <p>
    ## TODO: Implement preview mode.  The preview mode should show all
    ## the abuse reports that this ban would cover.
    <input type="submit" name="save" value="Save"/>
  </p>
  
</form>
