<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<stl:block xmlns="http://www.w3.org/1999/xhtml" xmlns:stl="http://www.hforge.org/xml-namespaces/stl">

<div class="context_menu" stl:if="items">
  <label>${title}</label>
  <ul>
    <li stl:repeat="item items" class="${item/class}">
      <img src="${item/src}" width="16" alt="" height="16" stl:if="item/src"></img>
      <a href="${item/href}" stl:omit-tag="not item/href">${item/title}</a>
    </li>
  </ul>
</div>

</stl:block>
