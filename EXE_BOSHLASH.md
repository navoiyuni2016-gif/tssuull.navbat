# TOŞDÖTAU — Windows EXE

Windows 10/11 **64-bit**. Python alohida örnatilmaydi; ilova bilan birga keladi. Internet faqat faylni yuklab oliş uçun kerak, tizim lokal işlaydi.

## Örnatiş

1. GitHub **Releases** sahifasidan `TOShDOTAU-Setup.exe` faylini oling.
2. Örnatuvçini oçing, Next → Install → Finish. Ixtiyoriy **Windowsga kirganda terminalni avtomatik oçiş** bandini belgilang.
3. Desktopdagi **TOShDOTAU** yorliğini bosing.
4. Birinçi marta kamida 12 belgili admin parolini ikki marta kiriting. Login: **admin**. Keyingi oçilişlarda parol yaratilişi söralmaydi.
5. Terminal Edge’da töliq ekranda oçiladi. Oddiy oynaga ötiş uçun Alt+F4; boşqaruv oynasida administrator, xodim, TV va printer tugmalari bor. Bu oddiy EXE rejimi OSni qulflamaydi; talabani faqat terminalda saqlaş uçun Windows Assigned Access alohida sozlanadi.
6. **Printerni sozlaş** → Windows’dagi `KPOS_80 Printer(1)`ni tanlang → Saqlaş. Yoki administrator panelidagi printer sozlamalaridan foydalaning. Ulangan qurilmada bitta çekni sinang.

Server fonda işlaydi; boşqaruv oynasini yopiş bazani öçirmaydi. Windows qayta yoqilganda ixtiyoriy Startup yorliği joriy foydalanuvçi kirgaç ilovani qayta oçadi. Bu Windows hisobiga avtomatik kiriş yoki tizim xizmati örnini bosmaydi. Töliq qulflangan boot rejimi alohida qurilma sozlamasi.

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
