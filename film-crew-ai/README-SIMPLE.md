# Film Crew AI - Simple Setup Guide

## 🚀 Quick Start in 5 Minutes

### Step 1: Install Python Dependencies
```bash
pip install PyPDF2 python-docx chardet
```

### Step 2: Add Your Script
Place your screenplay in the `scripts` folder (create it if it doesn't exist)

### Step 3: Run the Program
```bash
python film_crew_ai_main.py scripts/your_script.txt
```

### Step 4: Get Your Prompts
Look in `output/[script_name]_[timestamp]/Veo3_Natural_Prompts/`

That's it! Copy any `.txt` file content and paste into Google Veo3.

## 📝 Example with Included Script

```bash
python film_crew_ai_main.py scripts/complex_script.txt
```

## 🆘 Common Issues

**"Module not found"**: Run `pip install PyPDF2 python-docx chardet`

**"File not found"**: Make sure your script is in the `scripts` folder

**"Python not found"**: Install Python 3.8+ from python.org

## 📁 File Structure

```
film-crew-ai/
├── scripts/              ← Put your screenplay here
├── output/               ← Find your prompts here
└── film_crew_ai_main.py  ← Run this file
```

## 🎬 Supported Formats

- `.txt` - Plain text
- `.pdf` - PDF documents  
- `.doc` - Word documents
- `.docx` - Word documents

## 💡 Script Format Example

```
INT. COFFEE SHOP - DAY

SARAH enters nervously.

SARAH
Is anyone here?

JAMES (V.O.)
I knew this day would come...
```

That's all you need to know! Run the example script first to test.