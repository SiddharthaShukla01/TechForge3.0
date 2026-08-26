"""
Sample Data Loader for Uttarakhand Disaster Alert & Resource Management System.
Populates complete bilingual (हिंदी / English) mock data across all 13 districts of Uttarakhand.
"""
from database import get_connection, create_tables, clear_all_data

def insert_sample_data(reset_existing=True):
    create_tables()
    
    if reset_existing:
        print("Clearing and recreating tables for clean bilingual schema...")
        clear_all_data()

    with get_connection() as conn:
        c = conn.cursor()
        
        # -------------------------------------------------------------
        # 1. SHELTERS ACROSS ALL 13 DISTRICTS (Bilingual)
        # -------------------------------------------------------------
        shelters = [
            # Dehradun
            ("Parade Ground Relief Camp", "परेड ग्राउंड आपातकालीन राहत शिविर", "Dehradun", "देहरादून", 350, 140, "0135-2651000", 30.3244, 78.0435),
            ("Clement Town Community Center", "क्लेमेंट टाउन सामुदायिक राहत केंद्र", "Dehradun", "देहरादून", 200, 75, "0135-2642100", 30.2700, 78.0100),
            ("Rishikesh ISBT Relief Shelter", "ऋषिकेश बस स्टैंड शरण स्थल", "Dehradun", "देहरादून", 280, 110, "0135-2435200", 30.1000, 78.2900),
            
            # Haridwar
            ("Pantdeep Relief Grounds", "पंतद्वीप राहत शिविर मैदान", "Haridwar", "हरिद्वार", 400, 260, "01334-226789", 29.9560, 78.1720),
            ("BHEL Sector-4 Community Hall", "बीएचईएल सेक्टर-4 सामुदायिक भवन", "Haridwar", "हरिद्वार", 250, 90, "01334-281000", 29.9200, 78.1100),
            
            # Tehri Garhwal
            ("GIC New Tehri Emergency Camp", "राजकीय इंटर कॉलेज नई टिहरी राहत शिविर", "Tehri Garhwal", "टिहरी गढ़वाल", 220, 110, "01376-233444", 30.3800, 78.4800),
            ("Muni Ki Reti Relief Base", "मुनि की रेती आपातकालीन शरण स्थल", "Tehri Garhwal", "टिहरी गढ़वाल", 180, 45, "01376-232111", 30.1200, 78.3200),
            
            # Chamoli
            ("Joshimath Tapovan Relief Camp", "जोशीमठ तपोवन राहत केंद्र", "Chamoli", "चमोली", 300, 210, "01372-222333", 30.5560, 79.5650),
            ("Gopeshwar GIC Relief Center", "गोपेश्वर जीआईसी शरण स्थल", "Chamoli", "चमोली", 150, 60, "01372-252444", 30.4100, 79.3300),
            
            # Uttarkashi
            ("Matli ITBP Relief Base", "मातली आईटीबीपी राहत बेस कैंप", "Uttarkashi", "उत्तरकाशी", 320, 180, "01374-222888", 30.7400, 78.4500),
            ("Barkot Tehsil Emergency Shelter", "बड़कोट तहसील आपातकालीन शरण केंद्र", "Uttarkashi", "उत्तरकाशी", 140, 50, "01374-252111", 30.8100, 78.2000),
            
            # Rudraprayag
            ("Augustmuni Sports Stadium Camp", "अगस्त्यमुनि खेल स्टेडियम राहत कैंप", "Rudraprayag", "रुद्रप्रयाग", 250, 190, "01364-233555", 30.3900, 79.0200),
            ("Guptkashi Helipad Relief Camp", "गुप्तकाशी हेलीपैड शरण स्थल", "Rudraprayag", "रुद्रप्रयाग", 180, 120, "01364-267222", 30.5200, 79.0800),
            
            # Pauri Garhwal
            ("Kotdwar Indoor Stadium Relief Shelter", "कोटद्वार इनडोर स्टेडियम राहत शिविर", "Pauri Garhwal", "पौड़ी गढ़वाल", 300, 95, "01382-224500", 29.7500, 78.5300),
            ("Pauri Town Hall Shelter", "पौड़ी टाउन हॉल शरण स्थल", "Pauri Garhwal", "पौड़ी गढ़वाल", 160, 40, "01368-222120", 30.1500, 78.7800),
            
            # Pithoragarh
            ("Pithoragarh Town Hall Camp", "पिथौरागढ़ टाउन हॉल राहत केंद्र", "Pithoragarh", "पिथौरागढ़", 220, 130, "01342-225600", 29.5828, 80.2182),
            ("Dharchula Sub-Division Relief Base", "धारचूला उप-प्रभाग राहत बेस", "Pithoragarh", "पिथौरागढ़", 200, 150, "01342-230100", 29.8500, 80.5400),
            
            # Bageshwar
            ("Degree College Ground Relief Camp", "डिग्री कॉलेज मैदान राहत शिविर", "Bageshwar", "बागेश्वर", 170, 65, "01363-222150", 29.8406, 79.7694),
            ("Kapkot Block Emergency Shelter", "कपकोट ब्लॉक आपातकालीन शरण स्थल", "Bageshwar", "बागेश्वर", 130, 40, "01363-255200", 29.9400, 79.9000),
            
            # Almora
            ("Almora Sports Stadium Relief Camp", "अल्मोड़ा स्पोर्ट्स स्टेडियम राहत कैंप", "Almora", "अल्मोड़ा", 240, 80, "01396-230500", 29.5971, 79.6591),
            ("Ranikhet Cantonment Hall", "रानीखेत छावनी राहत भवन", "Almora", "अल्मोड़ा", 180, 50, "01396-220100", 29.6400, 79.4200),
            
            # Champawat
            ("Tanakpur Mandi Parishad Shelter", "टनकपुर मंडी परिषद राहत केंद्र", "Champawat", "चंपावत", 260, 110, "01343-223400", 29.0700, 80.1100),
            ("GIC Champawat Ground", "राजकीय इंटर कॉलेज चंपावत मैदान", "Champawat", "चंपावत", 140, 35, "01343-230100", 29.3347, 80.0911),
            
            # Nainital
            ("Haldwani International Stadium Camp", "हल्द्वानी अंतरराष्ट्रीय स्टेडियम राहत शिविर", "Nainital", "नैनीताल", 500, 160, "01346-282100", 29.2200, 79.5100),
            ("Nainital Club Emergency Camp", "नैनीताल क्लब आपातकालीन शरण स्थल", "Nainital", "नैनीताल", 150, 45, "01346-235600", 29.3919, 79.4542),
            
            # Udham Singh Nagar
            ("Rudrapur Community Relief Center", "रुद्रपुर सामुदायिक राहत केंद्र", "Udham Singh Nagar", "उधम सिंह नगर", 350, 120, "01344-242300", 28.9800, 79.4000),
            ("Kashipur Krishi Mandi Camp", "काशीपुर कृषि मंडी शरण स्थल", "Udham Singh Nagar", "उधम सिंह नगर", 280, 80, "01344-275100", 29.2100, 78.9600)
        ]
        c.executemany(
            """
            INSERT INTO shelters (name, name_hi, district, district_hi, capacity, occupied, contact, latitude, longitude)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            shelters
        )

        # -------------------------------------------------------------
        # 2. HOSPITALS ACROSS ALL 13 DISTRICTS (Bilingual)
        # -------------------------------------------------------------
        hospitals = [
            ("AIIMS Rishikesh (Super Specialty)", "एम्स ऋषिकेश (सुपर स्पेशलिटी अस्पताल)", "Dehradun", "देहरादून", 600, 145, "0135-2471000", 30.0758, 78.2882),
            ("Doon Govt Medical College Hospital", "दून राजकीय मेडिकल कॉलेज अस्पताल", "Dehradun", "देहरादून", 450, 90, "0135-2726020", 30.3200, 78.0350),
            ("Haridwar Civil Hospital", "हरिद्वार मुख्य नागरिक अस्पताल", "Haridwar", "हरिद्वार", 250, 65, "01334-227520", 29.9540, 78.1510),
            ("Ramakrishna Mission Hospital Kankhal", "रामकृष्ण मिशन अस्पताल कनखल", "Haridwar", "हरिद्वार", 180, 42, "01334-246141", 29.9300, 78.1400),
            ("Tehri Govt District Hospital Baurari", "टिहरी जिला अस्पताल बौराड़ी", "Tehri Garhwal", "टिहरी गढ़वाल", 160, 55, "01376-233100", 30.3900, 78.4700),
            ("Chamoli District Hospital Gopeshwar", "चमोली जिला अस्पताल गोपेश्वर", "Chamoli", "चमोली", 140, 35, "01372-252100", 30.4100, 79.3200),
            ("Sub-District Hospital Joshimath", "उप-जिला अस्पताल जोशीमठ", "Chamoli", "चमोली", 80, 18, "01372-222108", 30.5500, 79.5600),
            ("Uttarkashi Base Hospital", "उत्तरकाशी बेस अस्पताल", "Uttarkashi", "उत्तरकाशी", 150, 48, "01374-222100", 30.7300, 78.4400),
            ("District Hospital Rudraprayag", "रुद्रप्रयाग जिला अस्पताल", "Rudraprayag", "रुद्रप्रयाग", 120, 28, "01364-233200", 30.2800, 78.9800),
            ("Base Hospital Kotdwar", "बेस अस्पताल कोटद्वार", "Pauri Garhwal", "पौड़ी गढ़वाल", 220, 70, "01382-222200", 29.7500, 78.5300),
            ("District Hospital Pauri", "पौड़ी जिला अस्पताल", "Pauri Garhwal", "पौड़ी गढ़वाल", 130, 45, "01368-222210", 30.1500, 78.7800),
            ("Pithoragarh Base Hospital", "पिथौरागढ़ बेस अस्पताल", "Pithoragarh", "पिथौरागढ़", 160, 52, "01342-225100", 29.5800, 80.2100),
            ("CHC Dharchula Emergency Unit", "सामुदायिक स्वास्थ्य केंद्र धारचूला", "Pithoragarh", "पिथौरागढ़", 60, 12, "01342-230020", 29.8500, 80.5400),
            ("District Hospital Bageshwar", "बागेश्वर जिला अस्पताल", "Bageshwar", "बागेश्वर", 110, 38, "01363-222020", 29.8406, 79.7694),
            ("SSJ Govt Medical College Hospital Almora", "एसएसजे मेडिकल कॉलेज अस्पताल अल्मोड़ा", "Almora", "अल्मोड़ा", 280, 85, "01396-230050", 29.5971, 79.6591),
            ("District Hospital Champawat", "चंपावत जिला अस्पताल", "Champawat", "चंपावत", 100, 32, "01343-225010", 29.3347, 80.0911),
            ("Dr. Sushila Tiwari Govt Hospital Haldwani", "डॉ. सुशीला तिवारी राजकीय अस्पताल हल्द्वानी", "Nainital", "नैनीताल", 550, 130, "01346-234415", 29.2150, 79.5200),
            ("BD Pandey District Hospital Nainital", "बीडी पांडे जिला अस्पताल नैनीताल", "Nainital", "नैनीताल", 120, 40, "01346-235012", 29.3919, 79.4542),
            ("Pt. Ram Sumer Shukla Govt Hospital Rudrapur", "पं. राम सुमेर शुक्ल राजकीय अस्पताल रुद्रपुर", "Udham Singh Nagar", "उधम सिंह नगर", 300, 95, "01344-243200", 28.9800, 79.4000)
        ]
        c.executemany(
            """
            INSERT INTO hospitals (name, name_hi, district, district_hi, beds_total, beds_available, contact, latitude, longitude)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            hospitals
        )

        # -------------------------------------------------------------
        # 3. RELIEF STOCKPILES (Bilingual)
        # -------------------------------------------------------------
        resources = [
            ("Food", "खाद्य सामग्री", "Dry Ration & Ready-to-Eat Packs", "सूखा राशन एवं तैयार भोजन पैकेट (5 किग्रा)", "Haridwar", "हरिद्वार", 1200, "Packets", "पैकेट", 1),
            ("Medicine", "दवाइयां व चिकित्सा", "Emergency First Aid & Trauma Kits", "आपातकालीन प्राथमिक उपचार एवं ट्रॉमा किट", "Dehradun", "देहरादून", 650, "Kits", "किट", 1),
            ("Equipment", "बचाव उपकरण", "Motorized Inflatable Rescue Boats", "मोटरयुक्त इन्फ्लेटेबल बचाव नौकाएं", "Chamoli", "चमोली", 14, "Boats", "नौकाएं", 1),
            ("Food", "खाद्य सामग्री", "Packaged Drinking Water (20L Cans)", "पीने का स्वच्छ पानी (20 लीटर केन)", "Tehri Garhwal", "टिहरी गढ़वाल", 1500, "Cans", "केन", 1),
            ("Equipment", "बचाव उपकरण", "Foldable Mountain Rescue Stretchers", "पर्वतीय फोल्डेबल रेस्क्यू स्ट्रेचर", "Uttarkashi", "उत्तरकाशी", 80, "Units", "स्ट्रेचर", 1),
            ("Medicine", "दवाइयां व चिकित्सा", "Portable Oxygen Cylinders", "पोर्टेबल मेडिकल ऑक्सीजन सिलेंडर", "Haridwar", "हरिद्वार", 50, "Cylinders", "सिलेंडर", 1),
            ("Equipment", "बचाव उपकरण", "High-Power Diesel Generators", "हाई-पावर बैकअप डीजल जनरेटर", "Rudraprayag", "रुद्रप्रयाग", 20, "Units", "यूनिट", 1),
            ("Equipment", "बचाव उपकरण", "Hydraulic Cutters & Heavy Torches", "हाइड्रोलिक कटर व शक्तिशाली सर्चलाइट", "Chamoli", "चमोली", 40, "Sets", "सेट", 1),
            ("Food", "खाद्य सामग्री", "Baby Food & Essential Milk Powder", "शिशु आहार एवं आवश्यक सूखा दूध पाउडर", "Pithoragarh", "पिथौरागढ़", 350, "Kits", "किट", 1),
            ("Medicine", "दवाइयां व चिकित्सा", "Anti-Venom & Water Purification Tablets", "एंटी-वेनम व क्लोरीन पानी शुद्धिकरण गोलियां", "Pauri Garhwal", "पौड़ी गढ़वाल", 2500, "Strips", "स्ट्रिप", 1),
            ("Equipment", "बचाव उपकरण", "Extreme Cold Weather Blankets & Tents", "शीतकालीन वाटरप्रूफ गर्म कंबल व टेंट", "Uttarkashi", "उत्तरकाशी", 900, "Sets", "सेट", 1),
            ("Equipment", "बचाव उपकरण", "Satellite Phones & VHF Radios", "सैटेलाइट फोन व वायरलेस रेडियो सेट", "Rudraprayag", "रुद्रप्रयाग", 25, "Devices", "डिवाइस", 1),
            ("Food", "खाद्य सामग्री", "Community Kitchen Grain Bags (Wheat/Rice 50kg)", "सामुदायिक रसोई अनाज बोरी (गेहूं/चावल 50 किग्रा)", "Nainital", "नैनीताल", 400, "Bags", "बोरी", 1),
            ("Medicine", "दवाइयां व चिकित्सा", "Trauma & Burn Care Emergency Packs", "गंभीर घाव व जलने की आपातकालीन दवा किट", "Almora", "अल्मोड़ा", 200, "Packs", "पैक", 1),
            ("Equipment", "बचाव उपकरण", "Snow Clearing Heavy Shovels & Chains", "बर्फ हटाने के भारी फावड़े व चेन सेट", "Bageshwar", "बागेश्वर", 120, "Units", "इकाइयां", 1),
            ("Food", "खाद्य सामग्री", "High-Energy Biscuits & ORS Packets", "ऊर्जा बिस्कुट एवं ओआरएस घोल पैकेट", "Champawat", "चंपावत", 3000, "Packets", "पैकेट", 1),
            ("Medicine", "दवाइयां व चिकित्सा", "Emergency Intravenous (IV) Fluid Kits", "आपातकालीन ड्रिप एवं ग्लूकोज आईवी किट", "Udham Singh Nagar", "उधम सिंह नगर", 800, "Boxes", "बॉक्स", 1)
        ]
        c.executemany(
            """
            INSERT INTO resources (type, type_hi, name, name_hi, district, district_hi, quantity, unit, unit_hi, available)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            resources
        )

        # -------------------------------------------------------------
        # 4. DISASTERS & GROUND INCIDENTS (Bilingual)
        # -------------------------------------------------------------
        disasters = [
            (
                "Flood",
                "बाढ़ (Flood)",
                "Haridwar",
                "हरिद्वार",
                "Critical",
                "अति-गंभीर (Critical)",
                "Ganga water level crossed warning mark (294.0m); inundation in Kangra Mandir and lower ghat slums.",
                "गंगा नदी खतरे के निशान (294.0 मी) से ऊपर बह रही है। कांगड़ा मंदिर और निचले स्नान घाटों के पास पानी भर गया है। SDRF की नावें तैनात हैं।",
                "9897112233",
                "",
                29.9457,
                78.1642,
                "2026-08-26 06:30",
                "Active",
                "सक्रिय (Active)"
            ),
            (
                "Landslide",
                "भूस्खलन (Landslide)",
                "Chamoli",
                "चमोली",
                "High",
                "गंभीर (High)",
                "Major rockfall and mountain debris blocked Badrinath National Highway (NH-58) near Helang.",
                "हेलंग के पास बद्रीनाथ राष्ट्रीय राजमार्ग (NH-58) पर भारी चट्टान व मलबा गिरने से सड़क पूरी तरह बंद। दोनों तरफ सैकड़ों वाहन रुके हैं।",
                "01372-252111",
                "",
                30.5500,
                79.5667,
                "2026-08-26 07:15",
                "Active",
                "सक्रिय (Active)"
            ),
            (
                "Cloudburst",
                "बादल फटना (Cloudburst)",
                "Rudraprayag",
                "रुद्रप्रयाग",
                "Critical",
                "अति-गंभीर (Critical)",
                "Severe cloudburst triggered flash flood in Madhmaheshwar valley near Guptkashi. 35 pilgrims stranded.",
                "गुप्तकाशी के पास मदमहेश्वर घाटी में बादल फटने से अचानक सैलाब आया। 35 श्रद्धालु फंसे हुए हैं, हेली-रेस्क्यू व एनडीआरएफ टीमें मौके पर हैं।",
                "9456596190",
                "",
                30.2844,
                78.9811,
                "2026-08-26 05:45",
                "Active",
                "सक्रिय (Active)"
            ),
            (
                "Earthquake",
                "भूकंप (Earthquake)",
                "Uttarkashi",
                "उत्तरकाशी",
                "Medium",
                "मध्यम (Medium)",
                "Magnitude 4.3 seismic tremors near Bhatwari fault line. Minor cracks in old wooden homes.",
                "भटवाड़ी फॉल्ट लाइन के पास 4.3 तीव्रता का भूकंप का झटका महसूस किया गया। पुराने मकानों में दरारें दर्ज की गई हैं, जान-माल सुरक्षित है।",
                "01374-222888",
                "",
                30.7268,
                78.4354,
                "2026-08-26 03:20",
                "Active",
                "सक्रिय (Active)"
            ),
            (
                "Landslide",
                "भूस्खलन (Landslide)",
                "Pithoragarh",
                "पिथौरागढ़",
                "High",
                "गंभीर (High)",
                "Tanakpur-Tawaghat mountain road damaged by torrential rain near Dharchula.",
                "धारचूला के पास टनकपुर-तवाघाट पहाड़ी मार्ग भारी बारिश के बाद क्षतिग्रस्त हुआ। सीमा सड़क संगठन (BRO) द्वारा मलबा हटाया जा रहा है।",
                "9756123456",
                "",
                29.5828,
                80.2182,
                "2026-08-25 18:00",
                "Active",
                "सक्रिय (Active)"
            ),
            (
                "Road Collapse",
                "सड़क धंसना (Road Collapse)",
                "Tehri Garhwal",
                "टिहरी गढ़वाल",
                "Medium",
                "मध्यम (Medium)",
                "Chamba-Dhanaulti road partially caved in due to rain; heavy vehicle traffic diverted.",
                "चंबा-धनोल्टी मुख्य मार्ग बारिश के कारण आंशिक रूप से धंस गया है। भारी वाहनों को चंबा बाईपास की ओर मोड़ा गया है।",
                "01376-233444",
                "",
                30.3800,
                78.4800,
                "2026-08-25 14:00",
                "Under Control",
                "नियंत्रण में (Under Control)"
            ),
            (
                "Flash Flood",
                "फ्लैश फ्लड (Flash Flood)",
                "Nainital",
                "नैनीताल",
                "Medium",
                "मध्यम (Medium)",
                "Waterlogging in lower Haldwani areas and Haldwani-Kathgodam road intersection.",
                "हल्द्वानी के निचले इलाकों और काठगोदाम तिराहे पर भारी जलभराव हुआ। पंपों की मदद से पानी निकाला जा रहा है।",
                "01346-282100",
                "",
                29.3919,
                79.4542,
                "2026-08-25 09:30",
                "Under Control",
                "नियंत्रण में (Under Control)"
            ),
            (
                "Forest Fire",
                "जंगल की आग (Forest Fire)",
                "Almora",
                "अल्मोड़ा",
                "Low",
                "सामान्य (Low)",
                "Controlled slope fire near Ranikhet forest boundary; extinguished by forest range teams.",
                "रानीखेत वन क्षेत्र की ढलान पर लगी आग पर वन विभाग की टीमों ने समय रहते पूरी तरह काबू पा लिया है।",
                "N/A",
                "",
                29.5971,
                79.6591,
                "2026-08-24 11:00",
                "Resolved",
                "समाधान हो गया (Resolved)"
            ),
            (
                "Building Collapse",
                "मकान ढहना (Building Collapse)",
                "Pauri Garhwal",
                "पौड़ी गढ़वाल",
                "Low",
                "सामान्य (Low)",
                "Abandoned structure collapsed due to seepage near Srinagar; site cleared by local municipality.",
                "श्रीनगर के पास एक पुराना खाली मकान सीलन के कारण गिर गया था। नगरपालिका द्वारा मलबा हटाकर रास्ता साफ कर दिया गया है।",
                "N/A",
                "",
                30.1500,
                78.7800,
                "2026-08-23 15:30",
                "Resolved",
                "समाधान हो गया (Resolved)"
            )
        ]
        c.executemany(
            """
            INSERT INTO disasters (type, type_hi, location, location_hi, severity, severity_hi, description, description_hi, reporter_contact, evidence_media, latitude, longitude, date_reported, status, status_hi)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            disasters
        )


        # -------------------------------------------------------------
        # 5. ALERTS & PUBLIC BROADCASTS (Bilingual)
        # -------------------------------------------------------------
        alerts = [
            (
                3,
                "CRITICAL: Cloudburst and flash flood in Rudraprayag (Guptkashi area)! SDRF and NDRF rescue teams dispatched. Move to high ground immediately.",
                "🚨 अति-गंभीर: रुद्रप्रयाग (गुप्तकाशी) में बादल फटने व फ्लैश फ्लड की सूचना! SDRF एवं NDRF दल रवाना। नदी किनारे से तुरंत सुरक्षित स्थानों पर जाएं।",
                "Critical",
                "2026-08-26 05:45",
                "All"
            ),
            (
                1,
                "CRITICAL: Ganga river at danger level in Haridwar. High alert issued for all bathing ghats and low-lying settlements.",
                "🚨 अति-गंभीर: हरिद्वार में गंगा नदी खतरे के निशान के करीब। सभी स्नान घाटों और निचले इलाकों में हाई अलर्ट जारी।",
                "Critical",
                "2026-08-26 06:30",
                "All"
            ),
            (
                2,
                "HIGH WARNING: Landslide on Badrinath NH-58 near Helang (Chamoli). Traffic halted. Travelers advised to stay at nearest transit camps.",
                "⚠️ उच्च चेतावनी: चमोली (हेलंग) के पास बद्रीनाथ राष्ट्रीय राजमार्ग NH-58 पर भारी भूस्खलन। मार्ग अवरुद्ध। यात्री नजदीकी विश्राम स्थल पर रुकें।",
                "High",
                "2026-08-26 07:15",
                "Chamoli"
            ),
            (
                5,
                "HIGH WARNING: Dharchula route in Pithoragarh disrupted due to mountain debris. Emergency clearance machines deployed.",
                "⚠️ उच्च चेतावनी: पिथौरागढ़ (धारचूला) मार्ग पर मलबा आने से आवागमन बाधित। जेसीबी एवं मार्ग खोलने वाले उपकरण तैनात।",
                "High",
                "2026-08-25 18:00",
                "Pithoragarh"
            ),
            (
                4,
                "MEDIUM: Magnitude 4.3 earthquake tremors felt in Uttarkashi. No major loss of life reported. Stay alert for minor aftershocks.",
                "ℹ️ सूचना: उत्तरकाशी में 4.3 तीव्रता का भूकंप का झटका। जान-माल के बड़े नुकसान की खबर नहीं है। सतर्क रहें।",
                "Medium",
                "2026-08-26 03:20",
                "Uttarkashi"
            ),
            (
                8,
                "SAFETY UPDATE: Ranikhet (Almora) forest fire has been completely controlled and extinguished. Area declared safe.",
                "🟢 सुरक्षा अपडेट: रानीखेत (अल्मोड़ा) के जंगल की आग पर वन विभाग द्वारा पूरी तरह काबू पा लिया गया है। क्षेत्र सुरक्षित है।",
                "Low",
                "2026-08-24 16:00",
                "Almora"
            )
        ]
        c.executemany(
            """
            INSERT INTO alerts (disaster_id, message, message_hi, severity, timestamp, target)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            alerts
        )

        # -------------------------------------------------------------
        # 6. SUGGESTIONS & COMMUNITY INNOVATIONS (Bilingual)
        # -------------------------------------------------------------
        suggestions = [
            (
                "Offline Bluetooth Mesh Alert App for Trekkers & Pilgrims",
                "चारधाम यात्रियों व ट्रेकर्स के लिए ऑफलाइन ब्लूटूथ मेश अलर्ट नेटवर्क",
                "Early Warning & Tech",
                "पूर्व चेतावनी व तकनीक (Technology)",
                "Develop an offline peer-to-peer mobile alert app that propagates emergency warnings between smartphones via Bluetooth even without cellular towers.",
                "बिना मोबाइल टावर वाले दुर्गम घाटी क्षेत्रों में एक फोन से दूसरे फोन में ब्लूटूथ द्वारा सीधे इमरजेंसी अलर्ट रिले करने वाली तकनीक विकसित की जाए।",
                "Rohan Joshi (Tech Volunteer, Dehradun)",
                "Chamoli",
                "चमोली",
                58,
                "Approved / In Progress",
                "स्वीकृत व प्रगति पर (Approved / In Progress)",
                "2026-08-24 10:30"
            ),
            (
                "Drone Emergency Medicine & First Aid Delivery in High Himalayas",
                "दुर्गम पहाड़ी गांवों में ड्रोन द्वारा जीवनरक्षक दवाओं की त्वरित आपूर्ति",
                "Rescue Operations",
                "राहत एवं बचाव कार्य (Rescue)",
                "Deploy medical delivery drones stationed at district bases to airlift anti-venom, ORS, and trauma supplies to isolated villages cut off by landslides.",
                "भूस्खलन से कटे हुए गांवों में एंटी-वेनम, दर्द निवारक दवाएं और फर्स्ट एड किट पहुंचाने के लिए तहसील स्तर पर मेडिकल ड्रोन दस्ते तैनात किए जाएं।",
                "Dr. Alok Nautiyal (Uttarkashi Relief NGO)",
                "Uttarkashi",
                "उत्तरकाशी",
                44,
                "Under Review",
                "समीक्षाधीन (Under Review)",
                "2026-08-25 12:15"
            ),
            (
                "Solar-Powered Phone Charging & Satellite WiFi at Relief Camps",
                "राहत शिविरों में सौर ऊर्जा संचालित मोबाइल चार्जिंग व सैटेलाइट वाईफाई पॉइंट",
                "Relief Shelters",
                "राहत शिविर सुविधाएं (Shelters)",
                "Install portable solar battery charging stations and VSAT connectivity at all community relief camps so stranded pilgrims can inform families.",
                "बाढ़ और आपदा के दौरान बिजली कटने पर शिविरों में सोलर पावर बैंक व सैटेलाइट कॉलिंग सुविधा दी जाए ताकि लोग अपने परिजनों से संपर्क कर सकें।",
                "Priya Rawat (Community Coordinator)",
                "Rudraprayag",
                "रुद्रप्रयाग",
                37,
                "Implemented",
                "लागू किया गया (Implemented)",
                "2026-08-23 16:40"
            ),
            (
                "Village Youth 'Aapda Mitra' Local First-Responder Corps",
                "प्रत्येक ग्राम पंचायत में प्रशिक्षित 'आपदा मित्र' युवा स्वयंसेवक दस्ता",
                "Community Support",
                "जन सहयोग व स्वयंसेवक (Volunteers)",
                "Equip and certify 10 local youth in each high-risk mountain village with rope rescue kits, high-frequency radios, and basic CPR training.",
                "हर ग्राम पंचायत के 10 युवाओं को SDRF द्वारा रोप रेस्क्यू, प्राथमिक चिकित्सा व वायरलेस संचालन का विशेष प्रशिक्षण दिया जाए।",
                "Harish Singh Negi (Pauri Garhwal)",
                "Pauri Garhwal",
                "पौड़ी गढ़वाल",
                49,
                "Approved / In Progress",
                "स्वीकृत व प्रगति पर (Approved / In Progress)",
                "2026-08-25 09:20"
            ),
            (
                "Live Heavy Machine & Route Clearance ETA Tracker on Portal",
                "वेब पोर्टल पर लाइव जेसीबी मशीन लोकेशन व मार्ग खुलने का अनुमानित समय (ETA)",
                "Web Portal Improvement",
                "वेब पोर्टल सुधार (Web Portal)",
                "Add GPS tracking of highway clearance excavators so travelers know when NH-58 and NH-108 will reopen in real time.",
                "वेब पोर्टल पर भूस्खलन हटाने वाली जेसीबी मशीनों की लाइव स्थिति और सड़क खुलने का अनुमानित समय प्रदर्शित किया जाए।",
                "Vikram Bist (Travel Guide Association)",
                "All Uttarakhand",
                "समस्त उत्तराखंड",
                65,
                "Under Review",
                "समीक्षाधीन (Under Review)",
                "2026-08-26 08:10"
            )
        ]
        c.executemany(
            """
            INSERT INTO suggestions (title, title_hi, category, category_hi, description, description_hi, contributor, district, district_hi, upvotes, status, status_hi, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            suggestions
        )

        conn.commit()

    print("SUCCESS: 13-district Uttarakhand bilingual dataset with suggestions inserted successfully!")


if __name__ == "__main__":
    insert_sample_data(reset_existing=True)
