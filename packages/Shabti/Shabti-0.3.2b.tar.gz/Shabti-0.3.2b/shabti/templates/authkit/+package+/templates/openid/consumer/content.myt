<%method heading>Consumer</%method>

% if c.message:
<div class="<% c.css_class or 'alert' %>"><% c.message %></div>
% #end if

    <form method="get" action="<% c.base_url + h.url(controller=c.controller_name, action='passurl') %>">
    <fieldset>
      <legend>PassURL</legend>
      <table border="0">
      <tr><td>Identity&nbsp;URL</td><td><input type="text" name="passurl" value="<% c.value %>" /></td></tr>
      
      <tr><td>&nbsp;</td><td><input type="submit" value="Verify" /></td></tr>
      </table>
    </fieldset>
    </form>

    <% c.body %>
