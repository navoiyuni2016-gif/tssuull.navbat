# TOŞDÖTAU TV — X96 Android ilovasi

Ilova Windows’dagi mavjud navbat serveriga lokal tarmoq orqali ulanadi. Alohida baza yoki eski Baraka servisi kerak emas. Universitet logotipi, fon, beshta operator oynasi, kutayotganlar, uç marta yonib-öçiş va yuklangan ovozlar mavjud serverdan olinadi.

## Örnatiş

1. [TOShDOTAU-TV.apk](https://github.com/navoiyuni2016-gif/tssuull.navbat/raw/refs/heads/main/downloads/TOShDOTAU-TV.apk)ni yuklab oling. USB fleshka orqali X96ga köçiriş ham mumkin.
2. X96 File Manager’da APKni oçing. Söralsa şu fayl menejeriga **Install unknown apps / Nomaʼlum manbadan örnatiş** ruxsatini bering, söng **Install**. Eski Android’da bu **Settings → Security → Unknown sources** bölişi mumkin. Örnatişdan keyin bu ruxsatni öçirib qöyiş mumkin.
3. **TOŞDÖTAU TV** ilovasini oçing.
4. **Server IP**: Windows kompyuterining lokal IPv4 manzilini yozing. Masalan, `192.168.1.10:8080`. Bu faqat misol: öz kompyuteringiz IP manzilini kiriting. `127.0.0.1`ni yozmang — u TV boxning özi.
5. Sozlamalar uçun **4–8 raqamli PIN** yarating va takrorlang. Bu TV box sozlamalari PINi, serverdagi admin paroli emas.
6. **Saqlaş**ni bosing. TV sahifasi töliq ekranda, manzil satrisiz oçiladi.

Windows serverini ishga tuşiring. Windows va X96 bir routerga ulangan bölsin; Ethernet yoki Wi-Fi böladi. Windows firewall’da server ilovasiga **Private** lokal tarmoq uçun ruxsat bering. Server IP manzilini routerda doimiy qilib qöying. IP özgarsa MENU / BACK → PIN orqali yangilang.

## Box yoqilganda avtomatik oçiliş

Ilovada **Box yoqilganda avtomatik oçiş**ni belgilang. Android 10 va yangiroğida bootdan ilova oçiş çeklangan: **TOŞDÖTAU TV’ni standart Home / Launcher** qilib tanlang. Sozlamalar dialogidagi **Android / Home sozlamalari** yordam beradi. X96ga qarab **Settings → Apps → Default apps → Home app**, yoki pultda Home bosib ilovani tanlaş va **Always** ishlatiladi.

Ilovani örnatgandan keyin kamida bir marta oçib sozlang. Avtostartga proşivka ruxsati kerak bölsa **Autostart**ni yoqing. Home sifatida tanlangan ilovani avtomatik oçirişni töxtatiş uçun Android sozlamalarida boşqa Home/Launcher tanlang; faqat checkboxni öçiriş Android Home tanlovini almaştirmaydi.

Eski Baraka ilovasi ham avtostart qilsa, yangi ilovani sinab körgaç eski avtostartni öçiring yoki Home tanlovini almaştiring. Eskisini sinov tugamagunça öçiriş şart emas.

Tokdan uzib qayta yoqib sinang. Ayrim X96 proşivkalari bootdagi ilova oçilişini çeklaydi; real qurilmada tasdiqlanişi kerak. TV yoqilişi X96ni har doim qayta yoqmaydi: doimiy quvvatdagi boxda ilova avvaldan oçiq qoladi. HDMI-CEC va uyqu sozlamalarini tekşiring.

Bu ilova standart launcher sifatida ishlaşi mumkin, lekin Android’ning administrator Device Owner / qulflangan Lock Task rejimi örnini bosmaydi.

## Ovoz va qayta ulaniş

TV manzili avtomatik `/tv?autostart=1` bilan oçiladi. Ilova WebView’da media autoplayga ruxsat beradi; serverga yuklangan yozuvlar ekran bosilmasdan yoqiladi. Administrator panelida barcha zarur ovozlar avval yuklangan bölsin. Ovoz sozlamalari va karnayni bir marta sinang.

Ilova ekran uyquga ketmasligini söraydi. Server ilk oçilişda topilmasa **har 5 soniyada** qayta urinadi; tarmoq qaytganda ham qayta ulanadi. Ishlayotgan sahifadagi jonli çaqiruv va aloqa server frontendining polling mexanizmi bilan davom etadi. IP va PIN ilova yopilganda saqlanadi.

## Pult bilan boşqariş

- **MENU** yoki **BACK** → PIN → server manzili / sozlamalar.
- Notoğri PIN beş marta kiritilsa 30 soniya kutiş kerak.
- **Android / Home sozlamalari** — launcher tanlaş yoki tizimga xizmat körsatiş.
- PIN unutilsa Android’da ilova maʼlumotlarini tozalaş IP/PINni ham öçiradi; söng qayta sozlang.

## Moslik va maʼlumotlar

Android **5.0+**, ishlaydigan va yangilangan **Android System WebView** kerak. Eski proşivkadagi eskirgan WebView zamonaviy TV JavaScriptini oçolmasligi mumkin; uni rasmiy manbadan yangilang. Ilova ARM32/ARM64 va boshqa arxitekturalarga mos: native CPU kutubxonasi yo‘q. X96ning Android versiyasi va HDMI ölchami hali shu qurilmada sinaladi.

Faqat private lokal IPv4 manzillari (10.*, 172.16–31.*, 192.168.*) qabul qilinadi. Tasodifiy saytlar, mahalliy fayllar va boşqa serverga ötiş bloklanadi. HTTPS xatolari çetlab ötilmaydi. PIN matn körinişida saqlanmaydi; ilova backup’i öçirilgan. Android ilova serverdagi çiptalar bazasini özida saqlamaydi.

## Yig‘iş va imzo

GitHub Android workflow Java/Gradle orqali APK yig‘adi; manzil tekşiruvlarini va Android emulatorda WebView, fullscreen, PIN, server qaytganda tiklaniş va gesturesiz audio ijrosini sinaydi. CI faqat imzosiz build ZIPni prerelease qiladi — uni örnatmang. Foydalanuvçi uçun `downloads/TOShDOTAU-TV.apk` haqiqiy alohida release kaliti bilan imzolangan nusxa. Maxfiy imzo kaliti GitHub’ga kiritilmaydi va keyingi yangilanişlar uçun xavfsiz saqlanişi kerak.
