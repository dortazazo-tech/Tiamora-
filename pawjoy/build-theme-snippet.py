# -*- coding: utf-8 -*-
import json
I = json.load(open('icons.json', encoding='utf-8'))

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
 '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
 '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
 'family=Heebo:wght@400;500;700&family=Rubik:wght@600;700;800&display=swap">')

CSS = """
.pj-page{--green:#0b4a37;--green2:#16734f;--lime:#1fa85a;--mint:#eaf7ee;--cream:#faf8f3;
--ink:#14201b;--muted:#6f7d76;--line:#e4e8e5;
font-family:"Heebo",-apple-system,"Segoe UI",Arial,sans-serif;color:var(--ink);background:#fff;direction:rtl;-webkit-font-smoothing:antialiased}
.pj-page *{box-sizing:border-box}
.pj-page h1,.pj-page h2,.pj-page h3,.pj-page strong,.pj-page b{font-family:"Rubik","Heebo",Arial,sans-serif}
.pj-page .i{width:1em;height:1em;flex:none;display:block}
.pj-topbar{background:var(--green);color:#fff;display:flex;justify-content:center;gap:44px;padding:11px 20px;font-size:13.5px;font-weight:500;flex-wrap:wrap}
.pj-topbar span{display:flex;align-items:center;gap:8px}
.pj-topbar .i{font-size:17px;opacity:.9}
.pj-header{max-width:1240px;margin:auto;display:flex;align-items:center;justify-content:space-between;gap:20px;padding:16px 24px;border-bottom:1px solid var(--line);background:#fff}
.pj-logo{display:flex;align-items:center;gap:10px;color:var(--green);text-decoration:none}
.pj-logo .i{font-size:34px}
.pj-logo-txt{display:flex;flex-direction:column;line-height:1}
.pj-logo-txt b{font-size:27px;font-weight:800;letter-spacing:-.6px}
.pj-logo-txt span{font-size:10.5px;color:var(--muted);font-weight:500;letter-spacing:.2px;margin-top:3px}
.pj-header nav{display:flex;gap:28px}
.pj-header nav a{color:#2b3a33;text-decoration:none;font-weight:700;font-size:15px}
.pj-header nav a:hover{color:var(--green)}
.pj-tools{display:flex;align-items:center;gap:14px}
.pj-icon-btn{border:0;background:transparent;color:#2b3a33;font-size:23px;cursor:pointer;padding:4px;display:grid;place-items:center;position:relative}
.pj-icon-btn:hover{color:var(--green)}
.pj-count{position:absolute;top:-2px;left:-4px;background:var(--green);color:#fff;font-size:10px;font-weight:800;min-width:16px;height:16px;border-radius:999px;display:grid;place-items:center;font-family:"Rubik",Arial,sans-serif}
.pj-main{max-width:1240px;margin:auto;padding:30px 24px 54px}
.pj-hero{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:46px;align-items:start}
.pj-main-image{position:relative;background:var(--cream);border-radius:22px;overflow:hidden;aspect-ratio:4/5;max-width:100%;border:1px solid var(--line)}
.pj-main-image img{width:100%;height:100%;object-fit:cover;object-position:center;display:block}
.pj-image-note{position:absolute;bottom:18px;right:18px;background:rgba(255,255,255,.94);backdrop-filter:blur(4px);padding:9px 15px;border-radius:999px;font-weight:700;font-size:13.5px;box-shadow:0 4px 16px rgba(0,0,0,.09)}
.pj-thumbs{display:flex;gap:9px;margin-top:11px}
.pj-thumb{width:70px;height:70px;border:1px solid var(--line);border-radius:12px;overflow:hidden;padding:0;background:var(--cream);cursor:pointer}
.pj-thumb img{width:100%;height:100%;object-fit:cover}
.pj-badge{display:inline-flex;align-items:center;gap:7px;background:var(--mint);color:#17543a;padding:8px 15px;border-radius:999px;font-weight:700;font-size:13.5px}
.pj-badge .i{font-size:16px}
.pj-info h1{font-size:37px;line-height:1.16;margin:16px 0 13px;letter-spacing:-1.1px;font-weight:800;text-wrap:balance}
.pj-sub{font-size:16.5px;line-height:1.75;color:#55625b;margin:0 0 24px}
.pj-benefits{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin:22px 0;padding:20px 0;border-block:1px solid var(--line)}
.pj-benefits div{display:flex;flex-direction:column;align-items:center;text-align:center;gap:9px;font-size:12.5px;font-weight:700;line-height:1.45;color:#2b3a33}
.pj-benefits .i{font-size:29px;color:var(--green2)}
.pj-guarantee{display:flex;gap:12px;align-items:flex-start;background:var(--mint);padding:15px 17px;border-radius:12px;margin:20px 0}
.pj-guarantee .i{font-size:23px;color:var(--green);margin-top:1px}
.pj-guarantee strong{color:var(--green);font-size:15px;display:block;margin-bottom:3px}
.pj-guarantee span{font-size:13px;color:#48574f;line-height:1.6}
.pj-choose{font-size:19px;margin:28px 0 13px;font-weight:700}
.pj-bundles{display:grid;grid-template-columns:repeat(3,1fr);gap:11px}
.pj-bundle{position:relative;border:1.5px solid #dbe1dd;border-radius:16px;padding:22px 11px 15px;display:flex;flex-direction:column;align-items:center;text-align:center;gap:8px;cursor:pointer;background:#fff;transition:border-color .18s,background .18s,box-shadow .18s}
.pj-bundle:hover{border-color:#b6c6bd}
.pj-bundle:has(input:checked){border-color:var(--lime);box-shadow:0 0 0 2.5px rgba(31,168,90,.13);background:#f8fdfa}
.pj-bundle:has(input:focus-visible){outline:2px solid var(--green);outline-offset:3px}
.pj-bundle input{position:absolute;opacity:0;pointer-events:none}
.pj-stack{display:flex;justify-content:center;height:52px;align-items:center}
.pj-stack img,.pj-stack .pj-chip{width:46px;height:46px;border-radius:50%;object-fit:cover;background:var(--cream);border:2px solid #fff;box-shadow:0 2px 7px rgba(0,0,0,.11)}
.pj-stack img+img,.pj-stack .pj-chip+.pj-chip{margin-right:-15px}
.pj-chip{display:grid;place-items:center;color:#c2b9a4;font-size:19px}
.pj-bundle strong{font-size:15.5px;font-weight:700}
.pj-bundle-desc{font-size:11.5px;color:var(--muted);min-height:32px;line-height:1.5}
.pj-bundle-price{font-size:23px;font-weight:800;display:flex;align-items:baseline;gap:6px;justify-content:center;flex-wrap:wrap;font-family:"Rubik",Arial,sans-serif;font-variant-numeric:tabular-nums}
.pj-bundle-price s{font-size:13.5px;font-weight:600;color:var(--muted)}
.pj-bundle-save{background:#e2f5e9;color:#146c3f;font-size:10.5px;font-weight:800;padding:4px 11px;border-radius:999px}
.pj-popular{position:absolute;top:-11px;background:var(--lime);color:#fff;border-radius:999px;padding:5px 13px;font-size:10.5px;font-weight:800;letter-spacing:.2px}
.pj-add{width:100%;border:0;border-radius:13px;background:linear-gradient(135deg,var(--green2),var(--green));color:#fff;font-size:19px;font-weight:800;font-family:"Rubik",Arial,sans-serif;padding:18px;margin-top:20px;display:flex;align-items:center;justify-content:center;gap:11px;cursor:pointer;box-shadow:0 9px 22px rgba(11,74,55,.22);transition:transform .12s}
.pj-add:hover{transform:translateY(-1px)}
.pj-add .i{font-size:22px}
.pj-micro{text-align:center;font-size:11.5px;color:var(--muted);margin:11px 0 0}
.pj-trust{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-top:20px;padding-top:20px;border-top:1px solid var(--line)}
.pj-trust span{display:flex;flex-direction:column;align-items:center;text-align:center;gap:7px;color:#55625b;font-size:11.5px;font-weight:600;line-height:1.45}
.pj-trust .i{font-size:22px;color:var(--green2)}
.pj-accordions{margin:44px 0 22px;display:grid;gap:11px}
.pj-accordions details{border:1px solid var(--line);border-radius:13px;background:#fff;overflow:hidden}
.pj-accordions summary{font-weight:700;cursor:pointer;font-size:16.5px;padding:17px 19px;display:flex;align-items:center;gap:10px;list-style:none}
.pj-accordions summary::-webkit-details-marker{display:none}
.pj-accordions summary .i{font-size:20px;color:var(--green2)}
.pj-accordions details>*:not(summary){padding:0 19px 19px}
.pj-accordions p{color:#55625b;line-height:1.75;margin:0}
.pj-rte{line-height:1.75;color:#2b3a33}
.pj-rte h3{font-size:17px;margin:19px 0 8px}
.pj-rte ul{padding-right:1.2em;margin:0 0 1em}
.pj-rte li{margin-bottom:5px}
.pj-why{background:var(--cream);border-radius:20px;padding:32px 28px;margin-top:20px;text-align:center;border:1px solid var(--line)}
.pj-why h2{margin:0 0 22px;font-size:26px;font-weight:800;letter-spacing:-.5px}
.pj-why-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:16px}
.pj-why-grid div{display:flex;flex-direction:column;gap:10px;align-items:center;font-weight:700;font-size:13.5px;color:#2b3a33}
.pj-why-grid .i{font-size:29px;color:var(--green2)}
.pj-footer{text-align:center;padding:38px 24px;background:#f5f7f6;border-top:1px solid var(--line)}
.pj-footer .pj-logo{justify-content:center;display:inline-flex}
.pj-footer-links{display:flex;justify-content:center;gap:20px;flex-wrap:wrap;margin:20px 0 14px}
.pj-footer-links a{color:#46534c;font-size:13px;text-decoration:none;border-bottom:1px solid #cfd8d3;padding-bottom:1px}
.pj-footer-links a:hover{color:var(--green)}
.pj-legal{font-size:11.5px;color:#9aa6a0;margin:0}
.pj-overlay{position:fixed;inset:0;background:rgba(10,20,15,.45);opacity:0;pointer-events:none;transition:.22s;z-index:9997}
.pj-overlay.is-open{opacity:1;pointer-events:auto}
.pj-drawer{position:fixed;top:0;left:0;width:min(430px,94vw);height:100vh;background:#fff;z-index:9998;transform:translateX(-102%);transition:transform .26s cubic-bezier(.4,0,.2,1);box-shadow:10px 0 40px rgba(0,0,0,.16);padding:20px;overflow:auto;direction:rtl}
.pj-drawer.is-open{transform:translateX(0)}
.pj-drawer-head{display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid var(--line);padding-bottom:14px}
.pj-drawer-head button{border:0;background:transparent;font-size:27px;cursor:pointer;color:var(--muted);line-height:1;padding:0 4px}
.pj-drawer-head h2{margin:0;font-size:21px;font-weight:800}
.pj-cart-product{display:flex;gap:14px;align-items:center;padding:18px 0;border-bottom:1px solid var(--line)}
.pj-cart-product img,.pj-cart-thumb{width:78px;height:78px;object-fit:cover;border-radius:12px;background:var(--cream);flex:none}
.pj-cart-thumb{display:grid;place-items:center;color:#c2b9a4;font-size:30px}
.pj-cart-price{font-weight:800;font-size:19px;margin-top:5px;font-family:"Rubik",Arial,sans-serif}
.pj-ship-bar{padding:17px 0;border-bottom:1px solid var(--line)}
.pj-ship-text{font-size:12.5px;font-weight:700;margin-bottom:9px;text-align:center;display:flex;align-items:center;justify-content:center;gap:7px}
.pj-ship-text .i{font-size:16px;color:var(--green2)}
.pj-ship-track{height:7px;background:#e9edea;border-radius:999px;overflow:hidden}
.pj-ship-fill{height:100%;width:0;background:linear-gradient(90deg,var(--green2),#31c47a);border-radius:999px;transition:width .35s}
.pj-upsells h3{margin:21px 0 12px;font-size:16px;font-weight:700}
.pj-up-card{display:grid;grid-template-columns:54px 1fr auto;gap:12px;align-items:center;border:1px solid var(--line);border-radius:14px;padding:11px;margin-bottom:9px}
.pj-up-card img,.pj-up-icon{width:54px;height:54px;border-radius:11px;object-fit:cover;background:var(--mint)}
.pj-up-icon{display:grid;place-items:center;font-size:25px;color:var(--green2)}
.pj-up-copy{display:flex;flex-direction:column;gap:2px;min-width:0}
.pj-up-copy strong{font-size:13.5px;font-weight:700}
.pj-up-copy span{font-size:11.5px;color:var(--muted)}
.pj-up-copy b{font-size:15px;font-family:"Rubik",Arial,sans-serif;font-weight:800}
.pj-up-copy s{font-size:11.5px;font-weight:600;color:var(--muted);margin-right:5px}
.pj-up-card button{border:0;background:var(--green2);color:#fff;padding:9px 13px;border-radius:9px;font-weight:800;font-size:12.5px;cursor:pointer;font-family:inherit}
.pj-up-card button:disabled{background:#a9b5ae;cursor:default}
.pj-checkout{display:block;text-align:center;background:var(--green);color:#fff;text-decoration:none;font-weight:800;font-family:"Rubik",Arial,sans-serif;padding:16px;border-radius:12px;margin-top:19px;font-size:16px}
.pj-continue{width:100%;border:0;background:transparent;padding:14px;color:var(--muted);cursor:pointer;font:inherit;font-size:13.5px}
@media (prefers-reduced-motion:reduce){.pj-page *{transition:none!important;animation:none!important}}
"""

NARROW = """
  .pj-topbar{gap:14px;font-size:11px;padding:9px 12px}
  .pj-topbar span:nth-child(n+3){display:none}
  .pj-header{padding:13px 16px}.pj-header nav{display:none}
  .pj-logo .i{font-size:29px}.pj-logo-txt b{font-size:22px}.pj-logo-txt span{font-size:9px}
  .pj-main{padding:20px 14px 38px}.pj-hero{grid-template-columns:1fr;gap:26px}
  .pj-info h1{font-size:27px;letter-spacing:-.7px}
  .pj-sub{font-size:15.5px}
  .pj-benefits{grid-template-columns:repeat(2,1fr);gap:18px}
  .pj-bundles{grid-template-columns:1fr}
  .pj-bundle{display:grid;grid-template-columns:58px 1fr auto;text-align:right;align-items:center;padding:14px 13px;gap:3px 12px}
  .pj-stack{grid-row:1/4;height:auto}
  .pj-stack img,.pj-stack .pj-chip{width:40px;height:40px}
  .pj-stack img+img,.pj-stack .pj-chip+.pj-chip{margin-right:-13px}
  .pj-bundle strong{align-self:end}
  .pj-bundle-desc{min-height:0}
  .pj-bundle-price{grid-row:1/3;grid-column:3;font-size:20px;flex-direction:column;gap:0;align-items:flex-end}
  .pj-bundle-save{grid-column:3;grid-row:3;font-size:9.5px}
  .pj-popular{top:-9px;left:12px}
  .pj-trust{grid-template-columns:repeat(2,1fr);gap:18px}
  .pj-why{padding:26px 20px}.pj-why h2{font-size:22px}
  .pj-why-grid{grid-template-columns:repeat(2,1fr)}
"""

def body(img_main, thumbs, stack, up_lick, up_ball, cart_thumb, links, desc_html, rating_note=""):
    return f"""{FONTS}
<div class="pj-topbar">
  <span>{I['truck']}משלוח 7–14 ימי עסקים</span>
  <span>{I['lock']}תשלום מאובטח</span>
  <span>{I['box']}14 יום החזר כספי</span>
  <span>{I['chat']}שירות בעברית</span>
</div>

<header class="pj-header">
  <a class="pj-logo" href="/">{I['paw']}<span class="pj-logo-txt"><b>PawJoy</b><span>Happy Dogs. Happier Days.</span></span></a>
  <nav>
    <a href="#pj-hero">עמוד הבית</a>
    <a href="#pj-benefits">למה PawJoy?</a>
    <a href="#pj-faq">שאלות נפוצות</a>
  </nav>
  <div class="pj-tools">
    <button class="pj-icon-btn" type="button" aria-label="חיפוש">{I['search']}</button>
    <button class="pj-icon-btn" type="button" data-pj-open-cart aria-label="עגלה">{I['cart']}<span class="pj-count" data-pj-count>0</span></button>
  </div>
</header>

<main class="pj-main">
  <section class="pj-hero" id="pj-hero">
    <div class="pj-gallery">
      <div class="pj-main-image">{img_main}
        <div class="pj-image-note">הופכים את זמן האוכל למשחק</div>
      </div>{thumbs}
    </div>

    <div class="pj-info">
      <div class="pj-badge">{I['paw']}תעסוקה יומיומית לכלב</div>
      <h1>הכלב שלכם מסיים את האוכל ב-40 שניות. המשטח הזה מחזיק אותו 15 דקות.</h1>
      <p class="pj-sub">מפזרים חטיפים בין הסיבים, והכלב מריח, מחפש, מתעסק ונהנה. אכילה איטית שמונעת בליעת אוויר, תעסוקה שמפחיתה שעמום — וחצי שעה שקטה גם כשאתם לא בבית.</p>

      <div id="pj-benefits" class="pj-benefits">
        <div>{I['brain']}<span>מעודד חיפוש וחשיבה</span></div>
        <div>{I['smile']}<span>מפחית שעמום</span></div>
        <div>{I['bowl']}<span>מאט את קצב האכילה</span></div>
        <div>{I['heart']}<span>לכל הגזעים והגדלים</span></div>
      </div>

      <div class="pj-guarantee">{I['shield']}<span><strong>14 יום להחזיר — ואנחנו סופגים את דמי הביטול.</strong><span>החוק מתיר לנו לגבות עד ₪100 דמי ביטול. אנחנו לא גובים.</span></span></div>

      <h2 class="pj-choose">בחרו את החבילה שלכם:</h2>
      <div class="pj-bundles">{stack}</div>

      <input type="hidden" data-pj-variant-id value="">
      <button type="button" class="pj-add" data-pj-add>{I['cart']}<span>הוסיפו לעגלה</span><span data-pj-button-price></span></button>
      <p class="pj-micro">משלוח 7–14 ימי עסקים · תשלום מאובטח SSL · 14 יום החזר כספי</p>

      <div class="pj-trust">
        <span>{I['truck']}משלוח לכל הארץ</span>
        <span>{I['lock']}תשלום מאובטח</span>
        <span>{I['box']}14 יום החזר כספי</span>
        <span>{I['chat']}שירות בעברית</span>
      </div>
    </div>
  </section>

  <section class="pj-accordions" id="pj-faq">
    <details open>
      <summary>{I['paw']}כל הפרטים על המוצר</summary>
      <div class="pj-rte">{desc_html}</div>
    </details>
    <details>
      <summary>{I['smile']}איך מתחילים?</summary>
      <p>מתחילים בכמות קטנה של מזון במקומות גלויים, כדי שהכלב יבין מה קורה. אחרי יום-יומיים מסתירים עמוק יותר בין שכבות הבד. רוב הכלבים מגיעים ל-10–15 דקות תעסוקה תוך שבוע.</p>
    </details>
  </section>

  <section class="pj-why">
    <h2>למה לבחור ב-PawJoy</h2>
    <div class="pj-why-grid">
      <div>{I['gem']}<span>מוצרים איכותיים</span></div>
      <div>{I['heart']}<span>כלבים מאושרים</span></div>
      <div>{I['leaf']}<span>פתרונות מעשיים</span></div>
      <div>{I['home']}<span>שירות בעברית</span></div>
    </div>
  </section>
</main>

<footer class="pj-footer">
  <a class="pj-logo" href="/">{I['paw']}<span class="pj-logo-txt"><b>PawJoy</b><span>Happy Dogs. Happier Days.</span></span></a>
  <nav class="pj-footer-links">{links}</nav>
  <p class="pj-legal">[שם העוסק] · ח.פ./ע.מ. [מספר] · [כתובת] · [טלפון] · [דוא"ל]</p>
</footer>

<div class="pj-overlay" data-pj-overlay></div>
<aside class="pj-drawer" data-pj-drawer aria-hidden="true">
  <div class="pj-drawer-head">
    <button type="button" data-pj-close aria-label="סגירה">&times;</button>
    <h2>העגלה שלך</h2>
  </div>
  <div class="pj-cart-product">{cart_thumb}
    <div><strong data-pj-cart-title>החבילה שבחרת</strong><div class="pj-cart-price" data-pj-cart-price></div></div>
  </div>
  <div class="pj-ship-bar">
    <div class="pj-ship-text" data-pj-ship-text></div>
    <div class="pj-ship-track"><div class="pj-ship-fill" data-pj-ship-fill></div></div>
  </div>
  <div class="pj-upsells">
    <h3>השלימו את החבילה</h3>{up_lick}{up_ball}
  </div>
  <a href="/checkout" class="pj-checkout">מעבר לתשלום</a>
  <button class="pj-continue" type="button" data-pj-close>המשך קנייה</button>
</aside>"""

JS = """
(function(){
  var root=SCOPE; if(!root)return;
  var THRESH=23900, extra=0, added=0;
  var radios=root.querySelectorAll('input[name="pjb"]');
  var hid=root.querySelector('[data-pj-variant-id]');
  var btn=root.querySelector('[data-pj-add]');
  var bp=root.querySelector('[data-pj-button-price]');
  var dr=root.querySelector('[data-pj-drawer]'), ov=root.querySelector('[data-pj-overlay]');
  var ct=root.querySelector('[data-pj-cart-title]'), cp=root.querySelector('[data-pj-cart-price]');
  var st=root.querySelector('[data-pj-ship-text]'), sf=root.querySelector('[data-pj-ship-fill]');
  var cnt=root.querySelector('[data-pj-count]');
  var SHIPICON='SHIPICON_HTML';
  function money(c){var v=(c/100).toFixed(2);if(v.slice(-3)==='.00')v=v.slice(0,-3);return '\\u20aa'+v;}
  function sel(){return root.querySelector('input[name="pjb"]:checked')||radios[0];}
  function ship(t){if(!st||!sf)return;var r=THRESH-t;
    if(r<=0){st.innerHTML=SHIPICON+'<span>\\u05d9\\u05e9 \\u05dc\\u05db\\u05dd \\u05de\\u05e9\\u05dc\\u05d5\\u05d7 \\u05d7\\u05d9\\u05e0\\u05dd!</span>';sf.style.width='100%';}
    else{st.innerHTML=SHIPICON+'<span>\\u05e0\\u05d5\\u05ea\\u05e8\\u05d5 '+money(r)+' \\u05dc\\u05de\\u05e9\\u05dc\\u05d5\\u05d7 \\u05d7\\u05d9\\u05e0\\u05dd</span>';sf.style.width=Math.min(100,(t/THRESH)*100)+'%';}}
  function sync(){var r=sel();if(!r)return;if(!r.checked)r.checked=true;
    if(hid)hid.value=r.value; bp.textContent='\\u2014 '+r.dataset.price;
    ct.textContent=r.dataset.title; cp.textContent=money(Number(r.dataset.cents)+extra);
    ship(Number(r.dataset.cents)+extra);}
  radios.forEach(function(r){r.addEventListener('change',sync)});
  function open(){dr.classList.add('is-open');ov.classList.add('is-open');dr.setAttribute('aria-hidden','false');AFTEROPEN}
  function close(){dr.classList.remove('is-open');ov.classList.remove('is-open');dr.setAttribute('aria-hidden','true');}
  root.querySelectorAll('[data-pj-open-cart]').forEach(function(e){e.addEventListener('click',function(){sync();open();})});
  root.querySelectorAll('[data-pj-close]').forEach(function(e){e.addEventListener('click',close)});
  ov.addEventListener('click',close);
  document.addEventListener('keydown',function(e){if(e.key==='Escape')close()});
  ADDHANDLER
  UPHANDLER
  THUMBS
  sync();
})();
"""

SHIPICON = I['truck'].replace('"', "\\'")

# ---------- 1) Shopify theme snippet ----------
liq_stack = """{% for variant in pj_product.variants %}
            {%- liquid
              assign idx = forloop.index
              assign feat = false
              if idx == 2
                assign feat = true
              endif
              assign saving = 0
              if variant.compare_at_price > variant.price
                assign saving = variant.compare_at_price | minus: variant.price
              endif
              assign unit = variant.price | divided_by: idx
            -%}
            <label class="pj-bundle">
              {% if feat %}<span class="pj-popular">הכי משתלם</span>{% endif %}
              <input type="radio" name="pjb" value="{{ variant.id }}"
                data-price="{{ variant.price | money_without_trailing_zeros | escape }}"
                data-cents="{{ variant.price }}"
                data-title="{{ variant.title | escape }}"{% if feat %} checked{% endif %}>
              <span class="pj-stack">
                {% for i in (1..idx) %}
                  {% if pj_product.featured_image %}{{ pj_product.featured_image | image_url: width: 140 | image_tag: alt: '' }}{% else %}<span class="pj-chip">""" + I['paw'] + """</span>{% endif %}
                {% endfor %}
              </span>
              <strong>{{ variant.title }}</strong>
              <span class="pj-bundle-desc">
                {%- case idx -%}
                  {%- when 1 -%}להתחיל — לנסות איך הכלב מגיב
                  {%- when 2 -%}זוג סבב — תמיד יש משטח נקי
                  {%- else -%}ערכת סבב מלאה — {{ unit | money_without_trailing_zeros }} ליחידה
                {%- endcase -%}
              </span>
              <span class="pj-bundle-price">{{ variant.price | money_without_trailing_zeros }}{% if saving > 0 %} <s>{{ variant.compare_at_price | money_without_trailing_zeros }}</s>{% endif %}</span>
              {% if saving > 0 %}<span class="pj-bundle-save">חיסכון {{ saving | money_without_trailing_zeros }}</span>{% endif %}
            </label>
          {% endfor %}"""

def up_card(var, icon, sub):
    return ("""
      {%- assign v = """ + var + """.first_available_variant -%}
      <div class="pj-up-card">
        {% if """ + var + """.featured_image %}{{ """ + var + """.featured_image | image_url: width: 160 | image_tag: alt: '' }}{% else %}<span class="pj-up-icon">""" + icon + """</span>{% endif %}
        <div class="pj-up-copy"><strong>{{ """ + var + """.title }}</strong><span>""" + sub + """</span>
          <b>{{ v.price | money_without_trailing_zeros }}{% if v.compare_at_price > v.price %} <s>{{ v.compare_at_price | money_without_trailing_zeros }}</s>{% endif %}</b></div>
        <button type="button" data-pj-upsell="{{ v.id }}">+ הוספה</button>
      </div>
    {% endif %}""")

liq_lick = "{% if lick != blank and lick.first_available_variant != blank %}" + up_card('lick', I['heart'], 'מעולה להרגעה ולהסחה')
liq_ball = "{% if ball != blank and ball.first_available_variant != blank %}" + up_card('ball', I['smile'], 'משחק שממשיך אחרי הארוחה')

liq_js = (JS.replace('SCOPE', "document.getElementById('pj-{{ section.id }}')")
   .replace('SHIPICON_HTML', SHIPICON)
   .replace('AFTEROPEN', "refresh();")
   .replace('ADDHANDLER', """
  function refresh(){fetch('/cart.js',{headers:{'Accept':'application/json'}}).then(function(r){return r.json()})
    .then(function(c){extra=0;ship(c.total_price);cp.textContent=money(c.total_price);if(cnt)cnt.textContent=c.item_count;}).catch(function(){});}
  btn.addEventListener('click',function(){var r=sel();if(!r)return;btn.disabled=true;
    fetch('/cart/add.js',{method:'POST',headers:{'Content-Type':'application/json','Accept':'application/json'},
      body:JSON.stringify({items:[{id:Number(r.value),quantity:1}]})})
    .then(function(x){if(!x.ok)throw 0;return x.json()}).then(function(){open();})
    .catch(function(){alert('\\u05dc\\u05d0 \\u05d4\\u05e6\\u05dc\\u05d7\\u05e0\\u05d5 \\u05dc\\u05d4\\u05d5\\u05e1\\u05d9\\u05e3 \\u05dc\\u05e2\\u05d2\\u05dc\\u05d4.');})
    .finally(function(){btn.disabled=false});});""")
   .replace('UPHANDLER', """
  root.querySelectorAll('[data-pj-upsell]').forEach(function(u){u.addEventListener('click',function(){
    u.disabled=true;
    fetch('/cart/add.js',{method:'POST',headers:{'Content-Type':'application/json','Accept':'application/json'},
      body:JSON.stringify({items:[{id:Number(u.dataset.pjUpsell),quantity:1}]})})
    .then(function(x){if(!x.ok)throw 0;u.textContent='\\u05e0\\u05d5\\u05e1\\u05e3 \\u2713';refresh();})
    .catch(function(){u.disabled=false;});});});""")
   .replace('THUMBS', """
  root.querySelectorAll('[data-pj-thumb]').forEach(function(t){t.addEventListener('click',function(){
    var im=root.querySelector('.pj-main-image img'); if(im)im.src=t.dataset.pjThumb;});});"""))

liquid = ("""{%- liquid
  assign lick = all_products['משטח-ליקוק-לכלבים']
  assign ball = all_products['כדור-חטיפים-מתגלגל-לכלבים']
-%}
{% if pj_product != blank %}
<div id="pj-{{ section.id }}" class="pj-page" dir="rtl">
"""
+ body(
    img_main="{% if pj_product.featured_image %}{{ pj_product.featured_image | image_url: width: 1400 | image_tag: loading: 'eager', alt: pj_product.title }}{% endif %}",
    thumbs="""{% if pj_product.images.size > 1 %}<div class="pj-thumbs">{% for image in pj_product.images limit: 5 %}<button type="button" class="pj-thumb" data-pj-thumb="{{ image | image_url: width: 1400 }}">{{ image | image_url: width: 180 | image_tag: alt: '' }}</button>{% endfor %}</div>{% endif %}""",
    stack=liq_stack, up_lick=liq_lick, up_ball=liq_ball,
    cart_thumb="{% if pj_product.featured_image %}{{ pj_product.featured_image | image_url: width: 240 | image_tag: alt: '' }}{% else %}<span class=\"pj-cart-thumb\">" + I['paw'] + "</span>{% endif %}",
    links='<a href="/pages/shipping-policy">מדיניות משלוחים</a><a href="/pages/refund-policy">ביטול והחזרות</a><a href="/pages/privacy-policy">מדיניות פרטיות</a><a href="/pages/terms-of-service">תנאי שימוש</a>',
    desc_html="{{ pj_product.description }}")
+ "\n</div>\n\n<style>\n.pawjoy-active .shopify-section-group-header-group,\n.pawjoy-active .shopify-section-group-footer-group{display:none!important}\n"
+ CSS + "@media(max-width:900px){" + NARROW + "}\n</style>\n\n<script>\ndocument.body.classList.add('pawjoy-active');\n"
+ liq_js + "\n</script>\n{% else %}\n<div style=\"padding:40px;text-align:center\">יש לבחור מוצר להצגה.</div>\n{% endif %}\n")

open('snippet_v3.liquid','w',encoding='utf-8').write(liquid)
print('theme snippet:', len(liquid), 'chars')

# ---------- 2) static preview artifact ----------
PH = '<span class="pj-chip">' + I['paw'] + '</span>'
V = [("1 משטח",13900,"139","189","50","להתחיל — לנסות איך הכלב מגיב",1,""),
     ("2 משטחים",21900,"219","278","59","זוג סבב — תמיד יש משטח נקי",2," checked"),
     ("3 משטחים",26900,"269","417","148","ערכת סבב מלאה — ₪89.66 ליחידה",3,"")]
pv_stack = "".join(
  f'<label class="pj-bundle">'
  + ('<span class="pj-popular">הכי משתלם</span>' if n==2 else '')
  + f'<input type="radio" name="pjb" value="{c}" data-cents="{c}" data-price="₪{p}" data-title="{t}"{ck}>'
  + '<span class="pj-stack">' + PH*n + '</span>'
  + f'<strong>{t}</strong><span class="pj-bundle-desc">{d}</span>'
  + f'<span class="pj-bundle-price">₪{p} <s>₪{cmp}</s></span>'
  + f'<span class="pj-bundle-save">חיסכון ₪{sv}</span></label>'
  for t,c,p,cmp,sv,d,n,ck in V)

def pv_up(title, sub, price, cmpp, icon):
    return (f'<div class="pj-up-card"><span class="pj-up-icon">{icon}</span>'
      f'<div class="pj-up-copy"><strong>{title}</strong><span>{sub}</span>'
      f'<b>₪{price} <s>₪{cmpp}</s></b></div>'
      f'<button type="button" data-pj-upsell="2900">+ הוספה</button></div>')

DESC = """<p>מפזרים חטיפים בין הסיבים, והכלב מריח, מחפש, מתעסק ונהנה. אכילה איטית שמונעת בליעת אוויר, תעסוקה שמפחיתה שעמום — וחצי שעה שקטה גם כשאתם לא בבית.</p>
<h3>פרטים טכניים</h3><ul><li><strong>חומר:</strong> בד פליז רך, נעים למגע, ללא חלקים קשיחים</li><li><strong>קוטר:</strong> כ-40 ס"מ</li><li><strong>בסיס:</strong> נגד החלקה</li><li><strong>מתאים ל:</strong> גורים, בוגרים ומבוגרים · גזעים קטנים עד גדולים</li></ul>
<div style="background:#fdf1f1;border-right:3px solid #c0392b;padding:13px 16px;border-radius:9px;margin:0 0 18px"><strong style="color:#c0392b">שימוש תחת השגחה בלבד.</strong><br>יש לבדוק את המשטח לפני כל שימוש ולהפסיק להשתמש בו אם נקרע או נשחק. המוצר אינו מיועד ללעיסה אגרסיבית או לבליעה.</div>
<h3>ניקוי ותחזוקה</h3><ul><li>כביס במכונה — מחזור עדין, מים קרים</li><li><strong>ייבוש באוויר בלבד.</strong> ייבוש מלא לוקח 4–8 שעות</li></ul>
<p style="background:#fdf8ea;padding:13px 16px;border-radius:9px;margin:0"><strong>בגלל זמן הייבוש</strong> — רוב הלקוחות בוחרים בחבילת 2 או 3 משטחים, כדי שתמיד יהיה משטח נקי מוכן לשימוש.</p>"""

pv_js = (JS.replace('SCOPE', "document.getElementById('pj')")
  .replace('SHIPICON_HTML', SHIPICON).replace('AFTEROPEN','')
  .replace('ADDHANDLER', """
  btn.addEventListener('click',function(){sync();added++;if(cnt)cnt.textContent=added;open();});""")
  .replace('UPHANDLER', """
  root.querySelectorAll('[data-pj-upsell]').forEach(function(u){u.addEventListener('click',function(){
    if(u.disabled)return;extra+=Number(u.dataset.pjUpsell);u.disabled=true;
    u.textContent='\\u05e0\\u05d5\\u05e1\\u05e3 \\u2713';added++;if(cnt)cnt.textContent=added;sync();});});""")
  .replace('THUMBS',''))

preview = ("""<title>PawJoy Build v3</title>
<style>
:root{--shell:#12100d;--shell2:#1c1916;--sl:#2e2a25;--si:#efeae2;--sm:#a79d90;--sa:#3fbf7f;color-scheme:dark}
body{margin:0;background:var(--shell);color:var(--si);font-family:"Heebo",-apple-system,"Segoe UI",Arial,sans-serif}
.wrap{padding-block:20px 44px;padding-inline:16px;max-width:1340px;margin:auto}
.bar{display:flex;flex-wrap:wrap;align-items:center;gap:12px 16px;background:var(--shell2);
  border:1px solid var(--sl);border-radius:13px;padding:13px 17px;margin-bottom:10px;direction:rtl}
.bar h1{font-size:15px;margin:0;font-weight:800;font-family:"Rubik",Arial,sans-serif;letter-spacing:-.2px}
.bar .dot{width:8px;height:8px;border-radius:50%;background:var(--sa);flex:none}
.bar .sp{flex:1}
.seg{display:flex;background:#0e0c0a;border:1px solid var(--sl);border-radius:999px;padding:3px;gap:2px}
.seg button{border:0;background:transparent;color:var(--sm);font:inherit;font-size:13px;font-weight:700;
  padding:7px 16px;border-radius:999px;cursor:pointer}
.seg button[aria-pressed="true"]{background:var(--sa);color:#07261a}
.seg button:focus-visible{outline:2px solid var(--sa);outline-offset:2px}
.note{direction:rtl;color:var(--sm);font-size:13px;line-height:1.75;margin:0 0 18px;padding:0 4px;max-width:72ch}
.note b{color:var(--si)}
.stage{display:flex;justify-content:center}
.frame{background:#fff;border-radius:15px;overflow:hidden;width:100%;
  box-shadow:0 20px 64px rgba(0,0,0,.5);transition:max-width .28s ease}
.frame[data-w="mob"]{max-width:412px}
.pj-page{container-type:inline-size}
.pj-page .pj-overlay,.pj-page .pj-drawer{position:absolute}
.pj-page{position:relative}
.pj-page .pj-drawer{height:100%;width:min(430px,94%)}
.pj-chip{display:grid;place-items:center;color:#cbc2ae;font-size:20px}
"""
+ CSS + "@container (max-width:900px){" + NARROW + "}\n</style>\n"
+ """<div class="wrap">
  <div class="bar"><span class="dot"></span><h1>PawJoy Build v3 — תצוגה מקדימה</h1><span class="sp"></span>
    <div class="seg" role="group" aria-label="רוחב תצוגה">
      <button type="button" id="bD" aria-pressed="true">מחשב</button>
      <button type="button" id="bM" aria-pressed="false">מובייל</button></div></div>
  <p class="note">אותו דף, אחרי החלפת <b>Arial</b> ב-Rubik + Heebo והחלפת כל האימוג'ים באייקוני קו.
  במקום תמונות המוצר בכרטיסי הבאנדל יש <b>עיגולי מקום</b> — באתר עצמו ייכנסו שם תמונות אמיתיות של 1, 2 ו-3 משטחים, בדיוק כמו במוקאפ שלך.</p>
  <div class="stage"><div class="frame" id="frame" data-w="desk"><div class="pj-page" id="pj" dir="rtl">
"""
+ body(img_main='<span class="pj-chip" style="position:absolute;inset:0;font-size:80px;border-radius:0">' + I['paw'] + '</span>',
       thumbs='', stack=pv_stack,
       up_lick=pv_up('משטח ליקוק סיליקון לכלבים','מעולה להרגעה ולהסחה','29','69',I['heart']),
       up_ball=pv_up('כדור חטיפים מתגלגל לכלבים','משחק שממשיך אחרי הארוחה','29','79',I['smile']),
       cart_thumb='<span class="pj-cart-thumb">' + I['paw'] + '</span>',
       links='<a href="#pj">מדיניות משלוחים</a><a href="#pj">ביטול והחזרות</a><a href="#pj">מדיניות פרטיות</a><a href="#pj">תנאי שימוש</a>',
       desc_html=DESC)
+ """
  </div></div></div>
</div>
<script>""" + pv_js + """
(function(){var f=document.getElementById('frame'),d=document.getElementById('bD'),m=document.getElementById('bM');
 function set(w){f.dataset.w=w;d.setAttribute('aria-pressed',String(w==='desk'));m.setAttribute('aria-pressed',String(w==='mob'));}
 d.addEventListener('click',function(){set('desk')});m.addEventListener('click',function(){set('mob')});})();
</script>""")
open('preview_v3.html','w',encoding='utf-8').write(preview)
print('preview:', len(preview), 'chars')
