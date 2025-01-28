# Technical Screen Task: Document Type Categorization

Add file type categorization to the document management system. Each document should be categorized based on its file extension into one of these types:
- IMAGE (.jpg, .png, .gif)
- DOCUMENT (.pdf, .doc, .txt)
- OTHER (everything else)

## Requirements

1. Update the Document model to include a `file_type` field
2. Modify document creation to automatically detect and set the file type

Run the test suite with `python tests.py` to check your changes.

## Example

A file named "report.pdf" should be categorized as "DOCUMENT" and displayed like: 