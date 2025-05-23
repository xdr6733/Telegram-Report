# -*- coding: utf-8 -*-
import os
from flask import Flask, jsonify
import requests

app = Flask(__name__)

# ----------------------------
# 1) Ortak sabitler: Cookie ve header bilgileri
# ----------------------------
COOKIES = {
    'stel_ssid': 'f62043ff66f4fc10b3_17959580901655951696',
    'stel_ln': 'tr'
}

HEADERS = {
    'authority': 'telegram.org',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
    'cache-control': 'max-age=0',
    'content-type': 'application/x-www-form-urlencoded',
    'origin': 'https://telegram.org',
    'referer': 'https://telegram.org/support?setln=tr',
    'sec-ch-ua': '"Chromium";v="137", "Not/A)Brand";v="24"',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-platform': '"Android"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36'
}


# ----------------------------
# 2) Kök rota (Render’ın Health Check’i veya direkt kontrol için)
# ----------------------------
@app.route('/', methods=['GET'])
def index():
    return jsonify({
        "status": "API çalışıyor. Tam t.me linki için: GET /https://t.me/<kanal_adresi> şeklinde istekte bulunun."
    }), 200


# ----------------------------
# 3) Dinamik rota: /<path:channel_path>
#    – Burada `channel_path`, URL’nin son kısmındaki tam linki (örn. “https://t.me/+abcdef123”) temsil eder.
#    – Flask’in `<path:...>` converter’ı sayesinde slash ve diğer özel karakterler de yakalanır.
#    – Telegram’a şikâyet formunu bir kez POST eder, ardından kanalın açık mı kapalı mı olduğunu kontrol eder.
# ----------------------------
@app.route('/<path:channel_path>', methods=['GET'])
def report_and_check(channel_path):
    """
    Örnek kullanım:
      http://127.0.0.1:5000/https://t.me/+t3FgxUGMadthNmM8
    Bu durumda `channel_path = "https://t.me/+t3FgxUGMadthNmM8"`.
    """

    # 1) Gelen path tam olarak "https://t.me/..." şeklinde gelmelidir. 
    #    Eğer kullanıcı bazen "t.me/..." gönderirse, eksik "https://" ekleyebiliriz:
    if not channel_path.startswith("http://") and not channel_path.startswith("https://"):
        channel_url = "https://" + channel_path
    else:
        channel_url = channel_path

    # 2) Telegram.org/support formu için gereken veri gövdesini (data) oluştur
    data = {
        'message': (
            f'Merhaba Telegram Güvenlik Ekibi,\r\n\r\n'
            f'Söz konusu kanalın linki: {channel_url}\r\n\r\n'
            'Bu kanal, iki temel suç işleyerek hem Telegram’ın topluluk kurallarını hem de uluslararası hukuku ihlal etmektedir:\r\n\r\n'
            '**1) Yasa Dışı (İllegal) İçerik Paylaşımı**\r\n'
            '   - Kanalda, yasa dışı uyuşturucu tacirlerine, dolandırıcılık şebekelerine ve zararlı yazılım dağıtımına aracılık eden bağlantılar ve dosyalar paylaşılmaktadır. '
            'Bu eylem, Türkiye’de 2313 sayılı Uyuşturucu Maddelerin Murakabesi Hakkında Kanun ve 5651 sayılı İnternet Kanunu kapsamında suçtur. '
            'Bu içerikler, kullanıcıların ciddi zarar görmesine, suç işlenmesine yardım edilmesine ve kamu düzeninin bozulmasına yol açmaktadır.\r\n\r\n'
            '**2) Telif Hakkı İhlali ve Korsan Yayın**\r\n'
            '   - Kanal, telif haklarıyla korunan kitap, film, müzik ve akademik makaleleri izinsiz paylaşmaktadır. '
            'Bu paylaşımlar, Türkiye’de 5846 sayılı Fikir ve Sanat Eserleri Kanunu’na ve uluslararası düzeyde Bern Konvansiyonu ile WIPO Antlaşması’na aykırıdır. '
            'Telif hakkı sahipleri bu durumdan büyük maddi zarar görmekte, platform ise yasal yaptırımlarla karşı karşıya kalmaktadır.\r\n\r\n'
            'Yukarıdaki ihlaller, Telegram’ın hem politikalarına hem de uluslararası sözleşmelere aykırıdır. '
            'Aşağıdaki adımların derhal atılmasını talep ediyorum:\r\n'
            '- Bu kanal ve bağlantılı tüm alt hesapların kalıcı olarak kapatılması.\r\n'
            '- Kanal sahibinin IP, cihaz ve hesap erişimlerinin engellenmesi ve bu bilgilerin yasal mercilerle paylaşılması.\r\n'
            '- Telif hakkı ihlali nedeniyle paylaşılan tüm içeriklerin sistemden silinmesi.\r\n'
            '- Yasadışı içerik tespit edilen dosya ve bağlantıların kaldırılması; otomatik tarama ve denetim mekanizmalarının güçlendirilmesi.\r\n'
            '- Mağdur telif hakkı sahipleri ve kullanıcılar adına resmi bilgilendirme yapılması.\r\n\r\n'
            'Şimdiden hassasiyetiniz ve hızlı aksiyonunuz için teşekkür ederim.\r\n\r\n'
            'Saygılarımla,\r\n'
            'SEBİH KAYA\r\n'
            'Email: sebihkaya@hotmail.com\r\n'
            'Telefon: +905324820750'
        ),
        'legal_name': 'SEBİH KAYA',
        'email': 'sebihkaya@hotmail.com',
        'phone': '+905324820750',
        'setln': 'tr'
    }

    # 3) Telegram.org/support formuna POST isteği gönder
    success = False
    try:
        resp = requests.post(
            'https://telegram.org/support',
            cookies=COOKIES,
            headers=HEADERS,
            data=data,
            timeout=10
        )
        # Eğer HTML içinde success mesajı varsa, başarılı kabul et
        if '<div class="alert alert-success"><b>' in resp.text:
            success = True
    except requests.RequestException:
        success = False

    # 4) Kanalın hâlâ açık mı-kapalı mı kontrol et
    channel_closed = None
    try:
        check = requests.get(channel_url, timeout=5)
        # HTTP 200 dönüyorsa ve "Join Channel" ifadesi varsa => açık; yoksa kapalı
        if check.status_code == 200 and 'Join Channel' in check.text:
            channel_closed = False
        else:
            channel_closed = True
    except requests.RequestException:
        # İstek hata verirse veya ulaşılamazsa büyük ihtimal kapalı
        channel_closed = True
    # 5) JSON olarak geri dön
    return jsonify({
        "rapor": success,            # Şikayet formu başarılı mı?
        "kanal_kapandi_mi": channel_closed
    }), 200


if __name__ == '__main__':
    # Local geliştirme/deneme için:
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
