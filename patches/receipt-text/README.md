# Chek matni va universitet nomining UZ/RU/EN tarjimasi

EXE qayta o‘rnatilmaydi. Hozirgi ovoz patchi, recordings.js, WAV/MP3 fayllar, navbatlar bazasi, printer nomi va qog‘oz sozlamalari saqlanadi. Faqat web/app.js, windows/print-ticket.ps1 va universitet tarjimalari uchun windows/university-names.json yangilanadi. Yangilashdan avval zaxira olinadi.

## O‘rnatish

Infokioskda navbat ilovasi ochiq tursin. ZIPni yangi alohida papkaga chiqaring. Shu papkada PowerShell ochib bajaring:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\Update-ReceiptText.ps1
```

Skript universitetning hozirgi to‘liq nomini mahalliy serverdan o‘qiydi. So‘raganda ilovani odatdagi admin paroli bilan yoping va Enter bosing. O‘zi qayta ochiladi. TV ilovasini ham qayta oching. Oldingi umumiy patchni yana o‘rnatmang: u eski chek skriptini qaytarishi mumkin.

Noodatiy o‘rnatish yo‘li:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\Update-ReceiptText.ps1 -AppPath 'C:\Sizning papkangiz\TOShDOTAU'
```

Standart mahalliy port 8080; boshqa port uchun -Server http://127.0.0.1:PORT. Skript masofadagi serverga administrator parolini yubormaydi, bazaga yozmaydi.

## Nima tuzatildi

- Backenddagi eski kod universitet nomini har uch tilga ham o‘zbekcha yuborgan. Source’da university_ru/university_en sozlamalari, API’da university_names va printer payloadida lang mavjud. Yangi sozlama kalitlari qo‘shilishi avvalgi nom/printer sozlamalarini almashtirmaydi.
- Eski EXE backendini almashtirish talab qilinmaydi. Unda lang yo‘q bo‘lsa, bosma skripti mavjud aniq ahead_label qiymati orqali UZ/RU/EN ni aniqlaydi, university-names.json dan nomni olib, TicketFile ichiga university va lang qiymatlarini GDI’dan oldin yozadi. Yangilangan backend bergan lang/university ustidan yozmaydi.
- Ekrandagi sarlavha osti nomi tilga mos. Eski EXE uchun tarjimalar installer tomonidan app.js ichiga kiritiladi. Yangi backendda API tarjimalari ustuvor.
- GDI’ning avtomatik satr bo‘lishi olib tashlandi. Har so‘z bosma maydonida o‘lchanadi, kerak bo‘lsa keyingi satrga o‘tadi. Har satr NoWrap/Trimming=None bilan alohida chiziladi. Belgilar yo‘qolmaganligi chizishdan oldin tekshiriladi.

Eski EXE’da RU/EN nomini qo‘lda tahrirlash zarur bo‘lsa, EXE papkasidagi _internal/windows/university-names.json ni UTF-8 formatida tahrirlang va ushbu skriptni qayta bajaring: avvalgi RU/EN qiymatlari saqlanib, ekranga ham kiritiladi. Source’dan yangilangan backendda uch nom administrator Sozlamalar panelida boshqariladi.

## Asl TicketFile va sababni aniqlash

Bir dona yangi chek chiqaring. Har bosmada quyidagi papkada oxirgi vazifa diagnostikasi yangilanadi:

```text
%LOCALAPPDATA%\TOShDOTAU\Navbat\data\print-diagnostics
```

NAVBAT_DATA maxsus yo‘lga sozlangan bo‘lsa o‘sha data/print-diagnostics ichida.

- last-input.json — printer worker bergan TicketFile’ning baytma-bayt asl nusxasi, o‘zgartirishdan oldin.
- last-effective.json — GDI uchun yakuniy university/lang ma’lumoti; TicketFile ham aynan shunga normallashtiriladi.
- last-text-check.json — asl/yakuniy universitet nomi, asl SHA256 va harflarning Unicode raqamlari. `k` = 107.
- last-layout.json — haqiqiy printer PrintPage hodisasida o‘lchangan bosma maydoni va aynan chizilgan satrlar. Printergacha xato bo‘lsa oldingi layout qolishi mumkin: nom/tilni last-effective bilan solishtiring.

Asl nom last-input.json ichida ham «o‘zbe» bo‘lsa — buzilish GDI’dan oldin. Asl/yakuniy nom va layout satrlarida «o‘zbek» to‘liq bo‘lib, qog‘ozda «o‘zbe» bo‘lsa — Windows GDI/drayver/apparat bosma tomoni. last-text-check.json va last-layout.json natijasini ko‘rib qaysi bosqich ekanini aniq ajratish mumkin. Faqat rasm asosida ushbu ikki sababdan birini tasdiqlash mumkin emas.

Qo‘lda faqat JSON tekshiruvi, hech qanday bosma yubormasdan (faylning alohida nusxasi bilan ishlating, skript uni normallashtiradi):

```powershell
powershell -NoProfile -File 'C:\ILOVA\_internal\windows\print-ticket.ps1' -TicketFile 'C:\TEST\ticket-copy.json' -InspectOnly
```

InspectOnly Spooler/GDI’ni ishga tushirmaydi va printed=false qaytaradi.

## Qaytarish

Ilovani yopib bajaring:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\Update-ReceiptText.ps1 -Restore
```

Oxirgi receipt-text-backups nusxasi qaytariladi. Baza va ovozlar o‘zgarmaydi.

## Tekshiruv va chegaralar

Python: 67 test, 65 muvaffaqiyatli, 2 faqat Windows EXE muhiti uchun o‘tkazib yuborildi. Haqiqiy TicketFile yozilishi tutib tekshirildi: «özbek» oxiridagi k saqlanadi; UZ/RU/EN payloadlari mos. Chromium’da til tanlovi, receipt HTML, mavjud navbat va audio oqimi tekshirildi. PowerShell’da asl UTF-8 JSON, legacy/yangi payloadlar, normallashtirish, apparatsiz inspect-only, backup/restore va ovoz faylining o‘zgarmasligi tekshirildi. Matn satrlash testi UZ/RU/EN, uzun so‘z va Unicode belgilarida yo‘qolish yo‘qligini tekshiradi.

Bu muhitda foydalanuvchining Windows/KPOS printeri ulanmagan. Uning avvalgi TicketFile fayli dastur tomonidan o‘chirilgan va bu yerda mavjud emas. Shuning uchun aynan rasmdagi chekning apparat sababini tasdiqlangan deb bo‘lmaydi; yuqoridagi haqiqiy diagnostika shu bo‘shliqni to‘ldiradi. GDI/drayver/apparat yakuniy tekshiruvi o‘rnatilgach bajariladi.
