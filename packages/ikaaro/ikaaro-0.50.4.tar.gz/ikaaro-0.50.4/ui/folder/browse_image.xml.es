<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<stl:block xmlns="http://www.w3.org/1999/xhtml" xmlns:stl="http://www.hforge.org/xml-namespaces/stl">

  <script type="text/javascript">
    $(document).ready(function() {
      var resolutions = new Array(${widths});
      apply_best_resolution(resolutions);
    });
  </script>

  <table class="${css}" id="browse_list">
    <thead stl:if="columns">
      <tr>
        <stl:block stl:repeat="column columns">
          <!-- checkbox -->
          <th class="checkbox" stl:if="column/is_checkbox">
            <label for="browse_list_select_all">Select All</label>
            <input onclick="select_checkboxes('form_table', this.checked);" id="browse_list_select_all" title="Click to select/unselect all rows" type="checkbox"></input>
          </th>
          <!-- checkbox -->
          <th stl:if="not column/is_checkbox">
            <a href="${column/href}" class="sort_${column/order}" stl:if="column/href">${column/title}</a>
          </th>
        </stl:block>
      </tr>
    </thead>
  </table>

  <form id="form_table" name="browse_list" stl:omit-tag="not actions" action="" method="post">
    <div id="browse_image">
      <a href="../;preview_content?size=${size}&amp;width=${width}&amp;height=${height}" title="Back"><img src="/ui/icons/16x16/up.png"></img></a>
      <div stl:repeat="row rows" class="thumbnail size${size}">
        <div stl:omit-tag="not row/is_folder" class="folder">
          <a href="${row/href}" stl:omit-tag="not row/href">
            <img src="${row/name}/;thumb?width=${size}&amp;height=${size}"></img>
          </a>
        </div>
        <p>
          <!-- checkbox -->
          <stl:block stl:if="row/checkbox">
            <input name="ids" checked="${row/checked}" class="checkbox" id="id_${row/id}" type="checkbox" value="${row/id}"></input>
            <label for="id_${row/id}" class="wf_${row/workflow_statename}">${row/title_or_name}</label>
          </stl:block>
          <stl:block stl:if="not row/checkbox">
            <label>${row/title_or_name}</label>
          </stl:block>
        </p>
      </div>
    </div>
    <p stl:if="actions">
      <stl:block stl:repeat="action actions">
        <input value="${action/value}" type="submit" name=";${action/name}" class="${action/class}" onclick="${action/onclick}"></input>
      </stl:block>
    </p>
  </form>

</stl:block>
