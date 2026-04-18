from flask import Flask, request, jsonify, render_template_string, session
from sentence_transformers import SentenceTransformer, util
import re

app = Flask(__name__)
app.secret_key = 'your_secret_key_here_change_it'

print("🔧 جاري تحميل نموذج الذكاء الاصطناعي...")
model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
print("✓ النموذج جاهز")

# ======================== اللائحة الكاملة ========================
# الدرجة الأولى
first_degree_violations = [
    {"id": 1, "violation": "تفحيط بمركبة حكومية بداعي القصد", "punishment": "ثلاث محاضر عسكرية", "level": "الدرجة الأولى", 
     "original_text": "تفحيط بمركبة حكومية بداعي القصد ( ثلاث مـــحـــاضـــر عـــســـكريــة ) -1"},
    {"id": 2, "violation": "قتل رجل امن دون قصد", "punishment": "ثلاث محاضر عسكرية", "level": "الدرجة الأولى", 
     "original_text": "قتل رجل امن - دون قصد ( ثلاث مـــحـــاضـــر عـــســـكريــة ) -2"},
    {"id": 3, "violation": "قتل رجل امن بداعي القصد", "punishment": "فصل من السلك العسكري", "level": "الدرجة الأولى", 
     "original_text": "قتل رجل امن - بداعي القصد ( فــــصـــل مــن الـــســلك الــعـــســكري ) -3"},
    {"id": 4, "violation": "حمل ممنوعات دون تسليمها", "punishment": "ثلاث محاضر عسكرية", "level": "الدرجة الأولى", 
     "original_text": "حمل ممنوعات دون تلسيمها ( ثلاث مـــحـــاضـــر عـــســـكريــة ) -4"},
    {"id": 5, "violation": "اظهار الشخصيه والتشبه بالنساء", "punishment": "ثلاث محاضر عسكرية - معرض للفصل", "level": "الدرجة الأولى", 
     "original_text": "اظهار الشخصيه ب اي شكل من الاشكال التي توحي بالتشبة بالنساء ( ثلاث مـــحـــاضـــر عـــســـكريــة - معرض للفصل) -5"},
    {"id": 6, "violation": "الهروب من محاسبة عسكرية واضحة", "punishment": "ثلاث محاضر عسكرية او باند ساعتين", "level": "الدرجة الأولى", 
     "original_text": "الهروب من محاسبة عسكرية واضحه ( ثلاث محاضر عسكرية ) او ( باند ساعتين ) -6"},
    {"id": 7, "violation": "التعدي على الضباط بالضرب او الصفع او القتل", "punishment": "ثلاث محاضر عسكرية او باند ساعتين", "level": "الدرجة الأولى", 
     "original_text": "التعدي على الضباط داخل الميدان بالضرب او الصفع او القتل ( ثلاث محاضر عسكرية ) او ( باند ساعتين ) -7"},
    {"id": 8, "violation": "استعمال الصلاحيات العسكرية بشكل خاطئ", "punishment": "ثلاث محاضر عسكرية - معرض للفصل", "level": "الدرجة الأولى", 
     "original_text": "استعمال الصلاحيات العسكرية بشكل خاطئ ( ثلاث محاضر عسكرية - معرض للفصل) -8"},
    {"id": 9, "violation": "الفساد العسكري", "punishment": "فصل عسكري", "level": "الدرجة الأولى", 
     "original_text": "الفساد العسكري بجميع اشكالة { رشوة , تسريب معلومات ... الخ } ( فصل عسكري ) -9"},
    {"id": 10, "violation": "الشتم داخل الموجة", "punishment": "باند ساعتين - معرض للفصل", "level": "الدرجة الأولى", 
     "original_text": "الشتم داخل الموجة ( باند ساعتين - معرض للفصل ) -10"},
    {"id": 11, "violation": "القذف داخل الموجة او الميدان", "punishment": "باند نهائي", "level": "الدرجة الأولى", 
     "original_text": "القذف داخل الموجة ~ داخل الميدان ( باند نهائي ) -11"},
    {"id": 12, "violation": "استعمال ثغرات او مواد الغش", "punishment": "باند نهائي", "level": "الدرجة الأولى", 
     "original_text": "استعمال ثغرات او مواد الغش بأي شكل من الاشكال ( باند نهائي ) -12"},
    {"id": 13, "violation": "انتحال شخصية ضابط", "punishment": "باند نهائي", "level": "الدرجة الأولى", 
     "original_text": "انتحال شخصية ضابط ( باند نهائي ) -13"},
    {"id": 14, "violation": "تكرار مخالفة من الدرجة الثانية", "punishment": "محضر عسكري ثالث - باند ساعتين - فصل", "level": "الدرجة الأولى", 
     "original_text": "تكرار مخالفة تصنف من الدرجة الثانية بعد ان تم محسابته بمحضر عسكري اول وثاني"},
]

# الدرجة الثانية
second_degree_violations = [
    {"id": 15, "violation": "التفحيط بالمركبة الحكومية بغير قصد", "punishment": "محضر عسكري اول وثاني", "level": "الدرجة الثانية", 
     "original_text": "التفحيط بالمركبة الحكومية ( بغير قصد ) -1"},
    {"id": 16, "violation": "عدم الانصياع لاوامر المسؤول", "punishment": "محضر عسكري", "level": "الدرجة الثانية", 
     "original_text": "عدم الانصياع لاوامر المسؤول اكثر من مره -2"},
    {"id": 17, "violation": "عدم الالتزام بالبروتوكولات والضوابط", "punishment": "محضر عسكري", "level": "الدرجة الثانية", 
     "original_text": "عدم الالتزام بالبروتوكولات والضوابط داخل الموجه -3"},
    {"id": 18, "violation": "عدم اخذ المهنة بجدية (استهبال)", "punishment": "محضر عسكري", "level": "الدرجة الثانية", 
     "original_text": "عدم اخذ المهنه بجديه ( استهبال ) -4"},
    {"id": 19, "violation": "عدم وضع مسمى عسكري او الرقم العسكري", "punishment": "محضر عسكري مع التنويه", "level": "الدرجة الثانية", 
     "original_text": "عدم وضع مسمى عسكري واضح داخل الموجه ويندرج تحت ذلك عدم ذكر الجهه الادارية ( القطاع ) عدم وضع الرقم العسكري ( الكود ) مع اشتراط التنويه -5"},
    {"id": 20, "violation": "الكتابة بالشات اثناء المنع", "punishment": "محضر عسكري", "level": "الدرجة الثانية", 
     "original_text": "الكتابه بالشات اثناء المنع -6"},
    {"id": 21, "violation": "التنقيط وكتابة حروف مالها معنى", "punishment": "محضر عسكري", "level": "الدرجة الثانية", 
     "original_text": "التنقيط و كتابة احرف مالها اي معنى مثال ( ب - م - ل - ا ) و كتابة الارقام التي لاتشير الى اي معنى داخل الشات الرسمي للقطاع -7"},
    {"id": 22, "violation": "استخراج مركبات الضباط", "punishment": "محضر عسكري", "level": "الدرجة الثانية", 
     "original_text": "استخراج مركبات ضباط بجميع انواعها او مسؤولي الافراد -8"},
    {"id": 23, "violation": "الجدال داخل الشاتات الرسمية", "punishment": "محضر عسكري", "level": "الدرجة الثانية", 
     "original_text": "الجدال داخل الشاتات الرسمية للقطاع -9"},
    {"id": 24, "violation": "عدم احترام الزملاء داخل الميدان", "punishment": "محضر عسكري", "level": "الدرجة الثانية", 
     "original_text": "عدم احترام الزملاء داخل الميدان -10"},
    {"id": 25, "violation": "الجدال مع ضابط وعدم التنفيذ", "punishment": "محضر عسكري", "level": "الدرجة الثانية", 
     "original_text": "الجدال مع ضابط وعدم التنفيذ -11"},
    {"id": 26, "violation": "تسجيل دخول وعدم تواجد", "punishment": "محضر عسكري مع التنويه", "level": "الدرجة الثانية", 
     "original_text": "تسجيل دخول وعدم تواجد ( داخل التردد ) ( داخل الموجه ) مع اشتراط التنويه -12"},
    {"id": 27, "violation": "التلاعب بدفتر الحضور", "punishment": "محضر عسكري", "level": "الدرجة الثانية", 
     "original_text": "التلاعب بدفتر الحضور -13"},
    {"id": 28, "violation": "مخالفة التعميمات الرسمية", "punishment": "محضر عسكري", "level": "الدرجة الثانية", 
     "original_text": "مخالفه التعميمات الرسمية ( بشكل عام ) -14"},
    {"id": 29, "violation": "حمل سلاح مواطن", "punishment": "محضر عسكري", "level": "الدرجة الثانية", 
     "original_text": "حمل سلاح مواطن -15"},
    {"id": 30, "violation": "المباشرة في حالة جنائية", "punishment": "محضر عسكري مع التنويه", "level": "الدرجة الثانية", 
     "original_text": "المباشره في حالة جنائية - مع اشتراط التنويه -16"},
    {"id": 31, "violation": "تكرار مخالفة من الدرجة الثالثة", "punishment": "سجن عسكري", "level": "الدرجة الثانية", 
     "original_text": "تكرار ارتكاب مخالفة تصنف من الدرجة الثالثه بعد ان تم تحذيره شفويا , سجنه عسكريا"},
]

# الدرجة الثالثة - الميدانية
third_degree_field = [
    {"id": 32, "violation": "تظليل المركبة بما يخالف الانظمة", "punishment": "تحذير شفوي اول مرة ثم سجن 10-15 يوم", "level": "الدرجة الثالثة", 
     "original_text": "تظليل المركبة بما يخالف الانظمة ( 01 - 02 - 03 - كتم ) -1"},
    {"id": 33, "violation": "قطع الاشارات المرورية", "punishment": "تحذير شفوي اول مرة ثم سجن 10-15 يوم", "level": "الدرجة الثالثة", 
     "original_text": "قطع الاشارات المرورية ومخالفة انظمة السير -2"},
    {"id": 34, "violation": "التدخل في حالة عسكري اخر دون داعي", "punishment": "تحذير شفوي اول مرة ثم سجن 10-15 يوم", "level": "الدرجة الثالثة", 
     "original_text": "التدخل في حالة عسكري اخر دون داعي , او دون بلاغ اسناد امني -3"},
    {"id": 35, "violation": "التعدي على الزملاء بالضرب او الصفع", "punishment": "تحذير شفوي اول مرة ثم سجن 10-15 يوم", "level": "الدرجة الثالثة", 
     "original_text": "التعدي على الزملاء داخل الميدان بالضرب او الصفع -4"},
    {"id": 36, "violation": "عدم تنفيذ الإيعاز العسكري", "punishment": "تحذير شفوي اول مرة ثم سجن 10-15 يوم", "level": "الدرجة الثالثة", 
     "original_text": "عدم تفيذ الإيعاز العسكري بالشكل الصحيح -5"},
    {"id": 37, "violation": "التحدث اثناء الثبات", "punishment": "تحذير شفوي اول مرة ثم سجن 10-15 يوم", "level": "الدرجة الثالثة", 
     "original_text": "التحدث اثناء الثبات -6"},
    {"id": 38, "violation": "القيادة الغير واقعية", "punishment": "تحذير شفوي اول مرة ثم سجن 10-15 يوم", "level": "الدرجة الثالثة", 
     "original_text": "القيادة الغير واقعيه -7"},
    {"id": 39, "violation": "عدم دخول الموجه", "punishment": "تحذير شفوي اول مرة ثم سجن 10-15 يوم", "level": "الدرجة الثالثة", 
     "original_text": "عدم دخول الموجه -8"},
    {"id": 40, "violation": "تشغيل الطواري دون وجود حالة", "punishment": "تحذير شفوي اول مرة ثم سجن 10-15 يوم", "level": "الدرجة الثالثة", 
     "original_text": "تشغيل الونان ( الطواري ) دون وجود حاله -9"},
    {"id": 41, "violation": "عدم تسجيل الرقم العسكري على اللوحة", "punishment": "تحذير شفوي اول مرة ثم سجن 10-15 يوم", "level": "الدرجة الثالثة", 
     "original_text": "عدم تسجيل الرقم العسكري على اللوحه -10"},
    {"id": 42, "violation": "الخروج بدورية مشتركة دون اذن", "punishment": "تحذير شفوي اول مرة ثم سجن 10-15 يوم", "level": "الدرجة الثالثة", 
     "original_text": "الخروج في دورية مشتركة دون اخذذ اذن من مركز العمليات -11"},
]

# الدرجة الثالثة - القيافة العسكرية (11 مخالفة)
third_degree_kiyafa = [
    {"id": 43, "violation": "نزول الميدان دون وضع اللبس الرسمي التابع للقطاع", "punishment": "تحذير شفوي اول مرة ثم سجن 10-15 يوم", "level": "الدرجة الثالثة", 
     "original_text": "نزول الميدان دون وضع اللبس الرسمي التابع للقطاع -1"},
    {"id": 44, "violation": "خروجك في وردية رسمية دون لبس البريهه العسكرية", "punishment": "تحذير شفوي اول مرة ثم سجن 10-15 يوم", "level": "الدرجة الثالثة", 
     "original_text": "خروجك في وردية رسمية دون لبس البريهه العسكرية -2"},
    {"id": 45, "violation": "وضع البريهه العسكرية بشكل خاطئ", "punishment": "تحذير شفوي اول مرة ثم سجن 10-15 يوم", "level": "الدرجة الثالثة", 
     "original_text": "وضع البريهه العسكرية بشكل خاطئ من ما يظهر انعدام الاحترافية داخل الميدان -3"},
    {"id": 46, "violation": "وضع جيب سلاح عسكري ( جراب الفرد ) في الفخذ", "punishment": "تحذير شفوي اول مرة ثم سجن 10-15 يوم", "level": "الدرجة الثالثة", 
     "original_text": "وضع جيب سلاح عسكري ( جراب الفرد ) في الفخذ -4"},
    {"id": 47, "violation": "ان يضع الفرد وسام دورة ( وينق ) لايمتلكها", "punishment": "تحذير شفوي اول مرة ثم سجن 10-15 يوم", "level": "الدرجة الثالثة", 
     "original_text": "ان يضع الفرد وسام دورة ( وينق ) لايمتلكها -5"},
    {"id": 48, "violation": "لبس البريهه المخصصه للضباط", "punishment": "تحذير شفوي اول مرة ثم سجن 10-15 يوم", "level": "الدرجة الثالثة", 
     "original_text": "لبس البريهه المخصصه للضباط -6"},
    {"id": 49, "violation": "لبس الاكسسوارات والنظارات والستره في الاصطفافات العسكرية", "punishment": "تحذير شفوي اول مرة ثم سجن 10-15 يوم", "level": "الدرجة الثالثة", 
     "original_text": "لبس الاكسسوارات والنظارات والستره في الاصطفافات العسكرية -7"},
    {"id": 50, "violation": "وضع محظورات على الوجه ( ميك اب , وشم , صبغ )", "punishment": "تحذير شفوي اول مرة ثم سجن 10-15 يوم", "level": "الدرجة الثالثة", 
     "original_text": "وضع محظورات على الوجه ( ميك اب , وشم , صبغ ) -8"},
    {"id": 51, "violation": "تعديل لون العيون", "punishment": "تحذير شفوي اول مرة ثم سجن 10-15 يوم", "level": "الدرجة الثالثة", 
     "original_text": "تعديل لون العيون -9"},
    {"id": 52, "violation": "وضع شعر كامل الراس ( محظور على جندي , جندي اول , عريف )", "punishment": "تحذير شفوي اول مرة ثم سجن 10-15 يوم", "level": "الدرجة الثالثة", 
     "original_text": "وضع شعر كامل الراس ( محظور على جندي , جندي اول , عريف ) -10"},
    {"id": 53, "violation": "عدم الالتزام بالواقعية وزرع ( شعر حاجب , شنب او لحية )", "punishment": "تحذير شفوي اول مرة ثم سجن 10-15 يوم", "level": "الدرجة الثالثة", 
     "original_text": "عدم الالتزام بالواقعية وزرع ( شعر حاجب , شنب او لحية ) -11"},
]

# الدرجة الثالثة - داخل الموجه
third_degree_inside = [
    {"id": 54, "violation": "عدم الالتزام بالتوجيه", "punishment": "تحذير شفوي اول مرة ثم سجن 10-15 يوم", "level": "الدرجة الثالثة", 
     "original_text": "عدم الالتزام بالتوجية -1"},
    {"id": 55, "violation": "عدم التوجه الى اصطفاف", "punishment": "تحذير شفوي اول مرة ثم سجن 10-15 يوم", "level": "الدرجة الثالثة", 
     "original_text": "عدم التوجه الى اصطفاف -2"},
    {"id": 56, "violation": "عدم الالتزام بالطريقة الرسمية لرفع البلاغ", "punishment": "تحذير شفوي اول مرة ثم سجن 10-15 يوم", "level": "الدرجة الثالثة", 
     "original_text": "عدم الالتزام بالطريقة الرسمية لرفع البلاغ -3"},
]

# دمج كل المخالفات للبحث
all_laws = (first_degree_violations + second_degree_violations + 
            third_degree_field + third_degree_kiyafa + third_degree_inside)

# ======================== دالة البحث ========================
def find_punishments_ai(user_query):
    """البحث بالذكاء الاصطناعي"""
    results = []
    user_query_lower = user_query.lower()
    
    # البحث عن قيافة - يطلع كل مخالفات القيافة الـ 11 كاملة
    if "قيافة" in user_query_lower or "القيافة" in user_query_lower:
        for law in third_degree_kiyafa:
            results.append({"type": "law", "data": law, "score": 0.95})
        return results
    
    # البحث العادي في المخالفات
    law_texts = [law["violation"] for law in all_laws]
    law_embeddings = model.encode(law_texts, convert_to_tensor=True)
    query_embedding = model.encode(user_query, convert_to_tensor=True)
    semantic_scores = util.cos_sim(query_embedding, law_embeddings)[0]
    
    for idx, score in enumerate(semantic_scores):
        score_value = score.item()
        if score_value >= 0.45:
            results.append({"type": "law", "data": all_laws[idx], "score": score_value})
    
    # إزالة التكرارات
    seen_ids = set()
    unique_results = []
    for r in results:
        if r["data"]["id"] not in seen_ids:
            seen_ids.add(r["data"]["id"])
            unique_results.append(r)
    
    unique_results.sort(key=lambda x: x["score"], reverse=True)
    return unique_results[:5]

# ======================== واجهة تسجيل الدخول ========================
login_html = """
<!DOCTYPE html>
<html lang="ar">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>تسجيل الدخول - الشرطة العسكرية الخاصة</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            background: linear-gradient(135deg, #dc2626, #991b1b);
            font-family: 'Tajawal', 'Segoe UI', system-ui, sans-serif;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .login-card {
            background: white;
            padding: 40px;
            border-radius: 24px;
            box-shadow: 0 25px 50px -12px rgba(0,0,0,0.25);
            width: 100%;
            max-width: 400px;
            text-align: center;
        }
        h1 { color: #dc2626; margin-bottom: 10px; font-size: 1.8rem; }
        .sub { color: #6b7280; margin-bottom: 30px; font-size: 0.9rem; }
        input {
            width: 100%;
            padding: 14px 16px;
            margin: 10px 0;
            border: 2px solid #e5e7eb;
            border-radius: 12px;
            font-size: 1rem;
            font-family: inherit;
            transition: all 0.2s;
        }
        input:focus {
            outline: none;
            border-color: #dc2626;
            box-shadow: 0 0 0 3px rgba(220,38,38,0.1);
        }
        button {
            width: 100%;
            background: #dc2626;
            color: white;
            border: none;
            padding: 14px;
            border-radius: 12px;
            font-size: 1rem;
            font-weight: bold;
            cursor: pointer;
            margin-top: 20px;
            transition: all 0.2s;
        }
        button:hover { background: #b91c1c; transform: translateY(-2px); }
        .error { color: #dc2626; margin-top: 15px; font-size: 0.85rem; }
    </style>
</head>
<body>
    <div class="login-card">
        <h1>⚖️ الشرطة العسكرية الخاصة</h1>
        <div class="sub">نظام العقوبات العسكرية</div>
        <form method="POST">
            <input type="text" name="username" placeholder="اسم المستخدم" autocomplete="off">
            <input type="password" name="password" placeholder="كلمة المرور">
            <button type="submit">دخول</button>
        </form>
        {% if error %}
        <div class="error">❌ {{ error }}</div>
        {% endif %}
    </div>
</body>
</html>
"""

# ======================== الواجهة الرئيسية ========================
main_html = """
<!DOCTYPE html>
<html lang="ar">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>الشرطة العسكرية الخاصة - نظام العقوبات</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        :root {
            --bg-gradient-start: #fef2f2;
            --bg-gradient-end: #ffffff;
            --card-bg: white;
            --text-primary: #374151;
            --text-secondary: #6b7280;
            --border-color: #fee2e2;
            --result-bg: #fef2f2;
            --header-bg: white;
            --tab-active: #dc2626;
            --tab-inactive: #9ca3af;
        }
        
        body.dark {
            --bg-gradient-start: #0f0f0f;
            --bg-gradient-end: #1a1a1a;
            --card-bg: #1e1e1e;
            --text-primary: #e5e5e5;
            --text-secondary: #9ca3af;
            --border-color: #333333;
            --result-bg: #2a2a2a;
            --header-bg: #1e1e1e;
            --tab-active: #ef4444;
            --tab-inactive: #6b7280;
        }
        
        body {
            background: linear-gradient(135deg, var(--bg-gradient-start) 0%, var(--bg-gradient-end) 100%);
            font-family: 'Tajawal', 'Segoe UI', system-ui, sans-serif;
            min-height: 100vh;
            transition: all 0.3s ease;
        }
        
        /* Modal Overlay */
        .modal-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(135deg, #1a472a, #0d2818);
            z-index: 9999;
            display: flex;
            justify-content: center;
            align-items: center;
            animation: fadeIn 0.5s ease;
            cursor: pointer;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        
        @keyframes pulse {
            0%, 100% { transform: scale(1); opacity: 1; }
            50% { transform: scale(1.05); opacity: 0.9; }
        }
        
        .modal-content {
            text-align: center;
            animation: pulse 1.5s infinite;
        }
        
        .modal-message {
            font-size: 4rem;
            font-weight: bold;
            color: #ffd700;
            text-shadow: 0 0 20px rgba(255,215,0,0.5);
            margin-bottom: 30px;
            line-height: 1.5;
        }
        
        .modal-submessage {
            font-size: 1.5rem;
            color: white;
            margin-bottom: 40px;
        }
        
        .modal-skip {
            background: #ffd700;
            color: #1a472a;
            border: none;
            padding: 12px 30px;
            border-radius: 50px;
            font-size: 1.2rem;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .modal-skip:hover {
            transform: scale(1.05);
            background: #ffed4a;
        }
        
        .container { max-width: 1400px; margin: 0 auto; padding: 20px; display: flex; gap: 25px; flex-wrap: wrap; }
        .main-content { flex: 2; min-width: 300px; }
        
        /* Theme Toggle */
        .theme-toggle {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 50px;
            padding: 10px 20px;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 8px;
            z-index: 1000;
            font-size: 0.9rem;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
        }
        
        .theme-toggle:hover { transform: scale(1.05); }
        
        /* Tabs */
        .tabs {
            display: flex;
            gap: 5px;
            background: var(--card-bg);
            border-radius: 16px;
            padding: 8px;
            margin-bottom: 25px;
            border: 1px solid var(--border-color);
            flex-wrap: wrap;
        }
        
        .tab {
            flex: 1;
            padding: 12px 20px;
            text-align: center;
            cursor: pointer;
            border-radius: 12px;
            font-weight: bold;
            transition: all 0.3s ease;
            color: var(--tab-inactive);
            background: transparent;
        }
        
        .tab.active {
            background: var(--tab-active);
            color: white;
        }
        
        .tab:hover:not(.active) {
            background: var(--result-bg);
            color: var(--tab-active);
        }
        
        /* Tab Content - Hidden by default, shown when active */
        .tab-content {
            display: none;
        }
        
        .tab-content.active {
            display: block;
            animation: fadeInContent 0.3s ease;
        }
        
        @keyframes fadeInContent {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .violations-list {
            display: flex;
            flex-direction: column;
            gap: 12px;
        }
        
        .violation-item {
            background: var(--result-bg);
            border-radius: 16px;
            padding: 15px;
            border-right: 4px solid #dc2626;
        }
        
        .violation-text {
            font-size: 1rem;
            color: var(--text-primary);
            margin-bottom: 8px;
        }
        
        .punishment-text {
            font-size: 0.9rem;
            font-weight: bold;
            color: #dc2626;
        }
        
        .section-title {
            font-size: 1.2rem;
            font-weight: bold;
            color: var(--text-primary);
            margin: 20px 0 10px 0;
            padding-bottom: 10px;
            border-bottom: 2px solid var(--border-color);
        }
        
        .under-construction {
            text-align: center;
            padding: 60px 20px;
            background: var(--result-bg);
            border-radius: 16px;
        }
        
        .under-construction h2 {
            font-size: 2rem;
            color: #dc2626;
            margin-bottom: 15px;
        }
        
        .under-construction p {
            font-size: 1.2rem;
            color: var(--text-secondary);
        }
        
        .saved-section {
            flex: 1;
            min-width: 280px;
            background: var(--card-bg);
            border-radius: 24px;
            padding: 20px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
            border: 1px solid var(--border-color);
            height: fit-content;
            position: sticky;
            top: 20px;
        }
        
        .saved-title {
            font-size: 1.3rem;
            font-weight: bold;
            color: #dc2626;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid var(--border-color);
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .saved-list { max-height: 500px; overflow-y: auto; }
        
        .saved-item {
            background: var(--result-bg);
            padding: 12px;
            border-radius: 12px;
            margin-bottom: 10px;
            font-size: 0.85rem;
            border-right: 3px solid #dc2626;
            cursor: pointer;
            transition: all 0.2s;
            color: var(--text-primary);
        }
        
        .saved-item:hover { background: #fee2e2; transform: translateX(-5px); }
        .saved-item .saved-pun { font-weight: bold; color: #dc2626; margin-top: 5px; font-size: 0.8rem; }
        
        .clear-btn {
            background: #dc2626;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 12px;
            cursor: pointer;
            margin-top: 15px;
            width: 100%;
            font-size: 0.8rem;
        }
        
        .clear-btn:hover { background: #b91c1c; }
        
        .header {
            background: var(--header-bg);
            padding: 25px 30px;
            border-radius: 24px;
            margin-bottom: 25px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.05);
            border: 1px solid var(--border-color);
            text-align: center;
        }
        
        .main-title {
            font-size: 2.5rem;
            font-weight: bold;
            color: #dc2626;
            margin-bottom: 10px;
            letter-spacing: -1px;
        }
        
        .subtitle {
            color: var(--text-secondary);
            font-size: 0.9rem;
            margin-bottom: 15px;
        }
        
        .search-card {
            background: var(--card-bg);
            border-radius: 24px;
            padding: 25px;
            margin-bottom: 25px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.05);
            border: 1px solid var(--border-color);
        }
        
        .input-group { display: flex; gap: 15px; flex-wrap: wrap; }
        
        .search-input {
            flex: 1;
            background: var(--result-bg);
            border: 2px solid var(--border-color);
            border-radius: 16px;
            padding: 16px 20px;
            font-size: 1rem;
            font-family: inherit;
            transition: all 0.3s ease;
            color: var(--text-primary);
        }
        
        .search-input:focus {
            outline: none;
            border-color: #dc2626;
            box-shadow: 0 0 0 3px rgba(220,38,38,0.1);
        }
        
        .search-input::placeholder { color: var(--text-secondary); }
        
        .search-btn {
            background: #dc2626;
            border: none;
            border-radius: 16px;
            padding: 16px 32px;
            font-size: 1rem;
            font-weight: bold;
            color: white;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        
        .search-btn:hover { background: #b91c1c; transform: translateY(-2px); }
        
        .results-area {
            background: var(--card-bg);
            border-radius: 24px;
            padding: 25px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.05);
            border: 1px solid var(--border-color);
        }
        
        .result-card {
            background: var(--result-bg);
            border-radius: 16px;
            padding: 20px;
            margin-bottom: 15px;
            border-right: 4px solid #dc2626;
            transition: all 0.2s;
        }
        
        .level-badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.7rem;
            font-weight: bold;
            margin-bottom: 12px;
        }
        .level-1 { background: #dc2626; color: white; }
        .level-2 { background: #ea580c; color: white; }
        .level-3 { background: #ca8a04; color: white; }
        
        .original-text {
            background: var(--card-bg);
            padding: 12px;
            border-radius: 12px;
            font-size: 0.9rem;
            color: var(--text-primary);
            margin-bottom: 12px;
            font-family: monospace;
            border: 1px solid var(--border-color);
        }
        
        .punishment-display {
            font-size: 1.2rem;
            font-weight: bold;
            color: #dc2626;
            margin: 10px 0;
        }
        
        .save-btn {
            background: #dc2626;
            color: white;
            border: none;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 0.7rem;
            cursor: pointer;
            margin-top: 10px;
            transition: all 0.2s;
        }
        
        .save-btn:hover { background: #b91c1c; transform: scale(0.95); }
        
        .footer {
            text-align: right;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid var(--border-color);
            color: var(--text-secondary);
            font-size: 0.8rem;
        }
        
        .loading { text-align: center; padding: 40px; color: var(--text-secondary); }
        @keyframes spin { to { transform: rotate(360deg); } }
        .loading::after {
            content: '';
            display: inline-block;
            width: 20px;
            height: 20px;
            margin-left: 10px;
            border: 2px solid #dc2626;
            border-top-color: transparent;
            border-radius: 50%;
            animation: spin 0.6s linear infinite;
        }
        
        .result-count {
            font-size: 0.85rem;
            color: var(--text-secondary);
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 1px solid var(--border-color);
        }
        
        @media (max-width: 900px) {
            .container { flex-direction: column; }
            .saved-section { position: static; }
            .main-title { font-size: 1.8rem; }
            .modal-message { font-size: 2rem; }
            .tabs { flex-direction: column; }
        }
    </style>
</head>
<body>
<div id="modalOverlay" class="modal-overlay" style="display: none;">
    <div class="modal-content">
        <div class="modal-message" id="modalMessage"></div>
        <div class="modal-submessage">رسالة من فيصل الهاشمي</div>
        <button class="modal-skip" onclick="closeModal()">جزاك الله خير</button>
    </div>
</div>

<div class="theme-toggle" id="themeToggle">
    <span>🌙</span> <span id="themeText">داكن</span>
</div>

<div class="container">
    <div class="main-content">
        <div class="header">
            <div class="main-title">⚖️ الشرطة العسكرية الخاصة</div>
            <div class="subtitle">نظام لتسهيل معرفة المخالفات للشرطة العسكرية الخاصة . صنع بواسطة فيصل الهاشمي</div>
        </div>

        <!-- Tabs -->
        <div class="tabs">
            <div class="tab" data-tab="first">📌 الدرجة الأولى</div>
            <div class="tab" data-tab="second">📌 الدرجة الثانية</div>
            <div class="tab" data-tab="third">📌 الدرجة الثالثة</div>
            <div class="tab" data-tab="construction">⏳ قيد الإنشاء</div>
        </div>

        <!-- Tab Content: الدرجة الأولى -->
        <div id="tab-first" class="tab-content">
            <div class="violations-list">
                {% for v in first_degree %}
                <div class="violation-item">
                    <div class="violation-text">📜 {{ v.original_text }}</div>
                    <div class="punishment-text">⚖️ العقوبة: {{ v.punishment }}</div>
                </div>
                {% endfor %}
            </div>
        </div>

        <!-- Tab Content: الدرجة الثانية -->
        <div id="tab-second" class="tab-content">
            <div class="violations-list">
                {% for v in second_degree %}
                <div class="violation-item">
                    <div class="violation-text">📜 {{ v.original_text }}</div>
                    <div class="punishment-text">⚖️ العقوبة: {{ v.punishment }}</div>
                </div>
                {% endfor %}
            </div>
        </div>

        <!-- Tab Content: الدرجة الثالثة -->
        <div id="tab-third" class="tab-content">
            <div class="section-title">📋 المخالفات الميدانية</div>
            <div class="violations-list">
                {% for v in third_field %}
                <div class="violation-item">
                    <div class="violation-text">📜 {{ v.original_text }}</div>
                    <div class="punishment-text">⚖️ العقوبة: {{ v.punishment }}</div>
                </div>
                {% endfor %}
            </div>
            
            <div class="section-title">👔 مخالفات القيافة العسكرية</div>
            <div class="violations-list">
                {% for v in third_kiyafa %}
                <div class="violation-item">
                    <div class="violation-text">📜 {{ v.original_text }}</div>
                    <div class="punishment-text">⚖️ العقوبة: {{ v.punishment }}</div>
                </div>
                {% endfor %}
            </div>
            
            <div class="section-title">🎧 المخالفات داخل الموجه</div>
            <div class="violations-list">
                {% for v in third_inside %}
                <div class="violation-item">
                    <div class="violation-text">📜 {{ v.original_text }}</div>
                    <div class="punishment-text">⚖️ العقوبة: {{ v.punishment }}</div>
                </div>
                {% endfor %}
            </div>
        </div>

        <!-- Tab Content: قيد الإنشاء -->
        <div id="tab-construction" class="tab-content">
            <div class="under-construction">
                <h2>⏳ قيد الإنشاء</h2>
                <p>جاري العمل على هذه الصفحة، سيتم إضافتها قريباً</p>
                <p style="margin-top: 20px; font-size: 2rem;">⌛</p>
            </div>
        </div>

        <div class="search-card">
            <div class="input-group">
                <input type="text" class="search-input" id="searchInput" placeholder="ابحث عن المخالفات...">
                <button class="search-btn" id="searchBtn">🔍 بحث</button>
            </div>
        </div>

        <div class="results-area">
            <div id="resultsContainer"></div>
        </div>
        
        <div class="footer">
            Done by : Faisal Alhashimy
        </div>
    </div>
    
    <div class="saved-section">
        <div class="saved-title">
            📋 المحفوظات
            <span style="font-size: 0.7rem; background:#fee2e2; padding:2px 8px; border-radius:20px;" id="savedCount">0</span>
        </div>
        <div class="saved-list" id="savedList">
            <div style="color:#9ca3af; text-align:center; padding:20px;">لا توجد عقوبات محفوظة<br>اضغط + على أي نتيجة لحفظها</div>
        </div>
        <button class="clear-btn" id="clearBtn">🗑️ مسح الكل</button>
    </div>
</div>

<script>
    // Dark Mode
    const themeToggle = document.getElementById('themeToggle');
    const themeText = document.getElementById('themeText');
    
    function setTheme(isDark) {
        if (isDark) {
            document.body.classList.add('dark');
            themeText.textContent = 'فاتح';
            themeToggle.innerHTML = '<span>☀️</span> <span>فاتح</span>';
            localStorage.setItem('theme', 'dark');
        } else {
            document.body.classList.remove('dark');
            themeText.textContent = 'داكن';
            themeToggle.innerHTML = '<span>🌙</span> <span>داكن</span>';
            localStorage.setItem('theme', 'light');
        }
    }
    
    const savedTheme = localStorage.getItem('theme');
    setTheme(savedTheme === 'dark');
    
    themeToggle.addEventListener('click', () => {
        setTheme(!document.body.classList.contains('dark'));
    });
    
    // Tabs functionality - Toggle (click to show, click again to hide)
    const tabs = document.querySelectorAll('.tab');
    const tabContents = {
        'first': document.getElementById('tab-first'),
        'second': document.getElementById('tab-second'),
        'third': document.getElementById('tab-third'),
        'construction': document.getElementById('tab-construction')
    };
    
    // متغير لتخزين التبويب النشط حالياً
    let activeTab = null;
    
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const tabId = tab.getAttribute('data-tab');
            const content = tabContents[tabId];
            
            // إذا كان التبويب الحالي هو نفسه التبويب النشط -> نغلقه
            if (activeTab === tabId) {
                content.classList.remove('active');
                tab.classList.remove('active');
                activeTab = null;
            } 
            // غير ذلك -> نفتح التبويب الجديد ونغلق القديم
            else {
                // إغلاق التبويب القديم
                if (activeTab) {
                    tabContents[activeTab].classList.remove('active');
                    document.querySelector(`.tab[data-tab="${activeTab}"]`).classList.remove('active');
                }
                // فتح التبويب الجديد
                content.classList.add('active');
                tab.classList.add('active');
                activeTab = tabId;
            }
        });
    });
    
    // Modal functions
    const messages = ["صلي على النبي ﷺ", "سبحان الله", "استغفر الله"];
    let messageIndex = 0;
    
    function showModal() {
        const modal = document.getElementById('modalOverlay');
        const modalMessage = document.getElementById('modalMessage');
        modalMessage.textContent = messages[messageIndex % messages.length];
        modal.style.display = 'flex';
        messageIndex++;
    }
    
    function closeModal() {
        document.getElementById('modalOverlay').style.display = 'none';
    }
    
    setTimeout(() => showModal(), 10000);
    setInterval(() => showModal(), 300000);
    
    // Saved items
    let savedItems = JSON.parse(localStorage.getItem('savedPunishments') || '[]');
    
    function updateSavedDisplay() {
        const savedList = document.getElementById('savedList');
        const savedCount = document.getElementById('savedCount');
        savedCount.textContent = savedItems.length;
        
        if (savedItems.length === 0) {
            savedList.innerHTML = '<div style="color:#9ca3af; text-align:center; padding:20px;">لا توجد عقوبات محفوظة<br>اضغط + على أي نتيجة لحفظها</div>';
            return;
        }
        
        savedList.innerHTML = savedItems.map((item, idx) => `
            <div class="saved-item" onclick="searchSaved('${item.violation.replace(/'/g, "\\'")}')">
                <div style="font-weight:bold;">📌 ${item.violation}</div>
                <div class="saved-pun">⚖️ ${item.punishment}</div>
                <div style="font-size:0.7rem; color:#9ca3af;">${item.level}</div>
            </div>
        `).join('');
    }
    
    function savePunishment(item) {
        savedItems.unshift(item);
        if (savedItems.length > 20) savedItems.pop();
        localStorage.setItem('savedPunishments', JSON.stringify(savedItems));
        updateSavedDisplay();
    }
    
    function searchSaved(violation) {
        document.getElementById('searchInput').value = violation;
        performSearch();
    }
    
    document.getElementById('clearBtn').addEventListener('click', () => {
        savedItems = [];
        localStorage.setItem('savedPunishments', JSON.stringify(savedItems));
        updateSavedDisplay();
    });
    
    updateSavedDisplay();
    
    async function performSearch() {
        const query = document.getElementById('searchInput').value.trim();
        const resultsContainer = document.getElementById('resultsContainer');
        
        if (!query) {
            resultsContainer.innerHTML = '<div class="result-card" style="text-align:center; color:#dc2626;">✏️ الرجاء كتابة المخالفة للبحث</div>';
            return;
        }
        
        resultsContainer.innerHTML = '<div class="loading">🤖 جاري البحث بالذكاء الاصطناعي...</div>';
        
        try {
            const response = await fetch('/search', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query: query })
            });
            const data = await response.json();
            
            if (data.results && data.results.length > 0) {
                resultsContainer.innerHTML = `
                    <div class="result-count">🔍 عدد النتائج: ${data.results.length}</div>
                    ${data.results.map(result => {
                        let levelClass = '';
                        if (result.data.level === 'الدرجة الأولى') levelClass = 'level-1';
                        else if (result.data.level === 'الدرجة الثانية') levelClass = 'level-2';
                        else levelClass = 'level-3';
                        
                        return `
                            <div class="result-card" id="result-${result.data.id}">
                                <span class="level-badge ${levelClass}">📌 ${result.data.level}</span>
                                <div class="original-text">
                                    📜 ${result.data.original_text}
                                </div>
                                <div class="punishment-display">
                                    ⚖️ العقوبة: ${result.data.punishment}
                                </div>
                                <button class="save-btn" onclick='savePunishment(${JSON.stringify({
                                    violation: result.data.violation,
                                    punishment: result.data.punishment,
                                    level: result.data.level
                                })})'>➕ حفظ العقوبة</button>
                                <div style="font-size:0.7rem; color:#9ca3af; margin-top:8px;">🎯 دقة التطابق: ${Math.round(result.score * 100)}%</div>
                            </div>
                        `;
                    }).join('')}
                `;
            } else {
                resultsContainer.innerHTML = '<div class="result-card" style="text-align:center; border-right-color:#9ca3af;"><div style="font-size:2rem;">😔</div><div style="color:#6b7280;">لم نجد نتائج دقيقة لهذا البحث</div><div style="font-size:0.8rem; margin-top:10px;">جرب كلمات مختلفة</div></div>';
            }
        } catch (error) {
            resultsContainer.innerHTML = '<div class="result-card" style="text-align:center; color:#dc2626;">❌ خطأ في الاتصال</div>';
        }
    }
    
    document.getElementById('searchBtn').addEventListener('click', performSearch);
    document.getElementById('searchInput').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') performSearch();
    });
</script>
</body>
</html>
"""

# ======================== Routes ========================
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        if username == 'faisalalhashimy' and password == '515ffashorta':
            session['logged_in'] = True
            return render_template_string(main_html, 
                first_degree=first_degree_violations,
                second_degree=second_degree_violations,
                third_field=third_degree_field,
                third_kiyafa=third_degree_kiyafa,
                third_inside=third_degree_inside)
        else:
            return render_template_string(login_html, error="اسم المستخدم أو كلمة المرور غير صحيحة")
    if session.get('logged_in'):
        return render_template_string(main_html,
            first_degree=first_degree_violations,
            second_degree=second_degree_violations,
            third_field=third_degree_field,
            third_kiyafa=third_degree_kiyafa,
            third_inside=third_degree_inside)
    return render_template_string(login_html, error=None)

@app.route('/search', methods=['POST'])
def search():
    data = request.get_json()
    user_query = data.get('query', '')
    
    if not user_query:
        return jsonify({"results": []})
    
    results = find_punishments_ai(user_query)
    
    formatted_results = []
    for r in results:
        formatted_results.append({
            "type": "law",
            "data": {
                "id": r["data"]["id"],
                "violation": r["data"]["violation"],
                "punishment": r["data"]["punishment"],
                "level": r["data"]["level"],
                "original_text": r["data"]["original_text"]
            },
            "score": r["score"]
        })
    
    return jsonify({"results": formatted_results})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)