"""Text cleaning and identifiers. PDF parsing itself is checked on the real corpus."""

from pathlib import Path

from rag_assistant.extract import clean_text, make_doc_id


def test_doc_id_keeps_corpus_slugs_and_strips_accents():
    assert make_doc_id(Path("data/raw/windows10_vbs.pdf")) == "windows10_vbs"
    assert make_doc_id(Path("Système Été.pdf")) == "systeme_ete"


def test_clean_text_drops_repeated_lines_with_their_page_number():
    text = "Contenu utile\n8 – GUIDE DE SECURITE"
    assert clean_text(text, {"guide de securite"}) == "Contenu utile"


def test_clean_text_joins_hyphenated_words_only():
    assert clean_text("la sécu-\nrité", set()) == "la sécurité"
    assert clean_text("Device-\nGuard", set()) == "Device-\nGuard"


def test_clean_text_keeps_measure_numbers_but_drops_page_numbers():
    assert clean_text("1414\nTitre\n8\nIdentifier\n15", set()) == "Titre\n8\nIdentifier"


def test_clean_text_normalises_ligatures_bullets_and_decorative_dots():
    assert clean_text(".\nLa conﬁguration\n.\n>>\nun point", set()) == "La configuration\n- un point"


def test_clean_text_keeps_paragraph_breaks():
    assert clean_text("un  deux\n\n\n\ntrois", set()) == "un deux\n\ntrois"
