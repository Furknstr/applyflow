# Otonom Multi-Agent İş Başvuru Sistemi — Revize Proje Planı

**Not:** Bu plan, orijinal dokümandaki Faz 2'de yer alan bot-tespit atlatma (stealth fingerprinting, "ban riskini sıfırlama" amaçlı proxy rotasyonu) ve Faz 5'teki üçüncü parti CAPTCHA çözme entegrasyonu çıkarılarak hazırlanmıştır. Bu unsurlar platformların kullanım şartlarını ihlal eden ve hesap/hukuki risk taşıyan yöntemlerdir. Yerine, resmi/yarı-resmi veri kaynakları ve tam insan onaylı otomasyon konulmuştur.

---

## 0. Genel Hedef ve Kapsam

- **Amaç:** İş ilanlarını toplayıp adayın profiliyle eşleştiren, uygun ilanlar için otomatik ön yazı taslağı üreten ve formu adayın onayıyla dolduran bir sistem.
- **Otonomi sınırı:** Sistem "gönder" butonuna kendi başına basmaz. Veri toplama, ilan sitelerinin ToS'unu ihlal etmeyecek şekilde yapılır.
- **Teknoloji yığını (değişmedi):** FastAPI, Docker Compose, ChromaDB, SQLite/PostgreSQL, LangGraph, Pydantic, Playwright (yalnızca form doldurma için, stealth olmadan).

---

## 1. Faz 1 — Altyapı ve Veri Modellenmesi

### 1.1 Standart Şema (Pydantic)
- `JobPosting` modeli: `id`, `source` (linkedin/indeed/greenhouse/lever/manual), `title`, `company`, `location`, `remote_type`, `requirements: list[str]`, `description_raw`, `url`, `posted_date`, `scraped_at`.
- `CandidateProfile` modeli: kişisel bilgiler, beceri listesi, proje referansları (RAG'a bağlanacak doküman ID'leri).
- `MatchResult` modeli: `job_id`, `score` (0-1), `matched_keywords`, `gaps` (eksik gereksinimler), `agent_notes`.
- `CoverLetterDraft` modeli: `job_id`, `draft_text`, `used_context_ids`, `status` (draft/approved/rejected).

### 1.2 Konteynerizasyon
- `docker-compose.yml` ile üç servis: `api` (FastAPI), `chroma` (vektör DB), `db` (PostgreSQL — ilan/durum takibi için; küçük ölçekte SQLite de yeterli).
- Her servis izole network'te, sadece gerekli portlar açık.
- `.env` dosyasında API anahtarları (LLM sağlayıcı, ATS API'leri) — repoya commit edilmez.

### 1.3 İlan Durum Makinesi
- Her ilan şu durumlardan birinde: `discovered → evaluated → drafted → pending_approval → approved → submitted → rejected/skipped`.
- Bu durum, PostgreSQL/SQLite tablosunda tutulur; LangGraph akışının state'i buradan beslenir.

**Çıktı:** Docker Compose ile ayağa kalkan, boş ama çalışan API + DB + Chroma altyapısı.

---

## 2. Faz 2 — Veri Toplama Motoru (Revize: ToS-Uyumlu Kaynaklar)

Orijinal plandaki "stealth scraping + residential proxy" yerine üç katmanlı, meşru veri toplama stratejisi:

### 2.1 Katman A — Resmi/Yarı-Resmi ATS API'leri (öncelikli)
Çoğu şirketin kariyer sayfası aslında bir ATS (Applicant Tracking System) üzerinde çalışır ve bunların genelde açık, kimlik doğrulama gerektirmeyen JSON uçları vardır:
- **Greenhouse:** `boards-api.greenhouse.io/v1/boards/{şirket}/jobs`
- **Lever:** `api.lever.co/v0/postings/{şirket}`
- **Workday, SmartRecruiters, Ashby** gibi platformların da benzer public feed'leri mevcut.
- Bu adaptörler, `JobPostingSource` arayüzünü implemente eden ayrı sınıflar olarak yazılır (her ATS için bir adaptör — orijinal plandaki "adapter mimarisi" fikri burada korunuyor, sadece hedef kaynak değişiyor).

### 2.2 Katman B — RSS / Job Board Export'ları
- Bazı iş ilanı siteleri (We Work Remotely, RemoteOK, bazı kurumsal kariyer sayfaları) RSS veya public JSON feed sunar. Bunlar kullanılabilir.

### 2.3 Katman C — Manuel/Yarı-Otomatik Giriş
- LinkedIn/Indeed gibi ToS'u scraping'e kapalı platformlar için: kullanıcı ilgilendiği ilanın **URL'sini kendisi yapıştırır**. Sistem, tarayıcıda o sayfayı normal (stealth olmadan, adayın kendi oturumuyla) açar, DOM'dan başlık/şirket/gereksinim gibi alanları çıkarır. Bu, kullanıcının kendi hesabıyla kendi manuel gezinme davranışını otomatikleştirmesidir; toplu/otonom tarama yapılmaz.
- Alternatif: Kullanıcı ilan metnini kopyala-yapıştır yoluyla sisteme verir; bu en düşük riskli ve en basit yoldur.

### 2.4 Ortak Normalizasyon
- Her kaynaktan gelen veri, Faz 1'deki `JobPosting` Pydantic şemasına dönüştürülür (adapter pattern korunuyor).
- Rate limiting: Her adaptör, hedef API'nin/sitenin kendi yayınladığı rate limit'e uyar (agresif "jitter ile ban'dan kaçınma" değil, standart nazik istemci davranışı).

**Çıktı:** Birden fazla kaynaktan `JobPosting` nesneleri üreten, ToS ihlali içermeyen bir veri toplama katmanı.

---

## 3. Faz 3 — Kişisel Bilgi Tabanı (RAG Katmanı)

*(Bu faz orijinal planla aynı, değişiklik yok.)*

### 3.1 İçerik Hazırlığı
- Geçmiş proje dökümleri (otonom ajan tasarımları, jailbreak değerlendirme altyapıları vb.)
- Staj deneyimleri (Siskon, HubX) — görev, teknoloji, sonuç odaklı özetler.
- Akademik çalışmalar (ICETAI vb.) — özet, katkı, kullanılan yöntem.
- Her doküman Markdown formatında, başlık + etiketler (skills, domain, tarih) ile yazılır.

### 3.2 Embedding ve Depolama
- Dokümanlar chunk'lara bölünür (örn. 300-500 token).
- Bir embedding modeliyle (OpenAI/Anthropic/açık kaynak) vektörleştirilip ChromaDB'ye yazılır.
- Metadata: `doc_type` (project/internship/academic), `skills`, `date`, `source_file`.

### 3.3 Retriever Katmanı
- İlan gereksinimlerine göre en alakalı 3-5 chunk'ı getiren bir `retriever.py` fonksiyonu.
- Hybrid arama (anahtar kelime + semantik) düşünülebilir; küçük ölçekte saf semantik yeterli.

**Çıktı:** Sorgulanabilir, adayın tüm geçmişini kapsayan bir vektör bilgi tabanı.

---

## 4. Faz 4 — Multi-Agent Karar ve Üretim Akışı

*(Orijinal planla aynı mantık, küçük netleştirmelerle.)*

### 4.1 Matcher Agent
- Girdi: `JobPosting` + RAG'dan adayın beceri/proje özeti.
- Çıktı: `MatchResult` (skor + eşleşen/eksik anahtar kelimeler).
- Skor eşiği (örn. 0.7) altındaki ilanlar otomatik `skipped` durumuna geçer, Writer Agent'a gitmez.

### 4.2 Writer Agent
- Sadece skor eşik üstü ilanlar için çalışır.
- RAG'dan ilgili 3-5 proje/deneyim chunk'ını çeker, ilandaki anahtar kelimelerle harmanlayarak taslak ön yazı üretir.
- **Önemli ilke:** Üretilen metin her zaman "taslak" statüsündedir; sistem bunu otomatik göndermez.

### 4.3 Durum Yönetimi (LangGraph)
- Graph düğümleri: `fetch → match → (skip | draft) → human_review → (approve → submit_queue | reject)`.
- Hata yönetimi: Her düğümde try/except + retry politikası; kalıcı hata durumunda ilan `error` durumuna düşer ve insan bildirimi tetiklenir.
- AgentScope, çoklu agent'lar arası mesajlaşma/log tutma için opsiyonel; küçük ölçekte LangGraph tek başına yeterli olabilir (karmaşıklığı azaltmak için başta LangGraph'la başlanması önerilir).

**Çıktı:** Girdi olarak ilan alan, çıktı olarak "onaya hazır ön yazı taslağı" üreten uçtan uca karar zinciri.

---

## 5. Faz 5 — Form Doldurma ve İnsan Onayı (Human-in-the-Loop)

### 5.1 Kapsam Sınırlaması
- CAPTCHA çözme entegrasyonu **yoktur**. Sistem bir CAPTCHA ile karşılaşırsa süreci durdurup kullanıcıdan manuel çözüm ister — bu zaten platformun "bunu bir insan mı yapıyor" testine doğru cevabı verir.
- Playwright, stealth eklentisi olmadan, kullanıcının kendi oturumu/tarayıcı profiliyle çalışır.

### 5.2 Akış
1. Onaylanan (`approved`) ilan ve taslak ön yazı, form doldurma modülüne geçer.
2. Playwright hedef başvuru formunu açar (kullanıcının önünde, headless değil — şeffaflık için).
3. Ad, e-posta, CV yolu, ön yazı gibi alanlar DOM'da tespit edilip doldurulur.
4. **Zorunlu durak:** Sistem "Gönder" butonuna basmadan önce ekranda "Formu incele ve onayla" adımında durur.
5. Kullanıcı formu gözden geçirir, gerekirse düzenler, kendi elleriyle (veya UI'daki "Onayla ve Gönder" butonuyla) gönderimi tamamlar.
6. Gönderim sonrası ilan durumu `submitted` olarak işaretlenir, tarih/saat loglanır.

### 5.3 Güvenlik ve Şeffaflık İlkeleri
- Sistem hiçbir zaman kullanıcı adına, kullanıcının görmediği bir ekranda form göndermez.
- Her başvuru için audit log tutulur: hangi veri hangi alana yazıldı, kullanıcı ne zaman onayladı.
- Kullanıcı, her an "otomatik doldurmayı durdur" diyebilir; sistem yarım kalan formu kaydeder, sonra devam edilebilir.

**Çıktı:** Kullanıcının tam kontrolünde, şeffaf, denetlenebilir bir form-doldurma yardımcı aracı.

---

## 6. Fazlar Arası Bağımlılık Özeti

| Faz | Bağımlı Olduğu Fazlar | Ana Çıktı |
|---|---|---|
| 1 | — | Şema + altyapı |
| 2 | 1 | Normalize `JobPosting` akışı |
| 3 | 1 | Sorgulanabilir RAG bilgi tabanı |
| 4 | 1, 2, 3 | Skorlanmış ilanlar + taslak ön yazılar |
| 5 | 4 | İnsan onaylı, gönderilmiş başvurular |

---

## 7. Riskler ve Açık Kalan Kararlar

- **ATS kapsama oranı:** Greenhouse/Lever gibi kaynaklar tüm sektörü kapsamaz; LinkedIn/Indeed ağırlıklı bir iş piyasasında Katman C'nin (manuel/yarı-otomatik) kullanım sıklığı yüksek olabilir — bu beklenmeli.
- **LLM maliyeti:** Writer Agent her yüksek skorlu ilan için LLM çağrısı yapacağından, günlük ilan hacmine göre maliyet tahmini yapılmalı.
- **Veri gizliliği:** Kişisel bilgi tabanı (RAG içeriği) hassas olabilir; ChromaDB volume'ünün şifrelenmesi veya en azından erişim kontrolü düşünülmeli.
- **Ölçek kararı:** Başlangıçta SQLite yeterli; eşzamanlı çoklu kullanıcı/yüksek hacim olursa PostgreSQL'e geçiş planlanmalı.

---

Bu plan, orijinal mimarinin iş değerini (RAG destekli, çok ajanlı, insan onaylı başvuru asistanı) korurken, ToS ihlali ve hesap/hukuki riski olan bot-tespit atlatma bileşenlerini çıkarır. İstersen bu planı temel alarak Faz 1'den başlayarak kod iskeletini (docker-compose, Pydantic modelleri, FastAPI endpoint'leri) adım adım kurabiliriz.