# Määrittelydokumentti

## Valittu ohjelmointikieli
Toteutan kurssiprojektin Pythonilla, koska kurssiin sisältyy vahvasti projektin testaus, jonka ohjeet on kirjoitettu tällä oletuksella. Tiedostonkäsittely ja matemaattisten funktioiden toteutus on myös melko helppoa, joka on etu projektissa joihinkin matalan tason kieliin verrattuna. Vastaavien projektien toteutus olisi tosielämässä todennäköisempää matalan tason kielillä kohdelaitteisto huomioiden, mutta itse algoritmin toiminnan sisäistämisen kannalta tällä ei ole juuri väliä, enkä kaipaa ylimääräistä monimutkaisuutta projektiympäristön kanssa työskentelyyn. Kokemuksen puolesta voisin todennäköisesti toteuttaa projektin C:llä, jollain C++ -variantilla, C#:lla, Adalla, Rustilla, Javalla, Rubylla tai LabVIEW:illa. Näiden vertaisarvointi on mahdollista, jos joku kurssilainen niitä projektiinsa käyttäisi.

## Ratkaistava ongelma
Aion toteuttaa DTMF-signaloinnin dekoodauksen nauhoitetusta äänitiedostosta, jossa taajuusparit esiintyvät luonnollisen valkoisen kohinan ja muiden häiriöiden seassa. Kukin 16:sta DTMF-symbolista koostuu kahdesta tunnetusta siniaaltotaajuudesta, jotka eivät ole keskenään harmonisessa suhteessa, jolloin niitä ei todennäköisesti esiinny vahingossa luonnollisina häiriöinä. Käytännössä ohjelman pitää muuntaa aikadomainissa tallennettu äänidata sopivilla aikaväleillä taajuusdomainiin, tutkia esiintyykö näytesarjan spektrimuotoisessa esityksessä tunnettuja taajuuksia tietyn virhemarginaalin sisällä, ja esittää näitä tarpeeksi suurella todennäköisyydellä tunnistettuja taajuuspareja vastaavat symbolit visuaalisesti käyttäjälle.

## Toteutettava algoritmi
Ongelman ratkaisuun voisi käyttää miltei mitä tahansa nopeaa FFT-algoritmia diskreetin Fourier-muunnoksen (DFT) laskemiseksi. Yleinen tällainen olisi esimerkiksi radix-2 Cooley-Tukeyn algoritmi, jossa jonkin kahden potenssin kokoinen näytesarja pilkotaan parillisiin ja parittomiin näytteisiin, joista lasketaan rekursiivisesti DFT:t, jonka jälkeen ne yhdistetään toistensa kanssa yhdeksi spektriksi.

Yleiset nopeat algoritmit DFT:n laskemiseen on suunniteltu yleiskäyttöisiksi, jolloin niissä käytännössä lasketaan syötesarjan ristikorrelaatio jokaisen mahdollisen taajuuslokeron kanssa. Koska DTMF-signalointi käyttää vain kahdeksaa tunnettua taajuutta, ei koko syötteen kaistanleveyden mukaista lokerointia kuitenkaan kannata laskea.

Kaupalliset ohjelmistopohjaiset toteutukset ja sovellusspesifit DTMF-dekooderipiirit ovat usein käyttäneet Gerald Goertzelin 1950-luvulla kehittämää Goertzelin algoritmia, jolla ratkaistaan pieni määrä DFT:n yksittäisiä termejä tehokkaasti. Toteutan Goertzelin algoritmin myös omassa projektissani, edellä mainitun ongelman ratkaisu tällä kyseisellä algoritmilla on projektin ydin.

## Ohjelmalle annettava syöte
Ohjelmalle annetaan syötteenä aikamuotoinen sarja lineaarisesti kvantisoituja pulssikoodimoduloituja näytteitä, eli käytännössä nauhoitettua kompressoimatonta PCM-audiodataa tietyn pituisena WAV-tiedostona. Algoritmin toiminnan testausta varten syötteenä voidaan käyttää myös laskennallisesti generoituja äänisignaalitiedostoja vastaavassa formaatissa.

Jos ohjelmasta haluaisi nauhoitettujen tiedostojen sijaan reaaliaikaista äänidataa prosessoivan dekooderin, pitäisi ohjelmaan luoda jatkuvan näytevirran tietyn pituisiksi sarjoiksi pilkkova ikkunointiominaisuus, sillä valittu algoritmi vaatii lähtökohtaisesti äärellisen pituisen näytesarjan.


## Aika- ja tilavaativuudet
Goertzelin algoritmin aikavaativuus on kirjallisuuden mukaan O(N) jokaista tarkasteltavaa taajuutta kohden, eli tässä tapauksessa O(8N), kun O=(M*N) ja M=8. Aikavaativuus on siis lineaarinen, joskin tarkasteltavien taajuuksien lukumäärästä riippuvalla kertoimella.

Aiemmin mainittu Cooley-Tukeyn algoritmi on aikavaativuudeltaan O(N log N) ja matemaattisesta määritelmästä suoraan johdettu DFT O(N²), eli pienellä tarkasteltavien taajuuksien määrällä Goertzelin algoritmi on merkittävästi nopeampi.

Goertzelin algoritmin tilavaativuus on kirjallisuuden mukaan jopa O(M), jonka vuoksi se soveltuu pienille vähämuistisille sulautetuille järjestelmille huomattavasti paremmin kuin yleiskäyttöisemmät FFT-algoritmit.


## Käytettävät lähteet
Algoritmien yleiset kuvaukset löytyy melko hyvin Wikipediasta, ja olen pitänyt sitä hyvänä lähteenä myös signaalinkäsittelyyn liittyvän matematiikan kertaamiseen, sillä monet käsitteet löytyvät nopeammin kuin esimerkiksi omista tallessa olevista matematiikan kurssikirjoista.

Varsinaisessa projektin toteutusvaiheessa aion etsiä artikkeleja akateemisten kustantamojen hakutyökaluilla, sekä esimerkiksi MIT:n ja muiden yliopistojen avointa kurssimateriaalia aiheesta. Aion etsiä soveltuvaa kirjallisuutta myös artikkeleiden lähdeviitteistä.

## Hallinnolliset lisätiedot
Kuulun tietojenkäsittelytieteen kandidaatin opinto-ohjelmaan. Projektin dokumentaatiokielinä ovat suomi ja englanti kulloinkin soveltuvin osin.
