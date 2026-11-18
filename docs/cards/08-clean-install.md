# Clean Install Test (Dev/Prod)

Durum: Yerel wheel ve CPU imajı kontrolü; Prod bekliyor

Kanıt / çıktı: tests/test_inference.py, tests/test_dataset_audit.py, tests/sdk_smoke.py, docs/VERIFICATION.md

## Kabul maddeleri

- [x] Birim testlerini çalıştır
- [x] Temiz CPU Docker ortamında gerçek çıkarımı çalıştır
- [x] Wheel kurulumunda modül ve ağırlığı doğrula
- [x] Mevcut NovaVision SDK ortamında sözleşmeyi dene
- [ ] Hedef AlfaSuite Dev uygulamasında kamera/Redis bağlantılarını test et
- [ ] Hedef Prod CPU/GPU imajında dağıtım ve performansı doğrula
