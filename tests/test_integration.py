import builtins
import io
import json


def test_end_to_end_cli_with_manual_text(monkeypatch, mock_ai_pipeline, mock_spacy):
    """Simulate CLI choosing manual text entry and run full pipeline."""
    from flashcard_generator.main import main

    inputs = iter(["2", "This is a simple document. It has useful content."])

    def fake_input(prompt=""):
        try:
            return next(inputs)
        except StopIteration:
            return ""

    # capture stdout
    buf = io.StringIO()
    monkeypatch.setattr(builtins, "input", fake_input)
    monkeypatch.setattr("sys.stdout", buf)

    main()

    output = buf.getvalue()
    assert "Successfully extracted" in output
    assert "Generated" in output or "Processing" in output


def test_end_to_end_with_text_file(tmp_path, monkeypatch, mock_fitz, mock_easyocr, mock_ai_pipeline, mock_spacy):
    from flashcard_generator.main import main

    # Prepare a text file input
    text_file = tmp_path / "doc.txt"
    text_file.write_text("Sentence one. Sentence two. Sentence three.", encoding="utf-8")

    inputs = iter(["1", str(text_file)])

    def fake_input(prompt=""):
        try:
            return next(inputs)
        except StopIteration:
            return ""

    buf = io.StringIO()
    monkeypatch.setattr(builtins, "input", fake_input)
    monkeypatch.setattr("sys.stdout", buf)

    main()

    out = buf.getvalue()
    assert "Proceeding to flashcard generation pipeline" in out
    assert "Generated" in out or "Flashcards" in out


