% for title in c.titles:
<p class="draggable" id="${unicode(title)}">
  ${title}&nbsp;[${h.link_to('visit', h.url('show_page', title=title))}]
</p>
% endfor