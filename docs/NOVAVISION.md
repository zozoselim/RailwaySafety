# NovaVision / AlfaSuite entegrasyonu

Araştırma tarihi: 16 Kasım 2026. Resmi belgeler platform davranışını
açıklıyor; özel paket geliştirme SDK'sının ayrıntılı sözleşmesini yayımlamıyor.
Bu projedeki `PackageModel`, `Component`, `PackageHelper` yapısı korunmuştur.

## Hazır YOLO paketiyle uygulama

1. AlfaSuite çalışma alanındaki Models bölümünde mevcut modelin Detection /
   YOLO Native olarak bulunduğunu doğrula. Model seçicide kendi `best.pt`
   modelini seç; genel COCO modelini seçme.
2. Workflow uygulaması oluştur; Flow'a Video Feed, YOLO Inference,
   Draw Bounding Box, Draw Label ve Video View ekle.
3. Video Feed görüntüsünü YOLO Inference ve Draw Bounding Box'a bağla.
   Detections çıkışını çizim paketlerine, çizilmiş görüntüyü Video View'a bağla.
4. Başlangıçta CPU ve confidence=0.25 kullan; eşik değerini bağımsız doğrulama
   görüntülerine göre belirle. GPU için hedef cihazın CUDA uyumunu doğrula.
5. Hedef cihaza bağlan, deploy et ve gerçek kamera görüntüsüyle test et.

Bu yol özel Python paketinin kaydını gerektirmez. AlfaSuite sürümünde paket ve
alan adları farklıysa o sürümün mevcut düğümlerini esas al.

## Özel RailwaySafety paketi

### Çalışma kaydı (0.2.2)

Paket kaydında executor `RailwaySafety` olmalıdır. `__init__` çalıştırıcı
değildir. Platformun executor taramasında karışıklık oluşturmaması için
`src/executors/__init__.py` bulunmaz; bu klasör Python namespace paketidir.

RailwaySafety, PyTorch ve Ultralytics içeren çalışma imajına atanmalıdır.
18 Kasım yerel uygulama incelemesinde `repos` kaydı `DigiNova/OpenCV` ve
`executors: ["__init__"]` gösteriyordu. Çalışan OpenCV ortamında `torch` ve
`ultralytics` yoktu. `assets/best.pt` de component klasörüne aktarılmamıştı.
Bu ortam mevcut haliyle çıkarım yapamaz. Paket kaydını uygun PyTorch imajı
ve `RailwaySafety` executor'ıyla yenile; uygulamayı tekrar deploy et.

Kaynakların platforma aktarılmasında yalnızca `src/` kopyalanıyorsa ağırlık
ayrıca çalışma ortamına sağlanmalıdır. Varsayılan component yolu:
`/opt/project/components/RailwaySafety/assets/best.pt`.
Alternatif olarak erişilebilir model dosyasının mutlak yolunu
`RAILWAY_SAFETY_MODEL_PATH` ile belirt. Suite Models'e yüklenmiş bir model
bu özel executor tarafından otomatik indirilmez; hazır YOLO Inference
model seçicisi ayrı bir entegrasyondur.

Dosyalar: `src/models/PackageModel.py`, `src/executors/RailwaySafety.py`,
`src/utils/response.py`. Executor adı `RailwaySafety`, paket türü `component`.

Girdi `inputImage`: Image Load / Video Feed'in SDK Image nesnesi. 0.2.1'de
doğrudan zorunlu şema referansıdır; nullable/isteğe bağlı giriş kullanılmaz.
Image Load ile uyum için tek Image veya tek elemanlı Image listesi kabul edilir.
Birden fazla görüntü içeren liste açık hata üretir. Gerçek SDK'nın
`Image.get_frame` yardımcısıyla bytes/Base64/medya deposu/Redis taşıması çözülür.
Kare BGR'den RGB'ye çevrilerek aynı modele verilir. Bozuk veya çözülemeyen
görüntü hata üretir.

Yerel dosya/Base64 çıkarımı platform girişinden ayrıdır: `apps/client.py`
ve `src.utils.inference.detect` üzerinden çalışır. Paket şemasında yalnızca
native `inputImage` vardır.

| Ayar | Varsayılan | Anlamı |
| --- | --- | --- |
| confidence | 0.25 | 0–1 güven eşiği |
| iou_threshold | 0.45 | NMS IoU eşiği |
| device | cpu | CPU veya CUDA indeksi, ör. `0` |
| image_size | 640 | 32–4096 arası çıkarım boyutu |

Çıkış `outputDetections`: SDK `Detection` listesi. `boundingBox` alanı
`left`, `top`, `width`, `height` piksel değerlerini taşır; diğer alanlar
`classLabel`, `classId`, `confidence`. Draw Bounding Box ve Draw Label'ın
tespit girişlerine bağlanabilir. Kaynak görüntü ayrıca çizim paketine bağlanır.

Çıkış `detections`: JSON metni. Alanlar `detections`, `count`, `image_width`,
`image_height`, `coordinate_format`, `defect_detected`. Her tespitte `class_id`,
`class_name`, `confidence`, `bbox_xyxy` bulunur. Kutular EXIF yönü düzeltilmiş
görüntünün piksel koordinatlarıdır. Boş sonuç hattın güvenli olduğunu göstermez.
Çizim düğümleri için JSON metni yerine `outputDetections` çıkışını kullan.

SDK, NovaVision çalışma ortamından sağlanmalıdır. Adı yalnızca `sdk` olan
genel PyPI bağımlılığı kaldırıldı; bunun `sdks.novavision` sağladığına dair
kanıt yoktu. SDK olmayan ortamda yerel istemci ve veri denetimi çalışır;
executor ve şema dışa aktarma SDK ister.

SDK ortamında proje kökünden:

```powershell
python apps/export.py
```

Bilgisayardaki `diginova-pytorch:latest` imajında bulunan gerçek SDK ile
şema üretimi ve executor round-trip testi yapıldı. Test Base64 dosya ve
native bytes görüntüyü, varsayılan ayarları ve her iki çıkışı kapsar.
Bu SDK, Video Feed ve Draw Bounding Box referansları aynı imajdan incelendi.
Canlı Redis taşıması ve AlfaSuite üzerinde uçtan uca deployment ayrıca gerekir.
Üretilen `data.json` dosyasını hedef AlfaSuite'in SDK/şema sürümünde doğrula.
Özel paket yayınlama veya AlfaSuite'e uygulama yükleme bu yerel hazırlığın
tamamlanmış bir parçası olarak iddia edilmez.

## Kaynaklar

- [Packages](https://docs.novavision.ai/en/build/packages/)
- [Models](https://docs.novavision.ai/en/data/models/)
- [Flow bağlantı örneği](https://docs.novavision.ai/en/build/flows/)
- [Uygulama oluşturma](https://docs.novavision.ai/en/build/create-app/)
- [Test ve çalıştırma](https://docs.novavision.ai/en/build/test-and-run/)
