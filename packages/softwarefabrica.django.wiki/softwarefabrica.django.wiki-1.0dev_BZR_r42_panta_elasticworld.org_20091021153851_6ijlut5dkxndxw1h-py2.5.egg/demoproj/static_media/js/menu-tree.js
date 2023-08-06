function menu_toggle(obj)
{
  var li_obj;
  var ul_obj;
  var icon;
  li_obj = obj.parentNode;
  ul_obj = li_obj.parentNode;
  li_obj.className = (li_obj.className == 'menu-item-open') ? 'menu-item-closed' : 'menu-item-open';
  icon = li_obj.getElementsByTagName("img");
  if (icon && (icon[0].className == 'menu-icon')) {
    icon = icon[0];
    icon.src = (li_obj.className == 'menu-item-open') ? '/static/images/folderopen.gif' : '/static/images/folder.gif';
  }
  return false;
}
