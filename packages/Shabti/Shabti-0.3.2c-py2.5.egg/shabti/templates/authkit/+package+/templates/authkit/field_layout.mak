    <div style="clear: both">
          <label style="float: left; width: 150px;" for="${c.name}">${c.caption}</label>
          ${getattr(c.form.field, c.field)(name=c.name, class_="txt", id=c.name, **c.params)} 
          ${c.form.get_error(c.name, format='<br /><span style="margin-left: 150px;"  class="bad">%s</span><br /><br />')}
    </div>