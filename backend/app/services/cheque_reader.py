import cv2
import numpy as np
import os
import easyocr
from ultralytics import YOLO
import json
import re
import base64
import difflib

# ====================================================================
# CONFIGURATION ET DONNÉES DE RÉFÉRENCE
# ====================================================================

# 1. LISTE DES VILLES (Existante)
VILLES_MAROC = [
    "Rabat", "Casablanca", "Marrakech", "Fès", "Tanger",
    "Agadir", "Oujda", "Meknès", "Laâyoune", "Kenitra",
    "Salé", "Tétouan", "Safi", "Mohammedia", "Khouribga",
    "Béni Mellal", "El Jadida", "Taza", "Nador", "Settat",
    "Berkane", "Khemisset", "Guelmim", "Errachidia"
]

# 2. LISTES DES NOMS ET PRÉNOMS (Nouvelles Listes)
NOMS_MAROCAINS = [
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

PRENOMS_H = [
    "Abad", "Abdennasser", "Amghar", "Abbas", "Abdelmoula", "Amimar", "Abbou", "Allal",
    "Amine", "Abdelaalim", "Abdennour", "Amjad", "Abdelaati", "Abderaouf", "Ammar", "Abdeladim",
    "Abderrafie", "Amrane", "Abdelali", "Abderrazak", "Anis", "Abdelaziz", "Abdessabour", "Anouar",
    "Abdelbadie", "Abdessadek", "Antar", "Abdelbaki", "Abdessafi", "Antara", "Abdelbasset", "Abdessalam",
    "Aouab", "Abdelfattah", "Abdessamad", "Aouiss", "Abdelghafour", "Abdessamie", "Arbi", "Abdelghani",
    "Abdessatar", "Archane", "Abdelhadi", "Abdou", "Aref", "Abdelhafid", "Abdourabih", "Arif",
    "Abdelhak", "Abdrabbou", "Arij", "Abdelhakim", "Abed", "Arkam", "Abdelhalim", "Abid",
    "Arsalane", "Abdelhamid", "Aboubaki", "Assad", "Abdelhaq", "Aboubakr", "Assil", "Abdelilah",
    "Aboud", "Assou", "Abdeljabbar", "Achour", "Atef", "Abdeljalil", "Achraf", "Atf",
    "Abdeljaouad", "Adam", "Atik", "Abdelkabir", "Addi", "Atiq", "Abdelkader", "Adel",
    "Atouf", "Abdelkamel", "Adham", "Ayache", "Abdelkarim", "Adib", "Ayachi", "Abdelkhalek",
    "Adil", "Ayad", "Abdelkouddous", "Adnane", "Ayich", "Abdellah", "Afif", "Ayman",
    "Abdellatif", "Ahmed", "Ayoub", "Abdelmalek", "Aissa", "Azam", "Abdelmoghit", "Akram",
    "Azhar", "Abdelmonaim", "Alaeeddine", "Azmi", "Abdelmouaiz", "Alami", "Azzam", "Abdelmoughit",
    "Ali", "Azzeddine", "Abdelmouhaimin", "Aliane", "Azzelarab", "Abdelmoujib", "Alif", "Azzouz",
    "Abdelmoumen", "Alilou", "Abdelmouttalib", "Allali", "Abdelouadoud", "Allou", "Abdelouafi", "Allouch",
    "Abdelouahab", "Amar", "Abdelouahid", "Amara", "Abdelouali", "Amer", "Abdelouarete", "Ameur",
    "Abdenbi", "Ameziane", "Baaka", "Bachar", "Baaqa", "Baba", "Badr", "Badr Ezzamane", "Badr Eddine", "Badri",
    "Bahae", "Bahi", "Bahssin", "Bachir", "Bakkar", "Bakr", "Bamou", "Barouk",
    "Belkassem", "Benissa", "Bassam", "Bassou", "Belaid", "Belkas", "Benaissa", "Benasser",
    "Bendaoud", "Bennacer", "Benyaakoub", "Bichara", "Bichr", "Bikr", "Bilal", "Bouamama",
    "Bouamar", "Bouamrou", "Bouazza", "Bouchaib", "Bouekri", "Bouchta", "Bouhout", "Boujemaa",
    "Bourhim", "Bourhime", "Bousedra", "Bouselham", "Bouziane", "Brahim", "Brik",
    "Chaabane", "Chaddad", "Chadi", "Chadli", "Chafai", "Chafik", "Chafiq", "Chahed",
    "Chahid", "Chaib", "Chakib", "Chakir", "Chaouki", "Charaf", "Charaf Eddine", "Charki",
    "Chedad", "Cherqi", "Chihab", "Choaib", "Chouaib", "Choukri",
    "Dahane", "Dahbi", "Dah Mane", "Daidai", "Dalil", "Daoud", "Daoui", "Darid",
    "Darous", "Diab", "Diae", "Diae Eddine", "Didi", "Douraid", "Driss",
    "Eddaoui", "Elaid", "Elarabi", "Elarbi", "Elaydi", "Elbachir", "Elbouchtaoui", "Elchafii",
    "Elchahid", "Ebdelkahar", "Ebdelkayyaoum", "Elfatmi", "Elghali", "Elghaouti", "Elghazouani", "Elhabib",
    "Elmokhtar", "Elhachemi", "Elhassan", "Elhouari", "Elkebir", "Elkhadioui", "Elkhadir", "Elkhamar",
    "Elmadani", "Essghir", "Elmostafa", "Elmouloudi", "Elouafi", "Elyazi", "Ezzine", "Eloualid",
    "Elmahdi", "Elmahi", "Elmahjoub", "Elmakki", "Fadoul", "Fael", "Fathoune", "Fahd",
    "Faras", "Fahim", "Fettah", "Fikri", "Fouad", "Frahat", "Fahmi", "Farji",
    "Farouk", "Faik", "Farid", "Fath Allah", "Fath Elkhir", "Fail", "Faraji", "Fares",
    "Farhate", "Fathi", "Faissal", "Fadel", "Faiz", "Fakher", "Fakhr Eddine", "Faouaz", "Faouzi",
    "Ghafour", "Ghali", "Ghanem", "Ghanim", "Gharib", "Ghassan", "Ghazal", "Ghazi", "Ghazil",
    "Habib", "Hossam", "Habib Allah", "Hossam Eddine", "Habika", "Houari", "Hachem", "Houcine",
    "Haddaoui", "Houd", "Haddou", "Houdaifa", "Hadi", "Houmad", "Hadou", "Houmam",
    "Hafid", "Houmane", "Hafs", "Hoummane", "Haidar", "Hourma", "Haitam", "Houssam",
    "Hajaj", "Houssine", "Hajjaj", "Houssni", "Hakim", "Hsina", "Halim", "Hssina",
    "Hamd", "Hamda", "Hamdane", "Hamdi", "Hamid", "Hamidan", "Hammadi", "Hamiddouche",
    "Hammam", "Hammed", "Hamou", "Hamoud", "Hamouda", "Hamza", "Hanafi", "Hani",
    "Hanifa", "Harouch", "Harrou", "Hassan", "Haroun", "Hassoun", "Hatim", "Hazaz",
    "Hazem", "Hazim", "Hicham", "Hilmi", "Hmad", "Hmida", "Hmidane", "Hmidouch", "Horma", "Hosni",
    "Iad", "Ibrahim", "Ider", "Idriss", "Ihssane", "Ikbal", "Ilias", "Ilyas",
    "Imad", "Imad Eddine", "Imran", "Irchad", "Isaad", "Ishaq", "Ismail", "Issa", "Iyad", "Issam",
    "Jaafar", "Jabbour", "Jaber", "Jabir", "Jabour", "Jabrane", "Jad", "Jad Elmoula",
    "Jadouane", "Jalal", "Jalal Eddine", "Jalil", "Jaloul", "Jamae", "Jamal", "Jamal Eddine",
    "Jamea", "Jamil", "Jaouad", "Jaouhar", "Jar Allah", "Jarrah", "Jbilou", "Jilali", "Jnina", "Joundol",
    "Kabbour", "Kabir", "Kacem", "Kadem", "Kadhem", "Kadour", "Kais", "Kamal",
    "Kamel", "Kandouz", "Karam", "Karim", "Kassem", "Kassou", "Kebour", "Khachane",
    "Khair Eddine", "Khairi", "Khales", "Khalid", "Khalifa", "Khalil", "Khalis", "Khatib", "Kotb", "Kouider",
    "Labib", "Lahbib", "Lahcen", "Laite", "Laith", "Lakbir", "Lakhdar", "Larbi",
    "Latif", "Layachi", "Lokmane", "Lotfi", "Louay", "Loukman", "Lounes", "Lounis", "Loutfi",
    "Mahdi", "Maamar", "Maamoun", "Maarouf", "Maatallah", "Maati", "Mabrouk", "Machich",
    "Madani", "Mahboub", "Maher", "Mahfoud", "Mahjoub", "Mahjoubi", "Mahmoud", "Mahraz",
    "Mahrez", "Majd", "Majdoub", "Majid", "Makhlouf", "Malek", "Malih", "Mallal",
    "Mamdouh", "Mamoun", "Mandil", "Mansour", "Marouane", "Marzak", "Marzouk", "Masaoud",
    "Masrour", "Massoud", "Mazigh", "M’barek", "Mesbah", "Meziane", "M’hamed", "Mimoun",
    "Mnaouar", "Moad", "Moaouia", "Moataz", "Mobarek", "Mofid", "Moflih",
    "Nabih", "Nabil", "Nacer", "Nader", "Nadim", "Nadir", "Nafie", "Nafis",
    "Nail", "Naim", "Najah", "Najd", "Najem", "Naji", "Najib", "Najm Eddine",
    "Namir", "Naoufal", "Nasr", "Nasr Eddine", "Nassef", "Nassif", "Nassih", "Nassim",
    "Nazih", "Nezar", "Nizar", "Nouaman", "Nouh", "Nour", "Nour Eddine", "Nouri",
    "Okacha", "Okba", "Omar", "Osmane", "Otaiba", "Othmane", "Ouadie", "Ouael",
    "Ouafi", "Ouafik", "Ouahab", "Ouahib", "Ouahid", "Ouail", "Ouajdi", "Ouajih",
    "Oualid", "Oualim", "Ouassim", "Ounssi", "Oussama", "Outaiba",
    "Rabbah", "Rabeh", "Rabie", "Rachad", "Rached", "Rachid", "Radi", "Raed",
    "Rafie", "Rafik", "Rahali", "Rahim", "Rahmoun", "Raif", "Ramdane", "Ramzi",
    "Raouad", "Raouf", "Rayan", "Razane", "Razek", "Razouk", "Reda", "Reda Allah",
    "Redad", "Redouane", "Refki", "Reyad", "Rezki", "Rhassane", "Riad", "Rouchdi", "Rostom",
    "Saad", "Saad Eddine", "Saadoune", "Saber", "Sabih", "Sabri", "Sadik", "Saeb",
    "Safi", "Safouane", "Saghir", "Sahel", "Said", "Saif", "Saif Eddine", "Saif Elarab",
    "Saif Elislam", "Salah", "Salah Eddine", "Salam", "Salama", "Saleh", "Salem", "Salim",
    "Sallam", "Salmane", "Samad", "Sami", "Samih", "Samir", "Saoud Rochd", "Sarhane",
    "Sarie", "Seddik", "Sedki", "Selam", "Seouar", "Sobhi", "Sofiane", "Sohaib",
    "Soltan", "Soubhi", "Souhaib", "Souhail", "Soulaimane", "Soultane", "Sourour", "Stela",
    "Tachfine", "Taha", "Taher", "Taib", "Taibi", "Taj Eddine", "Taki Eddine", "Talal",
    "Taleb", "Talha", "Tami", "Tamime", "Taoufik", "Tarik", "Tareq", "Thami",
    "Tijani", "Tofail", "Touhami", "Yaakoob", "Yachou", "Yahia", "Yahya",
    "Yakd", "Yanis", "Yasser", "Yassine", "Yassir", "Yazid", "Younes", "Yousri", "Youssef",
    "Zahid", "Zahir", "Zaid", "Zakaria", "Zaki", "Zekri", "Zeriab", "Zeroual",
    "Zeryab", "Zidane", "Zine", "Zine Eddine", "Zine Elabidine", "Ziyad", "Zoubir", "Zouhir"
]

PRENOMS_F = [
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

# Fusion de tous les prénoms et noms pour la correction globale du champ bénéficiaire
ALL_NAMES_REF = list(set(NOMS_MAROCAINS + PRENOMS_H + PRENOMS_F))

# 3. MAPPING POUR CHIFFRES
CHIFFRES_LETTRES = {
    "un": "1", "une": "1", "deux": "2", "trois": "3", "quatre": "4",
    "cinq": "5", "six": "6", "sept": "7", "huit": "8", "neuf": "9",
    "dix": "1", "onze": "1", "douze": "1", "treize": "1", "quatorze": "1",
    "quinze": "1", "seize": "1", "vingt": "2", "trente": "3", "quarante": "4",
    "cinquante": "5", "soixante": "6", "soixante-dix": "7",
    "quatre-vingt": "8", "quatre-vingt-dix": "9", "cent": "0", "mille": "000"
}

# --------------------------------------------------------------------
# INITIALISATION DES MODÈLES
# --------------------------------------------------------------------
# Chemin du modèle YOLO
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
YOLO_MODEL_PATH = os.path.join(BASE_DIR, "yolov8n.pt")

YOLO_MODEL = None
READER = None

def load_yolo_model():
    global YOLO_MODEL
    if YOLO_MODEL is None:
        if os.path.exists(YOLO_MODEL_PATH):
            print("Chargement du modèle YOLO...")
            YOLO_MODEL = YOLO(YOLO_MODEL_PATH)
            print("✅ Modèle YOLO chargé avec succès!")
        else:
            print(f"⚠️ Modèle YOLO introuvable à : {YOLO_MODEL_PATH}")
            # Téléchargement auto si absent
            YOLO_MODEL = YOLO("yolov8n.pt") 

def load_easyocr():
    global READER
    if READER is None:
        print("Chargement du lecteur EasyOCR (fr/en)...")
        READER = easyocr.Reader(['fr', 'en']) # Ajout 'en' pour chiffres
        print("✅ EasyOCR chargé avec succès!")

# --------------------------------------------------------------------
# FONCTIONS UTILITAIRES
# --------------------------------------------------------------------

def image_to_base64(img_array):
    """Convertit une image OpenCV en base64 pour l'envoi JSON"""
    _, buffer = cv2.imencode('.png', img_array)
    return base64.b64encode(buffer).decode('utf-8')

def correct_city_name(detected_text):
    """Corrige le nom de la ville en comparant avec la liste connue"""
    matches = difflib.get_close_matches(detected_text, VILLES_MAROC, n=1, cutoff=0.6)
    if matches:
        return matches[0]
    return detected_text

def correct_name_entity(detected_text):
    """
    Corrige un nom complet (Prénom + Nom) mot par mot.
    Exemple: "Abdelbadie Havat" -> "Abdelbadie Hayat"
    """
    if not detected_text:
        return detected_text
        
    words = detected_text.split()
    corrected_words = []
    
    for word in words:
        # On nettoie le mot (garde que les lettres) pour la comparaison
        word_clean = re.sub(r'[^a-zA-ZàâéèêîôùûçÀÂÉÈÊÎÔÙÛÇ]', '', word)
        
        if len(word_clean) > 2: # Ne pas corriger les mots trop courts
            # On cherche une correspondance (cutoff élevé car on veut être sûr)
            # On capitalize pour matcher avec la liste (ex: "havat" -> "Havat")
            matches = difflib.get_close_matches(word_clean.capitalize(), ALL_NAMES_REF, n=1, cutoff=0.7)
            if matches:
                corrected_words.append(matches[0])
            else:
                corrected_words.append(word) # On garde l'original si pas de match sûr
        else:
            corrected_words.append(word)
            
    return " ".join(corrected_words)

def clean_ocr_text(text, label):
    """Nettoie le texte brut selon le type de champ"""
    if not text:
        return ""
    
    # 1. Suppression caractères spéciaux génériques
    # (On garde lettres, chiffres, espaces, points, virgules, tirets)
    text = re.sub(r'[^a-zA-Z0-9\s.,\-\']', '', text)
    text = text.strip()

    # 2. Règles spécifiques par Label
    if label == "Montant_Chiffres":
        # Garder uniquement chiffres, points, virgules
        text = re.sub(r'[^0-9.,]', '', text)
        # Remplacer virgule par point pour standardisation décimale
        text = text.replace(',', '.')
        # Supprimer multiples points (ex: 12.34.5 -> 1234.5)
        if text.count('.') > 1:
            parts = text.split('.')
            text = "".join(parts[:-1]) + '.' + parts[-1]

    elif label == "Num_Cheque":
        # Uniquement des chiffres, souvent 7 caractères
        text = re.sub(r'[^0-9]', '', text)

    elif label == "Num_Compte":
        # Uniquement des chiffres (RIB/Compte)
        text = re.sub(r'[^0-9]', '', text)
    
    elif label == "Ligne_MICR":
        # Caractères spécifiques MICR (souvent chiffres et symboles < > :)
        # Ici on garde chiffres et chevrons si EasyOCR les lit
        text = re.sub(r'[^0-9<>]', '', text)

    elif label == "Lieu":
        # Correction automatique via liste des villes
        text = correct_city_name(text)
        
    elif label == "Beneficiaire":
        # --- NOUVEAU : Correction via liste des noms/prénoms ---
        text = correct_name_entity(text)

    return text

def run_ocr_on_zone(cropped_img):
    """Exécute EasyOCR sur une zone découpée"""
    if READER is None:
        load_easyocr()
    
    # Pour les chiffres, on peut pré-traiter l'image (seuil)
    # gray = cv2.cvtColor(cropped_img, cv2.COLOR_BGR2GRAY)
    # _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

    results = READER.readtext(cropped_img)
    
    # Concaténer tous les textes trouvés dans la zone
    full_text = " ".join([res[1] for res in results])
    return full_text

# --------------------------------------------------------------------
# LOGIQUE PRINCIPALE
# --------------------------------------------------------------------

def detect_and_read_cheque_zones(image_path):
    """
    1. Charge l'image
    2. Détecte les zones avec YOLO
    3. Applique OCR sur chaque zone
    4. Renvoie le JSON structuré
    """
    # Chargement Modèles
    load_yolo_model()
    load_easyocr()

    # Lecture image
    img = cv2.imread(image_path)
    if img is None:
        return {"error": "Impossible de lire l'image"}

    # Inférence YOLO
    results = YOLO_MODEL(img)
    
    extracted_data = {}
    temp_results = {} # Pour stocker les confiances et choisir le meilleur doublon

    for r in results:
        boxes = r.boxes
        for box in boxes:
            # Coordonnées
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            
            # Classe et Confiance
            cls_id = int(box.cls[0])
            label = YOLO_MODEL.names[cls_id]
            confidence = float(box.conf[0])

            # Découpage de la zone (Crop)
            cropped_zone = img[y1:y2, x1:x2]
            
            # Si on a déjà détecté ce label avec une meilleure confiance, on ignore celui-ci
            # Sauf si c'est une zone différente (ex: signature multiple ?) - Ici on simplifie : 1 champ par type
            if label in temp_results and temp_results[label]['confidence'] > confidence:
                continue

            data_entry = {
                "confidence": f"{confidence:.2f}",
                "bounding_box": [x1, y1, x2, y2]
            }

            if label == "Signature":
                # Pour la signature, on ne fait pas d'OCR, on renvoie l'image (base64) ou juste ok
                # Ici on renvoie l'image découpée en Base64 pour l'affichage frontend
                base64_img = image_to_base64(cropped_zone)
                data_entry["base64_image"] = f"data:image/png;base64,{base64_img}"
                data_entry["text"] = "Signature Détectée"
                data_entry["is_image"] = True
            else:
                # OCR sur la zone
                raw_text = run_ocr_on_zone(cropped_zone)
                clean_text = clean_ocr_text(raw_text, label)
                
                data_entry["text"] = clean_text
                data_entry["is_image"] = False

            extracted_data[label] = data_entry
            temp_results[label] = {'confidence': confidence}

    # --- VALIDATION CROISÉE FINALE ---
    # Comparaison Montant Chiffres vs Lettres (Optionnel / Avancé)
    # Si besoin, on peut ajouter ici une logique utilisant 'num2words' ou fuzzy match
    if "Montant_Chiffres" in extracted_data and "Montant_Lettres" in extracted_data:
        amount_digits = extracted_data["Montant_Chiffres"]["text"]
        amount_text = extracted_data["Montant_Lettres"]["text"]
        
        # Exemple simple de correction : si le montant chiffre contient des lettres par erreur
        # ou si le montant commence par un caractère parasite
        corrected_digits = correct_digits_with_text(amount_digits, amount_text)
        if corrected_digits != amount_digits:
            extracted_data["Montant_Chiffres"]["text"] = corrected_digits
            print(f"💰 Correction Montant: {amount_digits} -> {corrected_digits}")

    return extracted_data

def correct_digits_with_text(digits, text_amount):
    """
    Tente de corriger le montant en chiffres si le montant en lettres est plus clair.
    Exemple très basique : "4 7900.00" (bruit au début) vs "Sept mille..."
    """
    # Nettoyage basique
    digits_clean = digits.replace(" ", "")
    
    # Logique simplifiée : si le montant commence par un chiffre qui ne correspond pas 
    # au premier mot du texte (ex: '4' vs 'Sept'), c'est peut-être du bruit.
    # Pour l'instant, on retourne tel quel sauf cas évident.
    
    # Cas fréquent : Un '4' ou '1' parasite au début à cause du signe "DH" ou bordure
    if len(digits_clean) > 3 and not digits_clean[0].isdigit():
         return digits_clean[1:] # Enlever le premier char non-chiffre

    # Essayer de voir si le premier mot correspond au premier chiffre
    first_word = text_amount.split(' ')[0].lower() if text_amount else ""
    first_digit_map = CHIFFRES_LETTRES.get(first_word, "")
    
    if first_digit_map and len(digits_clean) > 1:
        if digits_clean[0] != first_digit_map:
            # Si le texte dit "Sept" (7) mais le chiffre dit "47..."
            # On regarde si le 2ème chiffre est le bon
            if len(digits_clean) > 1 and digits_clean[1] == first_digit_map:
                 print(f"💰 Suppression du bruit '{digits_clean[0]}' au début")
                 return digits_clean[1:]

    return digits_clean