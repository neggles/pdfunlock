from pathlib import Path
from typing import Optional

from pikepdf import Pdf
import typer

from pdfunlock import __version__
from pdfunlock.console import console, err_console

app = typer.Typer()


def version_callback(value: bool):
    if value:
        console.print(f"{__package__} v{__version__}")
        raise typer.Exit()


@app.command()
def cli(
    input_file: Path = typer.Argument(
        ...,
        path_type=Path,
        exists=True,
        dir_okay=False,
        help="Source edit-locked PDF file",
    ),
    output_file: Optional[Path] = typer.Argument(
        None,
        path_type=Path,
        help="Destination PDF file (default: <input_file>-unlocked.pdf)",
    ),
    version: Optional[bool] = typer.Option(
        None, "--version", "-v", callback=version_callback, is_eager=True, help="Show version"
    ),
):
    """
    Main entrypoint for pdfunlock
    """
    if output_file is None:
        output_file = input_file.with_name(f"{input_file.stem}-unlocked{input_file.suffix}")
        console.log(f"No output path specified, using {output_file}")
    elif output_file.is_dir():
        output_file = output_file.joinpath(input_file.name)
        console.log(f"Output path is a directory, using {output_file}")

    remove_edit_password(input_file, output_file)
    raise typer.Exit()


def remove_edit_password(input_file: Path, output_file: Optional[Path] = None):
    console.log(f"Removing edit password from {input_file} to {output_file}")
    if input_file.resolve() == output_file.resolve():
        console.log("input and output paths are the same, will overwrite input file")
        overwrite = True
    else:
        overwrite = False

    try:
        with Pdf.open(input_file, allow_overwriting_input=overwrite) as src_pdf:
            console.log(f"Got {len(src_pdf.pages)} pages, saving to {output_file.name}...")
            with Pdf.new() as dst_pdf:
                dst_pdf.pages.extend(src_pdf.pages)
                dst_pdf.save(output_file)
        console.log("Done!")
    except Exception as e:
        err_console.print_exception(show_locals=True)
        raise typer.Exit(1)
