# Doğrulama kaydı — 16 Kasım 2026

## Tamamlanan kontroller

- `python -m pytest -q`: 13 test geçti. Modelden gelen sınıf adları, RGB renk
  sırası, boş sonuç, ayar aktarımı, hatalı Base64, eşik değerleri, büyük görüntü,
  eksik model, veri kutuları ve bölümler arası kopya denetimi kapsanır.
- `python -m compileall -q src apps tests`: Python sözdizimi kontrolü.
- `python -m pip wheel . --no-deps --wheel-dir dist`: 0.2.0 wheel üretildi.
  İçindeki ağırlık ve modüller incelendi; temiz Python ortamında paket importu
  ve ağırlığın SHA256 eşitliği kontrol edildi. Bu kontrol bağımlılıklar için
  tam NovaVision Prod kurulumu sayılmaz.
- Bağımsız CPU Docker imajı oluşturuldu. Gerçek `best.pt`, testten bir ray
  çatlağı görüntüsünde çalıştırıldı; `outputs/example-result.json` ve
  `outputs/example-result.jpg` üretildi. Bir rail_crack, güven 0.584201.
- Mevcut `diginova-pytorch:latest` içindeki gerçek NovaVision SDK ile
  `apps/export.py` şemayı üretti. `tests/sdk_smoke.py` gerçek model kullanarak
  Base64 ve native bytes girişi, varsayılan ayarlar ve JSON/native liste
  çıktısını doğruladı. Geçerli bir SDK Request ve PackageHelper kullanıldı.
- `apps/audit_dataset.py`: 1774 görüntü; koordinat hatası 0, eksik etiket 0,
  boş etiket 0, bölümler arası aynı dosya grubu 0.
- `apps/validate_model.py`: orijinal test bölümünde 184 görüntü ve 604 nesne;
  Ultralytics 8.4.198 ile mAP50 0.8350868, mAP50-95 0.4333527.
  [Sayısal rapor](test-metrics.json), [yorum](BENCHMARK.md).

## Ortam ve sınırlar

Windows'taki eski eğitim ortamında PyTorch `c10.dll` yüklemesi Uygulama
Denetimi tarafından WinError 4551 ile engellendi. Güvenlik ayarı değiştirilmedi;
model çalıştırma Linux Docker ortamında doğrulandı.

SDK imajı: Python 3.11.11, PyTorch 2.6.0+cu124, Ultralytics 8.4.6; test CPU'da.
Bağımsız paket imajı: Python 3.11.18, CPU PyTorch 2.15.0, Ultralytics 8.4.198.
Sabitlenmiş paket sürümündeki tam test sonucu ana rapordur. İmaj kurulumunda
PyTorch ve alt bağımlılıklar sürümleri sabitlenmemiştir; rapor kullanılan
sürümleri kaydeder.

Docker Desktop yeni konteyner ve son imaj yenilemesi sırasında tekrarlayan
API 500 hatası verdi. İlk CPU imajı, gerçek çıkarım, SDK Base64/native smoke
testi ve tam test-seti değerlendirmesi başarıyla tamamlandı. Son kaynak
değişikliklerinin tamamını içeren imajın yeniden build edilmesi bu ortamda
tamamlanamadı; teslim kaynakları ve wheel günceldir. Gerçek örnek görüntülü
ikinci SDK smoke denemesi de bu API hatasıyla başlayamadı. İlk gerçek SDK
testi sentetik kırmızı görüntü + gerçek model ile tamamlanmıştır.

Canlı AlfaSuite hesabına uygulama kurulmadı, harici panoda kart oluşturulmadı.
17 Kasım 2026 tarihli depo teslimine mevcut `assets/best.pt` de dahil edildi.
Hedef AlfaSuite Dev/Prod, canlı Redis/medya deposu,
kamera/RTSP, GPU ve saha kabul testleri açık iş kartlarında belirtilir.
Model eğitim not defteri hazırlanmıştır; yeni eğitim çalıştırılmamıştır.

## 17 Kasım 2026 — 0.2.1 görüntü girişi düzeltmesi

Flow ekran görüntüsünde Railway Safety düğümünün görüntü giriş noktası yoktu.
Şemadaki iki nullable giriş yerine platform referans paketleriyle aynı şekilde
zorunlu, doğrudan `inputImage` referansı tanımlandı. Image Load'un gerçek SDK
modeli `diginova-opencv:latest` imajından kontrol edildi; tek Image ve Image
listesi çıkışları verdiği doğrulandı. Tek elemanlı liste kabul edilir; boş ve
çoklu listeler reddedilir.

`apps/export.py` gerçek SDK ile tekrar çalıştı. `tests/sdk_smoke.py`
`outputs/example-input.jpg` üzerinde gerçek modelle native Base64, native
bytes ve tek elemanlı liste girişlerini test etti. Üç yolda aynı tespitler ve
doğru native kutu dönüşümü doğrulandı. Girişin şemada required ve doğrudan
referans olması ayrıca kontrol edildi. 13 birim testi tekrar geçti.

AlfaSuite'in canlı Flow arayüzünde giriş noktasının görünmesi yerelden
doğrulanmadı. Bunun için hedef paket/şema tanımı güncellenmeli ve mevcut
Railway Safety düğümü yeni tanımla yeniden oluşturulmalıdır.

## 18 Kasım 2026 — 0.2.2 çalışma kaydı incelemesi

Yerel uygulama `repos` kaydında RailwaySafety için `DigiNova/OpenCV` imajı
ve `executors: ["__init__"]` bulundu. Çalışan OpenCV konteynerinde `torch`,
`ultralytics` ve model dosyası yoktu. Mevcut ağırlık, bu yerel deployment'ın
component `assets/best.pt` yoluna kopyalandı ve konteynerden 5503194 byte
olarak doğrulandı. Yeniden deploy sırasında ağırlığın ayrıca aktarılması
gerektiği entegrasyon rehberinde açıklandı.

Executor taramasının `__init__` seçmesini önlemek için executors klasöründeki
başlangıç dosyası kaldırıldı. 0.2.2 wheel içinde yalnızca RailwaySafety.py
executor'ının bulunduğu kontrol edildi. 13 birim testi ve gerçek PyTorch/SDK
ile örnek fotoğraf üzerinde native Base64/bytes/tekli liste testi geçti.
Canlı uygulamanın PyTorch imajı ve RailwaySafety executor'ıyla tekrar kaydı
ve deploy işlemi henüz doğrulanmadı. WebSocket bağlantı hataları da gözlendi.
