<%inherit file="/base.mako"/>\

<%def name="header()">Title List</%def>

<%def name="jscript()">
    <script type="text/javascript" src='http://ui.jquery.com/testing/jquery-1.3.1.js'></script>
    <script type="text/javascript" src='http://ui.jquery.com/testing/ui/ui.core.js'></script>
    <script type="text/javascript" src='http://ui.jquery.com/testing/ui/ui.draggable.js'></script>
    <script type="text/javascript" src='http://ui.jquery.com/testing/ui/ui.droppable.js'></script>
    <script type="text/javascript">
    $(document).ready(function(){
        $(".draggable").draggable();
        $("#droppable").droppable({
            drop: function(event, ui) { 
                $.ajax({
                    url: '/pages/delete/'+ui.draggable.context.id,
                    type: 'DELETE',
                    success: function(response) {ui.draggable.remove()},
                    error: function(xhr) {alert('Error!  Status = ' + xhr.status)}
                });
            }
        });
    });
    </script>
</%def>

<div id="droppable">
    Delete a page by dragging its title here
</div>


<%include file="list-titles.mako"/>
