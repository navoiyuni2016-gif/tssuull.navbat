# WebView2 va yangi Windows oynasi

Yangi EXE Chrome/Edge brauzer oynasini oçmaydi. Terminal va administrator paneli **Microsoft WebView2** ichidagi alohida Windows oynalarida ishlar. Python, VS Code va Chrome alohida kerak emas.

Windows 10/11 x64 va .NET Framework 4.6.2+ talab qilinadi (yangilangan Windows 10/11da mavjud). Microsoft Edge WebView2 Runtime brauzer ilovasi emas, ichki render komponenti.

Setup.exe runtime mavjudligini tekşiradi. Mavjud bölmasa, paketdagi Microsoft imzosi tekşirilgan `WebView2Setup.exe` uni örnatadi. Runtime yo‘q kompyuterda **shu birinçi örnatişga internet kerak bölişi mumkin**. Keyin universitet tizimi lokal tarmoqda internetsiz ishlar.

Örnatiş xatosida loyiha örnatilgan papkadagi `WebView2Setup.exe`ni oçing, Microsoft örnatişini yakunlang va TOShDOTAU’ni qayta oçing. Tashkilot siyosati örnatişni bloklasa, administrator orqali rasmiy WebView2 Runtime örnatiladi; TLS yoki imzo tekşiruvini öçirmang. Maʼlumotlar `data` papkasida qoladi.

## Boşqariş

- Oddiy yorliq → terminal ilovaning töliq ekranli oynasida.
- **F10** → alohida administrator oynasi; login/parol talab qilinadi.
- **F11** → töliq ekran / oynali rejim.
- Start menyusidagi **Sozlamalar** yorliği ham administrator oynasini oçadi.
- Terminalni **Alt+F4** bilan yopishda administrator login/paroli söraladi. Yopilganda ichki server va yordamçi oynalar ham töxtaydi; bosma boshlangan bölsa uning natijasi bazaga yozilgunça jarayon yakunlanadi.
- Qayta ikki marta oçiş ikkinçi serverni yaratmaydi; mavjud oynaga ötiladi.

Windows Assigned Access / OS qulfi alohida sozlanadi: F11ning özi Windows’dagi boşqa dasturlarni bloklamaydi. Lokal qurilmalar `http://SERVER_IP:8080/staff` va X96 Android ilovasi orqali avvalgidek ulanadi. Infokiosk ilovasi yopilsa server ham töxtaydi.

## Yangilaş

Eski EXE versiyasi serverni fonda qoldirgan: yangilaşdan oldin Task Manager’da eski **TOShDOTAU.exe** jarayonlarini yakunlang. Buni çek bosilayotgan paytda qilmang. `data` papkasini zaxiralang, yangi Setup.exe’ni örnating. Yangi versiyada oddiy yopiş serverni ham töxtatadi.

## Printer

Birinçi yangi oçilişda `windows / KPOS_80 Printer(1) / 80 mm` boshlanğiç sozlama bazaga saqlanadi. Keyin administrator qölda özgartirgan qiymat saqlanadi; har oçilişda ustidan yozilmaydi.

Administrator → Sozlamalar → **Printer diagnostikasi**: Windows hisobi, Spooler, aniqlangan printer, drayver/port, oxirgi bosma holatlari. Tanlangan printerni yuqoridagi nom maydoniga ötkazib **Saqlaş**ni bosing. **Sinov çeki** navbat va hisobot statistikasiga kirmaydi. Haqiqiy qog‘ozni tekşirib, keyin kerak bölsa **shu çiptani qayta çop etiş**ni bosing.

Holatlar: `preview → pending → printing → printed` yoki `failed`. Jarayon natijasi nomaʼlum bölgan uzilişda `uncertain` saqlanadi va avtomatik takrorlanmaydi. `printed` Windows spooleriga qabul qilinganini bildiradi — qog‘oz çiqqanining apparat tasdiği emas. Xato tafsiloti bazada va diagnostikada körinadi.
