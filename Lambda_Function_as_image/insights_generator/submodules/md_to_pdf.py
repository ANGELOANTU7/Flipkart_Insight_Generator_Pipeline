import markdown
import pdfkit

def md_to_pdf(md_content, pdf_file_path):
    """
    Convert a Markdown string to a PDF file.

    Parameters:
        md_content (str): Markdown content as a string.
        pdf_file_path (str): Path to the output PDF file.
    """
    try:
        # Convert Markdown to HTML
        html_content = markdown.markdown(md_content)

        # Convert HTML to PDF
        pdfkit.from_string(html_content, pdf_file_path)

        print(f"PDF successfully created at: {pdf_file_path}")
    except Exception as e:
        print(f"Error during conversion: {e}")

