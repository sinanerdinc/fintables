# Fintables

Fintables mobil API'si için Python paketi ve CLI aracı.

## Özellikler
- **Public Endpointler**: Şirket detayları (`company`), sembol özetleri (`symbol summary`), analist değerlendirmeleri (`analyst`), çoklu arama (`search`).
- **Authenticated Endpointler**: Finansal tablolar (`symbol sheets`), haber akışı (`feed`), favoriler (`watchlist`), notlar (`memo`).
- **Zengin Terminal Görünümü**: `rich` destekli tablolar, renkli kartlar, rozetler ve ikonlar.
- **JSON Çıktı Desteği**: Otomasyonlar ve scriptler için `--output json`.
- **Async-First Mimari**: `httpx` ve `pydantic v2` tabanlı.

## Kurulum
```bash
pip install -e .
# veya test paketleri ile:
pip install -e ".[dev]"
```

## Yapılandırma
`.env.example` dosyasını `.env` olarak kopyalayın ve kimlik bilgilerinizi girin:
```bash
cp .env.example .env
```

## CLI Kullanımı
```bash
# Şirket bilgisi
fintables company ASELS

# Sembol özeti
fintables symbol ASELS summary

# Analist tahminleri
fintables analyst ASELS
fintables analyst ASELS --model-portfolio

# Çoklu arama
fintables search Polyester

# Finansal tablolar (Authenticated)
fintables symbol FROTO sheets
fintables symbol FROTO sheets --sheet balance --periods 5

# Haber akışı (Authenticated)
fintables feed
fintables feed FROTO

# Favori hisseler (Authenticated)
fintables watchlist add FROTO
fintables watchlist remove FROTO

# Notlar (Authenticated)
fintables memo list
fintables memo add FROTO "Beklentim pozitif"
fintables memo update 42212 "Güncellenmiş not"
fintables memo delete 42212

# Fonlar
fintables fund TLY
fintables fund MAC

# Araştırma Yazıları & Şirket Notları (Authenticated)
fintables post list                                          # tüm yazıları listele
fintables post list --filter "Şirket Notları"               # kategori filtresi
fintables post list --page 2                                 # sayfa ilerle
fintables post read altny-analist-toplantisi-notlari-2026-6 # yazıyı oku (+ benzer yazılar)
fintables post read <slug> --output json                    # JSON çıktı

# Bültenler (Authenticated)
fintables newsletter list                                    # tüm bültenleri listele
fintables newsletter list --category bist                   # kategori filtresi
fintables newsletter list --filter "Günlük"                 # başlık/kategori filtresi
fintables newsletter list --page 2                          # sayfa ilerle
fintables newsletter read endekslerde-tarihi-degisim        # bülten içeriğini oku
fintables newsletter read <slug> --output json              # JSON çıktı

# Videolar (YouTube & Borsa Programları)
fintables video list                                         # videoları listele
fintables video list --series "Haftalık Sohbetler"           # seriye göre filtrele
fintables video list --series "Halka Arz Oluyor"             # halka arz videoları
fintables video list --filter "Bilanço"                      # başlığa göre filtrele
fintables video list --page 2                                # sayfa ilerle
fintables video show bilanco-donemini-kapatiyoruz-fintables-haftalik-sohbetler-149 # detay & bölümler
fintables video show <slug> --output json                    # JSON formatında çıktı

# Ajanda / Ekonomik Takvim (Authenticated)
fintables agenda                         # bugünün ajandası (varsayılan)
fintables agenda today                   # bugün
fintables agenda thisWeek                # bu hafta
fintables agenda nextWeek                # gelecek hafta
fintables agenda thisWeek --type dividend  # sadece temettüler
fintables agenda thisWeek --type macro     # sadece makro veriler
fintables agenda thisWeek --output json    # JSON çıktı

# Sanal Portföy (Authenticated)
fintables portfolio list                                                # tüm portföyleri listele
fintables portfolio create "Benim Portföyüm"                           # yeni portföy oluştur
fintables portfolio show "Benim Portföyüm"                             # pozisyonları göster
fintables portfolio buy  "Benim Portföyüm" SASA 250000 2.76 --date 2026-09-22   # alış ekle
fintables portfolio sell "Benim Portföyüm" SASA 100000 3.10 --date 2026-09-22   # satış ekle
fintables portfolio delete "Benim Portföyüm"                           # portföyü sil (onay yok)
fintables portfolio rename "Benim Portföyüm" "Yeni İsim"               # portföy adını değiştir

# UUID ile de kullanılabilir (isimsiz veya belirsiz durumlarda)
fintables portfolio show ad857c49-d902-4f58-a57a-6429e7b40460

# Bildirimler (Authenticated)
fintables notification list                   # bildirimleri listele
fintables notification list --page-size 50    # sayfa boyutu ile listele
fintables notification unread                 # okunmamış bildirim durumu ve son okuma tarihi
fintables notification mark-read              # tüm bildirimleri okundu olarak işaretle
fintables notification list --output json     # JSON çıktısı

# Dil Desteği (i18n)
fintables --lang tr [KOMUT]                   # Türkçe CLI ve çıktılar (varsayılan: sistem dili veya tr)
fintables --lang en [COMMAND]                 # İngilizce CLI ve çıktılar
# Veya ortam değişkeni:
export FINTABLES_LANG=tr  # ya da en
```


