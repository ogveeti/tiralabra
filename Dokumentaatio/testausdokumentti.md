# Testausraportti

## Yksikkötestauksen kattavuusraportti.
![Kuvankaappaus kattavuusraportista](https://raw.githubusercontent.com/ogveeti/tiralabra/refs/heads/main/Dokumentaatio/test_coverage.png)

## Mitä on testattu, miten tämä tehtiin?
Ohjelmaa on testattu automaattisilla yksikkö- ja integraatiotesteillä, sekä laajemmin manuaalisesti kokonaisuutena.
Yksikkötestit tällä hetkellä:

 - Hiljainen näytekehys tunnistuu hiljaiseksi tyhjällä äänisignaalilla.
 - Goertzelin algoritmi laskee riittävän suuren tehon signaalille, kun syötetty taajuus ja tarkasteltu taajuus ovat samat.
 - Goertzelin algoritmi laskee riittävän pienen tehon signaalille, kun syötetty taajuus ei ole sama kuin tarkasteltava taajuus.
 - Pelkkää DC-komponenttia sisältävä näytekehys ei tunnistu virheellisesti symboliksi.
 - Pelkkää valkoista kohinaa sisältävä näytekehys ei tunnistu virheellisesti symboliksi.
 - Jokainen yksittäinen DTMF-symboli tunnistetaan oikein puhtaista taajuuspareista.

Manuaalisesti ohjelman toimintaa on testattu äänitiedostoilla, jotka sisältävät sarjan tunnettuja symboleja ja erilaisia haastavia häiriöitä. Näitä tiedostoja ajamalla on säädetty tunnistusrajoja, joilla on suurelta osin päästy eroon häiriöistä johtuvista virheellisistä tai ylimääräisistä symboleista, häiriöiden peittämistä aidoista symboleista sekä symbolien virheellisestä toistosta. Lisäksi ohjelman toimivuutta on testattu äänikorttisyötteellä, käyttäen siirtotienä analogiradioita sekä erilaisia kaiutin- ja mikrofonipareja.

## Minkälaisilla syötteillä testaus tehtiin?
Automaattitesteissä on käytetty Pythonissa laskennallisesti generoituja näytesarjoja, jotka ovat siniaaltoja eri taajuuksilla, satunnaista kohinaa tai DC-komponenttia.

Manuaalisesti testatessa generoin Audacityn avulla muutaman DTMF-merkkisarjan, joihin lisäsin valkoista kohinaa, vaaleanpunaista kohinaa ja 100 Hz taajuisen kanttiaallon eri amplitudeilla. Valkoinen kohina on laajakaistainen häiriö ja lähellä luonnollista kohinaa mm. analogiradioissa. 100 Hz kanttiaallolla voidaan simuloida läpi kuuluvaa kokoaaltotasasuuntaajan kytkentähäiriötä, voimakkaana se käytännössä simuloi rikki olevaa äänilaitetta, jonka häiriö kytkeytyy siirtolinjalle. Kanttiaalto koostuu kantataajuuden parittomista harmonisista siniaalloista ja muodostaa hankalasti pois suodatettavan laajakaistaisen kampailmiön hyötysignaalin päälle. 100 Hz kantataajuudella piikit osuvat lähelle DTMF:n käyttämiä taajuuksia, eikä suotimia voi virittää tarpeeksi kapeakaistaisiksi laitteiden taajuusvirhevaatimusten vuoksi. Tämä tekee kyseisestä häiriöstä todella vaikean poistettavan DTMF-signaloinnissa.

## Miten testit voidaan toistaa?
Yksikkötestit voidaan toistaa ajamalla ne Pytestillä.
Manuaalisesti ohjelmaa voi testata ajamalla sitä /test_audio_files/ -kansiosta löytyvillä generoiduilla äänitiedostoilla. Valinnainen käynnistysparametri --realtime ajaa ohjelmaa suunnilleen äänitiedoston normaalissa tahdissa, jolloin on helppo tarkastella yksittäisiä tunnistettuja symboleja visuaalisesti.
