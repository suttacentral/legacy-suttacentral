


var scUrlCreator = (function(){
    var _data = {"an": "Aṅguttara Nikāya", "an1": "Ekaka Nipāta", "an10": "Dasaka Nipāta",
        "an11": "Ekādasaka Nipāta", "an2": "Duka Nipāta", "an3": "Tika Nipāta",
        "an4": "Catukka Nipāta", "an5": "Pañcaka Nipāta", "an6": "Chakka Nipāta",
        "an7": "Sattaka Nipāta", "an8": "Aṭṭhaka Nipāta", "an9": "Navaka Nipāta",
        "arv": "Arthaviniścaya", "avs": "Avadānaśataka",
        "bo-mu-bi-pm": "Bhikkhunī Pātimokkha", "bo-mu-bi-pm-as": "Adhikaraṇasamathā",
        "bo-mu-bi-pm-np": "Nissaggiyā Pācittiyā", "bo-mu-bi-pm-pc": "Pācittiyā",
        "bo-mu-bi-pm-pd": "Pāṭidesanīyā", "bo-mu-bi-pm-pj": "Pārājika",
        "bo-mu-bi-pm-sk": "Sekhiyā", "bo-mu-bi-pm-ss": "Saṅghādisesā",
        "bo-mu-bi-vb": "Bhikkhunī Vibhaṅga", "bo-mu-bi-vb-np": "Nissaggiyā Pācittiyā",
        "bo-mu-bi-vb-pc": "Pācittiyā", "bo-mu-bi-vb-pd": "Pāṭidesanīyā",
        "bo-mu-bi-vb-pj": "Pārājika", "bo-mu-bi-vb-sk": "Sekhiyā",
        "bo-mu-bi-vb-ss": "Saṅghādisesā", "bo-mu-bu-kammavaca": "Bhikkhu Kammavācā",
        "bo-mu-bu-pm": "Bhikkhu Pātimokkha", "bo-mu-bu-pm-as": "Adhikaraṇasamathā",
        "bo-mu-bu-pm-ay": "Aniyatā", "bo-mu-bu-pm-np": "Nissaggiyā Pācittiyā",
        "bo-mu-bu-pm-pc": "Pācittiyā", "bo-mu-bu-pm-pd": "Pāṭidesanīyā",
        "bo-mu-bu-pm-pj": "Pārājika", "bo-mu-bu-pm-sk": "Sekhiyā",
        "bo-mu-bu-pm-ss": "Saṅghādisesā", "bo-mu-bu-vb": "Bhikkhu Vibhaṅga",
        "bo-mu-bu-vb-as": "Adhikaraṇasamathā", "bo-mu-bu-vb-ay": "Aniyatā",
        "bo-mu-bu-vb-np": "Nissaggiyā Pācittiyā", "bo-mu-bu-vb-pc": "Pācittiyā",
        "bo-mu-bu-vb-pd": "Pāṭidesanīyā", "bo-mu-bu-vb-pj": "Pārājika",
        "bo-mu-bu-vb-sk": "Sekhiyā", "bo-mu-bu-vb-ss": "Saṅghādisesā",
        "bo-mu-kd": "Khandhaka", "bo-mu-khuddakavatthu": "Khuddakavatthu",
        "bo-mu-uttaragantha": "Uttaragantha (1st)",
        "bo-mu-uttaragantha-2": "Uttaragantha (2nd)", "bv": "Buddhavaṃsa",
        "cnd": "Cūḷaniddesa", "cp": "Cariyāpiṭaka", "da": "Dīrghāgama",
        "dhatukaya": "Dhātukāya", "dhp": "Dhammapada", "divy": "Divyāvadāna",
        "dn": "Dīgha Nikāya", "dq": "Derge / Peking editions", "ds": "Dhammasaṅgaṇī",
        "dt": "Dhātukathā", "ea": "Ekottarikāgama (1st)", "ea-2": "Ekottarikāgama (2nd)",
        "ea1": "Ekottarikāgama 1", "ea10": "Ekottarikāgama 10",
        "ea11": "Ekottarikāgama 11", "ea12": "Ekottarikāgama 12",
        "ea13": "Ekottarikāgama 13", "ea14": "Ekottarikāgama 14",
        "ea15": "Ekottarikāgama 15", "ea16": "Ekottarikāgama 16",
        "ea17": "Ekottarikāgama 17", "ea18": "Ekottarikāgama 18",
        "ea19": "Ekottarikāgama 19", "ea2": "Ekottarikāgama 2",
        "ea20": "Ekottarikāgama 20", "ea21": "Ekottarikāgama 21",
        "ea22": "Ekottarikāgama 22", "ea23": "Ekottarikāgama 23",
        "ea24": "Ekottarikāgama 24", "ea25": "Ekottarikāgama 25",
        "ea26": "Ekottarikāgama 26", "ea27": "Ekottarikāgama 27",
        "ea28": "Ekottarikāgama 28", "ea29": "Ekottarikāgama 29",
        "ea3": "Ekottarikāgama 3", "ea30": "Ekottarikāgama 30",
        "ea31": "Ekottarikāgama 31", "ea32": "Ekottarikāgama 32",
        "ea33": "Ekottarikāgama 33", "ea34": "Ekottarikāgama 34",
        "ea35": "Ekottarikāgama 35", "ea36": "Ekottarikāgama 36",
        "ea37": "Ekottarikāgama 37", "ea38": "Ekottarikāgama 38",
        "ea39": "Ekottarikāgama 39", "ea4": "Ekottarikāgama 4",
        "ea40": "Ekottarikāgama 40", "ea41": "Ekottarikāgama 41",
        "ea42": "Ekottarikāgama 42", "ea43": "Ekottarikāgama 43",
        "ea44": "Ekottarikāgama 44", "ea45": "Ekottarikāgama 45",
        "ea46": "Ekottarikāgama 46", "ea47": "Ekottarikāgama 47",
        "ea48": "Ekottarikāgama 48", "ea49": "Ekottarikāgama 49",
        "ea5": "Ekottarikāgama 5", "ea50": "Ekottarikāgama 50",
        "ea51": "Ekottarikāgama 51", "ea52": "Ekottarikāgama 52",
        "ea6": "Ekottarikāgama 6", "ea7": "Ekottarikāgama 7", "ea8": "Ekottarikāgama 8",
        "ea9": "Ekottarikāgama 9", "gf": "Gāndhārī fragments",
        "gr-dg-bu-pm": "Bhikkhu Pātimokkha", "gr-dg-bu-pm-pc": "Pācittiyā",
        "gr-pm-bf13": "Bhikkhu Pātimokkha", "gr-pm-bf13-np": "Nissaggiyā Pācittiyā",
        "it": "Itivuttaka", "ja": "Jātaka", "jnanaprasthana": "Jnānaprasthāna",
        "kf": "Khotanese fragments", "kn": "Khuddaka Nikāya", "kp": "Khuddakapāṭha",
        "kv": "Kathāvatthu", "lal": "Lalitavistara",
        "lzh-dg-bi-kammavaca": "Bhikkhunī Kammavācā",
        "lzh-dg-bi-pm": "Bhikkhunī Pātimokkha",
        "lzh-dg-bi-pm-np": "Nissaggiyā Pācittiyā", "lzh-dg-bi-pm-pc": "Pācittiyā",
        "lzh-dg-bi-pm-pd": "Pāṭidesanīyā", "lzh-dg-bi-pm-pj": "Pārājika",
        "lzh-dg-bi-pm-sk": "Sekhiyā", "lzh-dg-bi-pm-ss": "Saṅghādisesā",
        "lzh-dg-bi-vb": "Bhikkhunī Vibhaṅga", "lzh-dg-bi-vb-np": "Nissaggiyā Pācittiyā",
        "lzh-dg-bi-vb-pc": "Pācittiyā", "lzh-dg-bi-vb-pd": "Pāṭidesanīyā",
        "lzh-dg-bi-vb-pj": "Pārājika", "lzh-dg-bi-vb-sk": "Sekhiyā",
        "lzh-dg-bi-vb-ss": "Saṅghādisesā",
        "lzh-dg-bu-kammavaca": "Bhikkhu Kammavācā (1st)",
        "lzh-dg-bu-kammavaca-2": "Bhikkhu Kammavācā (2nd)",
        "lzh-dg-bu-pm": "Bhikkhu Pātimokkha (1st)",
        "lzh-dg-bu-pm-2": "Bhikkhu Pātimokkha (2nd)",
        "lzh-dg-bu-pm-2-as": "Adhikaraṇasamathā", "lzh-dg-bu-pm-2-ay": "Aniyatā",
        "lzh-dg-bu-pm-2-np": "Nissaggiyā Pācittiyā", "lzh-dg-bu-pm-2-pc": "Pācittiyā",
        "lzh-dg-bu-pm-2-pd": "Pāṭidesanīyā", "lzh-dg-bu-pm-2-pj": "Pārājika",
        "lzh-dg-bu-pm-2-sk": "Sekhiyā", "lzh-dg-bu-pm-2-ss": "Saṅghādisesā",
        "lzh-dg-bu-pm-as": "Adhikaraṇasamathā", "lzh-dg-bu-pm-ay": "Aniyatā",
        "lzh-dg-bu-pm-np": "Nissaggiyā Pācittiyā", "lzh-dg-bu-pm-pc": "Pācittiyā",
        "lzh-dg-bu-pm-pd": "Pāṭidesanīyā", "lzh-dg-bu-pm-pj": "Pārājika",
        "lzh-dg-bu-pm-sk": "Sekhiyā", "lzh-dg-bu-pm-ss": "Saṅghādisesā",
        "lzh-dg-bu-vb": "Bhikkhu Vibhaṅga", "lzh-dg-bu-vb-as": "Adhikaraṇasamathā",
        "lzh-dg-bu-vb-ay": "Aniyatā", "lzh-dg-bu-vb-np": "Nissaggiyā Pācittiyā",
        "lzh-dg-bu-vb-pc": "Pācittiyā", "lzh-dg-bu-vb-pd": "Pāṭidesanīyā",
        "lzh-dg-bu-vb-pj": "Pārājika", "lzh-dg-bu-vb-sk": "Sekhiyā",
        "lzh-dg-bu-vb-ss": "Saṅghādisesā", "lzh-dg-kd": "Khandhaka",
        "lzh-dg-ve": "Ekottara", "lzh-dg-vs": "Saṁyutta",
        "lzh-dharmaskandha": "Dharmaskandha",
        "lzh-ka-bu-pm": "Kāśyapīya Bhikkhu Pātimokkha",
        "lzh-ka-bu-pm-as": "Adhikaraṇasamathā", "lzh-ka-bu-pm-ay": "Aniyatā",
        "lzh-ka-bu-pm-np": "Nissaggiyā Pācittiyā", "lzh-ka-bu-pm-pc": "Pācittiyā",
        "lzh-ka-bu-pm-pd": "Pāṭidesanīyā", "lzh-ka-bu-pm-pj": "Pārājika",
        "lzh-ka-bu-pm-sk": "Sekhiyā", "lzh-ka-bu-pm-ss": "Saṅghādisesā",
        "lzh-mg-asc": "Abhisamācārika", "lzh-mg-bi-pm": "Bhikkhunī Pātimokkha",
        "lzh-mg-bi-pm-as": "Adhikaraṇasamathā",
        "lzh-mg-bi-pm-np": "Nissaggiyā Pācittiyā", "lzh-mg-bi-pm-pc": "Pācittiyā",
        "lzh-mg-bi-pm-pd": "Pāṭidesanīyā", "lzh-mg-bi-pm-pj": "Pārājika",
        "lzh-mg-bi-pm-sk": "Sekhiyā", "lzh-mg-bi-pm-ss": "Saṅghādisesā",
        "lzh-mg-bi-pn": "Bhikkhunī Pakiṇṇaka", "lzh-mg-bi-vb": "Bhikkhunī Vibhaṅga",
        "lzh-mg-bi-vb-as": "Adhikaraṇasamathā",
        "lzh-mg-bi-vb-np": "Nissaggiyā Pācittiyā", "lzh-mg-bi-vb-pc": "Pācittiyā",
        "lzh-mg-bi-vb-pd": "Pāṭidesanīyā", "lzh-mg-bi-vb-pj": "Pārājika",
        "lzh-mg-bi-vb-sk": "Sekhiyā", "lzh-mg-bi-vb-ss": "Saṅghādisesā",
        "lzh-mg-bu-pm": "Bhikkhu Pātimokkha", "lzh-mg-bu-pm-as": "Adhikaraṇasamathā",
        "lzh-mg-bu-pm-ay": "Aniyatā", "lzh-mg-bu-pm-np": "Nissaggiyā Pācittiyā",
        "lzh-mg-bu-pm-pc": "Pācittiyā", "lzh-mg-bu-pm-pd": "Pāṭidesanīyā",
        "lzh-mg-bu-pm-pj": "Pārājika", "lzh-mg-bu-pm-sk": "Sekhiyā",
        "lzh-mg-bu-pm-ss": "Saṅghādisesā", "lzh-mg-bu-pn": "Bhikkhu Pakiṇṇaka",
        "lzh-mg-bu-pn-kd": "(Khandhaka)", "lzh-mg-bu-vb": "Bhikkhu Vibhaṅga",
        "lzh-mg-bu-vb-as": "Adhikaraṇasamathā", "lzh-mg-bu-vb-ay": "Aniyatā",
        "lzh-mg-bu-vb-np": "Nissaggiyā Pācittiyā", "lzh-mg-bu-vb-pc": "Pācittiyā",
        "lzh-mg-bu-vb-pd": "Pāṭidesanīyā", "lzh-mg-bu-vb-pj": "Pārājika",
        "lzh-mg-bu-vb-sk": "Sekhiyā", "lzh-mg-bu-vb-ss": "Saṅghādisesā",
        "lzh-mi-bi-pm": "Bhikkhunī Pātimokkha",
        "lzh-mi-bi-pm-np": "Nissaggiyā Pācittiyā", "lzh-mi-bi-pm-pc": "Pācittiyā",
        "lzh-mi-bi-pm-pd": "Pāṭidesanīyā", "lzh-mi-bi-pm-pj": "Pārājika",
        "lzh-mi-bi-pm-sk": "Sekhiyā", "lzh-mi-bi-pm-ss": "Saṅghādisesā",
        "lzh-mi-bi-vb": "Bhikkhunī Vibhaṅga", "lzh-mi-bi-vb-np": "Nissaggiyā Pācittiyā",
        "lzh-mi-bi-vb-pc": "Pācittiyā", "lzh-mi-bi-vb-pd": "Pāṭidesanīyā",
        "lzh-mi-bi-vb-pj": "Pārājika", "lzh-mi-bi-vb-sk": "Sekhiyā",
        "lzh-mi-bi-vb-ss": "Saṅghādisesā", "lzh-mi-bu-kammavaca": "Bhikkhu Kammavācā",
        "lzh-mi-bu-pm": "Bhikkhu Pātimokkha", "lzh-mi-bu-pm-as": "Adhikaraṇasamathā",
        "lzh-mi-bu-pm-ay": "Aniyatā", "lzh-mi-bu-pm-np": "Nissaggiyā Pācittiyā",
        "lzh-mi-bu-pm-pc": "Pācittiyā", "lzh-mi-bu-pm-pd": "Pāṭidesanīyā",
        "lzh-mi-bu-pm-pj": "Pārājika", "lzh-mi-bu-pm-sk": "Sekhiyā",
        "lzh-mi-bu-pm-ss": "Saṅghādisesā", "lzh-mi-bu-vb": "Bhikkhu Vibhaṅga",
        "lzh-mi-bu-vb-as": "Adhikaraṇasamathā", "lzh-mi-bu-vb-ay": "Aniyatā",
        "lzh-mi-bu-vb-np": "Nissaggiyā Pācittiyā", "lzh-mi-bu-vb-pc": "Pācittiyā",
        "lzh-mi-bu-vb-pd": "Pāṭidesanīyā", "lzh-mi-bu-vb-pj": "Pārājika",
        "lzh-mi-bu-vb-sk": "Sekhiyā", "lzh-mi-bu-vb-ss": "Saṅghādisesā",
        "lzh-mi-kd": "Khandhaka", "lzh-mi-vs": "Saṁyutta",
        "lzh-mu-bi-pm": "Bhikkhunī Pātimokkha", "lzh-mu-bi-pm-as": "Adhikaraṇasamathā",
        "lzh-mu-bi-pm-np": "Nissaggiyā Pācittiyā", "lzh-mu-bi-pm-pc": "Pācittiyā",
        "lzh-mu-bi-pm-pd": "Pāṭidesanīyā", "lzh-mu-bi-pm-pj": "Pārājika",
        "lzh-mu-bi-pm-sk": "Sekhiyā", "lzh-mu-bi-pm-ss": "Saṅghādisesā",
        "lzh-mu-bi-vb": "Bhikkhunī Vibhaṅga", "lzh-mu-bi-vb-np": "Nissaggiyā Pācittiyā",
        "lzh-mu-bi-vb-pc": "Pācittiyā", "lzh-mu-bi-vb-pd": "Pāṭidesanīyā",
        "lzh-mu-bi-vb-pj": "Pārājika", "lzh-mu-bi-vb-sk": "Sekhiyā",
        "lzh-mu-bi-vb-ss": "Saṅghādisesā", "lzh-mu-bu-kammavaca": "Bhikkhu Kammavācā",
        "lzh-mu-bu-pm": "Bhikkhu Pātimokkha", "lzh-mu-bu-pm-as": "Adhikaraṇasamathā",
        "lzh-mu-bu-pm-ay": "Aniyatā", "lzh-mu-bu-pm-np": "Nissaggiyā Pācittiyā",
        "lzh-mu-bu-pm-pc": "Pācittiyā", "lzh-mu-bu-pm-pd": "Pāṭidesanīyā",
        "lzh-mu-bu-pm-pj": "Pārājika", "lzh-mu-bu-pm-sk": "Sekhiyā",
        "lzh-mu-bu-pm-ss": "Saṅghādisesā", "lzh-mu-bu-vb": "Bhikkhu Vibhaṅga",
        "lzh-mu-bu-vb-as": "Adhikaraṇasamathā", "lzh-mu-bu-vb-ay": "Aniyatā",
        "lzh-mu-bu-vb-np": "Nissaggiyā Pācittiyā", "lzh-mu-bu-vb-pc": "Pācittiyā",
        "lzh-mu-bu-vb-pd": "Pāṭidesanīyā", "lzh-mu-bu-vb-pj": "Pārājika",
        "lzh-mu-bu-vb-sk": "Sekhiyā", "lzh-mu-bu-vb-ss": "Saṅghādisesā",
        "lzh-mu-kd": "Khandhaka", "lzh-mu-khuddakavatthu": "Khuddakavatthu",
        "lzh-sarv-ba": "Bhikkhu Ajjhāya", "lzh-sarv-bi-pm": "Bhikkhunī Pātimokkha",
        "lzh-sarv-bi-pm-as": "Adhikaraṇasamathā",
        "lzh-sarv-bi-pm-dh": "Bhikkhunī Pātimokkha (Dunhaung)",
        "lzh-sarv-bi-pm-dh-np": "Nissaggiyā Pācittiyā", "lzh-sarv-bi-pm-dh-pc": "Pācittiyā",
        "lzh-sarv-bi-pm-dh-pd": "Pāṭidesanīyā", "lzh-sarv-bi-pm-dh-sk": "Sekhiyā",
        "lzh-sarv-bi-pm-np": "Nissaggiyā Pācittiyā", "lzh-sarv-bi-pm-pc": "Pācittiyā",
        "lzh-sarv-bi-pm-pd": "Pāṭidesanīyā", "lzh-sarv-bi-pm-pj": "Pārājika",
        "lzh-sarv-bi-pm-sk": "Sekhiyā", "lzh-sarv-bi-pm-ss": "Saṅghādisesā",
        "lzh-sarv-bi-vb": "Bhikkhunī Vibhaṅga", "lzh-sarv-bi-vb-np": "Nissaggiyā Pācittiyā",
        "lzh-sarv-bi-vb-pc": "Pācittiyā", "lzh-sarv-bi-vb-pd": "Pāṭidesanīyā",
        "lzh-sarv-bi-vb-pj": "Pārājika", "lzh-sarv-bi-vb-sk": "Sekhiyā",
        "lzh-sarv-bi-vb-ss": "Saṅghādisesā",
        "lzh-sarv-bu-kammavaca": "Bhikkhu Kammavācā (1st)",
        "lzh-sarv-bu-kammavaca-2": "Bhikkhu Kammavācā (2nd)",
        "lzh-sarv-bu-pm": "Bhikkhu Pātimokkha (1st)",
        "lzh-sarv-bu-pm-2": "Bhikkhu Pātimokkha (2nd)",
        "lzh-sarv-bu-pm-2-as": "Adhikaraṇasamathā", "lzh-sarv-bu-pm-2-ay": "Aniyatā",
        "lzh-sarv-bu-pm-2-np": "Nissaggiyā Pācittiyā", "lzh-sarv-bu-pm-2-pc": "Pācittiyā",
        "lzh-sarv-bu-pm-2-pd": "Pāṭidesanīyā", "lzh-sarv-bu-pm-2-pj": "Pārājika",
        "lzh-sarv-bu-pm-2-sk": "Sekhiyā", "lzh-sarv-bu-pm-2-ss": "Saṅghādisesā",
        "lzh-sarv-bu-pm-as": "Adhikaraṇasamathā", "lzh-sarv-bu-pm-ay": "Aniyatā",
        "lzh-sarv-bu-pm-np": "Nissaggiyā Pācittiyā", "lzh-sarv-bu-pm-pc": "Pācittiyā",
        "lzh-sarv-bu-pm-pd": "Pāṭidesanīyā", "lzh-sarv-bu-pm-pj": "Pārājika",
        "lzh-sarv-bu-pm-sk": "Sekhiyā", "lzh-sarv-bu-pm-ss": "Saṅghādisesā",
        "lzh-sarv-bu-vb": "Bhikkhu Vibhaṅga", "lzh-sarv-bu-vb-as": "Adhikaraṇasamathā",
        "lzh-sarv-bu-vb-ay": "Aniyatā", "lzh-sarv-bu-vb-np": "Nissaggiyā Pācittiyā",
        "lzh-sarv-bu-vb-pc": "Pācittiyā", "lzh-sarv-bu-vb-pd": "Pāṭidesanīyā",
        "lzh-sarv-bu-vb-pj": "Pārājika", "lzh-sarv-bu-vb-sk": "Sekhiyā",
        "lzh-sarv-bu-vb-ss": "Saṅghādisesā", "lzh-sarv-kd": "Khandhaka",
        "lzh-sarv-matika": "Mātikā", "lzh-sarv-upali": "Upāliparipucchā",
        "lzh-sarv-ve": "Ekottara", "lzh-sarv-vi-misc": "Miscellaneous",
        "lzh-upali-bu": " Upāliparipṛcchā (T1466)",
        "lzh-upali-bu-as": "Adhikaraṇasamathā",
        "lzh-upali-bu-np": "Nissaggiyā Pācittiyā", "lzh-upali-bu-pc": "Pācittiyā",
        "lzh-upali-bu-pd": "Pāṭidesanīyā", "lzh-upali-bu-pj": "Pārājika",
        "lzh-upali-bu-sk": "Sekhiyā", "lzh-upali-bu-ss": "Saṅghādisesā",
        "ma": "Madhyamāgama", "mil": "Milindapañha", "mn": "Majjhima Nikāya",
        "mnd": "Mahāniddesa", "mvu": "Mahāvastu", "ne": "Netti",
        "oa": "Other Āgama Sūtras", "ot": "Other Taishō Texts", "other-matika": "Mātikā",
        "pariprccha": "Upāliparipṛcchā", "pe": "Peṭakopadesa", "pf": "Prākrit fragments",
        "pi-tv-bi-pm": "Bhikkhunī Pātimokkha", "pi-tv-bi-pm-as": "Adhikaraṇasamathā",
        "pi-tv-bi-pm-np": "Nissaggiyā Pācittiyā", "pi-tv-bi-pm-pc": "Pācittiyā",
        "pi-tv-bi-pm-pd": "Pāṭidesanīyā", "pi-tv-bi-pm-pj": "Pārājika",
        "pi-tv-bi-pm-sk": "Sekhiyā", "pi-tv-bi-pm-ss": "Saṅghādisesā",
        "pi-tv-bi-vb": "Bhikkhunī Vibhaṅga", "pi-tv-bi-vb-as": "Adhikaraṇasamathā",
        "pi-tv-bi-vb-np": "Nissaggiyā Pācittiyā", "pi-tv-bi-vb-pc": "Pācittiyā",
        "pi-tv-bi-vb-pd": "Pāṭidesanīyā", "pi-tv-bi-vb-pj": "Pārājika",
        "pi-tv-bi-vb-sk": "Sekhiyā", "pi-tv-bi-vb-ss": "Saṅghādisesā",
        "pi-tv-bu-pm": "Bhikkhu Pātimokkha", "pi-tv-bu-pm-as": "Adhikaraṇasamathā",
        "pi-tv-bu-pm-ay": "Aniyatā", "pi-tv-bu-pm-np": "Nissaggiyā Pācittiyā",
        "pi-tv-bu-pm-pc": "Pācittiyā", "pi-tv-bu-pm-pd": "Pāṭidesanīyā",
        "pi-tv-bu-pm-pj": "Pārājika", "pi-tv-bu-pm-sk": "Sekhiyā",
        "pi-tv-bu-pm-ss": "Saṅghādisesā", "pi-tv-bu-vb": "Bhikkhu Vibhaṅga",
        "pi-tv-bu-vb-as": "Adhikaraṇasamathā", "pi-tv-bu-vb-ay": "Aniyatā",
        "pi-tv-bu-vb-np": "Nissaggiyā Pācittiyā", "pi-tv-bu-vb-pc": "Pācittiyā",
        "pi-tv-bu-vb-pd": "Pāṭidesanīyā", "pi-tv-bu-vb-pj": "Pārājika",
        "pi-tv-bu-vb-sk": "Sekhiyā", "pi-tv-bu-vb-ss": "Saṅghādisesā",
        "pi-tv-kd": "Khandhaka", "pi-tv-pvr": "Parivāra",
        "pi-tv-pvr-bi": "(Bhikkhunī Parivāra)", "pi-tv-pvr-bi-as": "Adhikaraṇasamathā",
        "pi-tv-pvr-bi-np": "Nissaggiyā Pācittiyā", "pi-tv-pvr-bi-pc": "Pācittiyā",
        "pi-tv-pvr-bi-pd": "Pāṭidesanīyā", "pi-tv-pvr-bi-pj": "Pārājika",
        "pi-tv-pvr-bi-sk": "Sekhiyā", "pi-tv-pvr-bi-ss": "Saṅghādisesā",
        "pi-tv-pvr-bu": "(Bhikkhu Parivāra)", "pi-tv-pvr-bu-as": "Adhikaraṇasamathā",
        "pi-tv-pvr-bu-ay": "Aniyatā", "pi-tv-pvr-bu-np": "Nissaggiyā Pācittiyā",
        "pi-tv-pvr-bu-pc": "Pācittiyā", "pi-tv-pvr-bu-pd": "Pāṭidesanīyā",
        "pi-tv-pvr-bu-pj": "Pārājika", "pi-tv-pvr-bu-sk": "Sekhiyā",
        "pi-tv-pvr-bu-ss": "Saṅghādisesā", "pp": "Puggalapaññatti",
        "prajnaptisastra": "Prajnaptiśāstra", "prakaranapada": "Prakaraṇapada",
        "ps": "Paṭisambhidāmagga", "patthana": "Paṭṭhāna", "pv": "Petavatthu",
        "sa": "Saṃyuktāgama (1st)", "sa-2": "Saṃyuktāgama (2nd)",
        "sa-3": "Saṃyuktāgama (3rd)", "sa1-100": "Saṃyuktāgama 1–100",
        "sa1001-1100": "Saṃyuktāgama 1001–1100", "sa101-200": "Saṃyuktāgama 101–200",
        "sa1101-1200": "Saṃyuktāgama 1101–1200", "sa1201-1300": "Saṃyuktāgama 1201–1300",
        "sa1301-1362": "Saṃyuktāgama 1301–1362", "sa201-300": "Saṃyuktāgama 201–300",
        "sa301-400": "Saṃyuktāgama 301–400", "sa401-500": "Saṃyuktāgama 401–500",
        "sa501-600": "Saṃyuktāgama 501–600", "sa601-700": "Saṃyuktāgama 601–700",
        "sa701-800": "Saṃyuktāgama 701–800", "sa801-900": "Saṃyuktāgama 801–900",
        "sa901-1000": "Saṃyuktāgama 901–1000", "sammitiya-sastra": "Saṁmitīya Śāstra",
        "sangitiparyaya": "Saṅgītiparyāya", "sariputrabhidharma": "Śāripūtrābhidharma",
        "sariputrapariprccha": "Śāriputraparipṛcchā", "sbv": "Saṅgha­bheda­vastu",
        "sf": "Other Fragments", "sht": "SHT fragments",
        "skt-bu-pm-qizil": "Bhikkhu Pātimokkha (Qizil)",
        "skt-bu-pm-qizil-np": "Nissaggiyā Pācittiyā", "skt-bu-pm-qizil-pc": "Pācittiyā",
        "skt-bu-pm-qizil-pj": "Pārājika", "skt-bu-pm-qizil-sk": "Sekhiyā",
        "skt-bu-pm-qizil-ss": "Saṅghādisesā", "skt-dharmaskandha": "Dharmaskandha",
        "skt-jnanaprasthana": "Jnānaprasthāna", "skt-lo-asc": "Abhisamācārika",
        "skt-lo-bi-pn": "Bhikkhunī Pakiṇṇaka", "skt-lo-bi-vb": "Bhikkhunī Vibhaṅga",
        "skt-lo-bi-vb-as": "Sekhiyā", "skt-lo-bi-vb-gd": "Garudhamma",
        "skt-lo-bi-vb-nidana": "Nidāna", "skt-lo-bi-vb-np": "Nissaggiyā Pācittiyā",
        "skt-lo-bi-vb-pc": "Pācittiyā", "skt-lo-bi-vb-pd": "Pāṭidesanīyā",
        "skt-lo-bi-vb-pj": "Pārājika", "skt-lo-bi-vb-sk": "Sekhiyā",
        "skt-lo-bi-vb-ss": "Saṅghādisesā", "skt-lo-bu-pm": "Bhikkhu Pātimokkha",
        "skt-lo-bu-pm-as": "Sekhiyā", "skt-lo-bu-pm-ay": "Aniyatā",
        "skt-lo-bu-pm-np": "Nissaggiyā Pācittiyā", "skt-lo-bu-pm-pc": "Pācittiyā",
        "skt-lo-bu-pm-pd": "Pāṭidesanīyā", "skt-lo-bu-pm-pj": "Pārājika",
        "skt-lo-bu-pm-sk": "Sekhiyā", "skt-lo-bu-pm-ss": "Saṅghādisesā",
        "skt-lo-bu-pn": "Bhikkhu Pakiṇṇaka", "skt-lo-vi-misc": "Miscellaneous",
        "skt-mg-bu-pm": "Bhikkhu Pātimokkha", "skt-mg-bu-pm-as": "Sekhiyā",
        "skt-mg-bu-pm-ay": "Aniyatā", "skt-mg-bu-pm-np": "Nissaggiyā Pācittiyā",
        "skt-mg-bu-pm-pc": "Pācittiyā", "skt-mg-bu-pm-pd": "Pāṭidesanīyā",
        "skt-mg-bu-pm-pj": "Pārājika", "skt-mg-bu-pm-sk": "Sekhiyā",
        "skt-mg-bu-pm-ss": "Saṅghādisesā", "skt-mu-bu-kammavaca": "Bhikkhu Kammavācā",
        "skt-mu-bu-pm-gbm2": "Bhikkhu Pātimokkha (Gilgit 2)",
        "skt-mu-bu-pm-gbm2-as": "Sekhiyā", "skt-mu-bu-pm-gbm2-pc": "Pācittiyā",
        "skt-mu-bu-pm-gbm2-pj": "Pārājika", "skt-mu-bu-pm-gbm2-sk": "Sekhiyā",
        "skt-mu-bu-pm-gbm2-ss": "Saṅghādisesā",
        "skt-mu-bu-pm-gbm3": "Bhikkhu Pātimokkha (Gilgit 3)",
        "skt-mu-bu-pm-gbm3-as": "Sekhiyā", "skt-mu-bu-pm-gbm3-ay": "Aniyatā",
        "skt-mu-bu-pm-gbm3-np": "Nissaggiyā Pācittiyā",
        "skt-mu-bu-pm-gbm3-pc": "Pācittiyā", "skt-mu-bu-pm-gbm3-pd": "Pāṭidesanīyā",
        "skt-mu-bu-pm-gbm3-pj": "Pārājika", "skt-mu-bu-pm-gbm3-sk": "Sekhiyā",
        "skt-mu-bu-pm-gbm3-ss": "Saṅghādisesā", "skt-mu-kd": "Khandhaka",
        "skt-mu-mpt-bu-pm": "Mahāvyutpatti", "skt-mu-mpt-bu-pm-as": "Sekhiyā",
        "skt-mu-mpt-bu-pm-ay": "Aniyatā", "skt-mu-mpt-bu-pm-np": "Nissaggiyā Pācittiyā",
        "skt-mu-mpt-bu-pm-pc": "Pācittiyā", "skt-mu-mpt-bu-pm-pd": "Pāṭidesanīyā",
        "skt-mu-mpt-bu-pm-pj": "Pārājika", "skt-mu-mpt-bu-pm-sk": "Sekhiyā",
        "skt-mu-mpt-bu-pm-ss": "Saṅghādisesā",
        "skt-sarv-bi-kammavaca": "Bhikkhunī Kammavācā",
        "skt-sarv-bi-pm": "Bhikkhunī Pātimokka", "skt-sarv-bi-pm-np": "Nissaggiyā Pācittiyā",
        "skt-sarv-bi-pm-pc": "Pācittiyā", "skt-sarv-bi-pm-pj": "Pārājika",
        "skt-sarv-bi-pm-ss": "Saṅghādisesā", "skt-sarv-bi-vb": "Bhikkhunī Vibhaṅga",
        "skt-sarv-bi-vb-pc": "Pācittiyā", "skt-sarv-bi-vb-ss": "Saṅghādisesā",
        "skt-sarv-bu-kammavaca": "Bhikkhu Kammavācā",
        "skt-sarv-bu-pm-finot": "Bhikkhu Pātimokkha (Finot)",
        "skt-sarv-bu-pm-finot-as": "Sekhiyā", "skt-sarv-bu-pm-finot-ay": "Aniyatā",
        "skt-sarv-bu-pm-finot-np": "Nissaggiyā Pācittiyā",
        "skt-sarv-bu-pm-finot-pc": "Pācittiyā", "skt-sarv-bu-pm-finot-pd": "Pāṭidesanīyā",
        "skt-sarv-bu-pm-finot-pj": "Pārājika", "skt-sarv-bu-pm-finot-sk": "Sekhiyā",
        "skt-sarv-bu-pm-finot-ss": "Saṅghādisesā",
        "skt-sarv-bu-pm-tf11": "Bhikkhu Pātimokkha (Turfan 11)",
        "skt-sarv-bu-pm-tf11-as": "Sekhiyā", "skt-sarv-bu-pm-tf11-ay": "Aniyatā",
        "skt-sarv-bu-pm-tf11-np": "Nissaggiyā Pācittiyā",
        "skt-sarv-bu-pm-tf11-pc": "Pācittiyā", "skt-sarv-bu-pm-tf11-pd": "Pāṭidesanīyā",
        "skt-sarv-bu-pm-tf11-pj": "Pārājika", "skt-sarv-bu-pm-tf11-sk": "Sekhiyā",
        "skt-sarv-bu-pm-tf11-ss": "Saṅghādisesā", "sn": "Saṃyutta Nikāya",
        "sn1": "Devatā Saṃyutta", "sn10": "Yakkha Saṃyutta", "sn11": "Sakka Saṃyutta",
        "sn12": "Nidāna Saṃyutta", "sn13": "Abhisamaya Saṃyutta",
        "sn14": "Dhātu Saṃyutta", "sn15": "Anamatagga Saṃyutta",
        "sn16": "Kassapa Saṃyutta", "sn17": "Lābhasakkāra Saṃyutta",
        "sn18": "Rāhula Saṃyutta", "sn19": "Lakkhaṇa Saṃyutta",
        "sn2": "Devaputta Saṃyutta", "sn20": "Opamma Saṃyutta",
        "sn21": "Bhikkhu Saṃyutta", "sn22": "Khandha Saṃyutta", "sn23": "Rādha Saṃyutta",
        "sn24": "Diṭṭhi Saṃyutta", "sn25": "Okkantika Saṃyutta",
        "sn26": "Uppāda Saṃyutta", "sn27": "Kilesa Saṃyutta",
        "sn28": "Sāriputta Saṃyutta", "sn29": "Nāga Saṃyutta", "sn3": "Kosala Saṃyutta",
        "sn30": "Supaṇṇa Saṃyutta", "sn31": "Gandhabbakāya Saṃyutta",
        "sn32": "Valāhaka Saṃyutta", "sn33": "Vacchagotta Saṃyutta",
        "sn34": "Samādhi Saṃyutta", "sn35": "Saḷāyatana Saṃyutta",
        "sn36": "Vedanā Saṃyutta", "sn37": "Mātugāma Saṃyutta",
        "sn38": "Jambukhādaka Saṃyutta", "sn39": "Sāmaṇḍaka Saṃyutta",
        "sn4": "Māra Saṃyutta", "sn40": "Moggallāna Saṃyutta", "sn41": "Citta Saṃyutta",
        "sn42": "Gāmani Saṃyutta", "sn43": "Asaṅkhata Saṃyutta",
        "sn44": "Avyākata Saṃyutta", "sn45": "Magga Saṃyutta",
        "sn46": "Bojjhaṅga Saṃyutta", "sn47": "Satipaṭṭhāna Saṃyutta",
        "sn48": "Indriya Saṃyutta", "sn49": "Sammappadhāna Saṃyutta",
        "sn5": "Bhikkhuṇī Saṃyutta", "sn50": "Bala Saṃyutta",
        "sn51": "Iddhipāda Saṃyutta", "sn52": "Anuruddha Saṃyutta",
        "sn53": "Jhāna Saṃyutta", "sn54": "Ānāpāna Saṃyutta",
        "sn55": "Sotāpatti Saṃyutta", "sn56": "Sacca Saṃyutta", "sn6": "Brahmā Saṃyutta",
        "sn7": "Brāhmaṇa Saṃyutta", "sn8": "Vangīsa Thera Saṃyutta",
        "sn9": "Vana Saṃyutta", "snp": "Sutta Nipāta",
        "t102-124": "Other Saṃyukta Sūtras", "t126-149": "Other Ekottarika Sūtras",
        "t150B": "", "t2-25": "Other Dīrgha Sūtras", "t27-98": "Other Madhyama Sūtras",
        "tc": "Critical editions", "tha-ap": "Therāpadāna", "thag": "Theragāthā",
        "thi-ap": "Therīapadāna", "thig": "Therīgāthā", "ud": "Udāna",
        "uf": "Uighur fragments", "up": "Upāyikā", "uv": "Udānavarga", "vb": "Vibhaṅga",
        "vijnanakaya": "Vijnānakāya", "vv": "Vimānavatthu",
        "ya": "Yamaka"},
        rex = /(\b[a-z][a-z0-9]+(?:-[1-3])?) ?(\d+(?:\.\d+)?(?:-\d+)?[abc]?)\b/gi;

    return function(text) {
        text.replace(rex, function(match, div_uid, num) {
            console.log(match, div_uid, num);
            if (div_uid in _data) {
                var url = 'http://suttacentral.net/' + match.replace(' ', '').toLowerCase();
                return '[' + match.toUpperCase() + '](' + url + ')'
            } else {
                return match
            }
        });
        return text
    }
})();
    

Discourse.Dialect.addPreProcessor(scUrlCreator)

