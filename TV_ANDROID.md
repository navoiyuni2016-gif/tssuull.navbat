# TOŞDÖTAU TV — X96 Android ilovasi

Ilova Windows’dagi mavjud navbat serveriga lokal tarmoq orqali ulanadi. Alohida baza yoki eski Baraka servisi kerak emas. Universitet logotipi, fon, beshta operator oynasi, kutayotganlar, uç marta yonib-öçiş va yuklangan ovozlar mavjud serverdan olinadi.

## Örnatiş

1. [TOShDOTAU-TV.apk](https://github.com/navoiyuni2016-gif/tssuull.navbat/raw/refs/heads/main/downloads/TOShDOTAU-TV.apk)ni yuklab oling. USB fleshka orqali X96ga köçiriş ham mumkin.
2. X96 File Manager’da APKni oçing. Söralsa şu fayl menejeriga **Install unknown apps / Nomaʼlum manbadan örnatiş** ruxsatini bering, söng **Install**. Eski Android’da bu **Settings → Security → Unknown sources** bölişi mumkin. Örnatişdan keyin bu ruxsatni öçirib qöyiş mumkin.
3. **TOŞDÖTAU TV** ilovasini oçing.
4. Server **`http://172.20.20.26:8080`** qilib tayyorlangan; ilova darhol `/tv?autostart=1`ni oçadi. TV boxning **`172.20.20.27`** manzili server maydoniga yozilmaydi. Uni router DHCP reservation yoki X96 Ethernet/Wi-Fi sozlamasida belgilang; APK tizim IPsini özgartirmaydi.
5. Pultda **MENU yoki BACK**ni bosing, birinçi martada sozlamalar oçiladi. Sozlamalar uçun **4–8 raqamli PIN** yarating va takrorlang. Bu TV box sozlamalari PINi, serverdagi admin paroli emas.
6. **Saqlaş**ni bosing. Keyin MENU/BACK → PIN → **Android / Home sozlamalari** orqali ilovani standart Home qilib tanlang. TV sahifasi töliq ekranda, manzil satrisiz qoladi.

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


## Universitetning hozirgi ulanişi

- Infokiosk/server: **172.20.20.26:8080**. Windows ilovasi oçiq tursin.
- X96/TV box: **172.20.20.27**. Bu manzil Android/routerda sozlanadi; APK server vazifasini bajarmaydi.
- Ushbu yangilaniş birinçi oçilişda serverni 172.20.20.26ga va avtostartni yoqilgan holatga bir marta ötqazadi. Mavjud PIN saqlanadi. Keyin qölda özgартirilgan server manzili har oçilişda ustidan yozilmaydi.
- Dizayn backenddan olinadi: hozirgi universitet logosi, moviy fon, yirik çipta, xizmat oynalari va kutayotganlar saqlanadi. APK faqat kichik/dense TV viewportda beshta oynani siğdiradi, yangi dizayn bilan almaştirmaydi.
- **TOŞDÖTAU TV → Home/Launcher → Always** bir marta tanlansa, Android Home vazifasi orqali qayta yoqilişda TV ilovasi oçiladi. Android 10+da ilova tizimning bu tanlovini foydalanuvçi örniga yashirinça bajara olmaydi. Qurilma proşivkasidagi avtostart taqiği yoki Force stop mavjud bölsa, uni X96da tekşiring.
- Android 10+da ilova Home rolini söraydigan tizim oynasini oçadi; eski Android’da Home sozlamasi oçiladi. Boot va APK yangilanişi hodisalari qöllanadi. Ilova Home bölsa doimiy ekran/brauzersiz rejim ishlar.

Tayyor yangilaniş: **1.0.8** (versionCode 8). Avvalgi APK bilan bir xil imzo: odatda eskisini o‘chirmasdan **Update / Yangilaş** orqali örnatiladi, PIN saqlanadi. Emulyator va layout sinovlari ötdi; qurilmaning Home/avtostart tanlovini X96da bir marta tasdiqlang va qayta yoqib sinang.

## Fon bor, jadval yo‘q: eski X96 WebView mosligi

Server PCda ishlasa, ammo TVda fon/logotipning eski belgisi va «Aloqa uzildi» qolsa, bu har doim LAN uzilgani degani emas. X96dagi eski Chromium WebView `replaceChildren`ni qo‘llamasligi mumkin. Tekshirishda bu imkoniyat olib tashlanganda aynan jadval bo‘shashi, clock/brand xatolari va offline yozuvi qayta hosil qilindi.

Yangi APK serverdan kelgan `app.js` oldiga zarur moslik funksiyalarini o‘zi qo‘shadi (replaceChildren, fromEntries va Animation.finished). Backend kodini yoki CSPni o‘zgartirmaydi. Eski asset keshi bir marta tozalanadi; IP/PIN saqlanadi. Windows ilovasini qayta o‘rnatish talab qilinmaydi. MENU/BACK → sozlamalarda WebView user-agent va oxirgi JavaScript xatosi ko‘rinadi.

Bu to‘liq Chromium yangilagichi emas. JavaScript sintaksisini umuman tushunmaydigan juda eski WebView bo‘lsa, Android System WebView’ni yangilash kerak bo‘ladi. Ilovaning moslik testi zamonaviy Android emulyatorida eski DOM imkoniyatlarini ataylab o‘chirib bajariladi; foydalanuvchining jismoniy X96ida qayta tekshiriladi.
