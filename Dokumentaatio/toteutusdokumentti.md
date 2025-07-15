# Toteutusdokumentti – DTMF-dekooderi

## Ohjelman yleisrakenne

Ohjelma on komentorivipohjainen DTMF-dekooderi, joka tukee sekä WAV-tiedostojen käsittelyä että reaaliaikaista äänentunnistusta mikrofonilta. Sen rakenne perustuu seuraaviin pääkomponentteihin:

- **Äänilähde**: joko WAV-tiedosto tai mikrofonisyöte (`read_wav_file`, `run_from_microphone`)
- **Esikäsittely**: ääni jaetaan päällekkäisiin kehyksiin (`split_into_overlapping_frames`)
- **Signaalianalyysi**: Goertzel-algoritmia käytetään taajuuspiikkien laskemiseen jokaisesta kehyksestä (`goertzel_power`)
- **DTMF-tunnistus**: yhdistetään kaksi voimakkainta DTMF-taajuutta ja tarkistetaan tulos taulukosta (`process_frame`)
- **Käyttöliittymä**: terminaalipohjainen graafinen näyttö (näppäinmatriisi + tehotasot, `draw_ui`)
- **Symbolin tila-analyysi**: suodatetaan virhesymboleita, hallitaan taukoja ja toistoja (`frame_state_tracking`)

Koko ohjelma on toteutettu yhdessä Python-tiedostossa, mutta toiminnallisuudet on jaettu loogisiin funktioihin.

## Saavutetut aika- ja tilavaativuudet

Ohjelman keskeinen laskennallinen komponentti on Goertzel-algoritmi, jota käytetään spektritehon laskemiseen rajatuissa taajuuksissa. Tämä algoritmi toimii lineaarisesti kehyksen koon suhteen. Yhdelle kehykselle lasketaan tehot 8 taajuudelle (DTMF), sekä 8 harmoniselle taajuudelle, joten:

- **Aikavaativuus per kehys**: `O(N)`  
  Goertzel-algoritmi toimii lineaarisesti kehyksen koon mukaan → `O(N)`  
16 taajuutta × `O(N)` = kokonaisuudessaan `O(N)` per kehys

- **Tilavaativuus**: `O(N)`  
 Käytössä on yksi liukuvan ikkunan pituinen kehys (205 näytettä): `O(N)`
 Muistiin tallennetaan ainoastaan viimeisin kehys ja Goertzelin väliarvot → `O(N)` muistia

## Suorituskyky- ja O-analyysivertailu

Goertzel-algoritmi on valittu, koska se on huomattavasti kevyempi kuin FFT, kun halutaan laskea vain muutaman ennalta tiedetyn taajuuden spektritehoja. Tyypillinen FFT (Fast Fourier Transform) toimii `O(N log N)` aikavaativuudella, mutta on tarpeettoman raskas DTMF-signaaleille, joissa kiinnostavia taajuuksia on vain 8. Tämän vuoksi Goertzel on optimaalisempi ja mahdollistaa kevyet reaaliaikaiset toteutuksen myös pienitehoisilla alustoilla.

## Työn puutteet ja parannusehdotukset

- **Modulaarisuus**: Koko ohjelman logiikka sijaitsee nykyisellään yhdessä tiedostossa. Koodin ylläpidettävyyttä voisi parantaa jakamalla toiminnallisuudet moduuleihin.
- **Konfigurointi**: Useat signaalinkäsittelyn kynnysarvot on kovakoodattu. Näiden siirtäminen konfiguraatiotiedostoon/asetusvalikoksi parantaisi joustavuutta.
- **Reaaliaikainen tarkkuus**: Symbolin toisto- ja taukologiikka toimii käytännössä hyvin, mutta sitä voisi kehittää esimerkiksi puskuroimalla edellisiä kehyksiä, jotta lyhyemmätkin painallukset havaitaan tarkasti.
- **Käyttöliittymä**: Tekstipohjainen käyttöliittymä toimii, mutta oikea graafinen näkymä voisi olla kiva lisä, etenkin VU-mittarin ja taajuuspalkkien osalta.
- **Syötteiden käsittely ja koodin loppuviilaus**: Mikrofonipohjainen tunnistus on tällä hetkellä eriytetty koodikannassa omaksi haarakseen, sillä se nojaa Linuxin kanssa toimiviin äänirajapintoihin, eikä toimi varmasti muilla alustoilla. Ohjelma vaatii tällä hetkellä toimiakseen 8kHz näytteenottotaajuutta tukevan äänikortin, jollaisia useimmat äänikortit eivät ole. Tällä hetkellä ratkaisuna on käyttää PortAudion kanssa välissä Alsaa, Pipewireä tai vastaavaa rajapintaa, joka hoitaa uudelleennäytteistyksen, mutta tästä aiheutuu paljon yhteensopivuusongelmia. Oikea ratkaisu olisi rakentaa uudelleennäytteistys mukaan ohjelmaan ja sitä kautta tuki yleisille kuluttajaäänikorteille.
- **Testaus**: Mikrofonisyötteelle ei ole tehty automaattitestejä ja muutenkin niitä voisi laajentaa.


## Laajojen kielimallien käyttö

Tässä työssä on hyödynnetty OpenAI:n GPT-4-kielimallia seuraaviin tarkoituksiin:

- Toteutusdokumentin rakenteen viimeistely ja O-analyysin tarkistus
- Tekstin muotoiluohjeiden ja vaatimusten varmistus
- Hyödyllisten lähteiden haarukointi laajan lähdeaineiston joukosta
- Tiettyyn tarkoitukseen soveltuvien kirjastojen/rajapintojen löytäminen
- Koodin debuggaus

Varsinainen ohjelmakoodi on toteutettu itsenäisesti ilman kielimallin suoraa apua.

## Käytetyt lähteet

- Silicon Labs AN218: [DTMF Tone Generator and Receiver](https://www.silabs.com/documents/public/application-notes/an218.pdf)
- Texas Instruments SPRA096A: [Detecting DTMF Tones Using the Goertzel Algorithm](https://www.ti.com/lit/an/spra096a/spra096a.pdf)
- Embedded.com: [Single Tone Detection with the Goertzel Algorithm](https://www.embedded.com/single-tone-detection-with-the-goertzel-algorithm/)
- Embedded.com: [The Goertzel Algorithm](https://www.embedded.com/the-goertzel-algorithm/)
- Wikipedia: [Goertzel Algorithm – Wikipedia](https://en.wikipedia.org/wiki/Goertzel_algorithm)
- Python-dokumentaatio: `wave`, `argparse`, `sounddevice`, `math`, `struct`, `os`, `time`
- Pytest-dokumentaatio: [https://docs.pytest.org](https://docs.pytest.org)
