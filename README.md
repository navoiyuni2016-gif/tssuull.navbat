# Universitet elektron navbat tizimi

Terminal → çipta → xodim çaqiruvi → TV → xizmatni yakunlaş. Server va SQLite bazasi terminalning özida işlaydi; işlaş vaqtida internet, Docker, taşqi server va eski DLL talab qilinmaydi. Python 3.12+ kerak. Frontend resurslari lokal.

Interfeys siz tanlagan yozuvda: **Ş, Ç, Ğ, Ö**. Masalan: **Çipta**, **Xizmat körsatiş**, **Özbekça**. Texnik fayl nomlari, URL, login va buyruqlar özgarmaydi. Terminal tillari: UZ / RU / EN. Kirill tanlovi örniga ingliz tili qoşildi.

## Windows’da birinçi sinov

1. ZIP’ni töliq oçing; içidan turib işga tuşirmang.
2. Python 3.12 yoki yangiroğini örnating. Xizmat sifatida örnatiş uçun Python barça foydalanuvçilarga örnatilgan bölsin.
3. `BOSHLASH.cmd` faylini oçing. Birinçi işga tuşişda kamida 12 belgili administrator parolini kiriting. Parol terilganda körinmaydi. Login: `admin`.
4. Server oynasini yopmang. Kiosk avtomatik oçiladi. Brauzerda quyidagi yöllarni sinang:

| Sahifa | Manzil |
|---|---|
| Terminal | `http://127.0.0.1:8080/` |
| Xodim | `http://127.0.0.1:8080/staff` |
| Televizor | `http://127.0.0.1:8080/tv` |
| Administrator | `http://127.0.0.1:8080/admin` |

Boşqa kompyuterda `127.0.0.1` örniga terminalning lokal IP manzilini yozing. Terminalga doimiy IP yoki router DHCP reservation sozlang. Qurilmalar bir lokal tarmoqda bölsin. HTTP işlatiladi: faqat işonçli lokal tarmoqda foydalaning, internetga port oçmang.

Qölda işga tuşiriş, loyiha papkasida:

```sh
python app.py --init
python app.py --host 0.0.0.0 --port 8080
```

`--init` faqat yangi bazada parol yaratadi. Mavjud administrator parolini lokal konsolda tiklaş:

```sh
python app.py --reset-admin
```

## Ovozlarni özingiz yuklaş

`sounds.rar` ZIP içiga qöşilmagan: yuklangan arxivni bu muhitga köçiriş 32 MB çegarasi tufayli bajarilmadi. Kompyuteringizda mavjud arxivni oçing. Eski audio yozuvlardan foydalaniş huquqini özingiz tekşiring; tizim eski dastur yoki litsenziyasiga ulanmaydi.

1. Administrator → **Ovozlar** sahifasini oçing.
2. Har WAV yoki MP3 yozuvni tegişli vazifaga biriktiring. Har bir fayl 8 MB gaça; WAV — PCM, mono yoki stereo, 8–96 kHz, 120 soniyagaça. MP3ning brauzerda ijro bölişini tekşiring.
3. Majburiy belgilar: `ticket` (çipta sözi), `prefix_A` (A harfi), `window` (oyna sözi), `digit_0` dan `digit_9` gaça raqamlar. Bu belgilar texnik identifikator, ularni özgartirmang.
4. Ixtiyoriy: `attention` — diqqat; `number_123` — 123 ni bir butun aytiş; `window_1` — 1-oyna raqamini bir butun aytiş. Maxsus belgi maydoniga yozing. Prefiksni B ga almaştirsangiz `prefix_B` yozuvini ham yuklang.
5. Sahifadagi audio boşqaruvi orqali har yozuvni tinglang. Raqam ovozlariga faqat raqamni aytadigan fayllarni biriktiring, ortiqça sözlar takrorlanmasin.
6. `/tv-audio` → **Yuklangan ovozlar** → **Ovozni yoqiş** → **Ovozni sinaş**. Brauzer çeklovi sababli TV sahifasi har qayta oçilganda ovozni bir marta yoqing.

Masalan, A001 / 2-oyna: diqqat → çipta → A → 0 → 0 → 1 → oyna → 2. `number_1` mavjud bölsa 0–0–1 örniga şu yozuv işlatiladi. Ovozlar va çaqiruvlar ketma-ket, ustma-ust tuşmaydi. Qayta çaqiriş yangi hodisa bölib yana aytiladi. Bir hodisa IDsi qayta kelganda takror aytilmaydi. Aloqa tiklanganda şu oçiq sahifada ötkazib yuborilgan çaqiruvlar olinadi. Sahifa yangi oçilganda eski çaqiruvlar qayta aytilmaydi. Ovoz öçirilgan davrdagi çaqiruvlar keyin ijro etilmaydi.

Yozuvlar hali tayyor bölmasa, **Kompyuter lokal ovozi** rejimini tanlang. Faqat qurilmaga örnatilgan lokal özbek yoki rus ovozlari qabul qilinadi, taşqi ovoz servisi işlatilmaydi. Rus ovozi rusça, özbek ovozi özbekça çaqiradi. TV brauzeri ovozni qöllamasa, Windows kompyuterini HDMI orqali TVga ulang.

## Administrator va xodimlar

Administrator xizmatlar, oynalar va loginlarni boşqaradi. Beş operator uçun alohida login yarating va 1–5-oynalarni biriktiring. Har bir operator barça beshta bölimni va kutayotgan çiptalarni köradi: umumiy navbatdan, tanlangan bölimdan yoki aniq çiptani çaqiradi. Boşqa oynalardagi faol çiptalar ham körinadi. Bir oynada faol çipta bölsa yangisi olinmaydi; uni yakunlang yoki yönaltiring. Bir çiptani bir vaqtda ikki operator ololmaydi.

Çipta holatlari: kutiş → çaqirildi → xizmat boşlandi → yakunlandi. Faqat çaqirilgan çipta kelmadi deb belgilanadi. Çaqirilgan yoki xizmatdagi çipta boşqa faol xizmatga öşa raqam bilan yönaltiriladi. Ruxsat va holat ötişlari serverda tekşiriladi; SQLite tranzaksiyasi bir çiptani ikki xodimga berişni oldini oladi.

**Sozlamalar**: universitet nomi, PNG/JPEG logotipi, iş kunlari/vaqti, çipta prefiksi, kunlik yoki uzluksiz raqamlaş, printer, qoğoz kengligi, harakatsizlik va TV qatorlari. Keçadan ertalabga ötuvçi tungi iş oraliği qöllanmaydi. Raqamlaş butun universitet uçun umumiy, xizmatlar böyiça alohida emas. Eski çiptalar öçirilmaydi. Vaqt zonasi UTC+5, Asia/Taşkent.

Yuborilgan arxivdagi rasmiy logotip `web/assets/university-logo.png`, fon `web/assets/campus-background.png` sifatida özgartirilmasdan kiritildi. Barcha sahifalar nomi: **TOŞDÖTAU — elektron navbat tizimi**. Administrator yuklagan logotip ustuvor.

## Printer

Boşlanğiç rejim — brauzer / PDF sinovi. Çipta olinganda çop etiş oynasi oçiladi. Oyna bekor qilinsa, şu çiptani qayta çop etiş mumkin. **HTML / PDF körinişi** saqlaş uçun qulay. Çipta universitet nomi, xizmat, yirik raqam, sana-vaqt va yaratilgan paytdagi oldinda kutayotganlar sonini körsatadi; bu son şu xizmat uçun hisoblanadi.

Haqiqiy printer uçun Windows drayverini örnating, Sozlamalarda printer nomini aynan Windows’dagidek yozing va **Windows drayveri orqali dialogsiz** rejimini tanlang. Lokal server içidagi bosma işçisi `System.Drawing.Printing` orqali çop etadi; alohida tarmoq printer porti oçilmaydi. ESC/POS taxmin qilinmaydi.

Bosma topşiriği bazada saqlanadi. Xatoda yangi navbat yaratilmaydi. Qayta çop etiş mavjud çiptaga yangi bosma topşiriğini beradi. Server çop etiş paytida öçsa natija **noma’lum** deb belgilanadi; qoğozni tekşirmasdan avtomatik qayta çop etilmaydi. **Windows bosma navbatiga yuborildi** — qoğoz çiqqani kafolati emas. Printer modeli, drayveri, 80 mm qoğoz çetlari va jismoniy natija qurilmada tekşirilişi şart.

Windows xizmati LocalService hisobida işlaydi. Faqat şaxsiy foydalanuvçingizga örnatilgan printer unga körinmasligi mumkin; printerni xizmat hisobiga mavjud qilib sozlang.

## Windows yoqilganda avtomatik işlaş

Avval oddiy işga tuşiriş va barça qurilmalarni sinang. Keyin PowerShell’ni administrator sifatida oçib, loyiha papkasida:

```powershell
.\windows\install-autostart.ps1
```

Skript loyihani `C:\ProgramData\UniversitetNavbat` ga yangi örnatadi va yangi administrator parolini söraydi. Bu sinov papkasidagi bazani avtomatik köçirmaydi. Yangi örnatişni sozlang yoki quyidagi zaxira/tiklaş yöli bilan ma’lumotlarni köçiring. Mavjud papkani/xizmatni ustidan yozmaydi.

Skript serverni Windows xizmati sifatida avtomatik işga tuşirişni, nosozlikda qayta işga tuşirişni, joriy foydalanuvçi Windows’ga kirganda Edge kioskini va faqat Private/LocalSubnet uçun tanlangan TCP portini sozlaydi. Avtomatik Windows loginini sozlamaydi. Xizmat va baza foydalanuvçi kirmasidan işga tuşadi; kiosk foydalanuvçi kirgaç oçiladi.

```powershell
.\windows\install-autostart.ps1 -Port 8080 -BindAddress 0.0.0.0
```

PowerShell faylni yuklangan deb bloklasa, uning Properties oynasida Unblock belgilang; imzo/TLS tekşiruvlarini öçirmang. Domen siyosati skriptni man qilsa, tizim administratoriga murojaat qiling. Pythonning barça foydalanuvçilar uçun örnatilgani va LocalService undan foydalana olişini tekşiring.

Avtomatik işga tuşirişni olib taşlaş:

```powershell
.\windows\uninstall-autostart.ps1
```

Baza va audio fayllar öçirilmaydi. Skriptlar şu Linux muhitida Windows’da bajarilib tekşirilmagan.

## Zaxira va tiklaş

`data/queue.db` çiptalar, sozlamalar, foydalanuvçilar, bosma holatlari va ovoz xaritasini saqlaydi. Audio yozuvlar `data/audio/` içida. `NAVBAT_DATA` muhit özgaruvçisi saqlaş manzilini özgartiradi. Bitta bazaga ikkita server bir vaqtda işga tuşmaydi.

Server birinçi işga tuşganda va keyingi har yangi Toşkent kunida SQLite backup API orqali zaxira oladi; şu papkadagi 14 ta eng yangi nusxa saqlanadi. `data/audio/` hamda kerakli nusxalarni vaqti-vaqti bilan boşqa diskka köçiring: bitta diskdagi nusxa disk buzilişidan himoya qilmaydi. Jurnal fayllari 1 MB dan, 3 ta eski fayl saqlanadi.

Qölda baza zaxirasi:

```sh
python app.py --backup
```

Tiklaşdan oldin serverni töxtating. Xizmat bölsa administrator PowerShell’da:

```powershell
Stop-Service UniversitetNavbat
```

Loyiha/örnatiş papkasida:

```sh
python tools/restore.py data/backups/tanlangan-nusxa.db
```

Tiklaş vositasi baza yaxlitligini va versiyasini tekşiradi, mavjud bazaning nusxasini saqlaydi va SQLite backup orqali tiklaydi. Audio uçun mos `data/audio/` nusxasini ham joyiga qaytaring. Söng serverni qayta oçing yoki:

```powershell
Start-Service UniversitetNavbat
```

## Hisobot hisoblaş qoidalari

Hisobot sana oraliği Toşkent böyiça çipta yaratilgan kuniga qarab tanlanadi, ikkala çegara kuni ham kiradi. Çiqarilgan — barça çiptalar; yakunlangan — hozirgi holati yakunlanganlar; kelmagan — hozirgi holati kelmaganlar; kutayotgan — hozir kutişda turganlar.

Örtaça kutiş: oxirgi çaqirilgan vaqt minus dastlabki yaratilgan vaqt, faqat çaqirilgan çiptalar böyiça. Qayta çaqiriş bu vaqtni almaştirmaydi. Örtaça xizmat: yakunlaş minus xizmat boşlanişi, faqat yakunlanganlar böyiça. Örtaçalar soniyada. Ma’lumot bölmasa «—». Xizmat kesimi çiptaning yakuniy/joriy xizmati böyiça; xodim kesimi oxirgi xizmat körsatgan xodim böyiça. Yönaltirilgan çiptada xizmat davomiyligi oxirgi bosqiçni, kutiş esa dastlabki yaratilişdan oxirgi xizmat çaqiruvigaça bölgan umumiy vaqtni bildiradi. Yönaltirişlar alohida yangi çipta sifatida sanalmaydi. Hodisalar tarixi bazada saqlanadi.

## Sinovlar

```sh
python -m unittest discover -s tests -v
node tests/test_announcer.js
node tests/test_recordings.js
node tests/test_flasher.js
node --check web/app.js
```

Python testlari vaqtinçalik bazalarda işlaydi. Node faqat dasturçi sinovlari uçun; terminalda talab qilinmaydi. Ixtiyoriy Playwright/Çromium brauzer sinovi:

```sh
node tests/smoke_browser.js
```

Playwright/Çromium ZIP içiga kiritilmagan. Dalillar va qurilmada qolgan sinovlar `VALIDATION.md` da.

## Yakuniy ekranlar va TV

Barcha ekranlarda yuborilgan moviy fon va rasmiy universitet logotipi bor. Terminalda beshta xizmat va UZ / RU / EN. Terminal, xodim va TVda sahifalararo navigatsiya yashirilgan. TVda yirik çaqiruv, oynalar va kutayotgan çiptalar körinadi. Har yangi çaqiruv va qayta çaqiruvda çipta/oyna **3 marta** yonib-öçadi (2,1 soniya); oddiy yangilanişda takrorlanmaydi. Kamaytirilgan animatsiya sozlamasida yumşoq yoruğlik pulsi işlatiladi.

Ovoz uçun `/tv-audio` sahifasida yoqib sinang va TVga öting. Bevosita `/tv` oçilsa ovozni yoqiş uçun ekranga bir marta bosiş mumkin.

## Excel, Word va PDF hisobotlari

Administrator → **Hisobotlar** → sana oraliğini tanlang → **Körsatiş** → **Excel**, **Word** yoki **PDF**. Fayllar internet va qöşimça Python paketlarisiz yaratiladi. Oddiy operator hisobot yuklay olmaydi.

Bir xil universitet şabloni: rasmiy logo, tizim nomi, davr va tayyorlangan vaqt (UTC+5), oltita umumiy körsatkiç, bölimlar va operatorlar kesimi, hisoblaş izohi. Excelda uç varaq: Umumiy, Bölimlar, Operatorlar; raqamlar hisoblaş uçun son sifatida saqlanadi. Word tahrirlanadi, PDF çop etiş uçun A4 albom shaklida. PDF şrifti va uning litsenziyasi `fonts/` içida.

Namuna fayllar faqat sinov maʼlumotlaridan iborat; haqiqiy hisobotda bazadagi tanlangan davr maʼlumotlari olinadi. Windows, termoprinter, TV karnayi va tarmoq ruxsatlari öz qurilmangizda sinaladi.

## KPOS_80 Printer(1): tugmani bosib avtomatik çek oliş

Windows’da aynan `KPOS_80 Printer(1)` drayveri mavjud bölsa, server ishga tushganda brauzer/PDF rejimidan Windows dialogsiz rejimiga avtomatik ötadi (80 mm). Avvaldan boshqa Windows printer tanlangan bölsa u özgarmaydi. Sektor bosilganda server çekni printer navbatiga yuboradi; brauzer çop etiş/PDF oynasi oçilmaydi.

Mavjud serverni qayta oçmasdan sozlash uçun `PRINTERNI_SOZLASH.cmd` faylini server kompyuterida ishga tushiring, terminal sahifasini **Ctrl+F5** bilan yangilang. Yoki Administrator → Sozlamalar: printer nomi `KPOS_80 Printer(1)`, rejim **Windows drayveri orqali dialogsiz**, qoğoz **80 mm**, Saqlash. Yangi sozlama avvalgi sinov çiptalarini qayta çop etmaydi.

Yangilash: serverni töxtating, eski `data` papkasining zaxirasini oling, yangi loyiha fayllarini ösha loyiha papkasiga köçiring; **data papkasini saqlang**. Söng `BOSHLASH.cmd`, kerak bölsa `PRINTERNI_SOZLASH.cmd`. Windows xizmatida esa örnatilgan papkadagi fayllarni yangilab xizmatni qayta yoqing. Printer shu xizmatning LocalService hisobiga ham körinişi kerak.

Logotip ostidagi oq oval olib taşlandi; logotip kök sarlavha ustida oq rangda körsatiladi; hisobotlardagi asl kök logo özgarmaydi. TV kutiş matni kichik ekranda ham qatorga bölinadi. Kiosk uçun `BOSHLASH.cmd` bilan oçing yoki brauzerda **F11** bosing. Haqiqiy TV natijasi uning ekran ölçami va brauzerida sinab köriladi.

## Oddiy terminal oqimi

Terminalda PDF/sinov yoki printer holati yozuvi yo‘q. Xizmat bosilganda faqat Windows printeriga bosma topşiriği yuboriladi; xizmat kartalari ekranda qoladi. Alohida çipta/PDF oynasi va «Çop etiş» tasdiği yo‘q. Yuborilayotganda tugmalar vaqtinça bloklanadi. Bosma navbatiga qabul qilingaç keyingi talabaga tayyor. Xatoda qisqa xabar va **öşa çiptani** qayta çop etiş tugmasi körinadi; yangi çipta yaratilmaydi. Printer sozlanmagan bölsa çipta çiqarilmaydi, xodimga murojaat xabari körinadi.

## Windows va X96ni avtomatik oçiş

Töliq ketma-ketlik **[KIOSK_VA_TV.md](KIOSK_VA_TV.md)** da. Windows serveri — xizmat; faqat terminalga ruxsat va avtomatik hisob — Windows 10 Pro/Enterprise/Education Assigned Access. Oddiy fullscreen bu çeklovni bermaydi. X96 — mos Android kiosk brauzerda `http://SERVER_IP:8080/tv?autostart=1`, bootda oçiliş, fullscreen va media autoplay. Maxsus APK şart emas.

Yangilangan xizmat örnatgichi loyiha ichidagi eski bazani/loginlarni/ovozlarni yangi örnatişga nusxalaydi; eski server avval töxtatilişi kerak. Eski örnatiş papkasi/xizmati ustidan yozmaydi. Oddiy fullscreen uçun `windows/install-display-autostart.ps1`, nashrni tekşiriş uçun `windows/check-kiosk.ps1`.

## Windows ilovasi (.exe)

Python/PowerShellsiz oson ishga tuşiriş uçun GitHub **Releases** ichidagi `TOShDOTAU-Setup.exe`. Örnatiş, eski bazani köçiriş, printer va Startup: **[EXE_BOSHLASH.md](EXE_BOSHLASH.md)**. EXE alohida Windows runnerida yig‘ilib, haqiqiy paket sinovi ötgaç tarqatiladi. Birinçi oçilişda parol ilova oynasida yaratiladi.
