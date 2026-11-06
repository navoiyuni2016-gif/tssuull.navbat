# Chekda uzun nom kesilishini tuzatish

80 mm qog‘oz kengligi va termoprinter bosish maydoni bir xil bo‘lmasligi mumkin. Tuzatma Windows drayverining PrintableArea va HardMargin qiymatlarini hisobga oladi. Matnni o‘lchash va chizishda bir xil kenglik va StringFormat ishlatiladi. Universitet va xizmat nomi shu maydonda satrlarga bo‘linadi.

Infokioskda ZIPni alohida papkaga chiqaring. Shu papkada PowerShell ochib bajaring:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\Update-Receipt.ps1
```

Skript so‘raganda navbat ilovasini odatdagidek administrator paroli bilan yoping va Enter bosing. Skript print-ticket.ps1 faylini zaxiralab yangilaydi, so‘ng mavjud EXE’ni ochadi. EXE qayta yig‘ilmaydi. Baza, navbatlar, ovozlar, LED, printer nomi va 80 mm sozlamasi o‘zgarmaydi. Oldingi ovoz patchi bilan birga ishlaydi. Eski cheklar avtomatik qayta chop etilmaydi.

Agar papka topilmasa, TOShDOTAU.exe turgan papka yo‘lini kiriting yoki:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\Update-Receipt.ps1 -AppPath 'C:\Sizning papkangiz\TOShDOTAU'
```

Administrator printer diagnostikasidan bitta sinov chekini chiqaring. Universitet nomidagi «o‘zbek tili» va xizmat nomi to‘liq tushishini tekshiring. Takror chiqarishdan oldin Windows bosma navbatida eski vazifa qolmaganini tekshiring. Rasmda xizmat inglizcha chiqishi terminaldagi EN tanloviga bog‘liq; bu tuzatma til tanlovini o‘zgartirmaydi.

Zaxira EXE papkasidagi receipt-patch-backups ichida. Ilovani yopib, eski bosma skriptini qaytarish:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\Update-Receipt.ps1 -Restore
```

Dasturiy tekshiruv: 80/58 mm, tor bosish maydoni, apparat chetlari, noto‘g‘ri maydonni rad etish; installerning takroriy ishlashi, zaxira va tiklash; mavjud printer konfiguratsiyasi va navbat testlari. PowerShell 7.4/Linuxda bajarildi. Windows GDI va haqiqiy KPOS apparat bosmasi bu muhitda tekshirilmagan.
