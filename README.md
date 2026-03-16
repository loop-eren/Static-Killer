# Static-Killer
Bu araç; statik web sayfalarında oluşabilecek tüm potansiyel zafiyetlerin sistematik ve hızlı bir şekilde tespit edilmesini sağlayan kapsamlı bir güvenlik analiz yazılımıdır.
# Daha fazla bilgi :)
Bu aracı geliştirmemdeki temel motivasyon, sızma testi süreçlerinde özellikle detaylara önem veren ve profesyonellik bekleyen kurumsal firmalara kapsamlı bir analiz sunabilmektir. Bilindiği üzere, tamamen statik sayfalarda karmaşık backend fonksiyonları bulunmadığı için güvenlik açığı taramaları genellikle yüzeysel kalmaktadır. Geliştirdiğim bu toolkit; statik yapıların doğasına uygun olarak açık portları, HTTP güvenlik başlıklarını (headers), iletişim formlarını ve e-posta gönderim mekanizmalarını en uç noktasına kadar test ederek, statik sayfalardaki 'bulgu bulma' sorununu sistematik bir şekilde çözmeyi hedeflemektedir.
# Use Case
![Araç Tanıtımı](ezgif-24c0a76ea0fdde48.gif)

Hazırladığım tanıtım videosunda (GIF), aracın en çok kullanılan temel özelliklerini sergiledim. 
## Tool içerisinde yer alan modüllerin işlevleri şu şekildedir:

### 1->HTTP Güvenlik Analizi: Hedef sitenin HTTP header yapılandırmasını inceleyerek; X-Frame-Options (Clickjacking), CSP (Script Injection/XSS), X-XSS-Protection (Cross-Site Scripting), X-Content-Type-Options (MIME Sniffing), Referrer-Policy (Bilgi Sızıntısı) ve Permissions-Policy (API İzin İstismarı) gibi kritik güvenlik eksikliklerini test eder.

### 2->DNS ve E-Posta Güvenliği: Kapsamlı DNS sorguları gerçekleştirerek SPF, DMARC ve DKIM gibi kayıtları analiz eder; olası mail spoofing (sahte e-posta) zafiyetlerini raporlar.

### 3->Port Taraması: Hedef sistem üzerindeki açık portları tespit eder ve çalışan servisler hakkında bilgi toplar.

### 4->Subdomain Takeover: DNS kayıtlarını analiz ederek, kullanılmayan ancak yönlendirmesi devam eden servisler üzerinden yapılabilecek alt alan adı devralma açıklarını denetler.

### 5->JavaScript Statik Analizi: Hedef sitedeki tüm .js dosyalarını otomatik olarak tarar; dosya içerisindeki API anahtarları, gizli endpoint'ler ve hassas anahtar kelimeleri tespit ederek ekrana yansıtır.

### 6->Form Parametre Analizi: İletişim formları gibi alanlardan giden istekleri (request) .txt formatında içe aktararak; parametreler üzerinde XSS, SQLi ve SSTI gibi olası enjeksiyon zafiyetlerini test eder.
