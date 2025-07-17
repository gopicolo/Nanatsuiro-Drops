
# Nanatsuiro★Drops Text Tool

A pair of Python scripts for extracting, editing, and repacking in-game text from the **PC version of Nanatsuiro★Drops**.  
This tool was created for translation purposes, but may also work with other visual novels using the same engine.

---

## 💡 Features

- 📤 **Dump script** that extracts dialogue lines from `textdata.dat` based on pointers from `scenario.dat`.
- 📥 **Repack script** that reinserts translated text into `textdata.dat`, updating `scenario.dat` if the new strings are longer.
- 🧠 Automatic offset tracking and preservation of Shift-JIS encoding.
- ✅ Safe replacement of strings with pointer redirection when needed.

---

## 📁 File Structure

```
project/
│
├── input/
│   ├── textdata.dat        # Original binary with Shift-JIS strings
│   └── scenario.dat        # Pointer table to strings inside textdata.dat
│
├── output/
│   └── text_with_pointers.txt   # Extracted text ready for translation
│
├── modified/
│   ├── textdata.dat        # Modified binary with translated strings
│   └── scenario.dat        # Pointer table updated to match relocated strings
│
├── dump.py
├── repack.py
└── README.md
```

---

## 🔧 Usage

### 1. Extract (dump)
```bash
python dump.py
```
This will read `scenario.dat` and `textdata.dat` from the `input/` folder and create a translation-ready file at:
```
output/text_with_pointers.txt
```

Each block will look like:
```
//=========== STRING 1 @0x27AC ===========//
Hello there! Are you okay?
```

### 2. Translate

Edit `text_with_pointers.txt` using any text editor.  
Preserve the `//=========== STRING X @0xOFFSET ===========//` lines, as they indicate where each string belongs.

- Line breaks (`\n`) are supported.
- Be mindful of Shift-JIS encoding (no emoji or uncommon Unicode).

### 3. Repack

After editing, run:
```bash
python repack.py
```

This will:
- Insert translated strings back into `textdata.dat`.
- Replace in-place if the string fits.
- Append at the end if the string is larger, and **update all corresponding pointers** in `scenario.dat`.

The new files will be saved in:
```
modified/textdata.dat
modified/scenario.dat
```

---

## 🧪 Tested on

- 🖼️ **Nanatsuiro★Drops** (PC)
- May also be compatible with other games using the same script structure or engine.

---

## 🛠️ Requirements

- Python 3.6+
- Works on Windows, Linux, and Mac (cross-platform)

---

## 📜 License

MIT License.  
Created by [gopicolo](https://github.com/gopicolo).
