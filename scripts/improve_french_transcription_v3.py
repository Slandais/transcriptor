from __future__ import annotations

import re
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


INPUT_TXT = Path("feht-ychebnik-Valvil-19v.fr.v2.txt")
OUTPUT_TXT = Path("feht-ychebnik-Valvil-19v.fr.v3.txt")
OUTPUT_PDF = Path("feht-ychebnik-Valvil-19v.fr.v3.pdf")

PAGE_RE = re.compile(r"^\[Page (\d+)\]$")

GLOBAL_REPLACEMENTS = [
    ("appellé", "appelé"),
    ("determiné", "déterminé"),
    ("arriére", "arrière"),
    ("vélocité", "vélocité"),
    ("où à l'être", "ou à l'être"),
    ("partie droite,,", "partie droite,"),
    ("hâché", "haché"),
    ("téte", "tête"),
    ("téle", "tête"),
    ("adversnire", "adversaire"),
    ("quelqu'il", "quel qu'il"),
    ("part ez", "partez"),
    ("partez et", "partant avec"),
    ("élèvant", "élevant"),
    ("vouloit", "voulait"),
    ("eu dessous", "en dessous"),
    ("eit", "et"),
    ("coté", "côté"),
    ("mérae", "même"),
    ("ßancs", "flancs"),
    ("bander oll es", "banderolles"),
    ("éde- paule", "épaule"),
    ("téte", "tête"),
    ("tems", "temps"),
    ("prit", "pris"),
    ("Ã§n", "en"),
    ("Voile", "Voltes"),
    ("va/te", "volte"),
    ("detour", "détour"),
    ("terrein", "terrain"),
    ("ä droite", "à droite"),
    ("ä gauche", "à gauche"),
    ("poilrine", "poitrine"),
    ("épaulo", "épaule"),
    ("app e rçu", "aperçu"),
    ("maitre", "maître"),
    ("Frédéric", "Frédéric"),
    ("bayonnette", "baïonnette"),
    ("regimens", "régimens"),
    ("mpériale", "Impériale"),
    ("carré", "carré"),
    ("galerie", "galerie"),
    ("avaient ignoraient", "avaient ignoré"),
]


def load_pages(text: str) -> list[tuple[int, list[str]]]:
    pages: list[tuple[int, list[str]]] = []
    current_number: int | None = None
    current_lines: list[str] = []

    for raw_line in text.splitlines():
        match = PAGE_RE.match(raw_line.strip())
        if match:
            if current_number is not None:
                pages.append((current_number, current_lines))
            current_number = int(match.group(1))
            current_lines = []
            continue
        current_lines.append(raw_line.rstrip())

    if current_number is not None:
        pages.append((current_number, current_lines))

    return pages


def clean_line(line: str) -> str:
    line = line.strip()
    line = re.sub(r"\s+", " ", line)
    for src, dst in GLOBAL_REPLACEMENTS:
        line = line.replace(src, dst)
    return line


def fix_page(number: int, lines: list[str]) -> list[str]:
    cleaned = [clean_line(line) for line in lines if line.strip()]

    if number == 6:
        return [
            "ARTICLE PREMIER.",
            "Des Gardes.",
            "La garde de la contre-pointe est à peu près celle de l'épée. La seule différence est dans la main droite, qui est tournée en tierce, à la hauteur et en ligne de l'épaule droite; la pointe de l'épée en ligne de l'œil de l'adversaire, le bras gauche derrière le dos, le revers de la main posé sur les reins. On marche, on rompt, et l'on se fend comme à l'épée. Mais ce qui n'est pas dans l'épée, c'est de doubler la détente, c'est-à-dire, après s'être fendu, de venir mettre le pied gauche contre le pied droit, et de reformer une seconde détente en se refendant de nouveau. C'est aussi de marcher en arrière en portant, étant premièrement en garde, le pied droit derrière, le pied gauche à un pas en arrière, et se remettant en garde en reportant le pied gauche en arrière.",
            "Il existe quatre gardes d'espadon, sans compter celle du montagnard écossais, qui tient encore à l'ancienne garde romaine, pour lesquelles je renvoie aux gravures ci-jointes.",
            "D'après de nombreux essais, j'ai toujours trouvé que celle de la contre-pointe était la meilleure, soit pour attaquer, en vous portant avec vélocité sur votre adversaire, soit en vous mettant à même de rompre à une grande distance. Je ne dirai qu'un mot de la garde du déterminé, appelée ainsi parce que celui qui la prend est déterminé à tuer ou à l'être par son adversaire. Par sa position, il est entièrement fendu et le corps sur la partie droite, son bras droit plié sur son épaule gauche; il attend le coup de son adversaire, qui se trouve, en le lui portant, ou la tête fendue, ou le corps haché en deux, ou coupé de bas en haut.",
            "L'énorme pas que le déterminé fait en arrière, sur l'attaque de son adversaire, le met à même de rendre son coup nul et de sabrer, soit perpendiculairement, soit transversalement, soit de bas en haut; mais tout cela devient nul si son adversaire l'attend.",
        ]

    if number == 8:
        return [
            "ARTICLE DEUXIÈME.",
            "Des coups des manchettes.",
            "Ce terme est emprunté de l'espadon; car il y a bien longtemps que nous ne portons plus de manchettes. Il désigne les coups avec lesquels on peut blesser le bras droit de son adversaire et, par conséquent, le désarmer; car il n'y a pas d'autre désarmement au sabre. Il y en a trois dans la contre-pointe: le premier, que nous appelions coup de manchette en dehors, car les deux côtés du corps, c'est-à-dire le côté de la poitrine, qui est comme à la pointe le dedans des armes, et le côté du dos, qui est le dehors. Il en est de même du bras.",
            "Le coup de manchette en dehors se forme en étant engagé de quarte et faisant un cercle au-dessus de la pointe de l'ennemi, puis venant couper le côté droit de son avant-bras, en portant tant soit peu le corps sur la jambe droite, sans se fendre.",
            "Le coup de manchette en dedans se forme, étant engagé en tierce avec son adversaire, longeant le long de sa lame et revenant perpendiculairement couper son bras au défaut du poignet.",
            "Le coup de manchette d'envers, que nous appelions ainsi vu que la main se tourne à l'envers en le donnant, se forme en faisant un cercle entier avec son sabre et venant couper toute la longueur du dessous de l'avant-bras de son adversaire. Ces trois coups de sabre ont l'avantage de se tirer sans se fendre et, par conséquent, sans s'engager sous le fer de son ennemi.",
        ]

    if number == 9:
        return [
            "ARTICLE TROISIÈME.",
            "Des coups de flancs, banderolles et coups de cuisse.",
            "Les coups de flancs, qui coupent le corps en deux transversalement, se forment soit en filant, soit en passant par-dessus la pointe de l'épée de son adversaire, se fendant vivement et coupant son corps en travers, soit en dedans, soit en dehors.",
            "Le coup de banderolle, ainsi nommé par les soldats parce qu'il décrit la même ligne que la bande de buffle qui supporte la giberne, se forme étant en garde de tierce, dégageant finement, filant le long de la lame de l'adversaire, et venant porter le coup depuis l'épaule gauche jusqu'à la hanche droite.",
            "Les coups de banderolle d'envers se forment en faisant un cercle avec la lame de votre sabre, en commençant par en haut, se fendant avec vitesse et venant donner le coup de bas en haut, depuis la hanche droite jusqu'à l'épaule gauche, ou depuis la hanche gauche jusqu'à l'épaule droite. Ces trois coups doivent être portés avec beaucoup de vivacité et de finesse; sans cela ils sont dangereux, car les coups d'arrêt peuvent être pris s'ils sont larges ou lents.",
            "Les coups de cuisse ne sont bons qu'en riposte ou comme feinte; ils se forment en filant le long du sabre de l'adversaire et venant couper sa cuisse de haut en bas, car il faut que la blessure soit profonde pour pouvoir mettre son ennemi hors de combat.",
        ]

    if number == 10:
        patched = []
        for line in cleaned:
            if line == "to":
                continue
            line = line.replace("ARTICLE QUATRIÈM E.", "ARTICLE QUATRIÈME.")
            line = line.replace("Des coups de lé te, de pointe, d'attaque.", "Des coups de tête, de pointe, d'attaque.")
            line = line.replace("seconde è la pointe", "seconde à la pointe")
            line = line.replace("tournant Ja main", "tournant la main")
            patched.append(line)
        return patched

    if number == 11:
        return [
            "Troisième coup double.",
            "Vous portez quarte, en vous fendant dans les armes; votre adversaire pare bas en reculant. Vous dégagez vivement, sans tourner la main, en doublant la détente, et vous reportez le second coup au flanc de votre adversaire.",
            "Quatrième coup double avec feinte.",
            "Vous portez seconde sous le poignet; votre adversaire pare; vous lui portez la pointe au visage, en mettant le pied gauche contre le pied droit, la main et les ongles en l'air; vous retournez vivement les ongles en dessous, en doublant la détente.",
            "Cinquième coup double.",
            "Vous vous fendez en portant quarte sur les armes; vous faites feinte seconde, sans baisser la main, la tournant seulement en dessous; mettant le pied gauche contre le droit, vous la retournez vivement en quarte, vous doublez la détente, en portant votre coup de pointe à la poitrine de votre adversaire.",
        ]

    if number == 12:
        return [
            "ARTICLE CINQUIÈME.",
            "Des coups d'arrêt.",
            "Si votre adversaire lève le bras ou découvre sa poitrine, soit en tierce, soit en quarte, il peut être arrêté sur-le-champ, soit qu'il donne le coup de tête ou tout autre coup de haut en bas où l'adversaire n'emploie pas le moulinet et où il lève le bras au-dessus de sa tête pour vous frapper. Prenez le temps où il découvre sa poitrine, droit vivement, les ongles en l'air, la main à la hauteur de votre tête, bien couvert en quarte; vous l'arrêtez sur son développement, vous lui plongez votre épée dans la poitrine, et par la position de votre main vous parez son coup, quel qu'il soit.",
            "S'il veut sabrer votre côté droit, comme son mouvement est large, vous le voyez; vous tournez la main de tierce, vous pointez seconde, vous couvrant bien sur votre droite. Si au contraire c'est en dedans des armes qu'il veut vous sabrer transversalement, vous le pointez, la main à la hauteur de votre poitrine, autant écartée sur la gauche que possible, les ongles en quarte.",
            "Ces coups doivent être portés avec une grande vitesse et une grande certitude de les réussir; surtout, que votre adversaire ne puisse pas s'en douter d'avance, car sans cela ils sont funestes pour celui qui les prend, n'ayant plus ni parade ni aucune ressource s'il les manque. Ils sont excellents contre tout homme qui se jette ou qui vous court dessus, et c'est pour cela qu'ils sont nommés coups d'arrêt.",
        ]

    if number == 15:
        return [
            "ARTICLE HUITIÈME.",
            "Du battement de fer.",
            "Le battement de fer est bon quand vous craignez un coup d'arrêt ou tout autre coup de pointe.",
            "Exemple. Battement de fer, coup de figure: il se forme, étant engagé de tierce avec votre adversaire, dégageant sans tourner la main, avec force et vivement, avec le dos de votre lame sur le tranchant de celle de votre adversaire, marchant un pas en avant et vous trouvant par ce mouvement votre épée engagée entre la sienne et sa tête; fendez-vous vivement, et tirez coup de figure.",
            "Le même battement peut être employé pour le coup de cuisse; et quand vous voulez l'employer pour le dehors, en battant le fer vous passez par-dessus son épée; alors vous pouvez tirer coup de manchette en dehors et coup de flanc. Ces coups sont bons quand votre adversaire vous donne du fer, en vous présentant la pointe aux yeux, ou s'il veut vous arrêter.",
        ]

    if number == 16:
        patched = []
        for line in cleaned:
            line = line.replace("ARTICLE NEU V I E M E.", "ARTICLE NEUVIÈME.")
            line = line.replace("comme d est trop loin pour-vous riposter", "comme il est trop loin pour vous riposter")
            line = line.replace("téte", "tête")
            line = line.replace("coté", "côté")
            patched.append(line)
        return patched

    if number == 20:
        return [
            "ARTICLE TREIZIÈME.",
            "Coups en moulinet.",
            "Le moulinet tire son nom de sa forme: il décrit un cercle entier avec l'épée, dont le poignet est le pivot. Il y a quatre moulinets simples: celui qui se fait en dedans, en baissant la pointe de votre épée et la faisant revenir par en haut pour couper de haut en bas; le second se fait en dehors dans la même direction; le troisième se forme, étant en garde, en élevant la pointe de l'épée et en faisant revenir de haut en bas. Les moulinets doubles se font d'un côté et de l'autre; ils sont bons dans une foule, pour se frayer un passage.",
        ]

    if number == 21:
        patched = []
        for line in cleaned:
            line = line.replace("Des coups de temps.", "Des coups de temps.")
            line = line.replace("Le coup de temps s'appelle ainsi par la raison qu'il est pris", "Le coup de temps s'appelle ainsi parce qu'il est pris")
            line = line.replace("çn dedans", "en dedans")
            line = line.replace("même", "même")
            patched.append(line)
        return patched

    if number == 22:
        return [
            "ARTICLE QUINZIÈME.",
            "Des écrasements de fer.",
            "Ces coups nous viennent de l'espadon et sont meilleurs dans cette arme que dans la contre-pointe, par la raison que, pour les faire, il faut se découvrir beaucoup. L'écrasement de fer et coup de banderolle d'envers se prend quand vous vous apercevez que votre adversaire veut vous prendre un coup de pointe, étant en garde de tierce tous les deux; vous appuyez fortement votre lame sur la sienne en marchant un pas en avant, et venant frapper la terre en dedans de son pied droit, renversant sa lame et l'ôtant entièrement de la ligne de votre corps; retournant vivement votre main, les ongles en l'air, vous vous fendez avec vélocité et lui tirez le coup de banderolle d'envers, depuis la hanche gauche jusqu'à l'épaule droite.",
            "L'écrasement de fer, coup défiguré, se forme de la même manière que le précédent, excepté qu'au lieu de passer votre sabre sous celui de l'adversaire, vous le laissez en dessus et le relevez à la hauteur de sa figure, que vous coupez transversalement.",
            "L'écrasement de fer, coup de flanc en dehors, se fait de la même manière, excepté qu'après avoir écrasé vous passez votre lame à droite de l'adversaire et lui tirez coup de flanc en dehors. Ces coups sont bons quand votre adversaire vous donne du fer ou veut vous pointer; mais ils sont dangereux s'il s'en doute, car il peut dégager sur le temps et vous arrêter.",
        ]

    if number == 23:
        return [
            "ARTICLE SEIZIÈME.",
            "Il ne me reste plus à parler que des voltes. Ce sont des espèces d'écarts que l'on fait à gauche ou à droite, quand il est impossible de rompre ou de reculer, et que l'on a affaire à un ennemi qui se jette sur vous.",
            "De la volte à droite.",
            "Elle se forme dans le moment que votre adversaire marche sur vous, en se lançant à droite, le pied droit le premier, tournant un quart de tour, et faisant face parallèlement à son épaule droite; en même temps il faut tirer le coup de banderolle d'envers de gauche à droite en dedans.",
            "S'il pare votre coup, ce qui est très difficile, il faut continuer la rotation de votre épée, vous fendre vivement, et lui porter le coup de tête qu'il lui est presque impossible de parer, se trouvant hors de garde et de ligne; par la raison qu'ayant fait un quart de détour sur sa droite, il est obligé de tourner lui-même pour se défendre, et dans le cas où vous ne le toucheriez pas, vous vous trouvez du terrain derrière vous pour pouvoir rompre.",
            "Volte à gauche.",
            "Elle se forme comme la précédente, excepté que vous vous élancez sur la gauche de votre ennemi, faisant face à sa poitrine, tirant le coup de banderolle du côté opposé, c'est-à-dire depuis la hanche droite jusqu'à l'épaule gauche; si votre adversaire pare, comme la pointe de votre épée se trouve en face de sa poitrine, portez-lui le coup de pointe, en vous fendant vivement.",
        ]

    if number == 24:
        return [
            "ARTICLE DIX-SEPTIÈME.",
            "De la demi-volte.",
            "Il n'en existe qu'une; elle ne s'emploie que quand vous n'avez pas d'autre ressource, c'est-à-dire quand vous ne pouvez ni rompre, ni volter à droite ni à gauche. Car dès qu'il n'y a plus de distance entre vous et votre adversaire, il n'y a plus moyen de parer; par conséquent vous faites coup pour coup, et vous vous hachez mutuellement.",
            "Pour éviter cette extrémité, si vous vous trouvez dans un chemin trop étroit pour volter, ou dans l'angle d'un mur, ou dans toute autre position qui vous empêche de rompre ou de vous élancer, soit à droite soit à gauche; dans le moment que votre ennemi court sur vous, le sabre levé, déterminé à faire coup pour coup, fendez-vous sur votre gauche de toute votre longueur, votre main gauche se portant par terre pour soutenir votre corps, votre pied droit parallèlement à la pointe de votre pied gauche, votre corps renversé sur votre main gauche, et portant en même temps un coup de flanc en dedans, qui se trouve être terrible par la force et la vivacité avec laquelle vous vous jetez du côté opposé.",
            "Il faut faire bien attention de ne pas manquer votre coup; car si cela vous arrive, vous êtes perdu, vous trouvant entièrement renversé et hors d'état de pouvoir parer les coups de votre adversaire. Je le répète, ce coup ne doit se faire que quand il n'y a pas d'autres ressources.",
            "Ici se termine cet aperçu sur la contre-pointe, fruit d'un long travail. Depuis trente ans je fais des armes, et depuis vingt-deux je suis maître; j'ai beaucoup voyagé, je connais depuis le double bâton nègre jusqu'au cudgel du montagnard écossais, depuis la garde basse napolitaine jusqu'à la garde haute du hongrois, depuis la superbe garde ancienne du slavon, telle qu'elle est",
        ]

    if number == 25:
        return [
            "représentée ici, et telle que je l'ai montrée dans mes combats funèbres de Fingal, jusqu'à la contre-pointe moderne, arme que le grand Frédéric a lui-même donnée à ses troupes, et qui dans ce moment-ci est l'épée que porte l'officier russe.",
            "C'est l'arme blanche la plus terrible après la baïonnette, puisqu'elle réunit la pointe de l'épée au tranchant du sabre.",
        ]

    if number == 26:
        return [
            "PLAN",
            "des salles d'armes des régimens de cavalerie de la Garde impériale.",
            "Les salles d'armes doivent être vastes et former un carré long pareil à celui d'un manège; les fenêtres doivent être des deux côtés pour que le jour soit égal partout; il faut une galerie qui sépare le maître des tireurs pour qu'il puisse donner sa leçon sans être interrompu. Cette galerie doit être en face de la porte d'entrée, en travers de la salle, à cinq pieds de distance du mur, et doit avoir trois pieds de haut. De cette manière le maître, en donnant leçon, voit tout ce qui se passe dans sa salle et tous ceux qui y entrent.",
            "Il faut que chaque jour un escadron y soit exercé par tous les maîtres d'armes et prévôts du régiment, soit le matin ou le soir; que chaque premier du mois, ou tout autre jour, les tireurs de chaque escadron soient réunis, et que le Général du régiment, avec son état-major, soit présent aux assauts qui se feront;",
            "qu'il y ait un inspecteur choisi parmi les meilleurs maîtres d'armes de la ville, avec le titre de premier maître d'armes de la Garde impériale, pour désigner au Général quels sont ceux qu'il doit récompenser d'une prime. Il doit visiter quatre fois par mois les salles d'armes des différens régimens de la cavalerie de la garde, pour voir si les maîtres d'armes en sous-ordre font bien leur devoir.",
            "Les généraux des régimens doivent le seconder et faire punir ceux qu'il désignerait paresseux et n'exécutant pas ses ordres. Il faut que chaque maître d'armes du régiment ait rang de sergent-major, qu'il ait une plaque ou médaille sur le côté gauche de la poitrine, sur laquelle il y ait deux sabres en croix, et un numéro du rang qu'il a dans le régiment, c'est-à-dire s'il est premier, second, troisième ou quatrième maître d'armes.",
            "Il faut que chaque année les différens tireurs qui se sont le plus distingués dans chaque régiment soient réunis publiquement, pour qu'on en prenne ceux qui seront jugés capables d'être maîtres d'armes, et que leurs noms soient mis sous les yeux de Sa Majesté.",
        ]

    if number == 27:
        return [
            "De cette manière, le soldat ayant l'espérance de devenir maître d'armes travaillera beaucoup; en peu de temps il y aura une foule de bons tireurs dans la garde, et dans quelques années on pourra même fournir des maîtres dans toutes les divisions de cavalerie de l'armée.",
            "Le soldat russe est capable d'apprendre tout ce que l'on veut lui montrer; je viens de le prouver, puisqu'en moins de trois mois j'ai accoutumé des hommes à parer tous les coups qu'on pouvait leur porter, eux qui avaient ignoré qu'il fût même possible de se servir d'un sabre ou d'une palache autrement que pour frapper.",
        ]

    return cleaned


def wrap_line(text: str, font_name: str, font_size: int, max_width: float) -> list[str]:
    words = text.split()
    if not words:
        return [""]
    lines = [words[0]]
    for word in words[1:]:
        candidate = f"{lines[-1]} {word}"
        if stringWidth(candidate, font_name, font_size) <= max_width:
            lines[-1] = candidate
        else:
            lines.append(word)
    return lines


def write_pdf(text: str, output_path: Path) -> None:
    font_name = "Helvetica"
    arial_path = Path(r"C:\Windows\Fonts\arial.ttf")
    if arial_path.exists():
        pdfmetrics.registerFont(TTFont("ArialCustomV3", str(arial_path)))
        font_name = "ArialCustomV3"

    pdf = canvas.Canvas(str(output_path), pagesize=A4)
    pdf.setTitle("Transcription francaise v3 - feht-ychebnik-Valvil-19v")

    width, height = A4
    left_margin = 18 * mm
    right_margin = 18 * mm
    top_margin = 18 * mm
    bottom_margin = 18 * mm
    font_size = 10
    line_height = 13
    max_width = width - left_margin - right_margin
    y = height - top_margin

    pdf.setFont(font_name, font_size)
    for paragraph in text.splitlines():
        wrapped = wrap_line(paragraph, font_name, font_size, max_width)
        for line in wrapped:
            if y <= bottom_margin:
                pdf.showPage()
                pdf.setFont(font_name, font_size)
                y = height - top_margin
            pdf.drawString(left_margin, y, line)
            y -= line_height
        y -= line_height / 2

    pdf.save()


def main() -> None:
    text = INPUT_TXT.read_text(encoding="utf-8")
    pages = load_pages(text)

    blocks: list[str] = []
    for number, lines in pages:
        fixed = fix_page(number, lines)
        if not fixed:
            continue
        blocks.append("\n".join([f"[Page {number}]"] + fixed))

    final_text = "\n\n".join(blocks).strip()
    OUTPUT_TXT.write_text(final_text, encoding="utf-8")
    write_pdf(final_text, OUTPUT_PDF)

    print(OUTPUT_TXT)
    print(OUTPUT_PDF)
    print(f"pages kept: {len(blocks)}")


if __name__ == "__main__":
    main()
