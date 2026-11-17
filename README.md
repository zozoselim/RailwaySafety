# RailwaySafety — NovaVision paketi

Mevcut eğitilmiş YOLO11n `assets/best.pt` modelini kullanarak ray görüntülerinde
kusur tespiti yapar. Veri seti eğitimde kullanılır; uygulama çalışırken kod
görüntüyü `best.pt` modeline verir. Her çalıştırmada yeniden eğitim gerekmez.

Sınıflar modelin kendisinden okunur: `rail_crack`, `fastener_defect`,
`broken_sleeper`, `obstacle`. `fastener_defect` fiziksel gevşeklik ölçümü
değildir. Tespit çıkmaması hattın güvenli olduğu anlamına gelmez.

## Yerel istemci

Python 3.10+ ve çalışan PyTorch ortamında, proje kökünden:

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python apps/client.py path/to/image.jpg --device cpu --output outputs/result.json --save-image outputs/result.jpg
```

GPU ortamında `--device 0` kullanılabilir. `--conf`, `--iou`, `--imgsz`
isteğe bağlıdır. Çıkış piksel koordinatlı kutular ve sınıf/güven bilgileri
içeren JSON'dur. PNG/JPEG gibi tek görüntü dosyası kabul edilir. Video/kamera
işleme NovaVision Video Feed ile kare başına yapılır.

Model yolu varsayılan `assets/best.pt`; farklı ağırlık için
`RAILWAY_SAFETY_MODEL_PATH` ortam değişkenini kullan. Bulunamazsa hata verir.

## Docker ile CPU çıkarımı

```powershell
docker build -t railway-safety:0.2.0 .
docker run --rm --mount "type=bind,source=C:\images,target=/data" railway-safety:0.2.0 /data/track.jpg --output /data/result.json --save-image /data/result.jpg
```

Bu Dockerfile bağımsız CPU istemcisi içindir. NovaVision SDK'sı ve platform
servisleri bu imajın parçası değildir. Platform executor'ı hedef NovaVision
runtime imajında çalıştırılır. Dockerfile CPU PyTorch kurar; GPU dağıtımı hedef
NovaVision CUDA imajıyla doğrulanmalıdır.

## NovaVision uygulaması

Özel paket akışı:

```text
Video Feed ── image ──> RailwaySafety.inputImage
Video Feed ── image ──> Draw Bounding Box.inputImage
RailwaySafety.outputDetections ──> Draw Bounding Box.inputDetections
Draw Bounding Box ──> Draw Label ──> Video View
```

`outputDetections` ayrıca Draw Label tespit girişine bağlanır.
Alternatif olarak Models'e yüklenmiş aynı `best.pt`, hazır `YOLO Inference`
düğümünde seçilebilir. Ayrıntılar: [NovaVision rehberi](docs/NOVAVISION.md).

Özel pakette iki giriş yolu vardır: `inputImage` platformun tek Image nesnesi
(SDK medya/Redis taşıması dahil); `image` yerel test için Base64 metni.
İkisi verilirse `inputImage` kullanılır. Çıkışlar: `outputDetections` native
SDK Detection listesi, `detections` ayrıntılı JSON metni. Ayarlar confidence,
iou_threshold, device, image_size. SDK ortamında şema: `python apps/export.py`.

## Eğitim ve doğrulama

```powershell
python apps/audit_dataset.py path/to/data.yaml
python apps/inspect_model.py --output outputs/model.json
python apps/validate_model.py path/to/data.yaml --split test --device cpu
```

İyileştirilmiş veri hazır olduğunda isteğe bağlı fine-tuning:

```powershell
python apps/train.py path/to/data.yaml --epochs 50 --device 0
```

[Colab/yerel eğitim not defteri](notebooks/train_railway.ipynb) aynı süreci
gösterir. Yeni ağırlık `runs/railway_training/finetune*/weights/best.pt` altında
oluşur; mevcut ağırlığı otomatik değiştirmez. İncelenmiş validation ve bağımsız
test sonuçlarına göre yeni modeli seç.

Mevcut validation metadata mAP50=0.80598, mAP50-95=0.42355; yeniden ölçüm
değildir. Bu çalışmada 184 test görüntüsünde yeniden ölçülen mAP50=0.83509,
mAP50-95=0.43335. Çatlak recall=0.54545; saha kullanımı için iyileştirilmelidir.
Eğitimde yalnızca 26 kırık travers nesnesi vardır. Yeniden eğitim
kararı ve kaynaklar: [model/veri raporu](docs/BENCHMARK.md).

## Geliştirici kontrolü ve teslim

```powershell
python -m pip install -r requirements-dev.txt
python -m pytest -q
python -m pip wheel . --no-deps --wheel-dir dist
python apps/package_release.py
```

Wheel `novavision.package` ad alanını korur ve mevcut `best.pt` dosyasını
içerir. Mevcut `assets/best.pt` Git takibindedir; diğer eğitim ağırlıkları,
veri setleri ve çalışma çıktıları depoya eklenmez. `sdk` adlı genel PyPI paketi
gereksinimlerden çıkarılmıştır; gerçek `sdks.novavision` platformdan sağlanır.

[Doğrulama kaydı](docs/VERIFICATION.md) ve [dokuz iş kartı](docs/cards/README.md).
Kartlar yerel Markdown dosyalarıdır; harici panoda oluşturulmuş sayılmazlar.
Üretim kullanımı için saha testi ve AlfaSuite dağıtım kontrolü gereklidir.
