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
