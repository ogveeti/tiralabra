# Algoritmit ja tekoäly -harjoitustyö
Sarja sovitettuja suotimia tunnettujen signaalien etsimiseen kohinan seasta äänitiedostossa.
Ohjelma etsii DTMF-signaloinnin käyttämiä taajuuspareja käyttäen hyväkseen Goertzelin algoritmia ja esittää löydetyt symbolit käyttäjälle.

[Dokumentit ja viikkoraportit](https://github.com/ogveeti/tiralabra/tree/main/Dokumentaatio)

## Käyttöohjeet testausta varten
- Kloonaa projektin päähaara omalle tietokoneelle, tietokoneella tulee olla asennettuna vähintään Python 3.10 ja Poetry
- Navigoi projektihakemiston juureen, asenna projekti komennolla:
```
$ poetry install
```
- Käynnistä sovellus komennolla:
```
$ poetry run dtmf-decoder --realtime <path/to/audio.wav>
```
- Sovellusta on helppo testata mukana tulevilla äänitiedostoilla, tällöin komento on esimerkiksi:
```
$ poetry run dtmf-decoder --realtime /home/user/Downloads/tiralabra-main/test_audio_files/123456789*#_clean.wav
```
- Käynnistysparametri --realtime on tarkoitettu reaaliaikaista äänitiedoston lukua simuloivaan käyttöön. Jos haluat dekoodata äänitiedoston nopeammin, jätä parametri pois.
- Sovellus vaatii tällä hetkellä yksikanavaisia pakkaamattomia 16-bittisellä lineaarisella PCM-koodauksella olevia .wav-tiedostoja 8kHz näytteenottotaajuudella. Muut formaatit eivät toimi ja näistä annetaan virheilmoitus käyttäjälle.
- Voit kuunnella mukana tulevia äänitiedostoja erikseen saadaksesi kuvan millaisia häiriöitä niissä on mukana.
- Sovellus ei vielä tällä hetkellä tarvitse ylimääräisiä ulkopuolisia riippuvuuksia ajamiseen, joten sitä voisi ajaa myös suoraan ilman Poetryn kautta asentamista. Ohjeistus Poetryä käyttäen on tehty tulevaisuuden varalle.

- Jos haluat käyttää sovellusta reaaliaikaisena äänikorttisyötteellä, kloonaa päähaaran sijaan soundcard-input-support -haara. Tällöin tarvitset PortAudion kanssa toimivan äänikorttilähteen, joka näkyy ohjelmalle 8kHz näytteenottotaajuutta tukevana. Suurella todennäköisyydellä törmäät yhteensopivuusongelmiin äänirajapintojen kanssa ja ne joutuu ratkomaan alustakohtaisesti.
