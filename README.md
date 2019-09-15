# Erginbot League of Legends temalı Discord botu
Discord League of Legends temalı basit bir bottur. Örnek olarak kullanmanız için yüklenmiştir, kod incelenerek düzenlendiği takdirde istediğiniz değişiklikleri yapabilirsiniz.

Bot içinde olan özellikler:
  - League of Legends panolarında paylaşılan her yeni konuyu bir kanala yansıtma
  - Belli kelimelere Ergin ile Gergin'deki Ergin'in parodisi
  - Mesajları topluca silme
  - Çekiliş komutu
  

# Gerekenler:
 - Python3.5
 
# İndirilmesi gereken 3. parti kütüphaneler:
 - asyncio ```python3 -m pip install -U asyncio```
 
 - discord.py ```python3 -m pip install -U discord.py```

 - BeautifulSoup ```python3 -m pip install -U beautifulsoup4```
 
 

# Çalıştırmak için uygulanması gereken aşamalar:
  - ```discordtils > ergindata.json``` içindeki klasörde bulunan ```token```'e kendi botunuzun tokeninizi girin. Bu tokeni developer sayfasında yarattığınız bot hesabınızda bulabilirsiniz.
  - erginbot.py içindeki self.admins değişkeninde kendi kullanıcı adınızı girin.
  - İsteğe bağlı: eğer botunuzu farklı sistemlere bağlamak isterseniz (genel bir serverınız gibi) en alttaki ```Discordbot.run()``` komutunu kaldırıp FactoryHandler sınıfını commentlerden çıkarabilirsiniz.
  - Discord sunucunuzda aşağıdaki kanalları açın:
    - duyurular_ozel (Kullanılan özel komutları görmek için)
    - moderasyon (Cezalandırılan mesajları görmek için)
    - silinen_mesajlar (Silinen mesajları görmek için)
    - panolar (League of Legends panolarında paylaşılan konuları görmek için)
    
  - Artık erginbot.py'ı çalıştırabilirsiniz!
 
 # Ekstralar:
    - Erginbot'un bir yazıya tepki vermesi için ```ergindata.json```'da ```responses``` içindeki örnekler gibi içine yazılar ekleyebilirsiniz.
    - Yasaklı kelimeleri düzenlemek için ```ergindata.json```'daki ```filters``` kısmına kelime eklemeniz yeterlidir.
 
 # Komutlar:
 - !addfilter <kelime> - Yasaklı kelime listesine kelime ekler. Admin komutudur.
 - !removefilter <kelime> - Yasaklı kelime listesinden kelimeyi çıkarır. Admin komutudur.
 - !showfilters - Yasaklı kelime listesini gösterir. Admin komutudur.
 - !lsfirstmembers - Sunucudaki tüm kullanıcıları gösterir. Admin komutudur.
 - !flipcoin - Yazı tura atar.
 - !rafflemode - Çekiliş modunu açıp kapatır. Admin komutudur.
 - !kelkodver - Çekiliş modu varsa çekilişe katılır.
 - !listparticipants - Çekilişe katılanların listesini gösterir.
 - !pickwinner - Çekilişin kazanını gösterir.
 - !random - Random gülüş yapar. Bunu niye eklediğime dair fikrim yok.
 - !purge <mesaj sayısı> Son X mesajları komutun kullanıldığı kanalda siler. Admin komutudur. 
 - !msg <kanal IDsi> <mesaj> - Seçilen kanala bottan mesaj atar. Admin komutudur.
    
