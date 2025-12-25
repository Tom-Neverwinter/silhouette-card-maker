import os
import re
import glob
import math

import click
from utilities import Registration, CardSize, PaperSize, generate_pdf

front_directory = os.path.join('out', 'front')
back_directory = os.path.join('out', 'back')
double_sided_directory = os.path.join('out', 'double_sided')
output_directory = os.path.join('out', 'output')

default_output_path = os.path.join(output_directory, 'game.pdf')

@click.command()
@click.option("--front_dir_path", default=front_directory, show_default=True, help="The path to the directory containing the card fronts.")
@click.option("--back_dir_path", default=back_directory, show_default=True, help="The path to the directory containing one or more card backs.")
@click.option("--double_sided_dir_path", default=double_sided_directory, show_default=True, help="The path to the directory containing card backs for double-sided cards.")
@click.option("--output_path", default=default_output_path, show_default=True, help="The desired path to the output PDF.")
@click.option("--output_images", default=False, is_flag=True, help="Create images instead of a PDF.")
@click.option("--card_size", default=CardSize.STANDARD.value, type=click.Choice([t.value for t in CardSize], case_sensitive=False), show_default=True, help="The desired card size.")
@click.option("--paper_size", default=PaperSize.LETTER.value, type=click.Choice([t.value for t in PaperSize], case_sensitive=False), show_default=True, help="The desired paper size.")
@click.option("--registration", default=Registration.THREE.value, type=click.Choice([t.value for t in Registration], case_sensitive=False), show_default=True, help="The desired registration.")
@click.option("--only_fronts", default=False, is_flag=True, help="Only use the card fronts, exclude the card backs.")
@click.option("--crop", help="Crop the outer portion of front and double-sided images. Examples: 3mm, 0.125in, 6.5.")
@click.option("--extend_corners", default=0, type=click.IntRange(min=0), show_default=True, help="Reduce artifacts produced by rounded corners in card images.")
@click.option("--ppi", default=300, type=click.IntRange(min=0), show_default=True, help="Pixels per inch (PPI) when creating PDF.")
@click.option("--quality", default=75, type=click.IntRange(min=0, max=100), show_default=True, help="File compression. A higher value corresponds to better quality and larger file size.")
@click.option("--load_offset", default=False, is_flag=True, help="Apply saved offsets. See `offset_pdf.py` for more information.")
@click.option("--skip", type=click.IntRange(min=0), multiple=True, help="Skip a card based on its index. Useful for registration issues. Examples: 0, 4.")
@click.option("--name", help="Label each page of the PDF with a name.")
@click.version_option("1.5.1")

def cli(
    front_dir_path,
    back_dir_path,
    double_sided_dir_path,
    output_path,
    output_images,
    card_size,
    paper_size,
    registration,
    only_fronts,
    crop,
    extend_corners,
    ppi,
    quality,
    skip,
    load_offset,
    name
):
    try:
        generate_pdf(
            front_dir_path,
            back_dir_path,
            double_sided_dir_path,
            output_path,
            output_images,
            card_size,
            paper_size,
            registration,
            only_fronts,
            crop,
            extend_corners,
            ppi,
            quality,
            skip,
            load_offset,
            name
        )
    except Exception as e:
        click.secho(f"[PDF] ERROR: {e}", fg="red", err=True)
        raise

    # On success, report counts and approximate pages (support common image formats)
    front_files = []
    back_files = []

    for pattern in ("*.png", "*.jpg", "*.jpeg", "*.webp"):
        front_files.extend(glob.glob(os.path.join(front_dir_path, pattern)))
        if back_dir_path:
            back_files.extend(glob.glob(os.path.join(back_dir_path, pattern)))

    # Basic estimate: assume 9 cards per page (3x3) if possible
    cards_per_page = 9
    pages = math.ceil(len(front_files) / cards_per_page) if cards_per_page else 0

    click.secho(
        f"[PDF] Success: {len(front_files)} fronts, {len(back_files)} backs, approx {pages} pages.",
        fg="green",
    )
    click.echo(f"[PDF] Output: {output_path}")
    click.secho("[PDF] Complete.", fg="cyan")

if __name__ == '__main__':
    cli()