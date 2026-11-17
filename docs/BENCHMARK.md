# Model ve veri incelemesi

İnceleme: 16 Kasım 2026. Mevcut `assets/best.pt` korunmuştur; yeniden eğitim
yapılmamıştır. Kaynak: komşu `datasets/rail_datasets` klasöründeki kayıtlar,
checkpoint içindeki metadata ve bu çalışmada yapılan salt okunur veri denetimi.

## Mevcut model

- Mimari: eğitim `args.yaml` kaydına göre YOLO11n detection.
- Ultralytics: checkpoint içinde 8.4.198.
- Eğitim ayarları: 20 epoch, 640 görüntü boyutu, batch 8, seed 0.
- Sınıflar checkpoint içinden doğrulandı: `rail_crack`, `fastener_defect`,
  `broken_sleeper`, `obstacle`.
- Checkpoint kayıtlı validation: precision 0.82828, recall 0.72295,
  mAP50 0.80598, mAP50-95 0.42355. Bunlar bu çalışmada yeniden ölçülmüş skorlar
  değildir. Bağımsız test bölümü bu çalışmada ayrıca yeniden değerlendirildi.

## Bu çalışmada yeniden ölçülen test başarısı

`docs/test-metrics.json`: 184 görüntü, 604 etiketli nesne, Ultralytics 8.4.198,
CPU. mAP50 yaklaşık **0.835**, mAP50-95 **0.433**, precision **0.781**,
recall **0.774**. Sınıf bazlı sayısal değerler JSON raporundadır.

Özellikle `rail_crack` recall yaklaşık **0.545**: bu testte çatlakların önemli
bir kısmı kaçırılıyor. Kırık travers için recall 1.0 olsa da testte yalnızca
17 nesne ve eğitimde 26 nesne var; bu sonuç saha genellemesi kanıtı değildir.
Bu değerlendirme orijinal, yerel `test` bölümündedir; bağımsız toplanmış yeni
bir saha veri seti değildir.

Ek karşılaştırma: mevcut NovaVision SDK imajındaki Ultralytics 8.4.6 ile
mAP50 0.838 ve mAP50-95 0.430 ölçüldü. Paket sürümüyle ölçüm farkı vardır;
raporun ana sonucu sabitlenmiş 8.4.198 sürümünü kullanır. CPU süreleri kaynak
yükünden etkilenmiştir; bu çalışmada gerçek zamanlı FPS kabul testi yapılmadı.

## Bu çalışmada yeniden yapılan veri denetimi

| Bölüm | Görüntü | Çatlak | Bağlantı kusuru | Kırık travers | Engel |
| --- | ---: | ---: | ---: | ---: | ---: |
| Train | 1376 | 221 | 986 | 26 | 3315 |
| Validation | 214 | 17 | 85 | 18 | 917 |
| Test | 184 | 33 | 109 | 17 | 445 |

Nesne sayıları görüntü sayısı değildir. `docs/dataset-audit.json`: eksik etiket
0, boş etiket 0, sayısal/koordinat hatası 0, bölümler arasında byte düzeyinde
aynı görüntü grubu 0. Bu denetim benzer kareleri, aynı ray kesimini veya
etiketlerin görsel doğruluğunu kanıtlamaz. Yakın kareler ve aynı güzergâh
train/test arasında kalmamalı; bölme güzergâh/video kaydı temelinde incelenmeli.

## Yeniden eğitim kararı

Entegrasyon ve demo için önce mevcut ağırlık kullanılır. Yeniden eğitim,
uygulamayı çalıştırmak için zorunlu değildir. Saha kullanımı öncesinde:

- 26 eğitim nesnesi bulunan kırık travers sınıfı için çeşitlilik artırılmalı.
- `fastener_defect`, eksik/kırık elemanların birleştirilmiş sınıfıdır; doğrudan
  fiziksel gevşeklik etiketi değildir. Gevşekliği gösterebilen çekim ve güvenilir
  etiket olmadan bu adla başarı iddiası yapılamaz.
- Birleştirme raporu 2600 manuel inceleme gerektiren kayıt bildiriyor;
  bu sayı hazır eğitim görüntüsü sayısı gibi yorumlanmamalı.
- `normal_track` gibi elenen kaynak etiketler dikkate alınarak sağlam ray,
  gölge, balast, yağmur ve gece için uygun negatif örnekler eklenmeli.
- `obstacle` görünür nesneyi tanımlar; nesnenin trenin geçiş koridorunda
  olduğunu kanıtlamaz. Gerçek hat engeli alarmı için ray ROI/segmentasyon,
  geometrik doğrulama ve zamansal filtre ayrı geliştirilmelidir.
- Son karar bağımsız testte sınıf bazlı recall/yanlış alarm ve saha koşulları
  üzerinden verilmeli. Bu paket tek başına işletme güvenliği kararı vermez.

## Veri kaynakları ve teknoloji

Yerel kaynak YAML dosyaları ve merge scripti şu dört kaynağı gösteriyor.
Web'de 1, 2 ve 4 numaralı kaynak sayfaları doğrulandı; üçüncü kaynağa web
erişimi sağlanamadı. Lisans bilgisi üçüncü kaynakta yalnızca yerel YAML kaydıdır.

| Kaynak | Yerel lisans kaydı | Birleştirmedeki rol |
| --- | --- | --- |
| [Fastener Detection v1](https://universe.roboflow.com/railway-defects-osolv/fastener-detection-7a3vn/dataset/1) | CC BY 4.0 | Missing Dogscrew/Fastener → fastener_defect |
| [Railway obstacle v1](https://universe.roboflow.com/railway-research/railway-track-obstacle-detection-gca3w/dataset/1) | CC BY 4.0 | Animal/Car/Person/Rock/Trash/Tree → obstacle |
| [Rail defects v2](https://universe.roboflow.com/roboflow100vl-fsod/l10ul502-fsod-mumk/dataset/2) | MIT, yerel kayıt | Rail Crack, kırık eleman, Wood Crossties Break |
| [Railway track v11](https://universe.roboflow.com/railway-project/railway-track-uqhmu/dataset/11) | CC BY 4.0 | bolt_missing/clip_missing/crack |

Kodda Ultralytics çıkarım/eğitim, Pillow görüntü çözme/çizme, PyYAML veri
denetimi ve NovaVision SDK executor/şema için kullanılır. Segmentasyon
poligonlarının kutuya çevrildiği kayıtlıdır; bu checkpoint segmentasyon
modeli değildir. Ultralytics checkpoint AGPL-3.0 lisans metni içeriyor;
ürün dağıtımında ilgili model/kütüphane ve veri atıfları ayrıca ele alınmalı.

Resmi teknik kaynaklar:
[Predict](https://docs.ultralytics.com/modes/predict/),
[Train](https://docs.ultralytics.com/modes/train/),
[Validation](https://docs.ultralytics.com/modes/val/).
