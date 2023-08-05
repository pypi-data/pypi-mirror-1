<div xmlns:py="http://purl.org/kid/ns#">
  <table id="${name}" class="grid" cellpadding="0" cellspacing="1" border="0">
    <thead py:if="columns">
      <tr> 
          <th py:if="show_actions">&nbsp;</th>
          <th py:for="col in columns">${col.title}</th>
      </tr>
    </thead>
    <tr py:for="i, row in enumerate(value)" class="${i%2 and 'odd' or 'even'}">
      <td py:if="show_actions">
        <a href="${get_edit_url(row)}">
          <img src="${tg.tg_static}/images/edit.png" border="0"/>
        </a>
        <a href="${get_delete_url(row)}" onclick="return confirm('${delete_link_msg}')">
          <img src="${tg.tg_static}/images/remove.png" border="0"/>
        </a>
      </td>
      <td py:for="col in columns">
        ${col.get_field(row)}
      </td>
    </tr>
  </table>
  <p py:if="show_add_link">
  <a href="${get_add_url()}" style="text-decoration:none"><img
    src="${tg.tg_static}/images/add.png" 
    border="0"/>${add_link_title}</a></p>
</div>

