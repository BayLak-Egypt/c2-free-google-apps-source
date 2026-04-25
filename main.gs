var cache = CacheService.getScriptCache();

function doPost(e) {
  var d = JSON.parse(e.postData.contents);
  var group = d.group;
  var role = d.role;
  var sid = d.sid || "default";
  var payload = d.payload || "";

  var key_h2j = group + "_" + sid + "_h2j";
  var key_j2h = group + "_" + sid + "_j2h";

  if (role == "HOST") {
    if (payload !== "") cache.put(key_h2j, payload, 60);
    
    // محاولة القراءة لمدة 4 ثوانٍ قبل الاستسلام (Long Polling)
    for (var i = 0; i < 4; i++) {
      var data = cache.get(key_j2h);
      if (data) {
        cache.remove(key_j2h);
        return ContentService.createTextOutput(JSON.stringify({data: data})).setMimeType(ContentService.MimeType.JSON);
      }
      Utilities.sleep(1000); // انتظر ثانية وحاول مجدداً
    }
  } else {
    if (payload !== "") cache.put(key_j2h, payload, 60);
    
    for (var i = 0; i < 4; i++) {
      var data = cache.get(key_h2j);
      if (data) {
        cache.remove(key_h2j);
        return ContentService.createTextOutput(JSON.stringify({data: data})).setMimeType(ContentService.MimeType.JSON);
      }
      Utilities.sleep(1000);
    }
  }
  return ContentService.createTextOutput(JSON.stringify({data: ""})).setMimeType(ContentService.MimeType.JSON);
}
