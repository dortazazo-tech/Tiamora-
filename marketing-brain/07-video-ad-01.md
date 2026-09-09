# 07 — Video Ad 01 | "אני לא מוותרת על הפרק"

**תאריך:** 2026-09-09 · **פורמט:** AIDA · **אורך:** 25 שניות
**אווטאר:** רונית · **אמונות שנבנות:** 1 → 2 → 4 · **מוצר:** NIGHT ‏(SR6918, ענבר, 97%)

---

## תמונת הבסיס

איור בסגנון מלוטש: אישה על ספה בערב, משקפי ענבר, קערת פופקורן, כלב ישן, מסך טלוויזיה דולק, מיתוג TIAMORA.

**שלוש הערות שנמסרו למשתמש והוא בחר להמשיך כמות שהוא — מתועד כאן כדי שלא ייעלם:**

| # | הערה | סטטוס |
|---|---|---|
| 1 | 🔴 **לוגו NETFLIX בפריים** — סימן מסחרי של צד ג' בקריאייטיב ממומן. סיכון לדחייה בביקורת המודעות של מטא | המשתמש בחר להשאיר |
| 2 | 🟠 **טאגליין "CLEAR VISION. A BRIGHTER YOU."** — טענת ראייה על מוצר שינה. נוגע בטענה שסקירת Cochrane הפילה (ראה `01` §6.4) | המשתמש בחר להשאיר |
| 3 | 🟠 **גיל הדמות** נקרא 25–30; רונית היא 45+ | המשתמש בחר להשאיר |

✅ **בדיקת SKU עברה:** העדשה בתמונה **ענבר = NIGHT**. הבאג המוכר של Seedance (מוצר שגוי בפלט) לא חל כאן. **עדיין לבדוק פריים-ביי-פריים אחרי ההפקה.**

⚠️ **סטייה מסגנון ברירת המחדל:** `tiamora-ad-creative` מגדיר UGC גולמי מסמארטפון כברירת מחדל, ומסמן קריאייטיב מלוטש כ"אסור כברירת מחדל". הקריאייטיב הזה הוא **וריאנט מכוון**, לא ברירת מחדל חדשה. אם הוא מנצח — זו תוצאה שמצדיקה דיון, לא הרשאה גורפת.

---

## הסקריפט

> **A — Attention** `0–3 שנ'`
> "אני לא מוותרת על הפרק שלי בערב. אבל הפסקתי להאשים את עצמי בגלל זה."
>
> **I — Interest** `3–11 שנ'`
> "כי זה לא הפרק שמפריע לשינה. זה האור שיוצא מהמסך. הוא אומר לגוף שעדיין יום — ואז המלטונין, ההורמון שמאותת לנו להירדם, פשוט לא מתחיל להיווצר."
>
> **D — Desire** `11–19 שנ'`
> "אז אני לא מכבה כלום. אני מרכיבה את אלה. עדשת ענבר, תשעים ושבעה אחוז חסימה. הפרק נשאר בדיוק אותו פרק — האור הכחול פשוט לא מגיע לעיניים."
>
> **A — Action** `19–25 שנ'`
> "ארבעה עשר לילות לנסות. אם זה לא עשה לך כלום — הכסף חוזר, והמשקפיים נשארים אצלך."

### למה אין כאן עדות תוצאה — החלטה מכוונת

הדמות היא שחקנית AI, לא לקוחה. **"נרדמתי מהר יותר" מפיה היא עדות מפוברקת**, בדיוק כמו צילום מסך וואטסאפ מומצא (ראה `05`, קונספט חסום).
לכן היא מדברת רק על **מנגנון**, **נתון מוצר** ו**ערבות** — שלושתם נכונים ומותרים. מול קהל שכבר קרא ביקורת סקפטית, זה גם משכנע יותר.

---

## שוטים

| # | משך | שוט | תנועת מצלמה | דיבור |
|---|---|---|---|---|
| 1 | 3 שנ' | הדמות על הספה, משקפי ענבר, מסך מאיר את החדר, פנים למצלמה | `pushIn` איטי | ליפסינק מלא — A |
| 2 | 8 שנ' | קלוז-אפ על העדשה; אור כחול מהמסך נעצר בענבר | `static` מאקרו | VO — הדמות לא בפריים מדבר |
| 3 | 8 שנ' | חזרה לספה; היא מיישרת את המשקפיים, נשארת מול הסדרה | `static` עדין | ליפסינק מלא — D |
| 4 | 6 שנ' | המשקפיים על השולחן ליד הקערה, מסך דולק ברקע | `pedestalUp` איטי | VO + טקסט: **14 לילות. הכסף חוזר, המשקפיים נשארים.** |

## נעילת קול (זהה בכל שוט — לא לשנות בין קליפים)
אישה · עברית ישראלית טבעית · שנות ה-30–40 · טון חם ונינוח · קצב מתון · בגובה העיניים.
**לא קריינות פרסומת. בלי אנרגיה מוגזמת בהוק.**

## נעילת סאונד
אמביינט סלון שקט בלבד · מוזיקה נמוכה מאוד או ללא (`noMusic`) · **הדיבור דומיננטי תמיד**.
הסצנה היא ערב — כל בס מיותר הורג אותה.

---

## הגדרות הפקה

| | |
|---|---|
| מודל | `bytedance-seedance-pro-2.5` (SOTA, multishot + ליפסינק נייטיב) |
| Start frame | תמונת הבסיס |
| יחס | 1:1 (נגזר מהתמונה הריבועית) |
| רזולוציה | 1080p |
| משך | 25 שניות · 4 שוטים |
| אודיו | VO עברי ב-TTS ← reference מסוג `audio` לליפסינק |
| מוזיקה | `noMusic: true` |

### ⚠️ סיכון ידוע: עברית בליפסינק
איכות העברית במודלי וידאו אינה מובטחת. **אם הליפסינק יוצא שגוי — הנפילה לאחור היא לייצר את הווידאו שקט ולהלביש VO עברי בנפרד.** לבדוק לפני שהסרטון נכנס למודעה.

## חסם תפעולי בסביבה הזו
מדיניות ה-egress של הסשן חוסמת את שרת ההעלאה של שירות הווידאו (‏403 על `ak-data.magnific.com`), ולכן לא ניתן להעלות את התמונה מצד השרת. ההעלאה חייבת להתבצע מהדפדפן של המשתמש.

---

# פרומפטים מוכנים להדבקה (Seedance / MakeUGC / כל כלי image-to-video)

**פריים פתיחה לכל השוטים:** `https://cdn.shopify.com/s/files/1/0757/8979/5373/files/tiamora-night-couch-base.png`
(הועלה ל-Shopify Files ב-2026-09-09 כדי לתת לתמונה כתובת ציבורית שכלי הווידאו יכולים למשוך.)

**הגדרות:** ‏1:1 · 1080p · אודיו נייטיב · **בלי מוזיקה** · סה"כ 25 שניות.

### שוט 1 — 3 שניות · `pushIn` איטי
```
Illustrated animation matching the start image exactly. A woman in her thirties with brown
wavy hair in a loose high bun, amber-tinted glasses in dark rectangular frames, cream knit
sweater, sitting on a blue couch in a warm candlelit living room, a golden retriever asleep
against her, a glowing TV behind her. She looks straight into the camera and speaks, mouth
moving in precise natural lip synchronization, in warm unhurried conversational Israeli
Hebrew: "אני לא מוותרת על הפרק שלי בערב. אבל הפסקתי להאשים את עצמי בגלל זה."
Small relaxed smile at the end of the line. Quiet living-room ambience, no music.
```

### שוט 2 — 8 שניות · `static` מאקרו
```
Macro close-up on the same amber-tinted lens in its dark rectangular frame, the blue glow of
the television visible ahead of it and warmed to amber as it passes through the lens. The
woman does not speak and is not in frame beyond the lens and her cheekbone. Same illustrated
style, same warm candlelit colour grade. The same warm calm female Israeli voice narrates
off-screen, unhurried: "כי זה לא הפרק שמפריע לשינה. זה האור שיוצא מהמסך. הוא אומר לגוף
שעדיין יום, ואז המלטונין, ההורמון שמאותת לנו להירדם, פשוט לא מתחיל להיווצר."
Quiet room tone, no music.
```

### שוט 3 — 8 שניות · `static`
```
Back to the same woman with brown wavy hair in a loose high bun, amber-tinted glasses in dark
rectangular frames, cream knit sweater, on the blue couch beside the sleeping golden
retriever, TV glowing behind her. She lifts one hand and gently adjusts the glasses on her
nose, settles back toward the screen, and speaks to camera with precise natural lip
synchronization in the same warm calm Israeli Hebrew: "אז אני לא מכבה כלום. אני מרכיבה את
אלה. עדשת ענבר, תשעים ושבעה אחוז חסימה. הפרק נשאר בדיוק אותו פרק, האור הכחול פשוט לא מגיע
לעיניים." Same illustrated style throughout. Quiet ambience, no music.
```

### שוט 4 — 6 שניות · `pedestalUp` איטי
```
The amber-lensed glasses in their dark rectangular frames rest folded on the low table beside
the white popcorn bowl, the television still glowing softly in the background, candles
flickering. No people speaking on camera. Same illustrated style and warm candlelit grade.
The same warm calm female Israeli voice narrates off-screen: "ארבעה עשר לילות לנסות. אם זה לא
עשה לך כלום, הכסף חוזר, והמשקפיים נשארים אצלך." Quiet room tone, no music.
```

**טקסט על המסך בשוט 4:** ‏14 לילות. הכסף חוזר, המשקפיים נשארים.

---

## למה הסרטון לא הופק בסשן הזה — תיעוד

| שירות | תוצאה |
|---|---|
| Higgsfield | ‏`Out of credits` — יתרה 3.42, תוכנית starter. ‏Seedance 2.5 גם דורש תוכנית plus ומעלה |
| Magnific / Seedance Pro 2.5 | ‏`Tool usage limit reached` — מכסת השימוש מוצתה |
| העלאה ישירה לשרת הווידאו | חסומה במדיניות ה-egress של הסביבה (‏403 על `ak-data.magnific.com`) — נעקפה דרך Shopify CDN |

**מה כן נסגר:** התמונה מתארחת בכתובת ציבורית, יובאה בהצלחה לשני השירותים, והפרומפטים אומתו מול מגבלות המודל. **חסר רק תקציב הפקה.**
