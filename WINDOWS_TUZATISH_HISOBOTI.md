# Windows ilovasi va printer — tekşiriş hisoboti

## Natija

Mavjud loyiha saqlandi: HTML/CSS dizayn, rasmlar, xizmatlar, operatorlar, statistika va SQLite bazasi qayta yozilmadi. Yangi Windows oynasi pywebview/WebView2 orqali shu interfeysni oçadi. Chrome yoki Edge brauzer oynasi işga tuşirilmaydi.

- Terminal töliq ekran; F10 alohida administrator oynasini oçadi. Kioskni yopiş administrator parolini talab qiladi.
- Administrator cookie-si kiosk profiliga ötmaydi. Ikkinçi nusxa yangi server oçmaydi; ilova yopilsa HTTP server, bosma işçisi va zaxira oqimi töxtaydi.
- Windows 10/11 x64. Python, VS Code va Chrome alohida kerak emas. WebView2 Runtime yo‘q bölsa Setup uni Microsoft örnatuvçisi orqali örnatadi; shu birinçi örnatişga internet kerak bölişi mumkin.
- Baza `%LOCALAPPDATA%\TOShDOTAU\Navbat\data\queue.db`da; ovozlar va zaxiralar ham shu doimiy data papkasida. `_internal` yoki vaqtinçalik PyInstaller papkasida emas.
- Boshqa lokal qurilmalar `http://SERVER_IP:8080/staff`, `/admin`, `/tv?autostart=1` orqali ulanadi. X96 APK özgarishi şart emas; backend yangilangandan keyin TV ilovasini qayta oçing.

## Printer va çek

Birinçi yangi EXE oçilişida `windows / KPOS_80 Printer(1) / 80 mm` qiymatlari bazaga bir marta saqlanadi. Keyingi qölda özgartirilgan qiymatlar saqlanadi. Validation umumiyligicha qoldi: rejim html/windows, nom satr, Windows rejimida nom böş emas, kenglik 58–100 mm.

Xizmat tanlanganda bitta çipta va bazada bosma vazifasi yaratiladi. Windows Spoolerga System.Drawing.Printing orqali yuboriladi; Ctrl+P/PDF oynasi çiqmaydi. Chekda universitet, xizmat, yirik navbat raqami, sana-vaqt va kutayotganlar soni bor.

`preview`, `pending`, `printing`, `printed`, `failed` holatlari birxil qo‘llanadi. Natija noaniq bölgan uziliş `uncertain`ga ötadi va avtomatik qayta bosilmaydi. Qayta bosiş o‘şa çiptani saqlaydi; retry token va oldingi job ID takroriy sörovdan himoya qiladi. Windows navbatida shu hujjat hali turgan bölsa yangi nusxa yuborilmaydi. `printed` — spooler qabul qilgani; fizik qoğoz tasdiği emas.

Administrator → Sozlamalar’da printerlarni aniqlash, drayver/port/Windows hisobi, Spooler, oxirgi vazifa xatolari, alohida sinov çeki va qayta çop etiş mavjud. Sinov cheki navbat/statistikaga kirmaydi. Start menyusidagi Diagnostika apparatsiz JSON hisobot saqlaydi; parollar va bosma request tokenlari hisobotga kiritilmaydi.

## Bölim harflari

| Harf | Bölim |
|---|---|
| A | Talabalarga xizmat körsatiş |
| B | Ilmiy va innovatsion faoliyat |
| C | Xalqaro aloqalar va akademik mobillik |
| D | Marketing va amaliyotlar |
| E | Buxgalteriya |

Administrator → Xizmatlar → Bölim harfi: 1–3 katta lotin harfi, ikki xizmatga bir xil harf berilmaydi. Eski çiptalar özgarmaydi. Raqam ketma-ketligi avvalgidek umumiy: A001, B002, C003. Yangi harflar uçun Ovozlar sahifasida tegişli yozuvlar yuklanadi; yetişmayotganlari körsatiladi.

## Özgarishlar

- `desktop_launcher.py`, `native_window.py`, `native_smoke.py`, `desktop_runtime.py`: native oyna, admin ajratilişi, jarayon/port hayot sikli, diagnostika, mavjud bazani köçiriş.
- `app.py`, `management.py`, `printer_adapter.py`, `runtime.py`: bosma navbati, validatsiya/migratsiya, retry himoyasi, bölim prefikslari, serverni töxtatiş. `windows_service.py`ning stop hodisasi bilan mosligi tekşirildi; faylga keraksiz özgarish kiritilmadi.
- `windows/print-ticket.ps1`, `windows/printer-info.ps1`: drayver orqali dialogsiz bosma va haqiqiy Windows diagnostikasi.
- `web/app.js`, `web/recordings.js`, `web/announcer.js`: mavjud admin uslubidagi printer/prefiks boshqaruvi, xato/retry, çiptadagi harfni ovozda aytiş. CSS/rang/logo/fon özgarmadi.
- `packaging/`, Windows workflow va testlar: universitet ikonkasini saqlaş, WebView2 tekşiruvi, PyInstaller/NSIS, haqiqiy EXEni tekşiriş.

## Qurilmada yakuniy tekşiriş

1. Eski ilova/serverni töxtating; çek bosilayotgan paytda majburan yopmang. Data papkasini zaxiralang.
2. Yangi Setup.exe’ni örnating. Oldin EXE işlatilgan bölsa mavjud data avtomatik olinadi; eski Python bazasi bölsa birinçi oçilişdagi köçirişni tanlang.
3. F10 → administrator → Sozlamalar → printerlarni yangilang. `KPOS_80 Printer(1)` va 80 mm ni tekşiring; sinov çekini bosing.
4. Terminalda har bir bölimni bosing: harfi töğri çek darhol çiqişini tekşiring.
5. Printer öçirilganda xabarni, ulab qayta bosişni va yangi navbat yaratilmasligini tekşiring. Windows navbatida eski hujjat qolgan bölsa avval uning natijasini tekşiring.
6. Ilovani parol bilan yoping va qayta oçing: baza saqlanişi, port band bölmasligi va lokal operator/X96 ulanişini tekşiring.

Haqiqiy KPOS_80 printer bu muhitga ulanmagan: fizik 80 mm çek, qog‘oz uzilişi, foydalanuvçi qurilmasidagi boot/OS qulfi va X96 apparat sinovi muvaffaqiyatli deb körsatilmadi. Native fullscreen Windows’dagi barcha boshqa dasturlarni bloklaydigan OS siyosati örnini bosmaydi.
