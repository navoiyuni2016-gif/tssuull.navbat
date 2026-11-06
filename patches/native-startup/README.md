# Brauzer o‘rniga mavjud EXE’ni avtomatik ochish

Eski windows/kiosk.ps1 kodi Edge brauzerini cheksiz qayta ochish siklida ishlatgan. Uni windows/install-autostart.ps1 `UniversitetNavbatKiosk`, windows/install-display-autostart.ps1 esa `UniversitetNavbatDisplayTerminal` rejalashtirilgan vazifasi orqali ishga tushirishi mumkin. Shu sabab shell:startup bo‘sh bo‘lsa ham brauzer ochiladi. Bu kompyuterda aynan qaysi vazifa borligini hali mahalliy tekshirish kerak; skript faqat ushbu ikki aniq nomdagi mavjud vazifalar bilan ishlaydi.

## Ishlatish

1. Infokioskdagi odatdagi Windows foydalanuvchisida ZIPni alohida papkaga chiqaring.
2. Shu foydalanuvchi hisobida PowerShell’ni **administrator sifatida** oching. Bu eski himoyalangan Scheduled Task’ni o‘chirish uchun kerak; ilovaning o‘zi standart foydalanuvchi sifatida ishlaydi. Boshqa administrator hisobiga kirmang.
3. ZIP papkasiga o‘ting va bajaring:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\Enable-NativeStartup.ps1
```

EXE papkasi avtomatik topilmasa, papka yo‘lini kiriting. Yoki:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\Enable-NativeStartup.ps1 -AppPath 'C:\Sizning papkangiz\TOShDOTAU'
```

4. Skript yakunida kompyuterni odatdagidek qayta yoqing. Hozir ishlayotgan eski brauzer sikli majburan o‘ldirilmaydi; qayta yuklanganda o‘chirilgan vazifa qayta ishga tushmaydi.
5. Windows hisobiga kirgach Startup yorlig‘i TOShDOTAU.exe --kiosk ni ochadi. Windows parol so‘rasa avval hisobga kirish kerak. Bu skript avtomatik login yoki Windows kiosk cheklovini sozlamaydi.

## Nima o‘zgaradi

- Faqat mavjud `UniversitetNavbatKiosk` va `UniversitetNavbatDisplayTerminal` vazifalari XML zaxirasi olinib Disable qilinadi. Vazifalar o‘chirilmaydi.
- Joriy foydalanuvchining Startup papkasidagi TOShDOTAU.lnk mavjud EXE’ga --kiosk bilan yo‘naltiriladi. Avvalgi shunday yorliq bo‘lsa zaxiralanadi.
- Baza, printer, ovoz patchi, receipt patchi, EXE va uning resurslari o‘zgarmaydi. TV vazifasi va boshqa dasturlarning autostarti o‘zgarmaydi.
- Zaxira `%LOCALAPPDATA%\TOShDOTAU\startup-backups` ichida.
- Eski `UniversitetNavbat` server xizmati topilsa faqat ogohlantirish chiqadi. Xizmat avtomatik to‘xtatilmaydi: unda boshqa bazadan foydalanilayotgan bo‘lishi mumkin. EXE «8080 port band» desa natijani yuboring; bazalar tekshirilmasdan xizmatni o‘chirmang yoki yangi baza yaratmang.

## Qaytarish

Startup papkasidagi TOShDOTAU.lnk ni olib tashlang yoki zaxiradagi avvalgi yorliqni qaytaring. Task Scheduler’da avval faol bo‘lgan eski terminal vazifasini qayta Enable qilish mumkin. Ikkala serverni bir vaqtda ochmang.

## Tekshiruv

Source windows/kiosk.ps1 terminal rejimi endi mavjud native EXE’ni bir marta ishga tushirib qaytadi, Edge sikliga kirmaydi. TV rejimi saqlangan. PowerShell testida native EXE yo‘li, --kiosk argumenti, bir martalik ishga tushish va ikki skript sintaksisi tekshirildi. Windows Task Scheduler/COM va haqiqiy qayta yuklash ushbu Linux muhitida tekshirilmagan.
