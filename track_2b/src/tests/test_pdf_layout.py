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
