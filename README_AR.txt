PBIS MVP - نسخة تجريبية

1) ثبّت Python 3.10 أو أحدث.
2) فك ضغط الملف.
3) افتح مجلد PBIS_MVP في VS Code.
4) افتح Terminal داخل المجلد ونفّذ:

Windows:
py -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
streamlit run app.py

macOS/Linux:
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
streamlit run app.py

ستفتح الواجهة في المتصفح تلقائياً، غالباً على http://localhost:8501

محتويات النسخة:
- Overview dashboard
- Project delay risk demo
- Financial risk demo
- CSV data explorer/download

تنبيه مهم:
هذه نسخة تعليمية ببيانات اصطناعية ونماذج Random Forest مدربة على بيانات اصطناعية مولدة داخل الكود.
النتائج ليست تنبؤات موثوقة ولا تصلح لاتخاذ قرارات فعلية. يلزم استبدال البيانات ببيانات ممثلة والتحقق من النموذج وقياس أدائه قبل الاستخدام الحقيقي.
