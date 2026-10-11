from klartext.adapters.pdf import strip_repeated_lines


def test_repeated_footer_is_removed_across_pages():
    pages = [
        "Zahlung bis 30.11.2026\nFooter AG Seite 1 von 2",
        "Betreibung folgt\nFooter AG Seite 2 von 2",
    ]
    result = strip_repeated_lines(pages)
    assert "Seite" not in "\n".join(result)
    assert "Zahlung bis 30.11.2026" in result[0]
    assert "Betreibung folgt" in result[1]


def test_single_page_is_left_untouched():
    pages = ["Zahlung bis 30.11.2026\nFooter AG Seite 1 von 1"]
    assert strip_repeated_lines(pages) == pages


def test_line_repeated_on_one_page_only_is_kept():
    pages = ["Total\nTotal\nBetrag 10", "Anderer Text"]
    assert "Total" in strip_repeated_lines(pages)[0]

def test_letterhead_repeated_in_signature_is_kept():
    pages = [
        "Steueramt Thurgau\nHerr Meier\nSteueramt Thurgau Seite 1/2",
        "Zahlung bis 15.12.2026\nSteueramt Thurgau\nSteueramt Thurgau Seite 2/2",
    ]
    result = strip_repeated_lines(pages)
    assert "Steueramt Thurgau" in result[0]
    assert "Steueramt Thurgau" in result[1]
    assert "Seite" not in "\n".join(result)
