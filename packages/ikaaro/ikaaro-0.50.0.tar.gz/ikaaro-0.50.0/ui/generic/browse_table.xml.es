<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<stl:block xmlns="http://www.w3.org/1999/xhtml" xmlns:stl="http://www.hforge.org/xml-namespaces/stl">

<form name="browse_list" id="form_table" action="" method="post" stl:omit-tag="not actions">
<table class="${css}" id="browse_list">
  <thead stl:if="columns">
    <tr>
      <stl:block stl:repeat="column columns">
        <!-- checkbox -->
        <th class="checkbox" stl:if="column/is_checkbox">
          <input onclick="select_checkboxes('form_table', this.checked);" title="Click to select/unselect all rows" type="checkbox"></input>
        </th>
        <!-- checkbox -->
        <th stl:if="not column/is_checkbox">
          <a href="${column/href}" class="sort_${column/order}" stl:if="column/href">${column/title}</a>  <span class="no_sort" stl:if="not column/href"> ${column/title}</span>
        </th>
      </stl:block>
    </tr>
  </thead>
  <tbody>
    <tr stl:repeat="row rows" class="${repeat/row/even}">
      <td stl:repeat="column row/columns">
        <!-- checkbox -->
        <input name="ids" checked="${column/checked}" class="checkbox" type="checkbox" value="${column/value}" stl:if="column/is_checkbox"></input>
        <!-- icon -->  <img src="${column/src}" stl:if="column/is_icon" border="0"></img>  <!-- link -->  <a stl:omit-tag="not column/href" href="${column/href}" stl:if="column/is_link">${column/value}</a>
      </td>
    </tr>
  </tbody>
</table>
<p stl:if="actions">
  <stl:block stl:repeat="action actions">
    <input onclick="${action/onclick}" type="submit" name=";${action/name}" class="${action/class}" value="${action/value}"></input>
  </stl:block>
</p>
</form>

</stl:block>
