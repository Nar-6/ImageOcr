import sys
import json
import re
from rapidfuzz import fuzz

# ----------------------------
# Calcul du score de similarité
# ----------------------------
def match_score(fields, text):
    total_score = 0
    text_lower = text.lower()

    for field in fields:
        score = fuzz.partial_ratio(field.lower(), text_lower)
        total_score += score

    return round(total_score / len(fields), 2) if fields else 0.0

# ----------------------------
# Extraction et vérification ID card
# ----------------------------
def extract_and_verify_id(country, doc_type, text, africa_formats, europe_america_formats):
    # Cas Afrique
    if country in africa_formats and doc_type in africa_formats[country]:
        fmt = africa_formats[country][doc_type]

        # Construire la regex en fonction du type
        if fmt["type"] == "numeric":
            regex_pattern = "^" + fmt["format"].replace("#", "[0-9]") + "$"
        elif fmt["type"] == "alphanumeric":
            regex_pattern = "^" + fmt["format"].replace("#", "[A-Z0-9]") + "$"
        else:
            return False, None

        # Chercher dans tout le texte OCR
        candidates = re.findall(r"[A-Z0-9]+", text.upper())

        for candidate in candidates:
            if len(candidate) == fmt["longueur"] and re.match(regex_pattern, candidate, re.IGNORECASE):
                return True, candidate  # ID trouvé et valide
        return False, None

    # Cas Europe/Amérique
    for entry in europe_america_formats["formats"]:
        if entry["country"].lower() == country.lower() and entry["type"].lower() == doc_type.lower():
            regex_pattern = entry["format_regex"]

            candidates = re.findall(r"[A-Z0-9]+", text.upper())
            for candidate in candidates:
                if re.match(regex_pattern, candidate):
                    return True, candidate
            return False, None

    return False, None  # Pas trouvé

# ----------------------------
# Main
# ----------------------------
if __name__ == "__main__":
    if len(sys.argv) < 5:
        print(json.dumps({"score": 0, "valid_id": False, "id_value": None}))
        sys.exit(0)

    fields = json.loads(sys.argv[1])   # Liste de champs (nom, prénom…)
    ocr_text = sys.argv[2]             # Texte OCR complet
    country = sys.argv[3]              # Pays
    doc_type = sys.argv[4]             # Type de doc (CNI, Passeport…)

    # Charger les bases de formats
    with open("formats_identite_afrique.json", "r", encoding="utf-8") as f:
        africa_formats = json.load(f)

    with open("formats_identite_verified_payseurope_amerique.json", "r", encoding="utf-8") as f:
        europe_america_formats = json.load(f)

    # Calcul du score de similarité
    score = match_score(fields, ocr_text)

    # Extraction + vérification de l’ID
    valid_id, id_value = extract_and_verify_id(country, doc_type, ocr_text, africa_formats, europe_america_formats)

    # Résultat JSON
    print(json.dumps({
        "score": score,
        "valid_id": valid_id,
        "id_value": id_value
    }))



# Exemple d'appel depuis PHP (Symfony) à redapter
# --------------------------------------------
# use Symfony\Component\Process\Process;
# use Symfony\Component\HttpFoundation\JsonResponse;

# public function verifyId(): JsonResponse
#     {
#         // Exemple de données (tu pourrais les récupérer d'une requête HTTP POST)
#         $fields = ["KOUNASSO", "Thibaut"];
#         $ocrText = "Carte nationale d'identité du Bénin Nom: KOUNASSO Prénom: Thibaut Numéro: 1234567890";
#         $country = "Bénin";
#         $docType = "CNI";

#         // Préparer les arguments pour Python
#         $args = [
#             'python3', // ou 'python' selon ton environnement Windows/Linux
#             __DIR__ . '/../../python/compareInfoWithImageOcr.py', // chemin vers ton script
#             json_encode($fields),
#             $ocrText,
#             $country,
#             $docType
#         ];

#         // Lancer le process
#         $process = new Process($args);
#         $process->run();

#         if (!$process->isSuccessful()) {
#             return new JsonResponse([
#                 'error' => 'Erreur lors de l\'exécution du script Python',
#                 'details' => $process->getErrorOutput()
#             ], 500);
#         }

#         // Récupérer le résultat JSON produit par Python
#         $output = $process->getOutput();
#         $result = json_decode($output, true);

#         return new JsonResponse([
#             'score'    => $result['score'] ?? 0,
#             'valid_id' => $result['valid_id'] ?? false,
#             'id_value' => $result['id_value'] ?? null,
#         ]);
#     }