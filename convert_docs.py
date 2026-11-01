from pathlib import Path
import win32com.client

BASE_DIR = Path(__file__).resolve().parent
RAW_DIR = BASE_DIR / "data" / "raw"

word = win32com.client.Dispatch("Word.Application")
word.Visible = False

converted = 0
skipped = 0
failed = 0

try:
    for doc_file in RAW_DIR.rglob("*.doc"):
        if doc_file.name.startswith("~$"):
            continue

        output_file = doc_file.with_suffix(".docx")

        if output_file.exists():
            print(f"SKIPPED: {doc_file.name} (DOCX already exists)")
            skipped += 1
            continue

        try:
            print(f"Converting: {doc_file.name}")

            document = word.Documents.Open(str(doc_file.resolve()))
            document.SaveAs2(
                str(output_file.resolve()),
                FileFormat=16
            )
            document.Close()

            converted += 1
            print(f"SUCCESS: {output_file.name}")

        except Exception as error:
            failed += 1
            print(f"FAILED: {doc_file.name} - {error}")

finally:
    word.Quit()

print("\n========== SUMMARY ==========")
print(f"Converted: {converted}")
print(f"Skipped: {skipped}")
print(f"Failed: {failed}")