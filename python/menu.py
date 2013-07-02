# Return the context of collections and divisions for menu display

other_divisions = [{"name": "Prākrit", "link": "/pf"},
			       {"name": "Gāndhārī", "link": "/gf"},
			       {"name": "Khotanese", "link": "/kf"},
			       {"name": "Uighur", "link": "/uf"}]

sanskrit_divisions = [{"name": "Avadānaśataka", "link": "/avs"},
				      {"name": "Divyāvadāna", "link": "/div"},
				      {"name": "Lalitavistara", "link": "/lal"},
				      {"name": "Mahāvastu", "link": "/mvu"},
				      {"name": "Saṅghabhedavastu", "link": "/sbh"},
				      {"name": "SHT", "link": "/sht"},
				      {"name": "Fragments", "link": "/sf"}]

tibetan_divisions = [{"name": "Derge / Peking editions", "link": "/dq"},
				     {"name": "Upāyikā", "link": "/up"},
				     {"name": "Critical editions", "link": "/tc"}]

chinese_divisions = [{"name": "Dīrghāgama", "link": "/da"},
				     {"name": "Madhyamāgama", "link": "/ma"},
				     {"name": "Saṃyuktāgama", "link": "/sa"},
				     {"name": "Saṃyuktāgama (2nd)", "link": "/sa-2"},
				     {"name": "Saṃyuktāgama (3nd)", "link": "/sa-3"},
				     {"name": "Ekottarikāgama", "link": "/ea"},
				     {"name": "Ekottarikāgama (2nd)", "link": "/ea-2"},
				     {"name": "Other Āgama sūtra", "link": "/oa"},
				     {"name": "Other Taishō texts", "link": "/ot"}]

pali_divisions = [{"name": "Dīgha Nikāya", "link": "/dn"},
			      {"name": "Majjhima Nikāya", "link": "/mn"},
			      {"name": "Saṃyutta Nikāya", "link": "/sn"},
			      {"name": "Aṅguttara Nikāya", "link": "/an"},
			      {"name": "Khuddaka Nikāya", "link": "/kn"}]

collections = []

collections.append({"name": "Other", "divisions": other_divisions})
collections.append({"name": "Sanskrit", "divisions": sanskrit_divisions})
collections.append({"name": "Tibetan", "divisions": tibetan_divisions})
collections.append({"name": "Chinese", "divisions": chinese_divisions})
collections.append({"name": "Pāli", "divisions": pali_divisions})

menu_data = collections
