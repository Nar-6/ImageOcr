import cv2
import pytesseract
import sys

# ⚠️ Indiquer le chemin complet de tesseract.exe sur Windows
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def preprocess_image(image):
    # Convertir en niveaux de gris + améliorer la qualité
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return thresh

def extract_text(image):
    processed = preprocess_image(image)
    # OCR avec Tesseract (langue française)
    text = pytesseract.image_to_string(processed, lang="fra")
    return text.strip()

def main():
    if len(sys.argv) < 2:
        print("❌ Utilisation : python imageOcr.py <image_path>")
        sys.exit(1)

    image_path = sys.argv[1]
    img = cv2.imread(image_path)

    if img is None:
        print(f"❌ Impossible de charger l'image: {image_path}")
        sys.exit(1)

    extracted_text = extract_text(img)

    print(extracted_text)
    print("\n" + "="*50)
    print("ℹ️ Conseils pour de meilleurs résultats :")
    print("- Utilisez des images haute résolution")
    print("- Assurez un bon contraste (fond clair, texte foncé)")
    print("- Évitez le flou et les ombres")
    print("="*50)

    # Sauvegarde du résultat dans un fichier texte
    with open("output.txt", "w", encoding="utf-8") as f:
        f.write(extracted_text)

if __name__ == "__main__":
    main()
