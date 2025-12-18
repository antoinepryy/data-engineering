# Documentation : Processus ETL

## \- Traitement des POI \-

Cette documentation spécifie les étapes du processus ETL ; de l’extraction des données à leur intégration en BDD. Les données que l’on traite ici sont celles des POI \- Points Of Interest.

# Extraction et normalisation des données

La première étape du processus est d’extraire les flux de données des diverses sources ; telles que Apidae, Datatourisme, Tourinsoft ou encore TripAdvisor, et de les normaliser. “Normaliser les données” fait référence à l’action de transformer la structure des données de base, ainsi que probablement leurs valeurs ou typages, en un contenu intégrable à notre BDD.

Ces traitements sont propres à chaque flux source traité. Nous n’allons donc pas les reprendre. L’objectif ici est de **présenter la structure finale des données** avant intégration en BDD :

| {  "id": 0,  "closed": false,  "display": true,  "tags": \["activities\_sites\_recreationpark\_amusementpark", "activities\_aquatic\_wellness\_spa", "sites\_monument\_castle"\],  "types": \["sites", "activities"\],    "age\_limit": {    "min\_age": 1,    "max\_age": 80  },  "duration": {    "average\_duration": 1440,    "min\_duration": 60,    "max\_duration": 2880  },  "group\_size\_limit": {    "min\_group\_size": 1,    "max\_group\_size": 100000,    "max\_wheelchairs": 50000  },  "poi\_name": {    "fr": "Parc d'attraction Disneyland",    "de": "Vergnügungspark Disneyland Paris",    "en": "Disneyland Paris theme park",    "es": "Parque temático Disneyland París",    "nl": "Disneyland Parijs themapark",    "ru": "Парижский парк развлечений «Диснейленд",    "it": "Parco tematico Disneyland Paris"  },  "ratings": {    "distributions": \[      {        "type": "general",        "values": \[          {            "nb\_ratings" : 99,            "value" : 0          },          {            "nb\_ratings" : 109,            "value" : 0.25          },          {            "nb\_ratings" : 202,            "value" : 0.5          },          {            "nb\_ratings" : 362,            "value" : 0.75          },          {            "nb\_ratings" : 300,            "value" : 1          }        \]      }    \],    "types": \[      {        "source": "tripadvisor",        "values": \[          {            "mean\_value" : 0.625,            "type" : "ambiance"          },          {            "mean\_value" : 0.5,            "type" : "price"          }        \]      }    \]  },  "addresses": \[    {      "insee\_code": 77700,      "city": "Coupvray",      "zip\_code": "77700",      "department": "Seine-et-Marne",      "region": "Ile-de-France",      "country": "France",      "address\_complement": "Bis",      "street\_addresses": \["1 bd du parc Disneyland"\]    }  \],  "contacts": \[    {      "first\_name": "Marion",      "last\_name": "Chazal",      "roles": \["Réceptionniste accueil", "Responsable communication"\],      "phones": \["0969326005"\],      "emails": \["marionchazal@disneylandparis.com"\],      "websites": \["https://www.disneylandparis.com/"\]    }  \],  "descriptions": \[    {      "type": "general",      "de": "Themenpark komplex mit familienfreundlichen Fahrgeschäften, Shows und kostümierten Figuren sowie Hotels.",      "en": "Theme park complex featuring family-friendly rides, shows and costumed characters, plus hotels.",      "it": "Complesso di parchi a tema con giostre, spettacoli e personaggi in costume adatti alle famiglie, oltre a hotel.",      "fr": "Complexe de parcs à thème proposant des manèges, des spectacles et des personnages costumés pour toute la famille, ainsi que des hôtels.",      "nl": "Themapark met gezinsvriendelijke attracties, shows en gekostumeerde personages, plus hotels.",      "es": "Complejo de parques temáticos con atracciones para toda la familia, espectáculos y personajes disfrazados, además de hoteles.",      "ru": "Комплекс тематических парков с аттракционами, шоу и костюмированными персонажами для всей семьи, а также отели.",      "zh": "主题公园综合体设有适合家庭游玩的游乐设施、表演和装扮角色，还有酒店。"    }  \],  "geopoints": \[    {      "latitude": 48.8673893,      "longitude": 2.7810181,      "altitude": 50    }  \],  "pictures": \[    {      "height": 1080,      "width": 1920,      "main\_picture": true,      "url": "https://wallpaperaccess.com/full/2040001.jpg",      "file\_type": "jpg",      "capture\_date": "2024-08-25",      "copyrights": \["DisneylandParis(c)"\],      "title": {        "fr": "Château de Disneyland",        "en": "Disneyland Castle",        "es": "Castillo de Disneyland",        "de": "Disneyland-Schloss",        "nl": "Kasteel Disneyland"      },      "caption": {        "fr": "Mickey et Dingo devant le château",      },      "validity\_period": {        "start\_date": "2024-08-25",        "end\_date": "2025-08-24"      }    }  \],  "products": \[    {      "min\_price": 10.0,      "max\_price": 100.0,      "name": "Poster du château de Disneyland",      "currency": "euro",      "price\_description": "Prix dépendant de la taille du poster.",      "validity\_period": {        "start\_date": "2024-08-25",        "end\_date": "2025-08-24"      }    }  \],  "schedules": \[    {      "opening\_duration": 37080,      "opening\_time": "09:30",      "weekdays": \["Monday"\],      "validity\_period": {        "start\_date": "2024-01-01",        "end\_date": "2024-12-31"      },      "description": {        "de": "Öffnungszeiten des Parks am Montag",        "en": "Park opens on Mondays",        "it": "Il parco è aperto il lunedì",        "fr": "Période d'ouverture du parc le lundi",        "nl": "Het park is open op maandag",        "es": "El parque abre los lunes"      }    }  \],  "sources": \[    {      "reference": "ASC41AAACT100718",      "source": "Datatourisme",      "last\_update": "2024-01-01",    }  \]} |
| :---- |

*N.B. : Vous pouvez observer que les attributs ont été ordonnés par degré de complexité de leur typage : types simples (integers, strings) \< listes de types simples \< objets complexes \< listes d’objets complexes.*

Voici dorénavant les tableaux décrivant les attributs :

| Attributs simples |  |  |
| ----- | ----- | ----- |
| Attribut | type | Description |
| *id* | integer | Identifiant final en BDD Remarque : En réalité cet attribut n’est créé qu’à la fin de l’agrégation des données |
| *closed* | boolean | Définit si le POI est fermé ou non |
| *display* | boolean | Définit si le POI est affichable en application ou non |
| *tags* | list of strings | Tags du POI |
| *types* | list of strings | Types du POI |

| Objets complexes |  |  |  |
| ----- | ----- | ----- | ----- |
| Objet | Attribut | type | Description |
| *age\_limit* | *min\_age* | integer | Age minimum d’accès |
|  | *max\_age* | integer | Age maximum d’accès |
| *duration* | *average\_duration* | integer | Durée d’exploitation moyenne (en minutes) |
|  | *min\_duration* | integer | Durée d’exploitation minimale (en minutes) |
|  | *max\_duration* | integer | Durée d’exploitation maximale (en minutes) |
| *group\_size\_limit* | *min\_group\_size* | integer | Taille minimale d’accueil d’un groupe |
|  | *max\_group\_size* | integer | Taille minimale d’accueil d’un groupe |
|  | *max\_wheelchairs* | integer | Capacité maximale d’accueil de fauteuils roulants |
| *poi\_name* | *fr / de / en / …* | string | Nom du POI |
| *ratings* | *distributions* | list of objects | Valeur de notation et nombre de notations |
|  | *types* | list of objects | Valeur moyenne de notations typées suivant une source donnée |

| Listes d’objets complexes |  |  |  |
| ----- | ----- | ----- | ----- |
| Objet | Attribut | Type | Description |
| *addresses* | *insee\_code* | integer | Code INSEE de la localisation |
|  | *city* | string | Nom de la ville |
|  | *zip\_code* | string | Code postal de localisation |
|  | *department* | string | Département de la localisation |
|  | *region* | string | Région de la localisation |
|  | *country* | string | Pays de la localisation |
|  | *address\_complement* | string | Complément d’adresse |
|  | *street\_addresses* | list of strings | Adresses du POI (possiblement différentes en fonction des sources) |
| *contacts* | *first\_name* | string | Prénom du contact |
|  | *last\_name* | string | Nom du contact |
|  | *roles* | list of strings | Rôles exercés du contact au sein du POI |
|  | *phones* | list of strings | Numéros de téléphones associés au contact |
|  | *emails* | list of strings | Adresses mail associées au contact |
|  | *websites* | list of strings | Sites web associés au contact |
| *descriptions* | *type* | string | Type de la description |
|  | *fr / de / en / …* | string | Contenu de la description |
| *geopoints* | *latitude* | float | Latitude du point géographique (en degrés) |
|  | *longitude* | float | Longitude du point géographique (en degrés) |
|  | *altitude* | integer | Altitude du point géographique (en mètres) |
| *pictures* | *height* | integer | Nombre de pixels en hauteur |
|  | *width* | integer | Nombre de pixels en largeur |
|  | *main\_picture* | boolean | Détermine s’il d’agit d’une image principale du POI ou non |
|  | *url* | string | Lien URL de l’image |
|  | *file\_type* | string | Type du fichier de l’image |
|  | *capture\_date* | string | Date de capture de l’image |
|  | *copyrights* | list of strings | Liste des copyrights de l’image |
|  | *title* | {*fr / de / en / …*} (strings) | Titre donné à l’image |
|  | *caption* | {*fr / de / en / …*} (strings) | Légende donnée à l’image |
|  | *validity\_period* | {*start\_date, end\_date*} (strings) | Période de validité de l’image |
| *products* | *min\_price* | float | Prix minimum |
|  | *max\_price* | float | Prix maximum |
|  | *name* | string | Nom du produit |
|  | *currency* | string | Monnaie des prix indiqués |
|  | *price\_description* | string | Description associée |
|  | *validity\_period* | {*start\_date, end\_date*} (strings) | Période de validité du produit |
| *schedules* | *opening\_duration* | integer | Durée d’ouverture en minutes |
|  | *opening\_time* | string | Horaire d’ouverture |
|  | *weekdays* | list of strings | Jours hebdomadaires auxquels ces horaires d’ouverture sont valides |
|  | *validity\_period* | {*start\_date, end\_date*} (strings) | Période de validité de l’horaire d’ouverture |
|  | *description* | {*fr / de / en / …*} (strings) | Description associée à l’horaire d’ouverture |
| *data\_sources* | *reference* | string | Référence du POI dans le flux source |
|  | *source* | string | Nom du flux source |
|  | *last\_update* | string | Date de la dernière mise à jour des données du POI dans le flux source |

## Équivalence des tags

Les tags nous permettent de caractériser précisément la nature et le contenu d’un POI (services, équipements, langues, etc). Un traitement particulier a été mis en place. Ce dernier est commun à tous les flux et est très important. Ainsi, ce sera le seul attribut dont on va détailler ici les opérations.

Dans le flux d’origine d’un POI, il existe une multitude de colonnes dont le contenu fait références à notre nomenclature des tags. Ainsi, un **système d’équivalence** des tags a été mis en place. Son rôle est de **traduire les tags des diverses sources dans notre nomenclature**.

Le fonctionnement du système d’équivalence est le suivant :

1. Chaque colonne (= attribut) faisant référence à un tag se voit individuellement :  
   1. Ajouter une colonne “*source\_name*” dont la valeur est égale au nom d’origine du tag. Exemples : “langues\_parlees”, “langues\_documentation”, …  
   2. Renommer le nom de base de la colonne du tag en “*source\_tag*”.  
2. Les datasets des tags ayant dorénavant tous la même structure, il sont concaténés dans un dataset final. Exemple : Nous pourrions avoir deux lignes où *source\_tag* \= “Anglais” mais où *source\_name* \= “langues\_parlees” ou “langues\_documentations”.  
3. Enfin, un traitement par fichier de type tableur a été mis en place afin de traduire les tags sources dans notre nomenclature. Exemple : (“Anglais”, “langues\_parlees”) → “spoken\_languages\_en” et (“Anglais”, “langues\_documentation”) → “document\_languages\_en”

*N.B. : Ce système d’équivalence s’est perfectionné avec le temps. Les plus vieux flux ETL ont un traitement des tags légèrement différent car il est individualisé pour chaque colonne de base.*

# Détection des redondances et agrégation des données

L’agrégation des données est l’étape la plus complexe du processus ETL. Cette étape a pour objectif d’éliminer la redondance (/répétition) des données. Une fois un ensemble d’objets redondants détecté, son rôle est de gérer pour chaque attribut de l’objet la manière dont les données sont agrégées, donc réunies, en une donnée finale.

Dans notre cas, les données peuvent être redondantes simplement parce qu’un même POI peut apparaître dans plusieurs flux sources.

Dans cette partie, nous présenterons tout d’abord les moyens utilisés pour **lier les POI redondants** des divers flux sources entre eux. Ensuite, nous détaillerons le **processus d’agrégation des données** pour chacun des attributs de notre structure de données finale.

## Détection des POI redondants

Après avoir réuni les données des flux sources dans un même dataframe, il existe divers moyens mis en place pour détecter les POI redondants. Nous allons voir par la suite comment ces étapes sont ordonnées au sein du processus ETL d’agrégation des données.

### Base de données

La première étape fondamentale afin d’alléger le processus est de comparer l’état de la BDD avec notre dataframe afin de relever les POI étant déjà présents en BDD. Un POI est présent en BDD si l’on y retrouve la référence de sa source correspondante (ex :{ASC41AAACT100718, Datatourisme}).

Les POI absents de la BDD passent directement à l’étape suivante. Pour les autres, on leur attribue un certain niveau de sourcing en fonction des autres sources externes au processus ETL en lui-même qui peuvent être y être rattachées :

* Les POI dont les informations en BDD ont été vérifiées, personnalisées et validées par l’un des **responsables du POI** ont un **niveau de sourcing égal à 3**. C’est le niveau maximal.  
* Sinon, les POI dont les informations ont été modifiées suite au reporting d’un **acteur externe au POI** se voient attribuer un **niveau de sourcing de 2**.  
* Enfin, les **POI restants** ont un **niveau de sourcing égal à 1**.

Tout cela nous permet de définir la règle suivante :

“**Lorsque le  niveau de sourcing d’un POI est supérieur à 1, alors rien ne modifiera les informations déjà présentes en BDD**.”

Cette règle se justifie simplement et logiquement par un ordre d’importance des sources de données. Cependant, il est important de noter qu’un large spectre de règles peuvent être prévues d’être mises en place à l’avenir afin de garantir la fiabilité des données. Ces règles pourront notamment être basées sur les dates de dernière mise à jour des sources.

Tous les POI déjà présents en BDD ont reçu l’identifiant interne correspondant. Cela permet d’agréger les POI redondants une première fois avant de passer à la suite.

### Références communes

Il est possible que des sources de données partagent les mêmes références de base. C’est par exemple le cas entre Datatourisme et Tourinsoft.

L’étape suivante a tout naturellement été de mettre en place un système de règles permettant d’**agréger les POI partageant une référence commune à partir de flux sources différents**.

### Mesures de similarité

La dernière étape de détection des redondances est un processus de mesures de similarité entre les POI. Pour ce faire, les étapes abstraites sont les suivantes :

1. Les POI ne possédant aucune coordonnées ou code postal sont écartés du processus.  
2. Un produit cartésien entre les POI partageant le même numéro de département est réalisé.  
3. Une mesure de similarité est faite sur les noms des POI joints afin de filtrer tous les couples dont les noms ne sont pas suffisamment similaires.  
4. Si les POI joints possèdent des coordonnées, alors la distance à vol d'oiseaux entre eux est calculée. Si cette dernière est inférieure à 200 mètres, alors les deux POI sont validés comme étant redondants et sont envoyés à l’agrégation des données. Pour le reste, seuls les couples de POI dont la distance est inférieure à 1 kilomètre passent à l’étape suivante.  
5. Si les couples de POI possèdent le même code postal et que la mesure de similarité entre leurs adresses est assez élevée, alors ces derniers sont également envoyés à l’agrégation des données.

*N.B. : Cette étape possède de nombreux cas limites dûs à l’imprécision, ou le niveau de complétude, des données des flux sources.*

## Agrégation des données

Les attributs des POI redondants avec un niveau de sourcing de 1 ou nul sont tout d’abord regroupés sous forme d’unions ensemblistes, donc une liste de valeurs ou d’objets, avant d’être agrégés. Ceux dont le niveau de sourcing est supérieur à 1 sont écartés du reste du processus ETL. Comme dit auparavant, il sera possible dans le futur de mettre en place un système de règles, notamment basées sur l’ancienneté la dernière date de mise à jour, afin d’assurer la fiabilité de ces données sur le long terme.

Nous décrivons dans les tableaux ci-dessous l’agrégation de chacun des attributs des POI traités.

| Agrégations des attributs simples |  |  |
| ----- | ----- | ----- |
| Attribut | Description | Exemple |
| *closed* | Valeur maximale | \[{closed: false}, {closed: true} (source externe ou POI)\] → {closed \= true} |
| *display* | Valeur minimale | \[{source: Datatourisme, display: true}, {source: Externe, display: false} (source externe ou POI)\] → {display \= false} |
| *tags* | Union des valeurs | \[tags: \[“activities\_sites\_recreationpark\_amusementpark”\]}, {tags: \[“activities\_sites\_recreationpark\_themepark”\]}\] → {tags \= \[“activities\_sites\_recreationpark\_amusementpark”, “activities\_sites\_recreationpark\_themepark”\]} |
| *types* | Union des valeurs | \[{types: \[“activity”\]}, {types: \[“site”\]}\] → {types \= \[“activity”, “site”\]} |

| Agrégation des objets complexes |  |  |  |
| ----- | ----- | ----- | ----- |
| Objet | Attribut | Description | Exemple |
| *age\_limit* | *min\_age* | Valeur minimale | \[{min\_age: 4, max\_age: 50}, {min\_age: 18, max\_age: 99}\] → {min\_age: 4, max\_age: 99} |
|  | *max\_age* | Valeur maximale |  |
| *duration* | *average\_duration* | Valeur moyenne | \[{average\_duration: 120, min\_duration: 60, max\_duration: 180}, {average\_duration: 150, min\_duration: 90, max\_duration: 210}\] → {average\_duration: 135, min\_duration: 75, max\_duration: 195} |
|  | *min\_duration* | Valeur moyenne |  |
|  | *max\_duration* | Valeur moyenne |  |
| *group\_size\_limit* | *min\_group\_size* | Valeur minimale | \[{min\_group\_size: 10, max\_group\_size: 40, max\_wheelchairs: 50}, {min\_group\_size: 5, max\_group\_size: 100, max\_wheelchairs: 60}\] → {min\_group\_size: 5, max\_group\_size: 100, max\_wheelchairs: 60} |
|  | *max\_group\_size* | Valeur maximale |  |
|  | *max\_wheelchairs* | Valeur maximale |  |
| *poi\_name* | *fr / de / en / …* | Première valeur non nulle | \[{fr: “Parc d’attraction Disneyland”}, {fr: “Parc à thème Disneyland”, en: “Disneyland theme park”}\] → {fr: “Parc d’attraction Disneyland”, en: “Disneyland theme park”} |
| *ratings* | *distributions* | Union et somme des valeurs | \[{type: “general”, values: \[{nb\_ratings: 10, value: 0}, {nb\_ratings: 50, value: 1}\]}, {type: “general”, values: \[{nb\_ratings: 25, value: 0.25}, {nb\_ratings: 20, value: 1}\]}\] → {type: “general”, values: \[{nb\_ratings: 10, value: 0}, {nb\_ratings: 25, value: 0.25}, {nb\_ratings: 70, value: 1} |
|  | *types* | Union des valeurs | → \[{source: “Tripadvisor”, values: \[{mean\_value: 0.625, type: “cooking”}\]}, {source: “Google”, values: \[{mean\_value: 0.375, type: “service”}\]}\] |

| Agrégation des listes d’objets complexes |  |  |  |
| ----- | ----- | ----- | ----- |
| Objet | Attribut | Description | Exemple |
| *addresses* | *insee\_code* | Première valeur non nulle | \[\[{insee\_code: 41232, city: “Salbris”, zip\_code: “41300”, department: “Loir-et-Cher”, region: “Centre-Val de Loire”, country: “France”, address\_complement: “RD 2020”, street\_adresses: \[“Circuit international”\]}\], \[{city: “Salbris”, zip\_code: “41300”, street\_adresses: \[“RD 2020”\]}\]\] → \[{insee\_code: 41232, city: “Salbris”, zip\_code: “41300”, department: “Loir-et-Cher”, region: “Centre-Val de Loire”, country: “France”, address\_complement: “RD 2020”, street\_adresses: \[“Circuit international”, “RD 2020”\]}\] |
|  | *city* | Première valeur non nulle |  |
|  | *zip\_code* | Première valeur non nulle |  |
|  | *department* | Première valeur non nulle |  |
|  | *region* | Première valeur non nulle |  |
|  | *country* | Première valeur non nulle |  |
|  | *address\_complement* | Première valeur non nulle |  |
|  | *street\_addresses* | Union des valeurs |  |
| *contacts* | *first\_name* | Composant de la clé unique objet | \[\[{first\_name: “Jean”, last\_name: “Dupont”, roles: \[“Directeur”\], phones: \[“0628154683”\], emails: \[“jeandupont@gmail.com”\]}\], \[{first\_name: “Jean”, last\_name: “Dupont”, roles: \[“Directeur”, “Responsable communication”\], phones: \[“0247956128”\], emails: \[”jean.dupont@hotel.fr”\], websites: \[“www.hoteljeandupon.com”, “www.facebookhoteljeandupont.com\]}\]\] → \[{first\_name: “Jean”, last\_name: “Dupont”, roles: \[“Directeur”, “Responsable communication”\], phones: \[“0628154683”, “0247956128”\], emails: \[“jeandupont@gmail.com”, ”jean.dupont@hotel.fr”\], websites: \[“www.hoteljeandupon.com”, “www.facebookhoteljeandupont.com\]}\] |
|  | *last\_name* | Composant de la clé unique objet |  |
|  | *roles* | Union des valeurs |  |
|  | *phones* | Union des valeurs |  |
|  | *emails* | Union des valeurs |  |
|  | *websites* | Union des valeurs |  |
| *descriptions* | *type* | Composant de la clé unique objet | \[\[{type: “short”, fr: “Bienvenue dans le monde de Mickey et ses amis \!”}\], \[{type: “short”, fr: “Bienvenue à Disneyland \!”, en: “Welcome to Disneyland\!”}\]\] → \[{type: “short”, fr: “Bienvenue dans le monde de Mickey et ses amis \!”, en: “Welcome to Disneyland\!”}\] |
|  | *fr / de / en / …* | Première valeur non nulle |  |
| *geopoints* |  | Union des objets | → \[{latitude: 48.8673893, longitude: 2.7810181, altitude: 50}, {latitude: 48.86, longitude: 2.78, altitude: 10}\] |
| *pictures* | *height* | Première valeur non nulle | \[\[{height: 1080, width: 1920, main\_picture: true, url: “www.imagechateau.png”, file\_type: “png”}\], \[{main\_picture: false, url: “www.imagechateau.png”, capture\_date: "2024-08-25", copyrights: \["DisneylandParis©"\], title: {fr: Château de Disneyland"}, caption: {fr: "Mickey et Dingo devant le château"}, validity\_period: {start\_date: “2024-08-25", end\_date: "2025-08-24"}\]\] → \[{height: 1080, width: 1920, main\_picture: true, url: “www.imagechateau.png”, file\_type: “png”}, capture\_date: "2024-08-25", copyrights: \["DisneylandParis©"\], title: {fr: Château de Disneyland"}, caption: {fr: "Mickey et Dingo devant le château"}, validity\_period: {start\_date: “2024-08-25", end\_date: "2025-08-24"}\] |
|  | *width* | Première valeur non nulle |  |
|  | *main\_picture* | Valeur maximale |  |
|  | *url* | Composant de la clé unique objet |  |
|  | *file\_type* | Première valeur non nulle |  |
|  | *capture\_date* | Première valeur non nulle |  |
|  | *copyrights* | Union des valeurs |  |
|  | *title* | Première valeur non nulle |  |
|  | *caption* | Première valeur non nulle |  |
|  | *validity\_period* | end\_date: valeur maximale start\_date: valeur minimale |  |
| *products* | *min\_price* | Valeur minimale | \[\[{name: “Entrée du parc”, min\_price: 0, max\_price: 29.99, currency: “Euro”, price\_description: “Gratuit pour les moins de 3 ans, 19,99€ par mineur, 29,99€ par adulte”}\], \[{name: “Entrée du parc”, min\_price: 19.99, max\_price: 39.99, currency: “Euro”, validity\_period: {start\_date: “2025-01-01”, end\_date: “2025-12-31”}}\]\] → \[{name: “Entrée du parc”, min\_price: 0, max\_price: 39.99, currency: “Euro”, price\_description: “Gratuit pour les moins de 3 ans, 19,99€ par mineur, 29,99€ par adulte”, validity\_period: {start\_date: “2025-01-01”, end\_date: “2025-12-31”}}\] |
|  | *max\_price* | Valeur maximale |  |
|  | *name* | Composant de la clé unique objet |  |
|  | *currency* | Composant de la clé unique objet |  |
|  | *price\_description* | Première valeur non nulle |  |
|  | *validity\_period* | end\_date: valeur maximale start\_date: valeur minimale |  |
| *sources* |  | Union des objets | → \[{source: “Datatourisme”, reference: “ASC41AAACT100933”, last\_update: “2025-01-01”}, {source: “Tourinsoft”, reference: “ASC41AAACT100933”, last\_update: “2025-01-01”}\] |

### Agrégation complexe : schedules

En réalité, l’agrégation de certains attributs peut être plus complexe que celle présentée dans les tableaux ci-dessus ; notamment via les composantes de la clé unique d’objet qui ont un rôle à jouer dans la méthodologie. De toute façon, rien ne remplace l’étude en profondeur des traitements dans le logiciel KNIME afin de pleinement maîtriser le processus ETL.

C’est notamment le cas de l’agrégation de l’attribut *schedules* dont le traitement est trop complexe pour être résumé dans ces tableaux. Nous allons donc l’expliquer ici.

# Intégration en base de données

## Problématiques

* Complète-t-on les données manquantes dans tous les cas de sourcing des données ?  
  * Si oui, comment suivre la suppression volontaire de données d’un POI ?