import os
import json
from google import genai

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

with open('system/progress_tracker.json', 'r', encoding='utf-8') as f:
    tracker = json.load(f)

if tracker.get('status') == "completed":
    print("🎉 ધોરણ 7 નો તમામ ડેટાબેઝ સફળતાપૂર્વક બની ગયો છે!", flush=True)
    exit(0)

# ધોરણ 7 ના તમામ વિષયો અને તેના કુલ પ્રકરણો
syllabus = [
    {"name": "Maths", "guj_name": "ગણિત", "chapters": 13},
    {"name": "Science", "guj_name": "વિજ્ઞાન", "chapters": 13},
    {"name": "SS", "guj_name": "સામાજિક વિજ્ઞાન", "chapters": 18},
    {"name": "Gujarati", "guj_name": "ગુજરાતી", "chapters": 15},
    {"name": "English", "guj_name": "અંગ્રેજી", "chapters": 8},
    {"name": "Hindi", "guj_name": "હિન્દી", "chapters": 10},
    {"name": "Sanskrit", "guj_name": "સંસ્કૃત", "chapters": 10}
]

# પ્રશ્નોના પ્રકાર અને ટાર્ગેટ
question_types = [
    {"id": "MCQs", "name": "બહુવિકલ્પી પ્રશ્નો (MCQs)", "marks": 1, "target_count": 60},
    {"id": "FillBlanks", "name": "ખાલી જગ્યા પૂરો", "marks": 1, "target_count": 60},
    {"id": "TrueFalse", "name": "ખરાં ખોટાં જણાવો", "marks": 1, "target_count": 60},
    {"id": "MatchPairs", "name": "જોડકાં જોડો", "marks": 1, "target_count": 60},
    {"id": "1_Mark", "name": "એક વાક્યમાં ઉત્તર", "marks": 1, "target_count": 60},
    {"id": "2_Marks", "name": "બે ગુણના ટૂંક જવાબી પ્રશ્નો", "marks": 2, "target_count": 10},
    {"id": "3_Marks", "name": "ત્રણ ગુણના મુદ્દાસર પ્રશ્નો", "marks": 3, "target_count": 10},
    {"id": "4_Marks", "name": "ચાર ગુણના વિસ્તૃત પ્રશ્નો", "marks": 4, "target_count": 10}
]

sub_idx = tracker['current_subject_index']
type_idx = tracker['current_type_index']
ch_num = tracker['current_chapter']

current_subject = syllabus[sub_idx]
current_q_type = question_types[type_idx]
max_chapters = current_subject["chapters"]

print(f"Generating {current_q_type['name']} for Std 7 {current_subject['name']} Chapter {ch_num}...", flush=True)

# પ્રશ્નના પ્રકાર મુજબ ચોક્કસ સૂચનાઓ
type_rules = ""
if current_q_type['id'] == "MCQs":
    type_rules = "દરેક પ્રશ્ન સાથે 4 વિકલ્પો (A, B, C, D) આપવા."
elif current_q_type['id'] == "FillBlanks":
    type_rules = "દરેક ખાલી જગ્યાના અંતે કૌંસમાં 3 વિકલ્પો આપવા."
elif current_q_type['id'] == "TrueFalse":
    type_rules = "વિધાન સાચું છે કે ખોટું તે સ્પષ્ટ લખવું અને ખોટું હોય તો કારણ આપવું."
elif current_q_type['id'] == "MatchPairs":
    type_rules = "વિભાગ A અને વિભાગ B ના જોડકાં સ્પષ્ટ કરવા અને નીચે સાચો ઉત્તર આપવો."

# AI માટેનો પ્રોમ્પ્ટ
prompt = f"""
તમે ગુજરાત બોર્ડ (GSEB) ના એક્સપર્ટ શિક્ષક છો.
તમારે ધોરણ 7, વિષય: '{current_subject['guj_name']}', પ્રકરણ: {ch_num} ના નવા ઘટાડેલા NCERT સિલેબસ મુજબ પ્રશ્નો બનાવવાના છે.

પ્રશ્નનો પ્રકાર: {current_q_type['name']} ({current_q_type['marks']} માર્ક)

અત્યંત કડક નિયમો (STRICT RULES):
1. વિષયની 100% શુદ્ધતા (ZERO MIXING): આ ફાઈલ માત્ર ધોરણ 7 ના વિષય '{current_subject['guj_name']}' ના પ્રકરણ {ch_num} માટે જ છે. ભૂલથી પણ અન્ય કોઈ વિષય કે અન્ય પ્રકરણના પ્રશ્નો મિક્સ કરવા નહિ.
2. પ્રશ્નોની સંખ્યા: લક્ષ્યાંક {current_q_type['target_count']} પ્રશ્નો બનાવવાનો છે. જો પ્રકરણ નાનું હોય તો જેટલા શ્રેષ્ઠ અને સાચા પ્રશ્નો બની શકે તેટલા બનાવવા. સંખ્યા વધારવા માટે ક્યારેય બહારનો પ્રશ્ન ઉમેરવો નહિ.
3. પ્રકાર મુજબ શરત: {type_rules}
4. લેવલ અને નો-રીપીટેશન: {current_q_type['marks']} ગુણના પ્રશ્નોની લંબાઈ અને ડેપ્થ બરાબર તેટલા જ માર્કસની હોવી જોઈએ. પ્રશ્નોનું પુનરાવર્તન ન થવું જોઈએ.
5. શોર્ટકટ ટ્રીક: દરેક પ્રશ્નના જવાબમાં સમજૂતી સાથે '💡 નિતેશ સરની શોર્ટકટ ટ્રીક (NJ Classes)' ફરજિયાત સામેલ કરવી.

ફોર્મેટ (STRICT JSON OBJECT):
કોઈપણ વેરીએબલ વગર માત્ર નીચે મુજબનું JSON Object આપવું:
{{
  "chapterName": "પ્રકરણ {ch_num}",
  "chapterTitle": "ધોરણ 7 {current_subject['guj_name']} પ્રકરણ {ch_num} નું સાચું નામ",
  "questionType": "{current_q_type['name']}",
  "qa_list": [
    {{
      "questionNumber": "પ્રશ્ન 1",
      "question": "અહીં પ્રશ્ન લખવો...",
      "answer": "<div style='background-color:#f0f8ff; padding:15px; border-left:5px solid #16a085; border-radius:8px;'><p><strong>ઉકેલ/જવાબ:</strong> અહીં સાચો જવાબ લખવો.</p><hr><p style='color:#d32f2f; font-weight:bold;'>💡 નિતેશ સરની શોર્ટકટ ટ્રીક: અહીં યાદ રાખવાની ટ્રીક લખવી...</p></div>"
    }}
  ]
}}
"""

print("Searching for live text models from your API account...", flush=True)
valid_models = []
try:
    for model in client.models.list():
        if hasattr(model, 'supported_actions') and "generateContent" in model.supported_actions:
            name = model.name.lower()
            if not any(word in name for word in ['video', 'audio', 'tts', 'vision', 'image', 'exp', 'learnlm', 'embedding', 'aqa']):
                valid_models.append(model.name)
except Exception as e:
    print(f"Error fetching models: {e}", flush=True)

valid_models.sort(key=lambda x: ('flash' not in x.lower(), x))
output_data = ""

for m in valid_models[:3]:
    try:
        print(f"⏳ Pending: {m} મોડલ દ્વારા પ્રશ્નો બની રહ્યા છે...", flush=True)
        response = client.models.generate_content(model=m, contents=prompt)
        raw_output = response.text.strip()
        
        if "{" in raw_output and "}" in raw_output:
            raw_output = raw_output[raw_output.find("{") : raw_output.rfind("}") + 1]
            
        output_data = raw_output.strip()
        print("✅ Success! ડેટા બની ગયો છે.", flush=True)
        break
    except Exception as e:
        print(f"❌ Failed with {m}. Error: {e}", flush=True)

if not output_data:
    print("Error: ડેટા જનરેટ કરવામાં નિષ્ફળતા મળી.", flush=True)
    exit(1)

# ફાઈલ સેવિંગ લોજિક: Std7/Maths/Maths_MCQs.js
folder_path = f"Std7/{current_subject['name']}"
os.makedirs(folder_path, exist_ok=True)

q_id = current_q_type['id']
file_path = f"{folder_path}/{current_subject['name']}_{q_id}.js"

mode = 'a' if os.path.exists(file_path) else 'w'
with open(file_path, mode, encoding='utf-8') as f:
    if mode == 'w':
        f.write(f"var Std7_{current_subject['name']}_{q_id} = {{\n")
        f.write(f'"{ch_num}": ' + output_data + '\n')
    else:
        f.write(f',\n"{ch_num}": ' + output_data + '\n')

# ---------------------------------------------------------
# ટ્રાન્ઝિશન લોજીક (પ્રકરણ -> પ્રશ્ન પ્રકાર -> વિષય)
# ---------------------------------------------------------
tracker['current_chapter'] += 1

if tracker['current_chapter'] > max_chapters:
    tracker['current_chapter'] = 1
    tracker['current_type_index'] += 1
    
    if tracker['current_type_index'] >= len(question_types):
        tracker['current_type_index'] = 0
        tracker['current_subject_index'] += 1
        
        if tracker['current_subject_index'] >= len(syllabus):
            tracker['status'] = "completed"
            tracker['current_subject_index'] -= 1

with open('system/progress_tracker.json', 'w', encoding='utf-8') as f:
    json.dump(tracker, f, indent=4)

print("Task Completed Successfully! Std 7 data saved.", flush=True)
