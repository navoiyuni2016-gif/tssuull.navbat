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
