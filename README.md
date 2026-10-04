# Image Tools

A batch image toolkit for Windows: resize, compress, convert and rename images with drag & drop.

> **Download:** grab the latest `ImageResizer.exe` from the [Releases](https://github.com/eazyfixgr/image-tools/releases) page. No installation required.

## Features

- Drag & drop support (tkinterdnd2)
- Batch resize by width/height or percentage
- Compression and format conversion (JPG, PNG, WEBP…)
- Batch rename
- Simple, fast tkinter interface

## Getting started (run from source)

```bash
python -m pip install -r requirements.txt
python image_resizer.py
```

## Build a standalone EXE

```bash
python -m pip install pyinstaller
python -m PyInstaller --onefile --windowed --collect-all tkinterdnd2 --name ImageResizer image_resizer.py
```

The executable is created in `dist/ImageResizer.exe`.

## License

Released under the [MIT License](LICENSE).

---

# Image Tools (Ελληνικά)

Εργαλείο μαζικής επεξεργασίας εικόνων: αλλαγή μεγέθους, συμπίεση, μετατροπή μορφής και μετονομασία με drag & drop.

> **Λήψη:** κατεβάστε το `ImageResizer.exe` από τη σελίδα [Releases](https://github.com/eazyfixgr/image-tools/releases).

## Δυνατότητες

- Υποστήριξη drag & drop
- Μαζική αλλαγή μεγέθους (πλάτος/ύψος ή ποσοστό)
- Συμπίεση και μετατροπή μορφής (JPG, PNG, WEBP…)
- Μαζική μετονομασία
