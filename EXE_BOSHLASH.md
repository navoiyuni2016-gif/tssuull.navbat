# TOŞDÖTAU — Windows EXE

Windows 10/11 **64-bit**. Python alohida örnatilmaydi; ilova bilan birga keladi. Internet faqat faylni yuklab oliş uçun kerak, tizim lokal işlaydi.

## Örnatiş

1. GitHub **Releases** sahifasidan `TOShDOTAU-Setup.exe` faylini oling.
2. Örnatuvçini oçing, Next → Install → Finish. Ixtiyoriy **Windowsga kirganda terminalni avtomatik oçiş** bandini belgilang.
3. Desktopdagi **TOShDOTAU** yorliğini bosing.
4. Birinçi marta kamida 12 belgili admin parolini ikki marta kiriting. Login: **admin**. Keyingi oçilişlarda parol yaratilişi söralmaydi.
5. Terminal brauzersiz, WebView2 ilova oynasida töliq ekranda oçiladi. F10 — alohida administrator oynasi; F11 — ekran rejimi. Alt+F4 bilan yopiş administrator parolini talab qiladi. Bu oddiy EXE rejimi OSni qulflamaydi; talabani faqat terminalda saqlaş uçun Windows Assigned Access alohida sozlanadi.
6. Printer qölda tanlanmaydi: EXE birinçi oçilişda `printer_mode=windows`, `printer_name=KPOS_80 Printer(1)`, `paper_width_mm=80`ni avtomatik saqlaydi. Eski bazadan köçirilgan printer sozlamasi ham shu qiymatlarga ötiladi. Windows’da aynan shu drayver örnatilgan bölsin. Ulangan qurilmada bitta çekni sinang. Printer vaqtinça öçiq bölsa sozlama qoladi, bosma xatosi körsatiladi; PDF oynasi oçilmaydi. Eski sinov çiptalari avtomatik qayta çop etilmaydi.

Server ilova oçiq paytda ishlar; ilova yopilsa server ham to‘ğri töxtaydi. Baza öçirilmaydi. Windows qayta yoqilganda ixtiyoriy Startup yorliği joriy foydalanuvçi kirgaç ilovani qayta oçadi. Bu Windows hisobiga avtomatik kiriş yoki tizim xizmati örnini bosmaydi. Töliq qulflangan boot rejimi alohida qurilma sozlamasi.

Ilova hozir raqamli imzolanmagan. Windows SmartScreen tanimagan publisher deb körsatişi mumkin; tashkilot siyosati man qilsa administrator orqali örnating. Örnatuvçi va tekşiriş uçun SHA256 fayli bir GitHub release ichida joylanadi.

## Eski bazani saqlaş

Eski `app.py` serverini avval töxtating, `data` papkasining zaxirasini oling. Yangi EXE birinçi oçilganda parol yaratmasdan **Eski data papkasidan bazani köçiriş**ni tanlang. Eski loyihadagi `data` papkasini körsating. Loginlar, sozlamalar, çiptalar va ovozlar köçiriladi; asl fayllar özgartirilmaydi. Mavjud yangi baza ustidan yozilmaydi.

EXE maʼlumotlari: `%LOCALAPPDATA%\TOShDOTAU\Navbat\data`. Loyiha yoki Downloads ichidagi papkaga boğliq emas. Örnatuvçi bazani tarqatmaydi va dasturni olib taşlaş bazani öçirmaydi.

Server oçilmasa eski PowerShell/app.py oynasini yoping: ikkala nusxa bir vaqtda 8080 portini işlatolmaydi. Xato tafsiloti `data\desktop-server.log` va `data\server.log`da.

## Boşqa qurilmalar

Xodim va X96 ilovaga LAN orqali ulanadi. Server IP manzilini routerda doimiy qiling. Windows firewall’da faqat işonçli **Private** lokal tarmoq uçun TOShDOTAU ilovasiga ruxsat bering. TV: `http://SERVER_IP:8080/tv?autostart=1`.

## Portativ nusxa

`TOShDOTAU-Windows.zip`ni töliq oçing va ichidagi `TOShDOTAU.exe`ni bosing. Yonidagi `_internal` papkasini ajratmang: u Python va lokal resurslarni saqlaydi. Bitta `.exe` faylini yolğiz köçiriş yetmaydi; oddiy örnatiş uçun Setup.exe tavsiya etiladi.

## Yangi EXEni yig‘iş

GitHub Actions → **Windows EXE** Windows runnerida manba testlarini bajaradi, PyInstaller orqali haqiqiy Windows EXE yaratadi, aynan yig‘ilgan EXE ichida Tk, SQLite, universitet rasmlari, shriftlar, uch hisobot formati va lokal HTTP serverni sinaydi. Ötgan paket NSIS örnatuvçisi va ZIP bilan Releases’ga joylanadi. Jismoniy printer va qurilmadagi Windows/X96 boot sinovi bunga kirmaydi.

Yangi native oyna, WebView2 örnatişi, yangilaş va diagnostika: **[WEBVIEW2_RUNTIME.md](WEBVIEW2_RUNTIME.md)**.

## Bölim harflari

Har bir bölimning öz harfi bor: dastlab beshta xizmatga A, B, C, D, E beriladi. Administrator → Xizmatlar → **Bölim harfi** orqali 1–3 katta lotin harfini kiriting va saqlang. Bir xil prefiks ikki bölimga berilmaydi. Avval çiqarilgan çiptalar özgarmaydi. Raqamlar avvalgidek umumiy ketma-ketlikda: A001, B002, C003; raqamlaşning kunlik/uzluksiz sozlamasi saqlanadi.

Yozib olingan ovoz rejimida yangi B, C, D, E harflari uçun ham ovoz fayllarini Administrator → Ovozlar orqali yuklang. Yetishmayotgan yozuvlar shu yerda körsatiladi. TV/X96 ilovasini yangilanişdan keyin qayta oçing.


## Hisobotlar va elektron tablolar

Hisobot kutiş/xizmat vaqtlarini minutda, har bir bölim va xodimning yakunlangan xizmatlar jamisini körsatadi. XLSX/DOCX/PDFda oq fondagi qora katakçali jadvallar bor; 0 natijali bölim/xodimlar ham çiqadi. Sana oralig‘i avvalgidek çipta yaratilgan kunga tegishli.

Administrator → **Elektron tablolar**: oyna, ID, ulaniş manzili va apparatsiz sinov. **Hozir faqat simulyator işlaydi**; u heç bir portga yozmaydi. COM/IP/agent sozlamasini saqlaş mumkin, lekin haqiqiy LED protokoli tasdiqlanmaganligi uçun yuboriş bloklanadi. `simulated` — apparatsiz sinov, jismoniy tablo emas. [Texnik dalillar va keyingi bosqiç](LED_TEXNIK_TAHLIL.md).
