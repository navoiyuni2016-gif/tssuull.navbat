# EXE ni almashtirmasdan ovozlarni tuzatish

Infokioskning o‘zida bajaring. Navbat ilovasi ochiq tursin. ZIPni alohida papkaga chiqaring, shu papkada PowerShell ochib bajaring:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\Update-Audio.ps1
```

1. C → S uchun mavjud administrator login/parolini mahalliy so‘rovda kiriting. Parolni chatga yubormang.
2. Skript so‘raganda navbat ilovasini odatdagidek administrator paroli bilan yoping, keyin PowerShellda Enter bosing. Ilova qayta ochiladi.
3. F10 → Ovozlar → «sN / pN fayllarini bir yo‘la biriktirish» bo‘limiga kiring.
4. S1.wav–S500.wav, sA.wav, sB.wav, sS.wav, sD.wav, sE.wav va p1.wav–p5.wav fayllarini birga tanlang (jami 510 fayl). Fayl nomidagi katta/kichik harflar farq qilmaydi. Huquq tasdig‘ini belgilang va «Tanlangan ovozlarni biriktirish»ni bosing. Tugaguncha kuting.
5. TV ilovasini qayta oching, kerak bo‘lsa ovozni yoqing va sinang.

E012 ni 5-oyna chaqirsa: E + S12.wav + p5.wav ijro etiladi. 001 uchun S1.wav ishlatiladi; oldidagi nollar aytilmaydi. Barcha harflar bitta umumiy S1–S500 to‘plamidan foydalanadi. p1–p5 fayllarida tegishli oynaga chaqirishning to‘liq iborasi bo‘lishi kerak. Noto‘g‘ri biriktirilgan digit_1=p1 kabi eski yozuvlar bu rejimda ishlatilmaydi. Yetishmagan son fayli aniq ko‘rsatiladi; faqat harf aytib qolmaydi. default.wav/default2.mp3 avtomatik taxmin bilan biriktirilmaydi.

C → S faqat bo‘limning yangi chiptalariga taalluqli. Eski C chiptalari va tarix saqlanadi. Umumiy raqamlash davom etadi. S boshqa bo‘limda band bo‘lsa, skript xabar beradi.

EXE, baza, printer, LED va mavjud ovoz fayllari o‘chirilmaydi. Ikki web fayl almashtiriladi. Zaxira EXE papkasidagi audio-patch-backups ichida saqlanadi. Noodatiy o‘rnatish yo‘li uchun:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\Update-Audio.ps1 -AppPath 'C:\Sizning papkangiz\TOShDOTAU'
```

Faqat ovoz patchi, C → S ni bajarmasdan: `-SkipRename`. Oldingi web fayllarini qaytarish (ilovani avval yoping):

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\Update-Audio.ps1 -Restore
```

Qaytarish S prefiksini va yuklangan ovozlarni o‘zgartirmaydi. Zarur bo‘lsa prefiksni Xizmatlar panelidan tahrirlang.

Tekshiruv: 9 yozilgan ovoz testi, 5 sintez ovoz testi, brauzer sinovi, 510 faylni haqiqiy API orqali biriktirish va E012 → 5-oyna ijro tartibi. PowerShell 7.4/Linuxda fayl almashtirish, takroriy ishga tushirish, zaxiradan tiklash va haqiqiy mahalliy API orqali C → S tekshirildi. Windows 10 PowerShell 5.1 va haqiqiy TV ovozi ushbu muhitda tekshirilmagan. Sinov WAVlari sun’iy; sizning yozuvlaringizning nutq mazmuni alohida tinglab tekshiriladi.
