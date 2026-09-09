# creative/video — הפקת וידאו

**סרטון AIDA ראשון של TIAMORA.** קונספט C1 "הסוללה", 16 שניות, שני יחסי מסך.

| קובץ | יחס | יעד |
|---|---|---|
| `out/TIAMORA_AIDA_battery_9x16.mp4` | 1080×1920 | Reels · Stories · TikTok |
| `out/TIAMORA_AIDA_battery_4x5.mp4` | 1080×1350 | פיד Facebook · Instagram |

מפרט טכני: H.264 High · yuv420p · 30fps · 16.000 שנ' · faststart · פס אודיו שקט (AAC) · ~500KB.
עומד בדרישות Meta Ads לשני המיקומים.

**התסריט המלא, הקופי למודעה ובקרת האיכות:** [`script-C1-battery.md`](script-C1-battery.md)

---

## איך זה נבנה — ולמה לא במודל וידאו

הסרטון מרונדר מקוד (`render_aida.py` → PIL → ffmpeg). זו לא הסתפקות בפחות, זו ההחלטה הנכונה לקריאייטיב הזה:

1. **`tiamora-ugc-video` מתעד באג SKU ב-Seedance** — מוצר שגוי הופיע בפלט. באנימציה מקודדת אין סיכון כזה: הענבר הוא `#EEA53C`, בכל פריים, תמיד.
2. **מודלים גנרטיביים משבשים עברית.** טקסט על מסך הוא ליבת המודעה; פה כל אות היא Liberation Sans מרונדרת עם BiDi תקין.
3. **דטרמיניסטי וברסיוני.** שינוי מילה = שינוי בקוד ורנדר חוזר — לא הגרלה חדשה ולא קרדיטים.
4. **אפס סימנים מסחריים של צד שלישי.** כל פיקסל הוא נכס של TIAMORA.

## רנדר מחדש

```bash
pip install Pillow
apt-get install -y ffmpeg fonts-noto-core         # Liberation Sans מגיע עם הבסיס
python3 render_aida.py out/TIAMORA_AIDA_battery_9x16.mp4 1080 1920
python3 render_aida.py out/TIAMORA_AIDA_battery_4x5.mp4  1080 1350
```

**תלות קריטית:** Pillow חייב להיות בנוי עם libraqm (`PIL.features.check('raqm')` ⇒ `True`).
בלעדיו העברית תרונדר הפוכה. `text()` מעביר `direction="rtl"` במפורש, כי זיהוי אוטומטי מציב `97%` ו-`NIGHT` בצד הלא נכון של שורה עברית.

---

## 🔊 קריינות — קיימת, לא מוטמעת

**הסרטון מיועד לצפייה ללא קול,** וזה נכון: מודעות בפיד של מטא מתנגנות מושתקות, וכל טיעון ה-AIDA כאן קריא לגמרי בטקסט. הסרטון שלם כפי שהוא.

במקביל **הופקה קריינות עברית מלאה** (Gemini TTS, קול Charon — ישיר, רגוע, מקצועי), בארבעה קטעים לפי הסצנות. הקבצים יושבים בחשבון Magnific של המותג ולא הוטמעו כאן: ה-egress policy של הסשן חסם את `pikaso.cdnpk.net` (403), כך שלא ניתן היה להוריד אותם לקונטיינר.

**כדי להוסיף אותם** — להוריד את ארבעת ה-WAV מהחשבון ל-`assets/vo/vo1..4.wav` ואז:

```bash
ffmpeg -i out/TIAMORA_AIDA_battery_9x16.mp4 \
  -i assets/vo/vo1.wav -i assets/vo/vo2.wav -i assets/vo/vo3.wav -i assets/vo/vo4.wav \
  -filter_complex "[1]adelay=200|200[a1];[2]adelay=4400|4400[a2];\
[3]adelay=9200|9200[a3];[4]adelay=13200|13200[a4];\
[a1][a2][a3][a4]amix=inputs=4:normalize=0,alimiter=limit=0.95[a]" \
  -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 128k -shortest \
  out/TIAMORA_AIDA_battery_9x16_VO.mp4
```

ה-`adelay` תואם לגבולות הסצנות ב-`render_aida.py` (0.2 / 4.4 / 9.2 / 13.2 שנ'). **לוודא באוזן אחרי המיזוג** — אורכי ה-TTS לא נמדדו בקונטיינר.

**גרסת ה-VO היא לטיקטוק ולריל עם קול, לא לפיד.** לא להחליף בה את הגרסה השקטה.

---

## מה עוד חסר בקונספט

| קריאייטיב | פורמט | סטטוס |
|---|---|---|
| C1-a | תמונת UGC סטילס | ❌ לא נוצר |
| C1-b | וידאו UGC 15–20 שנ' | ❌ לא נוצר — דורש שחקן |
| **C1-c** | **אנימציה 16 שנ'** | ✅ **כאן** |

האנימציה **לא מחליפה** את שתי האחרות — אד-סט עם קריאייטיב אחד לא נותן למטא מה לבחור.
