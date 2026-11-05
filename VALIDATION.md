# Tekşiriş natijalari

Mustaqil Python/SQLite tizimi; eski dastur, DLL, litsenziya serveri yoki frontend kodi işlatilmagan. Yuborilgan arxivdagi rasmiy PNG logo va moviy fon özgartirilmasdan kiritildi.

## 2026-11-05: yangi tekşiruvlar

- 23 Python testi ötdi: parallel/idempotent çiptalar, besh operatorning barça bölimlarga kirişi, bir çiptani faqat bir operator olişi, boshqa oynalarni köriş, holatlar, yönaltiriş, restart, migratsiya, ish vaqti, zaxira/tiklaş, printer xatosi, audio va admin HTTP huquqlari.
- Hisobotlar: uch formatning admin-only HTTP yuklanishi; XLSX sonli qiymatlar va formula matnining xavfsizligi; DOCX XML/jadvallar/logo; PDF Unicode, font, logo va xref yaxlitligi. Namuna fayllar openpyxl, python-docx va PyMuPDF bilan mustaqil oçildi; 40 çipta, 32 yakunlangan, 3 kelmagan, 5 kutayotgan, 180.0 va 265.8 soniya natijalari tasdiqlandi.
- 10 JavaScript testi ötdi: lokal nutq, yozuvli ovoz ketma-ketligi, alifbo, har çaqiruv/qayta çaqiruvda aniq uch animatsiya sikli va oxirida körinişning tiklanişi.
- Haqiqiy Chromium: UZ/EN, administrator sahifalari, WAV yuklash va ijro, terminal → xodim → TV → yakunlash. Çağiruv va qayta çaqiruvda brauzer animatsiyasining uch sikli tekşirildi. JavaScript xatosi yo‘q.
- PDF namuna uç sahifa, Excel uç varaq, Word uç jadval. Sinov namunalari NAMUNA deb belgilangan. Runtime uch formatni qöshimça paketlarsiz yaratadi. PDF shriftining litsenziyasi fonts/ ichida.

## Qurilmada qolgan tekşiruvlar

Windows xizmatini örnatiş/qayta yoqiş, Edge kioski, LocalService printer ruxsatlari, printer drayveri va 80 mm jismoniy çop etiş bu Linux muhitida sinalmagan. Haqiqiy TV brauzeri, karnay, yuklanadigan ovozlar, LAN va internet uzilgan holatni öz qurilmangizda sinang. sounds.rar hajmi yuklaş çegarasidan katta edi; uning yozuvlari paketga kiritilmagan, keyin Administrator → Ovozlar orqali yuklanadi.

ZIP manba va ishga tuşiriş skriptlarini öz içiga oladi; Python 3.12+ alohida örnatiladi. Mustaqil EXE yoki Python örnatuvçisi kiritilmagan. Test parollari faqat vaqtinçalik sinov bazalari uçun; tayyor administrator paroli yoki real baza tarqatilmaydi.

## Kiosk printeri va logotip tuzatişi

KPOS drayveri aniqlansa faqat yangi çiptalar avtomatik bosmaga ötadi. Uch yangi test drayver mavjudligi, topilmaganda sozlamani saqlash, boshqa printerga tegmaslik va eski preview çiptani qayta çop etmaslikni tekşiradi. Windows drayveri/haqiqiy çek bu Linux muhitida sinalmagan.

Yakuniy 26 Python testi ötdi. Chromium’da shaffof/square logo joyi, 1366×768 terminal/TV siğişi va Windows printer rejimida sektor bosilganda brauzer print oynasi çaqirilmasligi hamda bosma navbatiga yozilişi tasdiqlandi.

## Xizmat → avtomatik çek

Chromium’da terminal xizmatlar oynasida qolişi, PDF/printer holati yozuvi va çipta oynasi yo‘qligi tekşirildi. Bosma jarayonida beshta xizmat tugmasi bloklanadi; ikki marta bosish bitta çipta yaratadi. Simulyatsiya qilingan printer xatosidan keyingi qayta bosma ösha request bilan bajariladi va yangi çipta yaratilmaydi. Bu sinov Windows bosma yakunini taqlid qiladi; haqiqiy qoğoz natijasi qurilmada sinaladi. Yangilangan terminal va TV 1366×768 ekran tekşiruvi ham ötdi.

## Windows 10 / X96 avtomatik oçiliş

27 Python testi ötdi. Yangi örnatişga köçiriş sinovi baza/loginlar/çiptalar va audio nusxasini, mavjud manzilga yozmaslikni va işlayotgan server bazasini köçirmaslikni tekşirdi. Chromiumda `/tv?autostart=1` sahifasi va autoplay ruxsati bilan yozuvli ovozning avtomatik yoqilişi ötdi; umumiy terminal→operator→TV oqimi ham ötdi. Xizmat örnatgichidagi service executable yöli tuzatildi.

Windows PowerShell parseri va Windows SCM/Task Scheduler/Assigned Access bu Linux muhitida mavjud emas. Shu sabab Windows skriptlari qurilmada bajarilmadi. X96 proşivkasi, Android boot/launcher ruxsatlari, HDMI-CEC va haqiqiy ovoz avtomatik oçilişi tekşirilmagan. Oddiy fullscreen tizimni qulflamaydi; cheklangan kiosk Windows nashriga qarab Assigned Access orqali bir marta sozlanadi. Töliq yöriq KIOSK_VA_TV.md ichida.

## Windows EXE — 2026-11-05

Windows runnerida muvaffaqiyatli yig‘ilgan va tarqatilgan release: **windows-4**, manba commit `c6e6162`. Dalil: https://github.com/navoiyuni2016-gif/tssuull.navbat/actions/runs/42084075436 .

- 32 manba testi: 31 ötdi, hali yig‘ilmagan frozen paket testi shu bosqiçda ötkazib yuborildi. Yig‘ilgandan keyin aynan öşa frozen test alohida ötdi.
- Haqiqiy Windows x64 EXE ichida Tk oçilishi, SQLite A001 çiptasi, PNG fon/logo, shrift va PowerShell printer resurslari, XLSX/DOCX/PDF eksportlari tekşirildi.
- Frozen EXEning fondagi serveri alohida jarayonda ishga tushdi: health, terminal HTML va HTTP orqali çipta oliş ötdi.
- NSIS Windows örnatuvçisi va portativ ZIP yaratildi, GitHub Releases’ga joylandi. Mahalliy qayta yuklangan örnatuvçi SHA256 bilan mos; installer PE sarlavhasi, ilovaning x64 PE turi, ZIP yaxlitligi va Python/PyInstaller litsenziyalari tekşirildi.
- Windows’da aniqlangan SQLite fayli oçiq qoliş muammosi tuzatildi: tranzaksiya yakunlanganda ulaniş ham darhol yopiladi. Commit/rollback va darhol faylni öçiriş regressiya testi qoşildi.
- Tuzatişdan keyin Linuxda 32 test (31 ötdi, Windows frozen testi ötkazib yuborildi), Chromiumdagi terminal→operator→TV jarayoni ham ötdi.

Jismoniy printer, foydalanuvçi qurilmasidagi installer oynalarini bosib örnatiş, Windows boot/Assigned Access va X96 hali shu qurilmalarda sinov talab qiladi. Raqamli kod imzosi yo‘q. Windows testlari manba yoki soxta EXEni emas, haqiqiy PyInstaller paketini işga tuşirdi.

## X96 Android TV APK

Tekşirilgan manba commit `5691eb5`; Android workflow: https://github.com/navoiyuni2016-gif/tssuull.navbat/actions/runs/42090037233 . Android release tag `android-build-6` aynan shu commitga mosligi Git orqali tekşirildi. APK 1.0.6, Android 5.0+ uçun, CPUga boğliq native kutubxonasiz.

- Java/JUnit manzil normalizatsiyasi, public/loopback/notoğri manzillarni rad etiş va bir origin/TV navigatsiyasini tekşiruvçi 3 test CI’da ötdi.
- Android 11 (API 30) emulatorda haqiqiy Activity/WebView sinovi ötdi: fullscreen sozlamasi va ekran uyqudan saqlanişi, JavaScript/DOM storage, gesturesiz media, fayl/content access çeklovi, IP/PIN saqlanişi va PINni tekşiriş.
- Dastlab ulanmaydigan private LAN manzilida native qayta ulaniş xabari tasdiqlandi; server qaytganda avtomatik retry bilan sahifa oçilib, strict Content-Security-Policy ostida WAV ovozi bosişsiz ijro etildi.
- Haqiqiy universitet serveri va beshta faol oyna bilan Chromium’da 640×360, 853×480, 960×540, 1280×720 va 1366×768 CSS ekranlari tekşirildi. Barcha oynalar/kutayotganlar siğdi; beşinçi oyna pastki ro‘yxat bilan ustma-ust tuşmadi. Server CSPsi yumşatilmadi: Android uslubi faqat bir originli virtual CSS javobi orqali beriladi.
- Imzolangan APK ichidagi uslub sinovdan ötgan manba bilan mos. APK v1, v2 va v3 imzolari Android API 21 minimumi bilan apksigner’da tasdiqlandi. Public GitHub APK qayta yuklab olinib mahalliy imzolangan fayl bilan SHA256 mosligi tekşirildi. Maxfiy signing key Git’dan taşqarida saqlanadi.

Haqiqiy X96 proşivkasi, HDMI ekran, karnay va tokdan keyingi Home/boot davranishi hali qurilmada sinalmagan. Android 10+ avtostart uçun Home/Launcher tanlovi kerak. APK universal klient, Windows’dagi mavjud lokal serverga ulanadi; bazani köçirmaydi.
