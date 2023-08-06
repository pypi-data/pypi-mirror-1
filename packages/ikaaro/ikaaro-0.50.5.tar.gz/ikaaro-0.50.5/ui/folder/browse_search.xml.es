<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<stl:block xmlns="http://www.w3.org/1999/xhtml" xmlns:stl="http://www.hforge.org/xml-namespaces/stl">

<form action="" method="get" stl:if="search_fields">
  <fieldset>
    <legend>Buscar</legend>
    <!-- Field -->
    <select name="search_field">
      <option value="${field/name}" selected="${field/selected}" stl:repeat="field search_fields">${field/title}</option>
    </select>
    <!-- Term -->
    <input value="${search_term}" name="search_term" size="35" type="text"></input>
    <!-- SubFolders -->   <input name="search_subfolders" type="checkbox" id="search_subfolders" value="1" checked="${search_subfolders}"></input><label for="search_subfolders">Search subfolders</label>  <!-- OK -->    
    <input value="Aceptar" class="button_search" type="submit"></input>
  </fieldset>
</form>

</stl:block>
