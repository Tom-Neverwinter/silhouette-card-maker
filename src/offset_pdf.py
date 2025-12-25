import os
import click
import pypdfium2 as pdfium

from utilities import load_saved_offset, offset_images, save_offset

output_directory = os.path.join('game', 'output')
default_output_pdf_path = os.path.join(output_directory, 'game.pdf')

@click.command()
@click.option("--pdf_path", default=default_output_pdf_path, help="The path of the input PDF.")
@click.option("--output_pdf_path", help="The desired path of the offset PDF.")
@click.option("-x", "--x_offset", type=float, help="The desired offset in the x-axis (mm, can be fractional).")
@click.option("-y", "--y_offset", type=float, help="The desired offset in the y-axis (mm, can be fractional).")
@click.option("-s", "--save", default=False, is_flag=True, help="Save the x and y offset values.")
@click.option("--ppi", default=300, type=click.IntRange(min=0), show_default=True, help="Pixels per inch (PPI) when creating PDF.")

def offset_pdf(pdf_path, output_pdf_path, x_offset, y_offset, save, ppi):
    new_x_offset = 0
    new_y_offset = 0

    saved_offset = load_saved_offset()
    if saved_offset is not None:
        new_x_offset = saved_offset.x_offset
        new_y_offset = saved_offset.y_offset

        click.secho(f"[OFFSET] Loaded saved offset: x={new_x_offset} mm, y={new_y_offset} mm", fg="cyan")

    # Check for new offset values
    if x_offset is not None:
        new_x_offset = x_offset

    if y_offset is not None:
        new_y_offset = y_offset

    click.echo(f"[OFFSET] Using offset: x={new_x_offset} mm, y={new_y_offset} mm (ppi={ppi})")

    # Save new offset
    if save:
        save_offset(new_x_offset, new_y_offset)
        click.secho("[OFFSET] Saved offset values.", fg="green")

    try:
        pdf = pdfium.PdfDocument(pdf_path)

        # Get all the raw page images from the PDF
        raw_images = []
        for page_number in range(len(pdf)):
            click.echo(f"[OFFSET] Rendering page {page_number + 1}")
            page = pdf.get_page(page_number)
            raw_images.append(page.render(ppi/72).to_pil())

        # Offset images
        final_images = offset_images(raw_images, new_x_offset, new_y_offset, ppi)

        # The default for output_pdf_path is the original path but with _offset.pdf appended to the end.
        if output_pdf_path is None:
            output_pdf_path = f"{pdf_path.removesuffix('.pdf')}_offset.pdf"

        final_images[0].save(output_pdf_path, save_all=True, append_images=final_images[1:], resolution=ppi, speed=0, subsampling=0, quality=100)
        click.secho(f"[OFFSET] Success: Offset PDF created at {output_pdf_path}", fg="green")
    except FileNotFoundError as e:
        click.secho(f"[OFFSET] ERROR: Cannot offset nonexistent PDF: {e}", fg="red", err=True)
    except Exception as e:
        click.secho(f"[OFFSET] ERROR: {e}", fg="red", err=True)
        raise

if __name__ == '__main__':
    offset_pdf()