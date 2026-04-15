from __future__ import annotations

from pathlib import Path
from io import BytesIO

from pypdf import PdfReader, PdfWriter, Transformation
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Flowable, Image, PageBreak, Paragraph, SimpleDocTemplate, Spacer


INPUT_TXT = Path("feht-ychebnik-Valvil-19v.fr.v3.txt")
SOURCE_PDF = Path("feht-ychebnik-Valvil-19v.pdf")
IMAGES_DIR = Path("img")
OUTPUT_PDF = Path("feht-ychebnik-Valvil-19v.fr.v4.pdf")
TEMP_OUTPUT_PDF = Path("feht-ychebnik-Valvil-19v.fr.v4.base.pdf")

ILLUSTRATION_CAPTIONS = [
    "Garde de la contre pointe",
    "Garde basse de l'espadon",
    "Garde haute de l'espadon",
    "Garde du déterminé",
    "Garde haute du hongrois",
    "Garde du montagnard Ecossais",
    "Parade et coup de manchette en dehors",
    "Parade et coup de manchette en dedans",
    "Parade et coup de manchette d'envers",
    "Parade et coup de flanc en dehors",
    "Parade et coup de flanc en dedans",
    "Parade et coup de cuisse en dehors",
    "Parade et coup de cuisse en dedans",
    "Parade et coup de tête",
    "Coup d'arrêt pris sur le coup de tête",
    "Coup d'arrêt pris sur le coup de flanc en dedans",
    "Coup d'arrêt pris sur le coup de flanc en dehors",
    "Coup de temps de tête",
    "Parade et coup de figure",
    "Volte en dehors",
    "Volte en dedans",
    "Demi-Volte",
    "Garde acnienne Slavonne",
]


class CenteredSpacedText(Flowable):
    def __init__(self, text: str, font_name: str, font_size: int, letter_spacing: float, height: float) -> None:
        super().__init__()
        self.text = text
        self.font_name = font_name
        self.font_size = font_size
        self.letter_spacing = letter_spacing
        self.height = height

    def wrap(self, availWidth, availHeight):
        self.width = availWidth
        return availWidth, self.height

    def draw(self):
        canvas = self.canv
        canvas.setFont(self.font_name, self.font_size)

        char_widths = [pdfmetrics.stringWidth(ch, self.font_name, self.font_size) for ch in self.text]
        total_width = sum(char_widths)
        if len(self.text) > 1:
            total_width += self.letter_spacing * (len(self.text) - 1)

        x = max(0, (self.width - total_width) / 2)
        y = 0

        for index, ch in enumerate(self.text):
            canvas.drawString(x, y, ch)
            x += char_widths[index]
            if index < len(self.text) - 1:
                x += self.letter_spacing


class LeftRightLine(Flowable):
    def __init__(self, left_text: str, right_lines: list[str], font_name: str, font_size: int, leading: float) -> None:
        super().__init__()
        self.left_text = left_text
        self.right_lines = right_lines
        self.font_name = font_name
        self.font_size = font_size
        self.leading = leading
        self.height = max(leading, leading * len(right_lines))

    def wrap(self, availWidth, availHeight):
        self.width = availWidth
        return availWidth, self.height

    def draw(self):
        canvas = self.canv
        canvas.setFont(self.font_name, self.font_size)
        top_y = self.height - self.leading
        canvas.drawString(0, top_y, self.left_text)
        for idx, line in enumerate(self.right_lines):
            line_width = pdfmetrics.stringWidth(line, self.font_name, self.font_size)
            x = max(0, self.width - line_width)
            y = top_y - (idx * self.leading)
            canvas.drawString(x, y, line)


def register_fonts() -> tuple[str, str]:
    regular_font = "Helvetica"
    italic_font = "Helvetica-Oblique"

    arial = Path(r"C:\Windows\Fonts\arial.ttf")
    arial_italic = Path(r"C:\Windows\Fonts\ariali.ttf")

    if arial.exists():
        pdfmetrics.registerFont(TTFont("ArialV4", str(arial)))
        regular_font = "ArialV4"

    if arial_italic.exists():
        pdfmetrics.registerFont(TTFont("ArialV4Italic", str(arial_italic)))
        italic_font = "ArialV4Italic"

    return regular_font, italic_font


def load_body_paragraphs() -> list[str]:
    text = INPUT_TXT.read_text(encoding="utf-8")
    paragraphs: list[str] = []

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            paragraphs.append("")
            continue
        if line.startswith("[Page ") and line.endswith("]"):
            continue
        paragraphs.append(line)

    collapsed: list[str] = []
    for paragraph in paragraphs:
        if not paragraph:
            if collapsed and collapsed[-1] != "":
                collapsed.append("")
            continue
        collapsed.append(paragraph)

    while collapsed and collapsed[-1] == "":
        collapsed.pop()

    return collapsed


def build_cover_story(regular_font: str, italic_font: str) -> list:
    title_medium = ParagraphStyle(
        "TitleMedium",
        fontName=regular_font,
        fontSize=28,
        leading=32,
        alignment=TA_CENTER,
        spaceAfter=10 * mm,
    )
    title_small = ParagraphStyle(
        "TitleSmall",
        fontName=regular_font,
        fontSize=18,
        leading=22,
        alignment=TA_CENTER,
        spaceAfter=10 * mm,
    )
    title_large = ParagraphStyle(
        "TitleLarge",
        fontName=regular_font,
        fontSize=38,
        leading=42,
        alignment=TA_CENTER,
        spaceAfter=20 * mm,
    )
    italic_center = ParagraphStyle(
        "ItalicCenter",
        fontName=italic_font,
        fontSize=18,
        leading=24,
        alignment=TA_CENTER,
        spaceAfter=8 * mm,
    )
    imprint = ParagraphStyle(
        "Imprint",
        fontName=regular_font,
        fontSize=18,
        leading=24,
        alignment=TA_CENTER,
        spaceAfter=6 * mm,
    )

    return [
        Spacer(1, 34 * mm),
        CenteredSpacedText("TRAITÉ", regular_font, 28, 3.2, 12 * mm),
        Spacer(1, 4 * mm),
        CenteredSpacedText("SUR", regular_font, 18, 2.6, 10 * mm),
        Spacer(1, 4 * mm),
        CenteredSpacedText("LA CONTRE-POINTE,", regular_font, 34, 2.4, 16 * mm),
        Spacer(1, 14 * mm),
        Paragraph("par Valville", italic_center),
        Paragraph("Maître en faits d'Armes.", italic_center),
        Spacer(1, 72 * mm),
        Paragraph("S<super size='9'>T</super>-PÉTERSBOURG,", imprint),
        Paragraph("DE L'IMPRIMERIE DE CHARLES KRAY,", imprint),
        Paragraph("1817.", imprint),
        PageBreak(),
    ]


def build_body_story(regular_font: str) -> list:
    styles = getSampleStyleSheet()
    italic_font = "Helvetica-Oblique"
    if "ArialV4Italic" in pdfmetrics.getRegisteredFontNames():
        italic_font = "ArialV4Italic"

    body = ParagraphStyle(
        "BodyJustified",
        parent=styles["BodyText"],
        fontName=regular_font,
        fontSize=11,
        leading=16,
        alignment=TA_JUSTIFY,
        spaceAfter=4 * mm,
        firstLineIndent=8 * mm,
    )
    heading = ParagraphStyle(
        "BodyHeading",
        parent=body,
        alignment=TA_CENTER,
        firstLineIndent=0,
        fontSize=16,
        leading=20,
        spaceBefore=4 * mm,
        spaceAfter=6 * mm,
    )
    subheading = ParagraphStyle(
        "BodySubheading",
        parent=body,
        fontName=italic_font,
        alignment=TA_CENTER,
        firstLineIndent=0,
        fontSize=13,
        leading=17,
        spaceBefore=2 * mm,
        spaceAfter=5 * mm,
    )

    story: list = []
    first_article_seen = False
    for paragraph in load_body_paragraphs():
        if not paragraph:
            story.append(Spacer(1, 2 * mm))
            continue

        if paragraph.isupper() or paragraph.startswith("ARTICLE "):
            if first_article_seen:
                story.append(PageBreak())
            first_article_seen = True
            story.append(Paragraph(paragraph, heading))
        elif paragraph == "des salles d'armes des régimens de Cavalerie de la Garde IMPÉRIALE.":
            story.append(Paragraph(paragraph.replace("&", "&amp;"), subheading))
        elif paragraph == "Il ne me reste plus à parler que des voltes. Ce sont des espèces d'écarts que l'on fait à gauche ou à droite, quand il est impossible de rompre ou de reculer, et que l'on a affaire à un ennemi qui se jette sur vous.":
            story.append(Paragraph("Il ne me reste plus à parler que des voltes.", subheading))
            story.append(
                Paragraph(
                    "Ce sont des espèces d'écarts que l'on fait à gauche ou à droite, quand il est impossible de rompre ou de reculer, et que l'on a affaire à un ennemi qui se jette sur vous.".replace("&", "&amp;"),
                    body,
                )
            )
        elif paragraph.startswith(
            "Coup de pointe en seconde, en se fendant, feinte de flanc en dedans,"
        ):
            story.append(Paragraph(paragraph.replace("&", "&amp;"), body))
        elif (
            len(paragraph) <= 70
            and (
                paragraph.startswith("Des ")
                or paragraph.startswith("De la ")
                or paragraph.startswith("De l'")
                or paragraph.startswith("Du ")
                or paragraph.startswith("Coup ")
                or paragraph.startswith("Coups ")
                or paragraph.startswith("Volte ")
                or paragraph.startswith("Premier coup")
                or paragraph.startswith("Deuxième coup")
                or paragraph.startswith("Troisième coup")
                or paragraph.startswith("Quatrième coup")
                or paragraph.startswith("Cinquième coup")
            )
        ):
            if paragraph.startswith("Quatrième coup double avec feinte."):
                story.append(PageBreak())
            story.append(Paragraph(paragraph.replace("&", "&amp;"), subheading))
        else:
            story.append(Paragraph(paragraph.replace("&", "&amp;"), body))

    return story


def build_dedication_story(regular_font: str) -> list:
    styles = getSampleStyleSheet()
    dedication_sire = ParagraphStyle(
        "DedicationSire",
        parent=styles["BodyText"],
        fontName=regular_font,
        fontSize=17,
        leading=22,
        alignment=0,
        spaceAfter=4 * mm,
    )
    dedication_royal = ParagraphStyle(
        "DedicationRoyal",
        parent=styles["BodyText"],
        fontName=regular_font,
        fontSize=17,
        leading=22,
        alignment=TA_CENTER,
        spaceAfter=8 * mm,
    )
    dedication_body = ParagraphStyle(
        "DedicationBody",
        parent=styles["BodyText"],
        fontName=regular_font,
        fontSize=11,
        leading=17,
        alignment=TA_JUSTIFY,
        spaceAfter=5 * mm,
        firstLineIndent=8 * mm,
    )

    paragraphs = [
        "SIRE,",
        "VOTRE MAJESTÉ ROYALE",
        "Permettra-t-Elle à celui qu'Elle a honoré de Son choix pour former des maîtres d'armes dans la cavalerie de Sa Garde, de mettre à Ses pieds cet aperçu sur la contre-pointe et sur les gardes des différents peuples d'Europe.",
        "Nous avons plusieurs traités sur l'épée triangulaire et l'espadon, mais il n'en existe point sur la contre-pointe.",
        "Trop heureux, SIRE, si vingt-deux ans de travaux et d'observations m'ont mis à même d'en présenter un à VOTRE MAJESTÉ sur cette arme, qui est dans ce moment-ci l'épée de l'officier russe; et si Elle daigne jeter sur ce travail un regard bienveillant, tous mes vœux seront comblés.",
    ]

    story: list = [Spacer(1, 16 * mm)]
    story.append(Paragraph(paragraphs[0], dedication_sire))
    story.append(Paragraph(paragraphs[1], dedication_royal))
    for paragraph in paragraphs[2:]:
        story.append(Paragraph(paragraph.replace("&", "&amp;"), dedication_body))
    story.append(PageBreak())
    return story


def build_print_permission_story(regular_font: str) -> list:
    styles = getSampleStyleSheet()
    permission_title = ParagraphStyle(
        "PermissionTitle",
        parent=styles["BodyText"],
        fontName=regular_font,
        fontSize=15,
        leading=20,
        alignment=TA_CENTER,
        spaceAfter=8 * mm,
    )
    permission_body = ParagraphStyle(
        "PermissionBody",
        parent=styles["BodyText"],
        fontName=regular_font,
        fontSize=11,
        leading=17,
        alignment=TA_JUSTIFY,
        spaceAfter=5 * mm,
        firstLineIndent=8 * mm,
    )
    story: list = [Spacer(1, 18 * mm)]
    story.append(Paragraph("PERMIS D'IMPRIMER,", permission_title))
    story.append(
        Paragraph(
            "À la charge de fournir au Comité de la Censure, après l'impression et avant de mettre l'ouvrage en vente, un exemplaire pour ledit Comité, un exemplaire pour le Département du Ministre de l'Instruction Publique, deux exemplaires pour la Bibliothèque Impériale publique, et un exemplaire pour l'Académie Impériale des Sciences.",
            permission_body,
        )
    )
    story.append(Spacer(1, 10 * mm))
    story.append(
        LeftRightLine(
            "St-Pétersbourg, le 15 octobre 1816.",
            ["SOHN, Censeur", "et Conseiller de Cour."],
            regular_font,
            11,
            16,
        )
    )
    story.append(PageBreak())
    return story


def build_notice_story(regular_font: str) -> list:
    styles = getSampleStyleSheet()
    notice_title = ParagraphStyle(
        "NoticeTitle",
        parent=styles["BodyText"],
        fontName=regular_font,
        fontSize=16,
        leading=20,
        alignment=TA_CENTER,
        spaceAfter=8 * mm,
    )
    notice_body = ParagraphStyle(
        "NoticeBody",
        parent=styles["BodyText"],
        fontName=regular_font,
        fontSize=11,
        leading=17,
        alignment=TA_JUSTIFY,
        spaceAfter=5 * mm,
        firstLineIndent=8 * mm,
    )
    notice_signature = ParagraphStyle(
        "NoticeSignature",
        parent=notice_body,
        alignment=2,
        firstLineIndent=0,
        spaceAfter=3 * mm,
    )

    story: list = [PageBreak(), Spacer(1, 18 * mm)]
    story.append(Paragraph("AVIS.", notice_title))
    story.append(
        Paragraph(
            "Je n'ai écrit cet ouvrage que pour servir de guide aux officiers généraux de cavalerie qui voudraient introduire l'art de tirer des armes dans leurs divisions, ainsi que pour tout amateur qui aurait déjà appris l'épée triangulaire ou pour tout écolier guidé par un maître. Il devient tout à fait inutile pour toute personne qui en ignorerait les premiers principes, vu que dans un traité aussi court et aussi précis, il est impossible de détailler chaque terme technique et leur signification; par conséquent il est inintelligible pour une personne qui le lirait sans connaître cet art. L'accueil qu'il a obtenu de SA MAJESTÉ est sa meilleure recommandation.",
            notice_body,
        )
    )
    story.append(Spacer(1, 8 * mm))
    story.append(Paragraph("A. VALVILLE.", notice_signature))
    story.append(Paragraph("Maître en faits d'armes.", notice_signature))
    return story


def build_user_illustrations_story() -> list:
    styles = getSampleStyleSheet()
    caption_style = ParagraphStyle(
        "IllustrationCaption",
        parent=styles["BodyText"],
        fontName="Helvetica-Oblique",
        fontSize=11,
        leading=15,
        alignment=TA_CENTER,
        spaceBefore=4 * mm,
        spaceAfter=0,
    )

    files = sorted(
        [p for p in IMAGES_DIR.iterdir() if p.is_file()],
        key=lambda p: (0, int(p.stem)) if p.stem.isdigit() else (1, p.name.lower()),
    )

    story: list = []
    max_width = A4[0] - (2 * 18 * mm)
    max_height = A4[1] - (2 * 18 * mm)

    for idx, image_path in enumerate(files):
        story.append(PageBreak())
        story.append(Spacer(1, 10 * mm))
        img = Image(str(image_path))
        img._restrictSize(max_width, max_height)
        story.append(img)
        if idx < len(ILLUSTRATION_CAPTIONS):
            story.append(Paragraph(ILLUSTRATION_CAPTIONS[idx], caption_style))

    return story


def main() -> None:
    regular_font, italic_font = register_fonts()

    doc = SimpleDocTemplate(
        str(OUTPUT_PDF),
        pagesize=A4,
        leftMargin=22 * mm,
        rightMargin=22 * mm,
        topMargin=20 * mm,
        bottomMargin=20 * mm,
        title="Traité sur la Contre-pointe",
    )

    story = []
    story.extend(build_cover_story(regular_font, italic_font))
    story.extend(build_dedication_story(regular_font))
    story.extend(build_print_permission_story(regular_font))
    story.extend(build_body_story(regular_font))
    story.extend(build_notice_story(regular_font))
    story.extend(build_user_illustrations_story())
    doc.build(story)

    print(OUTPUT_PDF)


if __name__ == "__main__":
    main()
