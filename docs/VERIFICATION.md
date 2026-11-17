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
