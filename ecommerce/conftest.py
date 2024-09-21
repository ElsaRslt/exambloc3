import pytest
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from bs4 import BeautifulSoup
from datetime import datetime

@pytest.hookimpl(tryfirst=True)
def pytest_sessionfinish(session, exitstatus):
    pdf_report = "report.pdf"
    html_report_path = "htmlcov/index.html"

    # Lire les données du rapport HTML
    with open(html_report_path, 'r') as file:
        soup = BeautifulSoup(file, 'html.parser')

    # Trouver les données dans le tableau
    table_rows = soup.find_all('tr')[1:]  # Ignorer l'en-tête
    data = []
    for row in table_rows:
        cols = row.find_all('td')
        if len(cols) > 0:
            data.append([col.get_text(strip=True) for col in cols])

    # Inclure l'en-tête dans les données
    headers = ["Name", "Statements", "Missing","Excluded", "Coverage"]
    data.insert(0, headers)
    


    # Calculer les largeurs maximales de chaque colonne
    column_widths = [0] * len(data[0])
    for row in data:
        for i, item in enumerate(row):
            column_widths[i] = max(column_widths[i], len(item))

    # Définir une largeur de base pour chaque colonne (en points)
    base_width = 60  # Largeur de base par colonne
    adjusted_widths = [base_width + (width * 6) for width in column_widths]  # Ajuster la largeur

    # Vérifier la largeur totale et ajuster si nécessaire
    total_width = sum(adjusted_widths)
    max_page_width = 500  # Largeur maximale de la page

    if total_width > max_page_width:
        scale_factor = max_page_width / total_width
        adjusted_widths = [width * scale_factor for width in adjusted_widths]

    # Créer un nouveau document PDF
    c = canvas.Canvas(pdf_report, pagesize=letter)
    width, height = letter

    # Titre
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width / 2, height - 50, "Rapport de test")
    
    # Date de génération
    generation_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.setFont("Helvetica", 10)
    c.drawString(50, height - 10, f"Date de génération : {generation_date}")


    # Ajouter les en-têtes de colonnes
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(colors.grey)
    c.rect(50, height - 80, sum(adjusted_widths), 20, fill=1)  # Fond gris
    c.setFillColor(colors.black)

    # Dessiner les en-têtes de colonnes
    for i, header in enumerate(headers):
        c.drawCentredString(50 + sum(adjusted_widths[:i]) + (adjusted_widths[i] / 2), height - 75, header)

    # Dessiner les lignes
    c.setFont("Helvetica", 10)
    y_position = height - 100

    # Hauteur de la cellule
    cell_height = 20

    for row in data[1:]:  # Commencer à partir de la deuxième ligne pour éviter les doublons
        # Vérifier si c'est la ligne du total
        if row[0] == "Total":
            c.setFillColor(colors.grey)  # Couleur grise pour la ligne du total
            c.rect(50, y_position, sum(adjusted_widths), cell_height, fill=1)  # Fond gris

        for i, item in enumerate(row):
            # Calculer la position pour centrer verticalement
            text_y_position = y_position + (cell_height / 2) - 5
            c.setFillColor(colors.black)  # Réinitialiser la couleur pour le texte
            c.drawCentredString(50 + sum(adjusted_widths[:i]) + (adjusted_widths[i] / 2), text_y_position, str(item))
        y_position -= cell_height  # Espacement entre les lignes

        # Dessiner la bordure
        c.rect(50, y_position, sum(adjusted_widths), cell_height)

        if y_position < 50:  # Si on atteint le bas de la page, créer une nouvelle page
            c.showPage()
            y_position = height - 100

    c.save()
    print(f"\nPDF report generated successfully: {pdf_report}")
