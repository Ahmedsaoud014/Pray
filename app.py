from flask import Flask, Response
import requests
from bs4 import BeautifulSoup
import json

app = Flask(__name__)

# قاموس يحتوي على الأكواد الصحيحة للمدن كما يستخدمها الموقع
CITY_CODES = {
    "eg": ("egypt", "360630", "القاهرة"),
    "sa": ("saudi-arabia", "108410", "الرياض"),
    "ae": ("united-arab-emirates", "292223", "أبو ظبي"),
    "kw": ("kuwait", "285787", "مدينة الكويت"),
    "qa": ("qatar", "289317", "الدوحة"),
    "ma": ("morocco", "254888", "الرباط"),
    "dz": ("algeria", "250748", "الجزائر"),
    "jo": ("jordan", "250441", "عمان"),
    "lb": ("lebanon", "276781", "بيروت"),
    "om": ("oman", "287286", "مسقط"),
    "bh": ("bahrain", "290203", "المنامة"),
    "iq": ("iraq", "98182", "بغداد"),
    "sy": ("syria", "170654", "دمشق"),
    "sd": ("sudan", "366730", "الخرطوم"),
    "ly": ("libya", "221024", "طرابلس"),
    "tn": ("tunisia", "2464470", "تونس"),
    "ye": ("yemen", "71137", "صنعاء"),
    "tr": ("turkey", "745044", "إسطنبول"),
}

def convert_time_format(time_str):
    """تحويل التوقيت من AM/PM إلى صباحًا/مساءً"""
    if "AM" in time_str:
        return time_str.replace("AM", "صباحًا")
    elif "PM" in time_str:
        return time_str.replace("PM", "مساءً")
    return time_str

@app.route('/api/pray-time/<country_code>', methods=['GET'])
def get_prayer_times(country_code):
    country_code = country_code.strip().lower()

    if country_code not in CITY_CODES:
        return Response(
            json.dumps({"خطأ": "❌ رمز الدولة غير مدعوم أو غير صحيح."}, ensure_ascii=False, indent=4),
            mimetype="application/json; charset=utf-8",
            status=400
        )

    country_name, city_code, city_name = CITY_CODES[country_code]
    url = f"https://www.islamicfinder.org/world/{country_name}/{city_code}/{city_name}-prayer-times/?language=ar"

    response = requests.get(url)
    if response.status_code != 200:
        return Response(
            json.dumps({"خطأ": "❌ حدث خطأ في جلب البيانات. تأكد من أن الدولة مدعومة في الموقع."}, ensure_ascii=False, indent=4),
            mimetype="application/json; charset=utf-8",
            status=500
        )

    html = response.text
    soup = BeautifulSoup(html, 'html.parser')
    prayer_tiles = soup.find_all('div', class_='prayerTiles')

    if not prayer_tiles:
        return Response(
            json.dumps({"خطأ": "❌ لم يتم العثور على أوقات الصلاة، ربما الدولة غير مدعومة."}, ensure_ascii=False, indent=4),
            mimetype="application/json; charset=utf-8",
            status=404
        )

    prayer_times = {}
    for tile in prayer_tiles:
        prayer_name = tile.find('span', class_='prayername')
        prayer_time = tile.find('span', class_='prayertime')

        if prayer_name and prayer_time:
            prayer_times[prayer_name.text.strip()] = convert_time_format(prayer_time.text.strip())

    # إنشاء JSON باللغة العربية بدون Unicode escape مع تنسيق مرتب
    json_response = json.dumps({
        "الدولة": country_name,
        "العاصمة": city_name,
        "أوقات الصلاة": prayer_times
    }, ensure_ascii=False, indent=4)

    return Response(json_response, mimetype="application/json; charset=utf-8", status=200)

if __name__ == '__main__':
    app.run(debug=True)
