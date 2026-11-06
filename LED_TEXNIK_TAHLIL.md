# LED tablo: birinçi bosqiç tahlili va integratsiya rejasi

2026-11-06. Manba: foydalanuvçi yuborgan 5-oyna surati va mavjud yuklangan fayllar.

## Tasdiqlangan maʼlumot

- Suratda 5-oynaga qöyilgan, tört belgili segmentli tablo körinadi. Uning orqa yorliği, kontrolleri, kabeli va porti körinmaydi.
- Mavjud «Новая папка.rar» ichida faqat `IMG_2919.PNG` va `Изображение ChatGPT 5 нояб. 2026 г., 16_18_00.png` rasmlari bor.
- `HardwareService`, `QueueServiceHost`, `QueueAdminService`, `SyncronService`, `QInfoPanel`, `control` dastur/konfiguratsiyalari hozirgi yuklangan fayllar va loyiha manbalarida topilmadi. Ularni tekşirilgan deb körsatib bölmaydi.

| Parametr | Dalil / holat |
|---|---|
| Model, ishlab çiqaruvçi | Aniqlanmagan |
| COM / RS-232 / RS-485 / USB / LAN / RF | Aniqlanmagan; rasmdan xulosa çiqarilmaydi |
| Qurilma IDsi | Aniqlanmagan; korpusdagi 5 — oyna yorliği, protokol manzili ekaniga dalil yo‘q |
| Buyruq freymi, kodirovka, checksum | Tasdiqlanmagan |
| Raqam va tozalaş buyruqlari | Tasdiqlanmagan |
| A–E prefikslarini aks ettiriş | Tasdiqlanmagan; segmentlar soni protokol alifbosini isbotlamaydi |

## Arxitektura

1. `display_adapter.py` mustaqil adapter: oyna–qurilma mosligi va navbatdagi buyruqlar bazada. Tasdiqlanmagunça faqat apparatsiz sinov adapteri; u port oçmaydi va tarmoqqa paket yubormaydi.
2. Operatorning çaqiruv/qayta çaqiruv hodisasi bilan bir tranzaksiyada kerakli oyna uchungina display vazifasi yoziladi. TV va amaldagi calls jadvali öz tartibida qoladi. LED xatosi çaqiruvni bekor qilmaydi.
3. Alohida işçi bazadagi vazifani oladi; holat va xato saqlanadi. Qayta çaqiruv alohida hodisa. Töxtab qolgan jo‘natiş avtomatik takrorlanmaydi.
4. Administrator → Elektron tablolar: oyna, qurilma IDsi, ulaniş turi, manzil, holat, sinov va tozalaş. Tasdiqlanmagan haqiqiy ulaniş rad etiladi.
5. Markaziy kontroller serverga ulangan bölsa — server adapteri; operator USB/COM portiga ulangan bölsa — keyingi bosqiçda har operatorga oyna bilan çegaralangan lokal agent. Bu tanlov haqiqiy ulaniş tasdiqlangandan keyin qilinadi. Hozir agent/transportni taxminan yoqiş mumkin emas.
6. Protokol hujjati yoki eski konfiguratsiyadagi dalil asosida transport, tezlik, adres, frame va checksum test vektorlari yoziladi. Prefiks/uzun raqamni kesiş, raqamga aylantiriş yoki xato bilan rad etiş siyosati apparat imkoniyatiga qarab aniqlanadi; A025 dan A ni yashirinça olib taşlaş mumkin emas.
7. Faqat shundan keyin haqiqiy qurilmaga nazoratli test, beshta oyna izolyatsiyasi va TV bilan sinxronlik sinovi bajariladi.

## Keyingi bosqiç uçun zarur manbalar

Eski `HardwareService` papkasi/arxivi va yonidagi `.config`, `.ini`, `.json` fayllar; mavjud bölsa boshqa sanalgan xizmatlar konfiguratsiyasi yoki ishlab çiqaruvçi protokol hujjati kerak. Tablo/kontroller orqa yorliği va ulaniş sxemasi apparatni aniqlashga yordam beradi. Fayllardagi parol/tokenlar oshkor qilinmaydi. Eski EXE/DLL işga tuşirilmaydi, pullik kod köçirilmaydi va litsenziya tekşiruvi çetlab ötilmaydi.

**Chegara:** apparatsiz modulni haqiqiy LED integratsiyasi tayyor deb talqin qilmang. Hozir protokol tasdiqlanmagan va jismoniy tablo sinovi bajarilmagan.

## Amalga oşirilgan xavfsiz birinçi bosqiç

`display_adapter.py`, SQLite `display_devices`/`display_jobs`, administratorning `/api/displays` API va Elektron tablolar menyusi, hodisali çaqiruv/qayta çaqiruv/tozalaş integratsiyasi qöşildi. Portlar faqat Windows registrydan o‘qiladi, port oçilmaydi. `mock` SQLite’da simulyatsiya qiladi; `serial`, `tcp`, `agent` — tasdiqlanmagan va bloklangan. Bu uchalasining haqiqiy transport/agent kodi yozilmagan; ulaniş tuzilişi aniqlangandan keyingi bosqiçga qoldi.

Haqiqiy EXEda apparatsiz oqim sinovi ötdi: https://github.com/navoiyuni2016-gif/tssuull.navbat/actions/runs/42176165897 . **windows-15** paketi shu sinov modulini öz ichiga oladi. Jismoniy LED tablosi sinalmagan. Kelgusi fizik protokol modulini amalga oşiriş hozir manba yetişmasligi sababli bloklangan.

## Yangi DLL va konfiguratsiya dalillari — 2026-11-06

Bu bölim avvalgi «fayllar yo‘q» inventarini yangilaydi. Endi `HardwareServiceSvc.dll` (221 696 bayt) va `HardwareServiceHost.exe.config` (4 316 bayt) yuborildi. `HardwareServiceHost.exe`ning özi va `Logs.rar` hali mavjud emas. Loglar böyiça 28 593 hodisa, COM2, tört belgi, 130–136 manzillar va A001–A003 misollari **foydalanuvçi bergan tahlil natijasi**; xom loglarsiz bu sonlar mustaqil qayta sanalmadi.

Tekşiriş: .NET metadata va CIL statik o‘qildi; DLL/EXE ishga tuşirilmadi, serial port yoki socket oçilmadi. Pullik dastur kodi yangi ilovaga köçirilmadi.

| Fayl | SHA-256 |
|---|---|
| HardwareServiceSvc.dll | `42018c6e909f7f68ee444ea7f242eccd644d4725ccf0ed5492b9ab5045d348f7` |
| HardwareServiceHost.exe.config | `49a9e479dfc47b8b2bc49b01c468e56c172f7366c1f886961cfc3d58c0359314` |

### Tasdiqlangan ichki aloqa

`HardwareServiceSvc.HardwareService.hwCallClient`, MethodDef token `0x0600000c`, RVA `0x20b0`. Quyidagi offsetlar dncil chiqarişidagi metod tanasi boşidan, 12 baytli header bilan birga hisoblangan:

- `isShowOnDisplay == true` bölganidagina display tarmoği ishlar (CIL body offset `0x50–0x59`).
- `0x77–0xa3`: TCP stream socket **127.0.0.1:7777**ga ulanadi. Bu LEDning LAN manzili emas, lokal oraliq dastur endpointi.
- `0xa9–0x102`: `.NET Encoding.Unicode.GetBytes` orqali UTF-16LE, BOMsiz, quyidagi matn yig‘iladi:

  `DisplayConnectionType%displaySegments%displayAddress%ticketNumber%port_name`

- Parametr ketma-ketligi metadata bilan tekşirildi: 6-port_name, 7-DisplayConnectionType, 8-displaySegments, 9-displayAddress, 10-ticketNumber, 11-deskNumber. CIL argument raqamlari instance metodidagi `this`ni ham hisoblaydi.
- `0x109–0x11e`: `Socket.Send`, so‘ng Shutdown/Close. Shu tarmoqda javobni o‘qiş/ACK tekşirişi yo‘q. Bu fizik qurilma ACK mexanizmi yo‘q degani emas — uni lokal qabul qiluvçi bajarishi mumkin.
- `deskNumber` ushbu display xabariga kiritilmaydi. Qurilma manzili va oyna mosligi chaqiruvçi/konfiguratsiyadan keladi; 130→1 deb taxmin qilinmaydi.
- Logdagi `sendToTCPdisplayData` nomi shu metoddagi log matni sifatida mavjud. Uning nomi fizik tablo TCPda ekanini isbotlamaydi.

Masalan, faqat parametrlarni `0, 4, 130, A001, COM2` deb olsak, **lokal IPC** xabari:

`0%4%130%A001%COM2`

UTF-16LE baytlari:

```text
30 00 25 00 34 00 25 00 31 00 33 00 30 00 25 00
41 00 30 00 30 00 31 00 25 00 43 00 4F 00 4D 00 32 00
```

Bu baytlar **COM2 yoki LEDga yuboriladigan freym emas**. Ularni bevosita qurilmaga yuboriş mumkin emas. Misol tekşirilgan xabar yig‘iş qoidasi böyiça hisoblangan; xom logdan yoki apparatdan olingan capture emas.

### Konfiguratsiya va nomaʼlumlar

`appSettings`da **displayOut=0**, **displayOutIsCOM=true** mavjud. WCF/HTTP konfiguratsiyasida `http://localhost:8081/HardwareService` endpointi ham bor; bu navbat serveri `172.20.20.26:8080` yoki LEDning porti emas.

| Savol | Hozirgi dalil / javob |
|---|---|
| DisplayConnectionType=0 transporti | DLL uni tarmoqqa oddiy raqam sifatida ötqazadi; COM/TCP enum tarjimasi yoki switch shu tarmoqda yo‘q. displayOutIsCOM=true COM yo‘lini körsatadigan konfiguratsiya dalili, lekin bu kalit va metod parametrining aynan bir enum ekanini receiver/caller kodisiz tasdiqlab bölmaydi. |
| COM2 baud/parity/data bits/stop bits | Tasdiqlanmadi. Configda bu qiymatlar yo‘q. DLL TypeRef ro‘yxatida SerialPort/System.IO.Ports mavjud emas. DisplayMessage’da baudRate xossasi bor, ammo hwCallClient uni yubormaydi va serial portni ochmaydi. 9600/8N1 deb taxmin qilinmaydi. |
| 130–136 → operator oynalari | Moslik nomaʼlum. 130,131,132,133,134,135,136 manzillarining har biri uçun oyna IDsi xom logdagi juftlik yoki eski navbat konfiguratsiyasidan olinishi kerak. Yettita manzilni beshta oynaga tartib böyiça biriktirish mumkin emas. |
| Fizik freym/CRC/checksum/kodlash | DLLdan topilmadi: u oraliq TCP xabarini yuboradi. Kerakli parser/encoder 7777-port qabul qiluvçisida yoki uning kutubxonasida. |
| Raqam chiqarish | Lokal IPC matn qoidasi tasdiqlandi; fizik buyruq hali tasdiqlanmadi. |
| Tozalaş | HardwareService metodlarida alohida LED clear funksiyasi topilmadi. Böş matn/0000/space fizik tozalaş ekaniga dalil yo‘q; sinab yuborilmaydi. |
| Ishlab çiqaruvçi/model | Hali nomaʼlum. .NET assembly nomi qurilma modelini bildirmaydi. |

### Keyingi aniq qadam

`HardwareServiceHost.exe` va **7777-portni tinglaydigan DisplayProcessing dasturi** (agar alohida EXE bölsa, öşa fayl), yonidagi konfiguratsiya hamda xom `Logs.rar` kerak. DLL tashqi `TicketProcessing` assemblysiga ham havola qiladi; receiver o‘sha DLLga delegatsiya qilsa, u ham tekşiriladi. Xom loglarda `deskNumber/displayAddress/DisplayConnectionType/port_name` juftliklari qidiriladi, keyin receiverning serial ochish va freym yozish yo‘li kuzatiladi. Parol/token/litsenziya maʼlumotlari hisobotga köçirilmaydi.

**Hozirgi ilova holati:** faqat apparatsiz sinov faol. Tasdiqlangan narsa eski jarayonlar örtasidagi ichki transport; mustaqil fizik LED encoder hali tasdiqlanmagan. Eski pullik jarayonga ulaniş yangi tizimning yechimi sifatida qöşilmadi. COM/IP/agent blokirovkasi saqlandi; taxminiy qurilma buyruği yuborilmadi. Operator/TV sinxron hodisalari mavjud outbox orqali tayyor, fizik transport dalil topilgandan keyin qöşiladi.

### Katta arxiv bo‘yicha çegara

Keyin yuborilgan `HardwareService.rar` executor transfer çegarasidan (**32 MiB**) katta bölgani sababli yuklab olinmadi. Bu arxivning içi tahlil qilinmadi. `HardwareServiceHost.exe`ni alohida yoki kerakli dastur/DLL/config/loglarni har biri 32 MiBdan kichik arxivlarda yuboriş kerak. Avval olingan 221 696 baytli DLL va 4 316 baytli config tahlili amalda qoladi. Hozirgi **windows-16** paketida ham fizik LED transportlari bloklangan.
