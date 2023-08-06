<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<stl:block xmlns="http://www.w3.org/1999/xhtml" xmlns:stl="http://www.hforge.org/xml-namespaces/stl">

<form id="form_table" action=";export_to_csv" method="GET">
  <stl:block stl:repeat="param search_parameters">${param}</stl:block>

  ${batch} ${table}
  <br></br>
  <fieldset>
    <legend>Exportar a CSV</legend>
    Please select encoding:<br></br><br></br>
    <input value="oo" name="editor" type="radio" id="editor_oo" checked="on"></input>
    <label for="editor_oo"> For OpenOffice (Encoding: UTF-8, Separator: ",") </label>  <br></br>  <input value="excel" name="editor" id="editor_excel" type="radio"></input>  <label for="editor_excel"> For Excel (Encoding: CP1252, Separator: ";") </label>  <br></br><br></br>
    <input value="Exportar" class="button_ok" type="submit"></input>
  </fieldset>
</form>

</stl:block>
