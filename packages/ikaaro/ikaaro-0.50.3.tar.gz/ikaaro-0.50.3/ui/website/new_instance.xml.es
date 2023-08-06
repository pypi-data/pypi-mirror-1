<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<stl:block xmlns="http://www.w3.org/1999/xhtml" xmlns:stl="http://www.hforge.org/xml-namespaces/stl">

<form action=";new_resource?type=${class_id}" method="post">
  <fieldset>
    <legend>Agregar un nuevo ${class_title}</legend>
    <dl>
      <dt><label for="title">Title</label></dt>
      <dd>
        <input id="title" name="title" size="40" type="text"></input>
      </dd>
      <dt><label for="name">Nombre</label></dt>
      <dd>
        <input id="name" name="name" size="40" type="text"></input>
      </dd>
      <stl:block stl:if="websites">
        <dt>Choose the Web Site type</dt>
        <dd>
          <div stl:repeat="website websites">
            <input id="${website/class_id}" type="radio" name="class_id" value="${website/class_id}" checked="${website/selected}"></input>
            <img src="${website/icon}" border="0"></img>  <label for="${website/class_id}">${website/title}</label>
          </div>
        </dd>
      </stl:block>
    </dl>
    <input value="Agregar" class="button_ok" type="submit"></input>
  </fieldset>
</form>

<script type="text/javascript">
  $("#title").focus();
</script>

</stl:block>
