# EXE’da LEDni qölda sozlaş

COM va IP transportlariga umumiy blok yo‘q. **Töliq qo‘lda profil** saqlangan va Faol tanlangan bölsa, test, çaqiruv, qayta çaqiruv va tozalaş shu profil orqali yuboriladi. Model avtomatik aniqlanmaydi, shablonlar taxminan to‘ldirilmaydi. Oldingi versiyalardagi «faqat sinov/bloklangan» çegarasi ushbu qo‘lda profil rejimi bilan almashtirildi.

## Tartib

1. F10 → Administrator → Elektron tablolar → kerakli oyna.
2. Qurilma ID manzilini kiriting; bu oynaning korpusidagi raqam degani emas. Oyna va ID mosligini özingiz belgilaysiz.
3. **COM — qo‘lda profil** yoki **IP — qo‘lda profil**ni tanlang. COM porti server/EXE ishlayotgan Windows kompyuteriga tegishli. IP uchunda qurilma IPsi va **IP port** alohida kiritiladi.
4. «Qo‘lda port va protokol sozlamalari»ni oçing. COM uchun baud rate, data bits, parity, stop bits; har ikkala ulaniş uchun timeout (millisekund) majburiy. IP port 1–65535. Nomaʼlum serial parametrlar avvaldan 9600/8N1 qilib to‘ldirilmaydi.
5. Protokol → **Qo‘lda HEX shablon**. Qurilma hujjatidagi **raqam chiqarish** va **tozalaş** paketlarini yozing. Bu maydonlar buyruqning fizik baytlarini belgilaydi; eski localhost:7777 IPC matnini COMga qo‘ymang.
6. Faol → Saqlaş. Töliq/noto‘g‘ri profil kerakli maydonni bildiradi. Tayyor profilda «Qo‘lda profil tayyor — ulanish hali tekshirilmagan» körinadi.
7. Sinov raqamini yuboring. «Holatni yangilash» orqali vazifani köring va jismoniy tabloni tekşiring. So‘ng operator çaqiruvi avtomatik shu oynaning qurilmasiga yuboriladi.

EXE tarkibida COM uchun pyserial bor; alohida Python kerak emas. Manba Python nusxasida COM ishlatish uchun `python -m pip install pyserial==3.5` kerak. Agent rejimi hali amalga oşirilmagan; boshqa operator kompyuteridagi COM port markaziy serverdan bevosita oçilmaydi.

## HEX shablon sintaksisi

Oddiy HEX baytlar (00–FF) va quyidagi belgilar aralaştiriladi. Qavslar orasiga Python/buyruq kodi yozilmaydi, kod bajarilmaydi. Tayyor, taxminiy qurilma paketi berilmaydi.

| Belgi | Aniq maʼnosi |
|---|---|
| `{address8}` | IDning o‘nlik son qiymati, bitta bayt; 0–255 |
| `{address_ascii}` | ID maydonidagi ASCII matn |
| `{label_ascii}` | To‘liq çipta, masalan A025ning to‘rt ASCII bayti |
| `{number_ascii}` | Faqat oxirgi raqamlar, boshi 0 saqlanadi |
| `{number_le16}` | Oxirgi raqam qiymati, little-endian 2 bayt |
| `{number_be16}` | Oxirgi raqam qiymati, big-endian 2 bayt |
| `{window8}` | Oyna raqami bitta bayt |
| `{xor8}` | Oldingi baytlarning XOR8 nazorat bayti |
| `{sum8}` | Oldingi baytlar yig‘indisi mod 256 |
| `{modbus16}` | Oldingi baytlar Modbus CRC16, initial FFFF, polinom A001, natija little-endian |

Checksum boshlanish bayti — 0dan boshlangan indeks; böş/0 bo‘lsa paket başidan. Hisob faqat shu indeksdan checksum belgisi oldigacha bo‘lgan baytlarni oladi. Belgidan keyingi suffix hisobga kirmaydi. Har shablonda ko‘pi bilan bitta checksum. Qurilmadagi CRC qoidasi bunga mos bölmasa, shu variantni tanlab yubormang; kerakli encoder maʼlum bo‘lgach kengaytiriladi.

Avtomatik CR/LF, STX/ETX, kodirovka yoki checksum qöşilmaydi — faqat yozilgan shablon va tanlangan belgilar yuboriladi. Paket 1–512 bayt, çipta 1–12 katta ASCII harf/raqam; sig‘magan raqam yashirincha kesilmaydi. Tozalaş shabloni çipta/raqam belgilarini ishlatmaydi; qurilmaga kerakli bo‘sh belgilar HEXda yoziladi. Prefiksni yashirish faqat `{number_*}`ni ataylab tanlaganingizda amalga oşadi.

## Natija va fayl

- `configured` — profil to‘liq; qurilma ishlagani tasdiği emas.
- `sending` — yuborilmoqda; shu paytda profil o‘zgartirilmaydi.
- `sent` — transport yozuvi tugadi; fizik LED ko‘rinishi/ACK tekşirilmagan.
- `failed` — masalan, COM/IPni oçib bölmadi.
- `uncertain` — qisman yuboriş/timeout yoki yuboriş paytida restart. Özidan takror yuborilmaydi.
- `simulated` — apparatsiz sinov; hech qanday fizik bayt yo‘q.

Tablo xatosida operator va TV davom etadi. Faol profilda çaqiruv/qayta çaqiruv raqamni, yakunlash/kelmadi/boshqa xizmat yoki adminga yönaltiriş tozalaş paketini yuboradi. Har bir amal faqat o‘sha oynaga tegishli.

**JSONga saqlaş / JSONdan yuklaş** orqali barcha sozlamalarni zaxiralang. Versiya 1; 1 MBgacha. Import boshqa qurilma IDlarini saqlagan holda bir tranzaksiyada bajariladi, xatoda to‘liq qaytariladi. Tegilmagan oynalar saqlanadi. Sozlama almaşganda hali yuborilmagan eski vazifalar bekor qilinadi; tarix va navbat bazasi o‘chirilmaydi.

Bu manual drayverning sinovlari fizik LED modelini tasdiqlamaydi. Sizning COM2 tezligi, qurilma modeli, 130–136ning oynalarga mosligi va fizik shablonlar hali tasdiqlanmagan; mavjud dalillar [LED_TEXNIK_TAHLIL.md](LED_TEXNIK_TAHLIL.md)da.
