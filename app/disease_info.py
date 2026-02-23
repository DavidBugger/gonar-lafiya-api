# Disease information: English + Hausa translations, advice, severity

DISEASE_INFO = {
    "FMD": {
        "name_en": "Foot-and-Mouth Disease (FMD)",
        "name_ha": "Cutar Ƙafa da Baki (FMD)",
        "severity": "High",
        "seek_vet": True,
        "advice_en": (
            "1. Immediately isolate the affected animal from others to prevent spread.\n"
            "2. Contact your local veterinary officer as soon as possible.\n"
            "3. Disinfect all areas the animal has been in contact with.\n"
            "4. Do not move the animal to markets or other farms.\n"
            "5. Ensure clean water and soft feed for the animal.\n"
            "6. Report to your local livestock authority immediately."
        ),
        "advice_ha": (
            "1. Nan da nan ka ware dabbar da ta kamu daga sauran don hana yada cuta.\n"
            "2. Ka tuntubi jami'in lafiyar dabbobi na gari da wuri-wuri.\n"
            "3. Ka tsaftace dukkan wuraren da dabbar ta taɓa.\n"
            "4. Kada ka kai dabbar kasuwa ko gona ta wani.\n"
            "5. Ka tabbatar da ruwan sha mai tsabta da abinci mai taushi.\n"
            "6. Ka sanar da hukumar kula da dabbobi nan take."
        )
    },

    "CBPP": {
        "name_en": "Contagious Bovine Pleuropneumonia (CBPP)",
        "name_ha": "Cutar Huhu ta Shanu (CBPP)",
        "severity": "Critical",
        "seek_vet": True,
        "advice_en": (
            "1. URGENT: Isolate the affected cattle immediately — this disease spreads fast.\n"
            "2. Call a veterinary officer right away, this is a notifiable disease.\n"
            "3. Do not allow other cattle to graze in the same area.\n"
            "4. Avoid sharing water troughs and feeding equipment.\n"
            "5. Vaccinate the rest of your herd if advised by a vet.\n"
            "6. Do not sell or transport affected animals."
        ),
        "advice_ha": (
            "1. GAGGAWA: Ka ware shanun da suka kamu nan take — wannan cuta tana yada da sauri.\n"
            "2. Ka kira jami'in lafiyar dabbobi yanzu haka, wannan cuta dole a ba da rahoto.\n"
            "3. Kada ka bar sauran shanu su yi kiwo a wannan wuri.\n"
            "4. Guji raba kwanon ruwa da kayan ciyarwa.\n"
            "5. Ka yi wa sauran shanun rigakafi idan jami'in lafiya ya ba da shawara.\n"
            "6. Kada ka sayar ko kai dabbar da ta kamu wani wuri."
        )
    },

    "PPR": {
        "name_en": "Peste des Petits Ruminants (PPR)",
        "name_ha": "Cutar Ƙananan Dabbobi (PPR) - Sangaya",
        "severity": "High",
        "seek_vet": True,
        "advice_en": (
            "1. Separate sick sheep/goats from healthy ones immediately.\n"
            "2. Contact a veterinary officer urgently — PPR can kill quickly.\n"
            "3. Provide clean water as diarrhea causes dehydration.\n"
            "4. Keep the sick animal warm and sheltered.\n"
            "5. Do not take animals to markets until cleared by a vet.\n"
            "6. Vaccinate remaining animals to prevent further spread."
        ),
        "advice_ha": (
            "1. Ka ware raguna/awaki marasa lafiya daga lafaffun nan take.\n"
            "2. Ka tuntubi jami'in lafiyar dabbobi da gaggawa — Sangaya na iya kashe dabba da sauri.\n"
            "3. Ka ba dabbar ruwan sha mai tsabta domin gudawa yana haddasa ƙishirwa.\n"
            "4. Ka ajiye dabbar cikin dumi da rufi.\n"
            "5. Kada ka kai dabbobi kasuwa sai jami'in lafiya ya yarda.\n"
            "6. Ka yi wa sauran dabbobin rigakafi don hana yada cuta."
        )
    },

    "Healthy": {
        "name_en": "No Disease Detected (Healthy)",
        "name_ha": "Babu Cuta (Lafiya)",
        "severity": "None",
        "seek_vet": False,
        "advice_en": (
            "1. Your animal appears healthy based on the symptoms provided.\n"
            "2. Continue regular feeding with clean water and balanced nutrition.\n"
            "3. Maintain a clean and hygienic living environment.\n"
            "4. Schedule routine vaccinations with your local vet.\n"
            "5. Monitor your animal daily for any new symptoms.\n"
            "6. Keep records of your animal's health history."
        ),
        "advice_ha": (
            "1. Dabbar ka tana da lafiya dangane da alamomin da ka bayar.\n"
            "2. Ka ci gaba da ciyarwa da kyau tare da ruwan sha mai tsabta.\n"
            "3. Ka kula da tsabtar mazaunin dabbar.\n"
            "4. Ka shirya allurar rigakafi na yau da kullum tare da jami'in lafiya.\n"
            "5. Ka lura da dabbar kowace rana don sabon alamomi.\n"
            "6. Ka riƙa rubuta tarihin lafiyar dabbar ka."
        )
    }
}


def get_confidence_label(probability: float) -> str:
    if probability >= 0.80:
        return "High"
    elif probability >= 0.55:
        return "Medium"
    else:
        return "Low"
