var SPECIAL_DAYS = {
     0 : [ 13, 24 ],// special days in January
     2 : [ 1, 6, 8, 12, 18 ],// special days in March
     8 : [ 21, 11 ] // special days in September
};

function dateIsSpecial(year, month, day) {
  return true;
  var m = SPECIAL_DAYS[month];
  if (!m) return false;
  for (var i in m) if (m[i] == day) return true;
  return false;
};

function ourDateStatusFunc(date, y, m, d) {
  return !dateIsSpecial(y, m, d)
};

function onSelect(cal)
{
   var p = cal.params;
   var update = (cal.dateClicked || p.electric);
   if (update && p.inputField) {
     p.inputField.value = cal.date.print(p.ifFormat);
     if (typeof p.inputField.onchange == "function")
       p.inputField.onchange();
   }
   if (update && p.displayArea)
     p.displayArea.innerHTML = cal.date.print(p.daFormat);
   if (update && typeof p.onUpdate == "function")
     p.onUpdate(cal);
   if (update && p.flat) {
     if (typeof p.flatCallback == "function")
       p.flatCallback(cal);
   }
   if (update && p.singleClick && cal.dateClicked)
     cal.callCloseHandler();
   submitForm(p.displayArea);
}

function submitForm(el) {
  while (el.tagName.toLowerCase() != "form")
  {
    el = el.parentNode;
  }
  el.submit()
}
