# Bitta PowerShell: ovozlar + C → S + chek

Infokioskda mavjud navbat ilovasi ochiq tursin. ZIPni alohida papkaga chiqaring. Shu papkada PowerShell ochib bitta buyruqni bajaring:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\Update-All.ps1
```

1. C prefiksli bo‘lim topilsa, mavjud administrator login/parolini mahalliy so‘rovda kiriting. U S ga almashtiriladi; eski chiptalar saqlanadi.
2. Skript so‘raganda navbat ilovasini odatdagi administrator paroli bilan yoping, PowerShellda Enter bosing.
3. Ovoz va chek tuzatmalari o‘rnatilib, mavjud EXE bir marta qayta ochiladi.
4. F10 → Ovozlar → bir yo‘la biriktirish: S1–S500, sA/sB/sS/sD/sE va p1–p5 fayllarini tanlang. Tasdiqlash belgisini qo‘yib, biriktiring. Bu 510 yozuv foydalanuvchining o‘z ovoz fayllaridir; ular ZIP ichida emas. Oldin shu to‘plamni to‘g‘ri yuklagan bo‘lsangiz, yana yuklash shart emas.
5. TV ilovasini qayta oching. E012 ni 5-oyna chaqirsa E + S12 + p5 ketma-ketligi ishlaydi. Bitta chek chiqarib, universitet nomi to‘liq tushishini tekshiring.

Oldingi alohida patchlarni o‘rnatish shart emas. Ulardan biri oldin o‘rnatilgan bo‘lsa ham bu umumiy patchni ishlatish mumkin: o‘rnatilgan qismi takror almashtirilmaydi.

EXE qayta yig‘ilmaydi; baza, navbat tarixi, printer nomi, qog‘oz sozlamalari va LED saqlanadi. Zaxiralar EXE papkasidagi audio-patch-backups va receipt-patch-backups ichida. Butun paket hash orqali ish boshlashdan oldin tekshiriladi. Jarayon to‘liq tugamasa, ilova avtomatik ochilmaydi; xabarni tekshiring va ayni buyruqni qayta bajaring. C → S saqlangan bo‘lsa qayta yozilmaydi. Tuzatmalar ketma-ket bajariladi; oldingi muvaffaqiyatli qadam xato tufayli avtomatik bekor qilinmaydi.

Noodatiy papka uchun:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\Update-All.ps1 -AppPath 'C:\Sizning papkangiz\TOShDOTAU'
```

C → S ni bajarmaslik uchun `-SkipRename`. Alohida tuzatmalar va qaytarish tartibi audio/README.md va receipt/README.md ichida. Ilova yopiq bo‘lsa qaytarish buyruqlari:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\audio\Update-Audio.ps1 -Restore -NoStart
powershell -NoProfile -ExecutionPolicy Bypass -File .\receipt\Update-Receipt.ps1 -Restore
```

Qaytarish C/S biznes sozlamasini va yuklangan ovozlarni o‘zgartirmaydi.

Tekshiruv: ikkala tuzatma birgalikda, takroriy o‘rnatish, zaxira, fayllar to‘g‘riligi va mavjud API orqali C → S; eski C001 saqlanib, keyingi S002 yaratilishi tekshirildi. PowerShell 7.4/Linux ishlatildi. Haqiqiy Windows GDI/KPOS va TV ovozining apparat tekshiruvi bu muhitda bajarilmadi.
