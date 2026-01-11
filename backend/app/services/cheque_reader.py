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
# CONFIGURATION ET LISTES DE RÉFÉRENCE
# ====================================================================

# 1. VILLES
VILLES_MAROC = [
    "Rabat", "Casablanca", "Marrakech", "Fès", "Tanger",
    "Agadir", "Oujda", "Meknès", "Laâyoune", "Kenitra",
    "Salé", "Tétouan", "Safi", "Mohammedia", "Khouribga",
    "Béni Mellal", "El Jadida", "Taza", "Nador", "Settat",
    "Berkane", "Khemisset", "Guelmim", "Errachidia"
]

# 2. LISTES DES NOMS ET PRÉNOMS (Fournies)
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
    "Abdeljaouad", "Adam", "Atik", "Addi", "Atiq", "Abdelkader", "Adel",
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
    "Chedad", "Cherqi", "Chihab", "Choaib", "Chouaib", "Choukri", "Dahane", "Dahbi", "Dah Mane", "Daidai",
    "Dalil", "Daoud", "Daoui", "Darid", "Darous", "Diab", "Diae", "Diae Eddine",
    "Didi", "Douraid", "Driss", "Eddaoui", "Elaid", "Elarabi", "Elarbi",
    "Elaydi", "Elbachir", "Elbouchtaoui", "Elchafii", "Elchahid", "Ebdelkahar", "Ebdelkayyaoum", "Elfatmi",
    "Elghali", "Elghaouti", "Elghazouani", "Elhabib", "Elmokhtar", "Elhachemi", "Elhassan", "Elhouari",
    "Elkebir", "Elkhadioui", "Elkhadir", "Elkhamar", "Elmadani", "Essghir", "Elmostafa", "Elmouloudi",
    "Elouafi", "Elyazi", "Ezzine", "Eloualid", "Elmahdi", "Elmahi", "Elmahjoub", "Elmakki",
    "Fadoul", "Fael", "Fathoune", "Fahd", "Faras", "Fahim", "Fettah", "Fikri",
    "Fouad", "Frahat", "Fahmi", "Farji", "Farouk", "Faik", "Farid", "Fath Allah",
    "Fath Elkhir", "Fail", "Faraji", "Fares", "Farhate", "Fathi", "Faissal", "Fadel",
    "Faiz", "Fakher", "Fakhr Eddine", "Faouaz", "Faouzi", "Ghafour", "Ghali", "Ghanem", "Ghanim",
    "Gharib", "Ghassan", "Ghazal", "Ghazi", "Ghazil", "Habib", "Hossam", "Habib Allah", "Hossam Eddine",
    "Habika", "Houari", "Hachem", "Houcine", "Haddaoui", "Houd", "Haddou", "Houdaifa",
    "Hadi", "Houmad", "Hadou", "Houmam", "Hafid", "Houmane", "Hafs", "Hoummane",
    "Haidar", "Hourma", "Haitam", "Houssam", "Hajaj", "Houssine", "Hajjaj", "Houssni",
    "Hakim", "Hsina", "Halim", "Hssina", "Hamd", "Hamda", "Hamdane", "Hamdi",
    "Hamid", "Hamidan", "Hammadi", "Hamiddouche", "Hammam", "Hammed", "Hamou", "Hamoud",
    "Hamouda", "Hamza", "Hanafi", "Hani", "Hanifa", "Harouch", "Harrou", "Hassan",
    "Haroun", "Hassoun", "Hatim", "Hazaz", "Hazem", "Hazim", "Hicham", "Hilmi",
    "Hmad", "Hmida", "Hmidane", "Hmidouch", "Horma", "Hosni", "Iad", "Ibrahim", "Ider", "Idriss",
    "Ihssane", "Ikbal", "Ilias", "Ilyas", "Imad", "Imad Eddine", "Imran", "Irchad",
    "Isaad", "Ishaq", "Ismail", "Issa", "Iyad", "Issam", "Jaafar", "Jabbour", "Jaber", "Jabir",
    "Jabour", "Jabrane", "Jad", "Jad Elmoula", "Jadouane", "Jalal", "Jalal Eddine", "Jalil",
    "Jaloul", "Jamae", "Jamal", "Jamal Eddine", "Jamea", "Jamil", "Jaouad", "Jaouhar",
    "Jar Allah", "Jarrah", "Jbilou", "Jilali", "Jnina", "Joundol", "Kabbour", "Kabir", "Kacem", "Kadem",
    "Kadhem", "Kadour", "Kais", "Kamal", "Kamel", "Kandouz", "Karam", "Karim",
    "Kassem", "Kassou", "Kebour", "Khachane", "Khair Eddine", "Khairi", "Khales", "Khalid",
    "Khalifa", "Khalil", "Khalis", "Khatib", "Kotb", "Kouider", "Labib", "Lahbib", "Lahcen", "Laite",
    "Laith", "Lakbir", "Lakhdar", "Larbi", "Latif", "Layachi", "Lokmane", "Lotfi",
    "Louay", "Loukman", "Lounes", "Lounis", "Loutfi", "Mahdi", "Maamar", "Maamoun", "Maarouf",
    "Maatallah", "Maati", "Mabrouk", "Machich", "Madani", "Mahboub", "Maher", "Mahfoud",
    "Mahjoub", "Mahjoubi", "Mahmoud", "Mahraz", "Mahrez", "Majd", "Majdoub", "Majid",
    "Makhlouf", "Malek", "Malih", "Mallal", "Mamdouh", "Mamoun", "Mandil", "Mansour",
    "Marouane", "Marzak", "Marzouk", "Masaoud", "Masrour", "Massoud", "Mazigh", "M’barek",
    "Mesbah", "Meziane", "M’hamed", "Mimoun", "Mnaouar", "Moad", "Moaouia", "Moataz",
    "Mobarek", "Mofid", "Moflih", "Nabih", "Nabil", "Nacer", "Nader", "Nadim", "Nadir", "Nafie", "Nafis",
    "Nail", "Naim", "Najah", "Najd", "Najem", "Naji", "Najib", "Najm Eddine",
    "Namir", "Naoufal", "Nasr", "Nasr Eddine", "Nassef", "Nassif", "Nassih", "Nassim",
    "Nazih", "Nezar", "Nizar", "Nouaman", "Nouh", "Nour", "Nour Eddine", "Nouri",
    "Okacha", "Okba", "Omar", "Osmane", "Otaiba", "Othmane", "Ouadie", "Ouael",
    "Ouafi", "Ouafik", "Ouahab", "Ouahib", "Ouahid", "Ouail", "Ouajdi", "Ouajih",
    "Oualid", "Oualim", "Ouassim", "Ounssi", "Oussama", "Outaiba", "Rabbah", "Rabeh", "Rabie", "Rachad",
    "Rached", "Rachid", "Radi", "Raed", "Rafie", "Rafik", "Rahali", "Rahim",
    "Rahmoun", "Raif", "Ramdane", "Ramzi", "Raouad", "Raouf", "Rayan", "Razane",
    "Razek", "Razouk", "Reda", "Reda Allah", "Redad", "Redouane", "Refki", "Reyad",
    "Rezki", "Rhassane", "Riad", "Rouchdi", "Rostom", "Saad", "Saad Eddine", "Saadoune", "Saber",
    "Sabih", "Sabri", "Sadik", "Saeb", "Safi", "Safouane", "Saghir", "Sahel",
    "Said", "Saif", "Saif Eddine", "Saif Elarab", "Saif Elislam", "Salah", "Salah Eddine", "Salam",
    "Salama", "Saleh", "Salem", "Salim", "Sallam", "Salmane", "Samad", "Sami",
    "Samih", "Samir", "Saoud Rochd", "Sarhane", "Sarie", "Seddik", "Sedki", "Selam",
    "Seouar", "Sobhi", "Sofiane", "Sohaib", "Soltan", "Soubhi", "Souhaib", "Souhail",
    "Soulaimane", "Soultane", "Sourour", "Stela", "Tachfine", "Taha", "Taher", "Taib",
    "Taibi", "Taj Eddine", "Taki Eddine", "Talal", "Taleb", "Talha", "Tami", "Tamime",
    "Taoufik", "Tarik", "Tareq", "Thami", "Tijani", "Tofail", "Touhami",
    "Yaakoob", "Yachou", "Yahia", "Yahya", "Yakd", "Yanis", "Yasser", "Yassine",
    "Yassir", "Yazid", "Younes", "Yousri", "Youssef", "Zahid", "Zahir", "Zaid", "Zakaria",
    "Zaki", "Zekri", "Zeriab", "Zeroual", "Zeryab", "Zidane", "Zine", "Zine Eddine",
    "Zine Elabidine", "Ziyad", "Zoubir", "Zouhir"
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

# Fusion de toutes les listes pour la recherche globale
ALL_NAMES = list(set(NOMS_MAROCAINS + PRENOMS_H + PRENOMS_F))

# Mapping pour les montants
CHIFFRES_LETTRES = {
    "un": "1", "une": "1", "deux": "2", "trois": "3", "quatre": "4",
    "cinq": "5", "six": "6", "sept": "7", "huit": "8", "neuf": "9",
    "dix": "1", "onze": "1", "douze": "1", "treize": "1", "quatorze": "1",
    "quinze": "1", "seize": "1", "vingt": "2", "trente": "3", 
    "quarante": "4", "cinquante": "5", "soixante": "6",
    "cent": "1", "mille": "1"
}

YOLO_WEIGHTS_PATH = os.path.abspath(os.path.join(
    os.path.dirname(__file__), 
    "..", "..", "runs", "cheque_detection_combined13", "weights", "best.pt"
))

LABELS = [
    "Signature", "Montant_Chiffres", "Montant_Lettres", 
    "Beneficiaire", "Date", "Lieu", 
    "Ligne_MICR", "Num_Cheque", "Num_Compte"
]

# ====================================================================
# CHARGEMENT DES MODÈLES
# ====================================================================

try:
    print("Chargement du modèle YOLO...")
    if not os.path.exists(YOLO_WEIGHTS_PATH):
        print(f"ERREUR: Le fichier modèle n'existe pas à: {YOLO_WEIGHTS_PATH}")
    
    DETECTION_MODEL = YOLO(YOLO_WEIGHTS_PATH)
    print("✅ Modèle YOLO chargé avec succès!")
    
    print("Chargement du lecteur EasyOCR (fr/en)...")
    OCR_READER = easyocr.Reader(['fr', 'en'], gpu=False) 
    print("✅ EasyOCR chargé avec succès!")
    
except Exception as e:
    print(f"❌ Erreur lors du chargement des modèles: {e}")
    DETECTION_MODEL = None
    OCR_READER = None

# ====================================================================
# FONCTIONS DE CORRECTION INTELLIGENTE
# ====================================================================

def get_expected_start_digit(text_amount: str) -> str:
    if not text_amount: return None
    words = re.sub(r"[^a-zA-Zàâäéèêëîïôöùûüç ]", " ", text_amount.lower()).split()
    for word in words:
        match = difflib.get_close_matches(word, CHIFFRES_LETTRES.keys(), n=1, cutoff=0.8)
        if match:
            return CHIFFRES_LETTRES[match[0]]
    return None

def correct_digits_with_text(digits: str, text_amount: str) -> str:
    if not digits or not text_amount: return digits
    expected_start = get_expected_start_digit(text_amount)
    if not expected_start: return digits
    
    if digits.startswith(expected_start):
        return digits
    if len(digits) > 1 and digits[1] == expected_start:
        print(f"💰 Correction Montant: Suppression du bruit '{digits[0]}' au début ({digits} -> {digits[1:]})")
        return digits[1:]
    return digits

def correct_city_name(text: str) -> str:
    if not text or len(text) < 3: return text
    clean = re.sub(r"[^a-zA-ZàâäéèêëîïôöùûüçÀÂÄÉÈÊËÎÏÔÖÙÛÜÇ ]", "", text).strip()
    matches = difflib.get_close_matches(clean, VILLES_MAROC, n=1, cutoff=0.6)
    if matches:
        return matches[0]
    return text

def correct_beneficiary_name(text: str) -> str:
    """
    Corrige le nom du bénéficiaire mot par mot en utilisant les listes fournies.
    Ex: "Havat" -> "Hayat", "Aiaoui" -> "Alaoui"
    """
    if not text or len(text) < 3: return text

    # Nettoyage initial : garder lettres et espaces
    clean_text = re.sub(r"[^a-zA-ZàâäéèêëîïôöùûüçÀÂÄÉÈÊËÎÏÔÖÙÛÜÇ ]", " ", text)
    words = clean_text.split()
    corrected_words = []

    for word in words:
        # Ignore les mots trop courts (de, le, el...)
        if len(word) <= 2:
            corrected_words.append(word)
            continue

        # Recherche de correspondance floue dans la grande liste fusionnée
        # On utilise capitalize() car nos listes sont en format Titre (ex: Alaoui)
        # cutoff=0.7 permet de corriger 1 ou 2 fautes de frappe
        matches = difflib.get_close_matches(word.capitalize(), ALL_NAMES, n=1, cutoff=0.7)

        if matches:
            # Si trouvé, on remplace par le nom correct de la liste
            corrected_words.append(matches[0])
        else:
            # Sinon on garde le mot original
            corrected_words.append(word)

    return " ".join(corrected_words)

def clean_ocr_text(text: str, label: str) -> str:
    if not text: return ""
    text = text.strip()

    if label == "Montant_Chiffres":
        cleaned = re.sub(r"[^0-9.,]", "", text)
        return cleaned.replace(',', '.')

    elif label in ["Num_Compte", "Num_Cheque", "Ligne_MICR"]:
        return re.sub(r"\D", "", text)

    elif label == "Lieu":
        return correct_city_name(text)
    
    elif label == "Beneficiaire":
        # Appel de la nouvelle fonction de correction des noms
        return correct_beneficiary_name(text)
        
    elif label == "Date":
        return text

    else:
        return re.sub(r"[#|_=<>*]", "", text).strip()

def image_to_base64(image_array: np.ndarray) -> str:
    try:
        _, buffer = cv2.imencode('.png', image_array)
        return base64.b64encode(buffer).decode('utf-8')
    except Exception as e:
        return ""

def run_ocr_on_zone(cropped_zone: np.ndarray) -> str:
    if OCR_READER is None: return "OCR_ERROR"
    try:
        if len(cropped_zone.shape) == 3 and cropped_zone.shape[2] == 3:
            rgb_zone = cv2.cvtColor(cropped_zone, cv2.COLOR_BGR2RGB)
        else:
            rgb_zone = cropped_zone
        results = OCR_READER.readtext(rgb_zone, detail=0, paragraph=True)
        return " ".join(results).strip() if results else ""
    except Exception as e:
        return f"OCR_FAIL: {e}"

# ====================================================================
# MAIN PROCESS
# ====================================================================

def detect_and_read_cheque_zones(image_path: str) -> dict:
    if DETECTION_MODEL is None or OCR_READER is None:
        return {"status": "ERROR", "message": "Les modèles ML ne sont pas chargés."}

    if not os.path.exists(image_path):
        return {"status": "ERROR", "message": f"Image introuvable: {image_path}"}

    img = cv2.imread(image_path)
    if img is None:
        return {"status": "ERROR", "message": "Impossible de charger l'image"}

    H, W, _ = img.shape
    results = DETECTION_MODEL(img, verbose=False)
    
    extracted_data = {}
    temp_results = {}

    for r in results:
        for box in r.boxes:
            cls = int(box.cls[0])
            label = LABELS[cls]
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
            confidence = float(box.conf[0])
            
            if label in temp_results and temp_results[label]['confidence'] > confidence:
                continue

            pad = 5
            x1, y1 = max(0, x1 - pad), max(0, y1 - pad)
            x2, y2 = min(W, x2 + pad), min(H, y2 + pad)

            cropped_zone = img[y1:y2, x1:x2]
            if cropped_zone.size == 0: continue

            data_entry = {
                "confidence": f"{confidence:.2f}",
                "bounding_box": (x1, y1, x2, y2)
            }

            if label == "Signature":
                base64_img = image_to_base64(cropped_zone)
                data_entry["base64_image"] = f"data:image/png;base64,{base64_img}"
                data_entry["text"] = "Signature Détectée"
                data_entry["is_image"] = True
            else:
                raw_text = run_ocr_on_zone(cropped_zone)
                clean_text = clean_ocr_text(raw_text, label)
                
                data_entry["text"] = clean_text
                data_entry["is_image"] = False

            extracted_data[label] = data_entry
            temp_results[label] = {'confidence': confidence}

    if "Montant_Chiffres" in extracted_data and "Montant_Lettres" in extracted_data:
        amount_digits = extracted_data["Montant_Chiffres"]["text"]
        amount_text = extracted_data["Montant_Lettres"]["text"]
        corrected_digits = correct_digits_with_text(amount_digits, amount_text)
        extracted_data["Montant_Chiffres"]["text"] = corrected_digits

    if not extracted_data:
        return {"status": "SUCCESS", "message": "Aucune zone détectée.", "data": {}}
        
    return {"status": "SUCCESS", "data": extracted_data}