# Windows 10 infokiosk va X96 televizor

Bir marta sozlanadi. Keyin server Windows yoqilganda xizmat sifatida ishga tushadi; kiosk hisobi avtomatik kirib faqat terminalni ochadi. X96 esa tarmoqdagi serverning TV sahifasini ochadi. Server kompyuteri va X96 bir LANda bolishi kerak.

## 1. Serverni Windows xizmatiga otkazish

Avval `data` papkasidan tashqi zaxira oling. Qora server oynasini yoping: eski server ishlayotganda nusxa kochirish rad etiladi. Python 3.12+ barcha foydalanuvchilar uchun ornatilgan bolsin.

Loyiha papkasida **PowerShell — Administrator** oynasini oching:

```powershell
.\windows\install-autostart.ps1
```

Yangi xizmat `C:\ProgramData\UniversitetNavbat` ga ornatiladi. Loyiha ichida eski `data\queue.db` bolsa baza, loginlar, sozlamalar va `data\audio` nusxasi kochiriladi; asl fayllar ozgarmaydi. Eski baza bolmasa yangi admin paroli soraladi. Mavjud xizmat/papka ustidan yozilmaydi. Eski baza zaxiralari asl papkada qoladi.

Server foydalanuvchi Windowsga kirmasdan ishga tushadi. Windows firewall faqat Private/LAN uchun ochiladi. LAN server IP manzilini routerda doimiy qiling. `BOSHLASH.cmd`ni xizmat bilan bir vaqtda ochmang.

Server allaqachon Windows xizmati sifatida ornatilgan bolsa bu ornatgichni qayta ishlatmang: xizmatni toxtatib, manba fayllarini yangilang va xizmatni qayta yoqing.

```powershell
Stop-Service UniversitetNavbat
# Yangilangan fayllarni ornatilgan papkaga kochiring; data papkasini saqlang.
Start-Service UniversitetNavbat
```

Printer `KPOS_80 Printer(1)` LocalService hisobiga ham korinishi kerak. Qurilmada bitta chek chiqarib sinang. Windows xizmatida printer topilmasa Windows drayverini barcha foydalanuvchilar uchun sozlang.

## 2. Faqat terminalga ruxsat: Windows Assigned Access

**Oddiy fullscreen / F11 boshqa dasturlarni bloklamaydi.** Haqiqiy cheklash uchun Windows 10 **Pro, Enterprise yoki Education**, yangilangan Microsoft Edge kerak. Home nashrida bu rejim yoq: Proga otish yoki mos boshqariladigan kiosk yechimi kerak. Windows tizimi va Edge qurilma uchun xavfsizlik yangilanishlarini olayotgan bolsin.

Nashrni bilish uchun:

```powershell
.\windows\check-kiosk.ps1
```

Windows 10 sozlamalarida:

1. **Settings → Accounts → Family & other users / Other users → Set up a kiosk → Assigned access → Get started**.
2. Alohida lokal kiosk hisobi yarating, masalan `NavbatTerminal`. Admin hisobini kiosk hisobiga aylantirmang.
3. Ilova sifatida **Microsoft Edge**ni tanlang.
4. Rejim: **As a digital sign or interactive display**. Public browsing rejimini tanlamang.
5. Manzil: **http://127.0.0.1:8080/**.
6. Hisobning avtomatik kirishini tanlang (sozlash oynasi/buildga qarab mavjud). Qayta yoqib kiosk hisobi avtomatik ochilishini tekshiring. Login oynasida qolsa auto sign-in shu qurilmada hali sozlanmagan; fullscreen vazifasi buni hal qilmaydi. Admin parolini Winlogon registriga ochiq matnda yozmang.
7. Elektr sozlamalarida elektrga ulanganda ekran ochishi/uyquni **Never** qiling.
8. **Restart** qiling. Server xizmati, avtomatik kiosk hisobi va terminal chiqishini sinang.

Bu rejimda talaba Edge terminali ichida qoladi; ish stoli, boshqa dasturlar va oddiy brauzer manzil satri ochilmaydi. Texnik xizmat uchun **Ctrl+Alt+Del → Sign out**, song alohida administrator hisobiga kiring. Admin kirish maʼlumotlarini faqat masʼul xodim saqlaydi. Kioskdan chiqish va tiklash yolini qurilmada sinang.

Assigned Access ishlagach oddiy admin loginidagi yordamchi fullscreen vazifasini ochirib qoyish mumkin:

```powershell
Disable-ScheduledTask -TaskName UniversitetNavbatKiosk
```

## 3. Faqat avtomatik fullscreen kerak bolsa

Qulflangan Assigned Access orniga ishlatilmaydi. Ushbu skript joriy foydalanuvchi Windowsga kirganda Edge terminalini ochadi, server/tarmoqni kutadi, brauzer yopilsa qayta ochadi. Windows parolini yoki auto sign-inni ozgartirmaydi.

```powershell
.\windows\install-display-autostart.ps1 -Server http://127.0.0.1:8080 -Mode Terminal
```

Faqat displey uchun Windows kompyuter ishlatilsa:

```powershell
.\windows\install-display-autostart.ps1 -Server http://192.168.1.10:8080 -Mode TV
```

`192.168.1.10` — misol; haqiqiy server IP bilan almashtiring. Skript joylashgan loyiha papkasini kochirmang. Bu Android X96 uchun skript emas.

## 4. X96: alohida yangi APK kerak emas

X96 oilasida turli Android versiyalari bor. Mos **kiosk brauzer** (masalan, Fully Kiosk Browser & App Lock) orqali mavjud TV sahifasi ochiladi. Ilovani rasmiy manbadan oling; ayrim kiosk/avtostart funksiyalari litsenziya talab qilishi mumkin. Model nomining ozi funksiyalarning proshivkada mavjudligini kafolatlamaydi.

Bir marta X96da sozlang:

1. X96ni server bilan bir routerga ulang; imkon bolsa LAN kabel ishlating.
2. Kiosk brauzer **Start URL / Home URL** maydoniga: **http://SERVER_IP:8080/tv?autostart=1**.
3. **Fullscreen / Immersive mode** — ON.
4. **Launch on boot / Start on boot** — ON.
5. **Keep screen on**, **Reload on network reconnect**, xato sahifani avtomatik qayta yuklash — ON (nomi ilovaga qarab farq qiladi).
6. **Media autoplay / Audio without user gesture** — ON. Administrator panelida barcha zarur ovozlar yuklangan bolsin. `autostart=1` TV ochilganda yozuvli ovozni avtomatik yoqishga urinadi; Android/WebView autoplayni bloklasa kiosk brauzer ruxsatini sozlash kerak. Avval oddiy `/tv-audio` sahifasida ovozlarni bir marta sinang.
7. Android sozlamalarida ushbu ilova uchun **Autostart**ga ruxsat bering, batareya optimizatsiyasini cheklamang; kerak bolsa kiosk ilovasini Home/launcher sifatida tanlang. Qaysi parametr borligi X96 proshivkasiga bogliq.
8. Chiqish/sozlamalar uchun xodim PINini qoying. Tarmoq uzilib qayta ulanishini va tokdan uzib yoqqanda avtomatik sahifa ochilishini sinang.

TVni yoqish X96ni har doim qayta yuklamaydi: X96 alohida adapterdan doimiy quvvat olsa TV yoqilganda avvaldan ochiq sahifa korinadi. Agar X96 uyquga ketsa HDMI-CEC / power-on sozlamasini tekshiring. TV yoki box ekran korinishini qisqartirsa HDMI resolution va overscan/display positionni sozlang.

X96 proshivkasi bootda ilova ochishni cheklasa mos launcher/kiosk ilovasi yoki boshqariladigan box kerak boladi; yangi sayt APKsi bu Android cheklovini oz-ozidan olib tashlamaydi. X96 Android versiyasi va proshivkasi qurilmada tekshirilmaguncha avtomatik boot natijasi tasdiqlanmaydi.

## Sinash

- Infokioskni qayta yoqing: parol/ish stolida toxtamasdan terminal chiqsin.
- Kiosk hisobida Windows tugmasi va Alt+Tab bilan boshqa dastur ochilmasin; admin chiqish yoli ishlasin.
- Bir xizmatni bosing: bittagina chek chiqsin, xizmatlar ekrani qolsin.
- X96/TVni ochirib yoqing: pultsiz TV sahifasi ochilsin; operator chaqirganda raqam uch marta yonsin va ovoz aytilsin.
- LAN uzilib tiklansa va server kech ishga tushsa sahifa ozidan tiklansin.

Windows Assigned Access, xizmat, Edge va X96ning real boot/HDMI/ovoz natijalari Linux muhitida bajarilmagan; qurilmada ushbu tekshirishlar shart.
