# Site üretici

Sitedeki HTML sayfalarının hepsi buradan üretilir. Sayfaları elle düzenleme; bir sonraki derleme üzerine yazar.
`_` ile başlayan klasörler GitHub Pages'te yayınlanmaz.

```
python _build/build.py
```

Pillow gerekir (`pip install pillow`).

| Dosya | Ne işe yarar |
|---|---|
| `games.json` | Oyunlar: ad, açıklama, renkler, özellik bölümleri, `live` (Play'de yayında mı) |
| `privacy/<Klasör>.html` | Her oyunun gizlilik politikası metni (üretici aracının ham HTML'i) |
| `build.py` | Ortak üst menü + alt bilgi + sayfa şablonları |
| `../assets/css/site.css` | Tüm tasarım |

Üretilen sayfalar: `index.html`, `404.html`, `funfunnygames/<Klasör>/index.html` ve `privacy.html`,
`sitemap.xml` (yayında olsun olmasın tüm oyunlar) ve `robots.txt`.

## Sık işler

- **Oyun Play'de yayına girdi:** `games.json` içinde o oyunda `"live": true` yap ve derle.
  Ana sayfada "Yakında" bölümünden çıkar; Google Play düğmeleri eklenir.
- **Gizlilik metni değişti:** `privacy/<Klasör>.html` dosyasını değiştir ve derle.
  Derleme, metnin kelimelerinin tasarım sırasında değişmediğini kendisi kontrol eder.
- **Ekran görüntüleri:** `assets/img/<slug>/shot-1.jpg, shot-2.jpg …` (ilk ikisi sayfanın üstündeki cihaz görselinde kullanılır).
- **İkon:** `assets/icons/<slug>.png` (256×256).

Play Console'da kayıtlı gizlilik adresleri değişmez: `/funfunnygames/PuzzleGame/privacy.html`, `/funfunnygames/FunCopter/privacy.html`.
