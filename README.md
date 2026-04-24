# c2-free-google-apps-source


نظام نفق (Tunneling) وجسر افتراضي (Virtual Bridge) مبني بلغة بايثون، يسمح بربط الأجهزة وتجاوز تضارب المنافذ (Port Conflicts) من خلال وسيط سحابي (Google Apps Script).

## 🚀 المميزات
- **Dynamic Port Mapping:** يقوم بإنشاء بورت وهمي (Virtual Port) عند المنضم لتجنب تضارب البرامج.
- **Cloud Signaling:** يستخدم Google Script لتبادل بيانات الهوست والمنضم تلقائياً.
- **Full-Duplex Bridge:** نقل بيانات حقيقي ثنائي الاتجاه (TCP Forwarding).
- **Secure ID:** توليد هوية فريدة لكل مستخدم بناءً على بصمة الجهاز.

---

## 🛠️ المتطلبات
- نظام تشغيل: Linux / Windows / macOS.
- لغة برمجة: Python 3.x.
- مكتبات مطلوبة: `requests`.
# Made By BayLak
يمكنك تثبيت المكتبات عبر الأمر:
```bash
pip install requests


