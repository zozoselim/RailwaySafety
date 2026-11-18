# Executor Implement (RailwaySafety.py)

Durum: Tamamlandı (CPU ve gerçek SDK)

Kanıt / çıktı: src/executors/RailwaySafety.py, src/utils/inference.py, src/utils/response.py

## Kabul maddeleri

- [x] Modeli süreçte bir kez yükle ve tahmini kilitle
- [x] Checkpoint sınıf isimlerini kullan
- [x] SDK BGR karesini RGB olarak modele ver
- [x] Piksel xyxy kutularını native left/top/width/height biçimine çevir
- [x] Gerçek SDK request/response döngüsünü dene
- [ ] Canlı medya deposu/Redis taşımasını hedef runtime içinde dene
