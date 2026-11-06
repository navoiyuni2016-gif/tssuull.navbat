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

## Native Windows va bölim prefikslari — 2026-11-06

Yakuniy ilova manbasi `860ca60582a2684979b219591c4ffd3dcc378be9`, release **windows-13**. Git tag aynan shu commitga mosligi tekşirildi. Windows yiğişi va haqiqiy EXE sinovlari: https://github.com/navoiyuni2016-gif/tssuull.navbat/actions/runs/42173128364 — barcha bosqiçlar muvaffaqiyatli.

- Linux manba: `python -m unittest discover -s tests -q` — 42 test, 40 ötgan, 2 Windows-only ötkazib yuborilgan. Windows CI shu manba testlarini qayta bajardi.
- Windows’da PyInstaller orqali yiğilgan haqiqiy EXEning ikki testi ötdi: Tk/resurslar/SQLite/uch hisobot formati/server/KPOS sozlama/read-only printer diagnostikasi; haqiqiy WebView2 oynasi, beshta xizmat, F10 lokal buyruği va administrator login sahifasi.
- Native loaded hodisasidagi parallel handler va test örtasidagi vaqt poygasi aniq readiness belgisi bilan tuzatildi; keyingi EXE sinovi ötdi. Content-Security-Policy yumşatilmadi, eval/JS API bridge qöşilmadi.
- `node tests/test_recordings.js`, `node tests/test_announcer.js` — 10 test ötgan; turli bölim harflari uçun toğri ovoz va yetişmayotgan yozuvlar tekşirildi.
- `node tests/smoke_browser.js` — haqiqiy Chromium’da admin bölim harfini Z ga almaştirib, API’da saqlanişi va B ga qaytariş; audio yuklaş/ijro, terminal → xodim → TV, 3 marta yonib-öçiş, bosma xatosida bir çiptani qayta bosiş ötdi. Bosma yakuni bu brauzer sinovida simulyatsiya qilingan.
- `node tests/android_tv_layout.js` — beshta faol oyna 640×360, 853×480, 960×540, 1280×720, 1366×768 ölchamlarda siğdi. Bu Chromium tekşiruvi, X96 apparat sinovi emas.
- Eski bazaga prefiks ustuni xavfsiz qöşilişi, A–E boshlanğiç harflar, eski çiptalar özgarmasligi, request takrorida raqam saqlanişi va prefiksning takrorlanmasligi alohida testlarda ötgan.
- Serverni yopiş → portni böşatiş → qayta oçiş → çiptaning saqlanişi, ikkinçi serverni rad etiş va administrator parolini tekşiriş testi ötgan.

Jismoniy KPOS_80 printer ulanmagan. Haqiqiy qoğoz, USB uzilişi, Windows 10/11 foydalanuvçi qurilmasidagi örnatiş/boot va X96 ekran-karnay natijalari bu dalillarga kirmaydi. Qurilma diagnostikasi va sinov çeki [WINDOWS_TUZATISH_HISOBOTI.md](WINDOWS_TUZATISH_HISOBOTI.md)da.

## Minutli hisobotlar va LEDning birinçi bosqiçi — 2026-11-06

Tekşirilgan manba `fdf47ddd8b6bf20f0281b54dd6dd55380ec94981`, release **windows-15**. Windows CI barcha bosqiçlarda muvaffaqiyatli: https://github.com/navoiyuni2016-gif/tssuull.navbat/actions/runs/42176165897 .

- Manba to‘plami: 49 test (47 manba testi, manba bosqiçida 2 Windows frozen testi skip). Keyin haqiqiy yiğilgan EXEning ikki testi ham Windows’da ötdi.
- Hisobotda 120 soniya → 2.0 minut, 300 soniya → 5.0 minut. Barcha bölimlar va xodimlar, shu jumladan 0 xizmatli xodim körinadi. Har kesimdagi `served` yig‘indisi umumiy jamiga mos. Eski soniya API maydonlari moslik uçun saqlandi; foydalanuvçi interfeysi va eksport minutdan foydalanadi.
- XLSX/DOCX XML tuzilişi, barcha to‘rt/ichki qora katak çiziqlari, oq fonlar, integer xizmat sonlari, minut uçun bir önlik xona, logo va raqamli kataklar testlarda tekşirildi. Namunalar openpyxl/python-docx bilan mustaqil qayta o‘qildi.
- Uch sahifali PDF PyMuPDF bilan o‘qildi va rasmlari körib tekşirildi: umumiy natija, bölimlar, operatorlar. Raqamlar uchala formatda bir xil. Misol: 40 çipta, 32 yakunlangan, 3 kelmagan, 5 kutayotgan; bu faqat belgilangan **NAMUNA** maʼlumotlari.
- Haqiqiy Chromium sinovi yangi Elektron tablolar menyusida sozlama saqlaş, sinov vazifasini yaratish, hisobotda minut yozuvi va qora katak çiziqlari, eski operator/TV/printer oqimini tekşirdi. Ovoz testlari 10/10 ötdi.
- LED adapteri: 5-oyna çaqiruvi faqat o‘z sinov tablosiga, qayta çaqiruv alohida hodisa, yakunlanganda tozalaş, restartda sozlama saqlanişi, sinov vazifasi statistikani özgartirmasligi, yaroqsiz IDlarni rad etiş va LED jadvali xatosida operator/TV çaqiruvi saqlanişi ötdi. Administratorga tegishli GET/POST huquqlari tekşirildi.
- Frozen Windows EXE API orqali sinov tablosi sozlandi, operator A001ni çaqirdi va alohida worker vazifani **simulated** holatiga ötkazdi. Shu paketda haqiqiy WebView2/F10/admin login sinovi ham ötdi.

Haqiqiy LED protokoli topilmadi; bu apparat muvaffaqiyati emas. Hech qanday COM/IP/RF buyruq taxminan yuborilmadi; serial/tcp/agent transportlari bloklangan. Ishlab çiqaruvçi modeli, manzil, frame/checksum, ACK va prefiks imkoniyati tasdiqlanmagan. Eski fayllar inventari va keyingi bosqiç [LED_TEXNIK_TAHLIL.md](LED_TEXNIK_TAHLIL.md)da. KPOS/LED/X96 foydalanuvçi qurilmasi sinovi va Word/Excel dasturlarida vizual print-preview bu muhitda bajarilmadi.
