import pandas as pd
import random
import os
from faker import Faker

print("Script de génération de dataset (Clients et Bénéficiaires) démarré...")

# --- 1. CONFIGURATION DES CHEMINS ---
LOCAL_DATA_DIR = "backend/app/data/sign_data"
NOM_FICHIER_CLIENTS = "backend/app/data/clients_training_map.csv"
NOM_FICHIER_BENEFICIAIRES = "backend/app/data/beneficiaires.csv"

# S'assurer que le dossier de données existe
os.makedirs("backend/app/data", exist_ok=True)


# --- 2. LISTES DE NOMS (Données marocaines) ---
fake = Faker('fr_FR')
noms_marocains = [
    "Alaoui", "Ait", "Alami", "Bennani", "Mohamed", "Idrissi", "Berrada", "Hassan",
    "Lahlou", "Tazi", "Aziz", "El idrissi", "Benjelloun", "Amine", "Ayoub", "Saidi",
    "Tahiri", "El mostafa", "Cherkaoui", "Filali", "Amrani", "Daoudi", "El alaoui",
    "Yassine", "Mohammed", "Karim", "Said", "El mehdi", "Naji", "Bennis", "Rachid",
    "Chakir", "Khalil", "Kamal", "Naciri", "El alami", "Ben", "Youssef", "Ahmed",
    "Salhi", "Drissi", "Hajji", "El amrani", "Fatima", "Hamza", "Mansouri", 
    "El hassan", "Benkirane", "Sbai", "Sabri", "Hassani", "Bel", "Kadiri", "Chraibi",
    "Benali", "Rachidi", "Sara", "Talbi", "Benchekroun", "Slimani", "Ali", "Belhaj",
    "Zaki", "Sabir", "Abou", "Bakkali", "Hicham", "Es", "Mounir", "Khalid", "Rami",
    "Fathi", "Abid", "Lotfi", "Chaoui", "Jamal", "Choukri", "Ouazzani", "Marsli",
    "Bensaid", "Saadi", "El hassane", "Badr", "Dahbi", "Abdo", "Tahri", "Chahid",
    "Benmoussa", "Slaoui", "Kabbaj", "Ismaili", "Zine", "Mehdi", "Moussaoui", 
    "Lamrani", "Zakaria", "Radi", "Saber", "Amal", "Salmi", "Ziani", "Lazrak", 
    "Abdel", "Saad", "Nabil", "Messaoudi", "Azizi", "Hilali", "Hamdi", "Loukili",
    "Sadik", "Hakim", "Taha", "Nour", "Omar", "Semlali", "Raji", "Fadil", "Bennouna",
    "El hassani", "Rochdi", "Maroc", "Taleb", "Omari", "Fikri", "Hamdaoui", "Hafid",
    "Abdellaoui", "Senhaji", "Jalal", "Salim", "Bouziane", "Zeroual", "Jabri",
    "Hamid", "Malki", "Hafidi", "Aarab", "Zahir", "El mansouri", "Mansour", 
    "Touzani", "Faouzi", "Hachimi", "Baba", "Fadili", "Adil", "Touil", "Zineb",
    "Amri", "Khadija", "Azzouzi", "El asri", "Naim", "El houssine", "Ait el", 
    "Chaouki", "Chafik", "Sami", "Samir", "Dahmani", "Rais", "Simo", "Nassiri",
    "Yousfi", "Laaroussi", "Lachhab", "Nait", "Rahmouni", "Nouri", "Elidrissi",
    "Moumen", "Rafik", "Amraoui", "Sebti", "Fares", "Regragui", "Farah", "Rahmani",
    "Allali", "Housni", "Sekkat", "Moussaid", "Guessous", "Ouali", "Zouhair",
    "El omari", "Benslimane", "Mustapha", "Karam", "Zerouali", "Hanane", "Benbrahim",
    "Salma", "Abdou", "Bouzid", "Rida", "Charaf", "Sadiki", "Soussi", "Ghazi",
    "Lakhal", "Amzil", "Badri", "Brahim", "Oussama", "Hamidi", "Bensouda", "Abbassi",
    "Badaoui", "Nadir", "Id", "Bentaleb", "Fahmi", "Mabrouk", "Hasnaoui", "Haddad",
    "Kettani", "Najib", "Mahfoud", "Soufiane", "Aissaoui", "Boukhari", "El hilali",
    "El mahdi", "Kasmi", "Reda", "Jabrane", "Wahbi", "Er", "Benomar", "El bakkali",
    "Salah", "Allaoui", "Fouad", "Mourad", "Sadki", "Adnane", "Bouayad", "Kaddouri",
    "Abdellah", "Ibrahimi", "Mokhtari", "Maarouf", "Toumi", "Younes", "Hanafi",
    "Taoufik", "Karimi", "Bouzidi", "Taibi", "Taki", "Faiz", "Anouar", "Hilal",
    "Moumni", "Yacoubi", "El filali", "Tijani", "Hamzaoui", "Nejjar", "El amri",
    "Oulad", "Mouhib", "Lachgar", "Mekkaoui", "Ouardi", "Chadli", "Benamar", "Chami",
    "Boutaleb", "Ramzi", "El bachir", "Khaldi", "Saoud", "Meziane", "Belghiti",
    "Hayat", "El mustapha", "Zaoui", "Diouri", "Zitouni", "Mahboub", "Barakat",
    "Tarik", "Marouane", "El ouardi", "Elalaoui", "Benani", "El ouazzani", "Cherif",
    "Fakir", "El ghazi", "El hachimi", "Nasri", "Hamdani", "Ismail", "Bahi",
    "Morchid", "Elasri", "El habib", "Benzakour", "Mekouar", "Erraji", "Anas",
    "Atif", "Bouali", "Amghar", "Rahali", "Saadaoui", "Fassi", "Bouazza", "Mimouni",
    "Chaib", "Lakhdar", "Kharbouch", "Jamali", "Mazouz", "Elamrani", "Farid", "Safi",
    "El azzouzi", "Mahmoudi", "Majid", "El kadiri", "Hatim", "Habib", "El mokhtar",
    "Cherradi", "Habibi", "Charif", "Saoudi", "Riad", "Jaafar", "Houari",
    "El haddad", "Meftah", "Halim", "Madani", "Achraf", "El abbassi", "Stitou",
    "Ennaji", "Zerhouni", "Kaoutar", "Chihab", "Khattabi", "Fadel", "Ameziane",
    "Zahraoui"
]

prenoms_h = [
    "Abad", "Abdennasser", "Amghar", "Abbas",
    "Abdelmoula", "Amimar", "Abbou", "Allal",
    "Amine", "Abdelaalim", "Abdennour", "Amjad",
    "Abdelaati", "Abderaouf", "Ammar", "Abdeladim",
    "Abderrafie", "Amrane", "Abdelali", "Abderrazak",
    "Anis", "Abdelaziz", "Abdessabour", "Anouar",
    "Abdelbadie", "Abdessadek", "Antar", "Abdelbaki",
    "Abdessafi", "Antara", "Abdelbasset", "Abdessalam",
    "Aouab", "Abdelfattah", "Abdessamad", "Aouiss",
    "Abdelghafour", "Abdessamie", "Arbi", "Abdelghani",
    "Abdessatar", "Archane", "Abdelhadi", "Abdou",
    "Aref", "Abdelhafid", "Abdourabih", "Arif",
    "Abdelhak", "Abdrabbou", "Arij", "Abdelhakim",
    "Abed", "Arkam", "Abdelhalim", "Abid",
    "Arsalane", "Abdelhamid", "Aboubaki", "Assad",
    "Abdelhaq", "Aboubakr", "Assil", "Abdelilah",
    "Aboud", "Assou", "Abdeljabbar", "Achour",
    "Atef", "Abdeljalil", "Achraf", "Atf",
    "Abdeljaouad", "Adam", "Atik", "Abdelkabir",
    "Addi", "Atiq", "Abdelkader", "Adel",
    "Atouf", "Abdelkamel", "Adham", "Ayache",
    "Abdelkarim", "Adib", "Ayachi", "Abdelkhalek",
    "Adil", "Ayad", "Abdelkouddous", "Adnane",
    "Ayich", "Abdellah", "Afif", "Ayman",
    "Abdellatif", "Ahmed", "Ayoub", "Abdelmalek",
    "Aissa", "Azam", "Abdelmoghit", "Akram",
    "Azhar", "Abdelmonaim", "Alaeeddine", "Azmi",
    "Abdelmouaiz", "Alami", "Azzam", "Abdelmoughit",
    "Ali", "Azzeddine", "Abdelmouhaimin", "Aliane",
    "Azzelarab", "Abdelmoujib", "Alif", "Azzouz",
    "Abdelmoumen", "Alilou", "Abdelmouttalib", "Allali",
    "Abdelouadoud", "Allou", "Abdelouafi", "Allouch",
    "Abdelouahab", "Amar", "Abdelouahid", "Amara",
    "Abdelouali", "Amer", "Abdelouarete", "Ameur",
    "Abdenbi", "Ameziane",
    "Baaka", "Bachar", "Baaqa", "Baba",
    "Badr", "Badr Ezzamane", "Badr Eddine", "Badri",
    "Bahae", "Bahi", "Bahssin", "Bachir",
    "Bakkar", "Bakr", "Bamou", "Barouk",
    "Belkassem", "Benissa", "Bassam", "Bassou",
    "Belaid", "Belkas", "Benaissa", "Benasser",
    "Bendaoud", "Bennacer", "Benyaakoub", "Bichara",
    "Bichr", "Bikr", "Bilal", "Bouamama",
    "Bouamar", "Bouamrou", "Bouazza", "Bouchaib",
    "Bouekri", "Bouchta", "Bouhout", "Boujemaa",
    "Bourhim", "Bourhime", "Bousedra", "Bouselham",
    "Bouziane", "Brahim", "Brik",
    "Chaabane", "Chaddad", "Chadi", "Chadli",
    "Chafai", "Chafik", "Chafiq", "Chahed",
    "Chahid", "Chaib", "Chakib", "Chakir",
    "Chaouki", "Charaf", "Charaf Eddine", "Charki",
    "Chedad", "Cherqi", "Chihab", "Choaib",
    "Chouaib", "Choukri",
    "Dahane", "Dahbi", "Dah Mane", "Daidai",
    "Dalil", "Daoud", "Daoui", "Darid",
    "Darous", "Diab", "Diae", "Diae Eddine",
    "Didi", "Douraid", "Driss",
    "Eddaoui", "Elaid", "Elarabi", "Elarbi",
    "Elaydi", "Elbachir", "Elbouchtaoui", "Elchafii",
    "Elchahid", "Ebdelkahar", "Ebdelkayyaoum", "Elfatmi",
    "Elghali", "Elghaouti", "Elghazouani", "Elhabib",
    "Elmokhtar", "Elhachemi", "Elhassan", "Elhouari",
    "Elkebir", "Elkhadioui", "Elkhadir", "Elkhamar",
    "Elmadani", "Essghir", "Elmostafa", "Elmouloudi",
    "Elouafi", "Elyazi", "Ezzine", "Eloualid",
    "Elmahdi", "Elmahi", "Elmahjoub", "Elmakki",
    "Fadoul", "Fael", "Fathoune", "Fahd",
    "Faras", "Fahim", "Fettah", "Fikri",
    "Fouad", "Frahat", "Fahmi", "Farji",
    "Farouk", "Faik", "Farid", "Fath Allah",
    "Fath Elkhir", "Fail", "Faraji", "Fares",
    "Farhate", "Fathi", "Faissal", "Fadel",
    "Faiz", "Fakher", "Fakhr Eddine", "Faouaz",
    "Faouzi",
    "Ghafour", "Ghali", "Ghanem", "Ghanim",
    "Gharib", "Ghassan", "Ghazal", "Ghazi", "Ghazil",
    "Habib", "Hossam", "Habib Allah", "Hossam Eddine",
    "Habika", "Houari", "Hachem", "Houcine",
    "Haddaoui", "Houd", "Haddou", "Houdaifa",
    "Hadi", "Houmad", "Hadou", "Houmam",
    "Hafid", "Houmane", "Hafs", "Hoummane",
    "Haidar", "Hourma", "Haitam", "Houssam",
    "Hajaj", "Houssine", "Hajjaj", "Houssni",
    "Hakim", "Hsina", "Halim", "Hssina",
    "Hamd", "Hamda", "Hamdane", "Hamdi",
    "Hamid", "Hamidan", "Hammadi", "Hamiddouche",
    "Hammam", "Hammed", "Hamou", "Hamoud",
    "Hamouda", "Hamza", "Hanafi", "Hani",
    "Hanifa", "Harouch", "Harrou", "Hassan",
    "Haroun", "Hassoun", "Hatim", "Hazaz",
    "Hazem", "Hazim", "Hicham", "Hilmi",
    "Hmad", "Hmida", "Hmidane", "Hmidouch",
    "Horma", "Hosni",
    "Iad", "Ibrahim", "Ider", "Idriss",
    "Ihssane", "Ikbal", "Ilias", "Ilyas",
    "Imad", "Imad Eddine", "Imran", "Irchad",
    "Isaad", "Ishaq", "Ismail", "Issa",
    "Iyad", "Issam",
    "Jaafar", "Jabbour", "Jaber", "Jabir",
    "Jabour", "Jabrane", "Jad", "Jad Elmoula",
    "Jadouane", "Jalal", "Jalal Eddine", "Jalil",
    "Jaloul", "Jamae", "Jamal", "Jamal Eddine",
    "Jamea", "Jamil", "Jaouad", "Jaouhar",
    "Jar Allah", "Jarrah", "Jbilou", "Jilali",
    "Jnina", "Joundol",
    "Kabbour", "Kabir", "Kacem", "Kadem",
    "Kadhem", "Kadour", "Kais", "Kamal",
    "Kamel", "Kandouz", "Karam", "Karim",
    "Kassem", "Kassou", "Kebour", "Khachane",
    "Khair Eddine", "Khairi", "Khales", "Khalid",
    "Khalifa", "Khalil", "Khalis", "Khatib",
    "Kotb", "Kouider",
    "Labib", "Lahbib", "Lahcen", "Laite",
    "Laith", "Lakbir", "Lakhdar", "Larbi",
    "Latif", "Layachi", "Lokmane", "Lotfi",
    "Louay", "Loukman", "Lounes", "Lounis",
    "Loutfi",
    "Mahdi", "Maamar", "Maamoun", "Maarouf",
    "Maatallah", "Maati", "Mabrouk", "Machich",
    "Madani", "Mahboub", "Maher", "Mahfoud",
    "Mahjoub", "Mahjoubi", "Mahmoud", "Mahraz",
    "Mahrez", "Majd", "Majdoub", "Majid",
    "Makhlouf", "Malek", "Malih", "Mallal",
    "Mamdouh", "Mamoun", "Mandil", "Mansour",
    "Marouane", "Marzak", "Marzouk", "Masaoud",
    "Masrour", "Massoud", "Mazigh", "M’barek",
    "Mesbah", "Meziane", "M’hamed", "Mimoun",
    "Mnaouar", "Moad", "Moaouia", "Moataz",
    "Mobarek", "Mofid", "Moflih",
    "Nabih", "Nabil", "Nacer", "Nader",
    "Nadim", "Nadir", "Nafie", "Nafis",
    "Nail", "Naim", "Najah", "Najd",
    "Najem", "Naji", "Najib", "Najm Eddine",
    "Namir", "Naoufal", "Nasr", "Nasr Eddine",
    "Nassef", "Nassif", "Nassih", "Nassim",
    "Nazih", "Nezar", "Nizar", "Nouaman",
    "Nouh", "Nour", "Nour Eddine", "Nouri",
    "Okacha", "Okba", "Omar", "Osmane",
    "Otaiba", "Othmane", "Ouadie", "Ouael",
    "Ouafi", "Ouafik", "Ouahab", "Ouahib",
    "Ouahid", "Ouail", "Ouajdi", "Ouajih",
    "Oualid", "Oualim", "Ouassim", "Ounssi",
    "Oussama", "Outaiba",
    "Rabbah", "Rabeh", "Rabie", "Rachad",
    "Rached", "Rachid", "Radi", "Raed",
    "Rafie", "Rafik", "Rahali", "Rahim",
    "Rahmoun", "Raif", "Ramdane", "Ramzi",
    "Raouad", "Raouf", "Rayan", "Razane",
    "Razek", "Razouk", "Reda", "Reda Allah",
    "Redad", "Redouane", "Refki", "Reyad",
    "Rezki", "Rhassane", "Riad", "Rouchdi",
    "Rostom",
    "Saad", "Saad Eddine", "Saadoune", "Saber",
    "Sabih", "Sabri", "Sadik", "Saeb",
    "Safi", "Safouane", "Saghir", "Sahel",
    "Said", "Saif", "Saif Eddine", "Saif Elarab",
    "Saif Elislam", "Salah", "Salah Eddine", "Salam",
    "Salama", "Saleh", "Salem", "Salim",
    "Sallam", "Salmane", "Samad", "Sami",
    "Samih", "Samir", "Saoud Rochd", "Sarhane",
    "Sarie", "Seddik", "Sedki", "Selam",
    "Seouar", "Sobhi", "Sofiane", "Sohaib",
    "Soltan", "Soubhi", "Souhaib", "Souhail",
    "Soulaimane", "Soultane", "Sourour", "Stela",
    "Tachfine", "Taha", "Taher", "Taib",
    "Taibi", "Taj Eddine", "Taki Eddine", "Talal",
    "Taleb", "Talha", "Tami", "Tamime",
    "Taoufik", "Tarik", "Tareq", "Thami",
    "Tijani", "Tofail", "Touhami",
    "Yaakoob", "Yachou", "Yahia", "Yahya",
    "Yakd", "Yanis", "Yasser", "Yassine",
    "Yassir", "Yazid", "Younes", "Yousri",
    "Youssef",
    "Zahid", "Zahir", "Zaid", "Zakaria",
    "Zaki", "Zekri", "Zeriab", "Zeroual",
    "Zeryab", "Zidane", "Zine", "Zine Eddine",
    "Zine Elabidine", "Ziyad", "Zoubir", "Zouhir"
]

prenoms_f = [
    "Aafrae","Aasmae","Abida","Abir","Abla","Abouch","Achouak","Achoura",
    "Adba","Adiba","Adila","Adrae","Afaf","Afifa","Afnane","Ahlam",
    "Aicha","Aida","Ainaya","Aissaouia","Aizza","Akida","Alia","Aliana",
    "Alou","Amal","Amane","Amani","Amat Errahmane","Amina","Amria","Anbar",
    "Anika","Anissa","Ansam","Anssi","Aouatif","Aouich","Aouicha","Arbia",
    "Arifa","Arije","Arjouane","Arwa","Asmae","Assala","Assia","Assila",
    "Atiba","Atifa","Atika","Atouch","Awicha","Aya","Ayacha","Ayada",
    "Azhar","Aziza","Azouzia","Azza","Bachira","Bada","Badda","Badia",
    "Badr Essououd","Badra","Badria","Bahia","Bahija","Bahria","Bahrya","Bakhta",
    "Bamou","Bardis","Barka","Baroudia","Basima","Basma","Batoul","Baya",
    "Bouchra","Bouchtaouia","Boutaina","Bouthaina","Brika","Chaden","Chadia",
    "Chadlia","Chafia","Chafika","Chahbae","Chahida","Chahrazad","Chaimae",
    "Chakira","Chama","Chams","Chams Eddouha","Charifa","Charkia","Chefae",
    "Chehabe","Chihab","Chmicha","Chokria","Chomeysa","Chouhaiba","Choukria",
    "Choumaissa","Chourouk","Dahbia","Dalal","Dalila","Daouia","Darifa",
    "Darous","Dikra","Dina","Doha","Dounia","Drissia","Elaidya","Elamria",
    "Elazzouzia","Elbahia","Elbatoul","Eldaouia","Elissaouia","Elkasmia",
    "Elkhamsa","Elmalha","Elzahia","Ettahra","Ettam","Ezzahiria","Fada",
    "Fadila","Fadma","Fadoua","Fahima","Fairouz","Faiza","Fakhita","Fakira",
    "Fama","Fanida","Farah","Farha","Farida","Fariha","Fathia","Fatima",
    "Fatima Zohra","Fatine","Fatna","Fatou","Fatouch","Fatoum","Fattouch",
    "Fattoum","Fayda","Fikria","Firdaous","Fouzia","Ghada","Ghalia","Ghania",
    "Ghanima","Ghannou","Gharae","Ghariba","Ghazala","Ghazil","Ghenou",
    "Ghita","Ghizlane","Hababa","Habbouba","Habiba","Hachmia","Hachouma",
    "Hada","Hadbae","Hadda","Hadhoum","Hadia","Hadifa","Hadil","Hadir",
    "Hafida","Hafsa","Haifae","Hajar","Hajiba","Hajjou","Hakima","Hala",
    "Halal","Halima","Hallouma","Hamdaouia","Hamida","Hammout","Hamou",
    "Hanae","Hanane","Hania","Hanifa","Hannou","Hasiba","Hasnae","Hassana",
    "Hassna","Haya","Hayat","Heba","Hedaya","Hiba","Hibat Allah","Hidaya",
    "Hikma","Hind","Hinda","Houbaba","Houda","Houria","Ibtihaj","Ibtihal",
    "Ibtissame","Ichraf","Ichrak","Ichraq","Ifak","Ihssan","Ijja","Ijjou",
    "Ijlal","Ikbal","Ikhlas","Ikram","Ilham","Ilhame","Imane","Inaam",
    "Inas","Inaya","Ines","Insaf","Intissar","Irchad","Irfane","Isaad",
    "Israe","Issoua","Istirae","Izdihar","Jadia","Jahina","Jalila","Jamila",
    "Jaouahir","Jaouda","Jaydae","Jeddia","Jenane","Jenna","Jennate","Jihane",
    "Jmia","Jouayria","Jouda","Jouhaina","Jouhairia","Joumala","Joumana",
    "Joumane","Jounaina","Kabira","Kaema","Kaeda","Kaima","Kamar","Kamaria",
    "Kamila","Kamilia","Kamria","Kaouakib","Kaoukeb","Kaoutar","Karima",
    "Kattou","Kawakib","Kawkab","Keltoum","Kenza","Ketou","Khaddouj",
    "Khadija","Khadijatou","Khadouja","Khadra","Khalfia","Khalida","Khalila",
    "Khansae","Khaoula","Khattou","Khdijtou","Khdrae","Kheira","Khira",
    "Khlifia","Khnata","Labiba","Lajin","Lamiae","Lamyae","Lara","Latifa",
    "Layla","Leila","Lina","Lobaba","Loubana","Loubna","Louiza","Loujain",
    "Maazouza","Mabrouka","Madiha","Maessa","Maha","Mahasine","Mahbouba",
    "Mahdia","Mahjouba","Maisae","Maisane","Maissa","Majda","Marzouka",
    "Majida","Malak","Malha","Maliha","Malika","Mama","Mamat","Manal",
    "Manar","Mansoura","Maouahib","Maounia","Maria","Mariem","Marima",
    "Marjana","Marjane","Maroua","Masen","Masouda","Mayada","Mazouara",
    "M’Barka","M’Birika","Menna","Mennana","Messouda","Mezouara","Milad",
    "Milouda","Miloudia","Mimouna","Mina","Momtaza","Morjana","Mouada",
    "Moufida","Mouina","Moumna","Mouna","Mounia","Mounira","Nabaouia",
    "Nabiha","Nabila","Nachita","Nachoua","Nachwa","Nada","Nadia","Nadifa",
    "Nadira","Nadoua","Nafissa","Naghma","Nahed","Nahid","Nahida","Nahila",
    "Nahla","Naima","Najat","Najda","Najia","Najiba","Najlae","Najma",
    "Najoua","Namae","Namira","Naoual","Naouar","Naouara","Narjis","Nasiba",
    "Nasima","Nasira","Nasma","Nasria","Nassiba","Nassria","Nazha","Naziha",
    "Neama","Nehad","Nehal","Nihad","Nihal","Nisrine","Nofayla","Nora",
    "Nouma","Nour","Odria","Olaya","Olfa","Omra","Omria","Othmana",
    "Ouadia","Ouafae","Ouahiba","Ouahida","Oualada","Oualida","Ouarda",
    "Ouardia","Ouasila","Ouasima","Oud Elouard","Ouiame","Ouidad","Ouihab",
    "Ouijdane","Ouissal","Oum Elaid","Oum Elbanine","Oum Elez","Oum Elghait",
    "Oum Elhine","Oum Elkhir","Oum Essaad","Oum Hani","Oum Keltoum","Oumama",
    "Oumayya","Oumelghit","Oumnia","Ourida","Rabab","Rabha","Rabia","Racha",
    "Rachida","Rachika","Radia","Radoua","Raeda","Raeja","Rafiaa","Rafika",
    "Rahiba","Rahila","Rahima","Rahma","Rahmouna","Raida","Raihana","Raihane",
    "Rajae","Rajia","Rakouch","Rana","Randa","Rania","Raoua","Raouane",
    "Ratiba","Rayda","Rayhana","Razika","Rehab","Rehame","R’Himou","Rim",
    "Rima","Rkia","Rochdia","Rouaya","Rouhia","Roukaya","Saadia","Sabhia",
    "Sabiha","Sabira","Sabra","Sabria","Sabrina","Sadika","Safae","Safia",
    "Safira","Safoua","Sahila","Saida","Saila","Sakina","Saliha","Salima",
    "Salma","Saloua","Salsabil","Samae","Samar","Samara","Samia","Samiha",
    "Samira","Samrae","Sanae","Saousane","Sara","Sarah","Seddika","Siham",
    "Siouar","Smahane","Sofia","Sonia","Soraya","Souad","Souhaila","Souhir",
    "Soukaina","Soultana","Soumia","Tafout","Tahera","Tahour","Tahra",
    "Taimae","Takwa","Tama","Tamimount","Tamou","Tamra","Taoufika","Tasnim",
    "Thouriya","Tilila","Tisba","Tlaitmas","Tohfa","Touda","Touiba","Wadia",
    "Wahida","Wiam","Widad","Widen-May","Wissal","Yaja","Yajjou","Yakout",
    "Yamama","Yamane","Yamina","Yamna","Yasamine","Yasmina","Yasmine",
    "Yassira","Yattou","Yazza","Yetou","Yezza","Yousra","Zahia","Zahida",
    "Zahira","Zahoua","Zahra","Zahria","Zaima","Zaina","Zaineb","Zakia",
    "Zanba","Zannouba","Zanou","Zanouba","Zaytouna","Zaytounia","Zhirou",
    "Zina","Zinba","Zineb","Zohra","Zoubida","Zouina","Zoulikha"
]

prenoms_disponibles = prenoms_h + prenoms_f

# --- 3. FONCTIONS DE GÉNÉRATION DE DONNÉES SYNTHÉTIQUES ---

def generer_noms_uniques(prenoms_list, noms_list, total_requis, noms_exclus=None):
    """
    Génère une liste de noms uniques (prénom + nom).
    Vérifie qu'un nom n'est pas dans le set 'noms_exclus'.
    """
    if noms_exclus is None:
        noms_exclus = set()
        
    noms_uniques_set = set()
    data_list = []
    
    # Augmentation des tentatives car les listes sont partagées
    max_tentatives = total_requis * 20 
    tentatives = 0

    while len(data_list) < total_requis and tentatives < max_tentatives:
        prenom = random.choice(prenoms_list)
        nom = random.choice(noms_list)
        full_name = f"{prenom} {nom}"
        
        # CONTRAINTE 2 : Le nom ne doit pas être déjà utilisé (dans ce set)
        # ET ne doit pas être dans le set des noms exclus (les clients)
        if full_name not in noms_uniques_set and full_name not in noms_exclus:
            noms_uniques_set.add(full_name)
            data_list.append({"prenom": prenom, "nom": nom})
            
        tentatives += 1

    if len(data_list) < total_requis:
        print(f"Attention: Listes de noms trop petites, arrêt à {len(data_list)} noms uniques.")
                
    return data_list, noms_uniques_set

def generer_ribs_rapide(nombre_total=600):
    banques_cibles = {"230": "CIH Bank", "007": "Attijariwafa Bank", "145": "Banque Populaire"}
    ribs = []
    clients_par_banque = nombre_total // len(banques_cibles) # 600 // 3 = 200
    
    for code_banque, _ in banques_cibles.items():
        for i in range(clients_par_banque): 
             rib = f"{code_banque}{random.randint(10000, 99999):05d}{(i * 1234567) % 100000000000000:014d}{random.randint(0, 99):02d}"
             ribs.append({"RIB": rib})
    return ribs

# --- 4. PARTIE 1 : GÉNÉRATION DES 1000 BÉNÉFICIAIRES ---

print("\n--- Partie 1 : Génération des 1000 Bénéficiaires ---")
NOMBRE_BENEFICIAIRES = 1000

# Générer les 1000 bénéficiaires uniques
beneficiaires_data, beneficiaires_names_set = generer_noms_uniques(
    prenoms_disponibles, 
    noms_marocains, 
    NOMBRE_BENEFICIAIRES
)

df_beneficiaires = pd.DataFrame(beneficiaires_data)
df_beneficiaires.reset_index(inplace=True)
df_beneficiaires.rename(columns={'index': 'ID_Beneficiaire'}, inplace=True)
df_beneficiaires['ID_Beneficiaire'] = df_beneficiaires['ID_Beneficiaire'] + 1 # ID de 1 à 1000

# AJOUT : Colonne Numéro_Cheque (simulant le chèque qu'ils ont reçu)
df_beneficiaires['Numero_Cheque'] = [random.randint(2000000, 9999999) for _ in range(len(df_beneficiaires))]

# Sauvegarde
df_beneficiaires.to_csv(NOM_FICHIER_BENEFICIAIRES, index=False, encoding="utf-8-sig")

print(f"✅ Fichier '{NOM_FICHIER_BENEFICIAIRES}' généré avec {len(df_beneficiaires)} bénéficiaires uniques.")
print("\nExemple de structure du CSV (bénéficiaires) :")
print(df_beneficiaires.head())


# --- 5. PARTIE 2 : GÉNÉRATION DES 600 CLIENTS ---

print("\n--- Partie 2 : Génération des 600 Clients ---")

# Scan des dossiers de signatures
print(f"🔍 Scan du dossier de données : {LOCAL_DATA_DIR}")
try:
    signer_dirs = [d for d in os.listdir(LOCAL_DATA_DIR) if os.path.isdir(os.path.join(LOCAL_DATA_DIR, d)) and d.isdigit()]
    SIGNATURE_IDS = sorted(signer_dirs)
    NOMBRE_SIGNATAIRES_DS = len(SIGNATURE_IDS)
    if NOMBRE_SIGNATAIRES_DS == 0:
         raise ValueError(f"Aucun dossier de signataire trouvé dans {LOCAL_DATA_DIR}.")
except FileNotFoundError:
    print(f"ERREUR FATALE: Le dossier '{LOCAL_DATA_DIR}' n'a pas été trouvé.")
    exit()
print(f"Nombre de signataires disponibles dans le DS : {NOMBRE_SIGNATAIRES_DS}")

# Génération des 600 clients
NOMBRE_CLIENTS = 600
ribs_rapides = generer_ribs_rapide(NOMBRE_CLIENTS)
print(f"\n👥 Génération de {NOMBRE_CLIENTS} clients (200 par banque)...")

# CONTRAINTE 2 : Générer des noms clients qui NE SONT PAS dans la liste des bénéficiaires
clients_data, _ = generer_noms_uniques(
    prenoms_disponibles, 
    noms_marocains, 
    NOMBRE_CLIENTS,
    noms_exclus=beneficiaires_names_set # <-- Vérification d'unicité
)

clients = []
for i, rib_data in enumerate(ribs_rapides):
    nom_prenom = clients_data[i]
    
    signature_id_ref = SIGNATURE_IDS[i % NOMBRE_SIGNATAIRES_DS]
    path_genuine = os.path.join(LOCAL_DATA_DIR, signature_id_ref)
    path_forged = os.path.join(LOCAL_DATA_DIR, f"{signature_id_ref}_forg")
    solde = round(random.uniform(100, 100000), 2)
    statut = random.choice(["Actif", "Inactif"])

    clients.append({
        "ID_CLIENT_SYNTH": i + 1,
        "RIB": rib_data["RIB"],
        "Nom": nom_prenom['nom'],
        "Prénom": nom_prenom['prenom'],
        "Solde_MAD": solde,
        "Statut_Compte": statut,
        "SIGNATURE_ID_REF": signature_id_ref,
        "PATH_GENUINE": path_genuine,
        "PATH_FORGED": path_forged
    })

df_clients = pd.DataFrame(clients)

# --- 6. PARTIE 3 : LIAISON DES BÉNÉFICIAIRES (Contrainte 1) ---
print("\n🔗 Liaison des 1000 bénéficiaires aux 600 clients (sans partage)...")

# 1. Pool d'IDs (1 à 1000)
all_beneficiaries_ids = list(range(1, NOMBRE_BENEFICIAIRES + 1))
random.shuffle(all_beneficiaries_ids)

# 2. Map pour les attributions
client_beneficiaries_map = {client_id: [] for client_id in df_clients['ID_CLIENT_SYNTH']}

# 3. CONTRAINTE 1 : Attribuer 1 bénéficiaire à chaque client (les 600 premiers)
#    .pop() garantit qu'un ID n'est utilisé qu'une seule fois.
for i in range(NOMBRE_CLIENTS):
    client_id = i + 1
    if all_beneficiaries_ids: 
        client_beneficiaries_map[client_id].append(all_beneficiaries_ids.pop())

# 4. Distribuer les 400 bénéficiaires restants aléatoirement aux clients
#    (Le pool 'all_beneficiaries_ids' contient maintenant les 400 restants)
for ben_id in all_beneficiaries_ids:
    random_client_id = random.randint(1, NOMBRE_CLIENTS)
    client_beneficiaries_map[random_client_id].append(ben_id)

# 5. Ajouter la colonne au DataFrame client
df_clients['ID_Beneficiaires_Payes'] = df_clients['ID_CLIENT_SYNTH'].map(client_beneficiaries_map).astype(str)

# --- 7. SAUVEGARDE LOCALE ---
df_clients.to_csv(NOM_FICHIER_CLIENTS, index=False, encoding='utf-8')

print("\n--- RÉSULTAT FINAL (CLIENTS) ---")
print(f"🎉 TERMINÉ ! {len(df_clients)} clients synthétiques uniques générés.")
print(f"💾 Fichier CSV de mapping client sauvegardé dans: {NOM_FICHIER_CLIENTS}")
print("\nExemple de structure du CSV (clients) :")
print(df_clients[['ID_CLIENT_SYNTH', 'Nom', 'RIB', 'ID_Beneficiaires_Payes']].head())