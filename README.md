# Picvert

Picvert is a simple desktop image converter built with Python, Tkinter, and Pillow. It lets you batch-convert images, preview selected files, resize images, adjust output quality, and export to a chosen folder from a clean GUI.

## Features

- Batch convert multiple images at once
- Supports `PNG`, `JPEG`, `WEBP`, `BMP`, `TIFF`, `GIF`, `ICO`, and `HEIC`/`HEIF` (requires `pillow-heif`)
- Can scan extensionless/recovered files and convert the ones Pillow detects as images
- Preview selected images inside the app
- Resize images before export
- Adjust quality for `JPEG` and `WEBP`
- Track progress, success count, failure count, and ETA
- Light and dark theme toggle
- Windows app icon support with `app.ico`

## Requirements

- Python 3.10+ recommended
- `Pillow`
- `pillow-heif` (for HEIC/HEIF support)

## Project Files

- `picvert.py` - main Tkinter application
- `app.ico` - application icon
- `picvert.spec` - PyInstaller build configuration
- `dist/` - generated executable output
- `build/` - PyInstaller temporary build files

## Install Dependencies

Open PowerShell in the project folder and run:

```powershell
pip install pillow pyinstaller pillow-heif
```

## Run the App

```powershell
python picvert.py
```

If needed, you can also use:

```powershell
py picvert.py
```

## How to Use

1. Open Picvert.
2. Click `Add Images` or `Add Folder`.
   Enable `Include extensionless/recovered files when adding folders` first if your files have no extension or show as unknown file types in Windows.
3. Choose the output format.
4. Optionally enable resizing and enter width and height.
5. Choose the output folder.
6. Click `Convert Images`.

Converted files are saved with the `_converted` suffix.

## Build an EXE

Use PyInstaller from the project folder:

```powershell
py -m PyInstaller --onefile --windowed --icon=app.ico --add-data "app.ico;." picvert.py
```

The generated executable will be created at:

```powershell
dist\Picvert.exe
```

## Notes

- `Auto` output format detects the source image format, including for extensionless recovered files.
- Converting transparent images to `JPEG` removes transparency.
- The app is primarily set up for Windows.
