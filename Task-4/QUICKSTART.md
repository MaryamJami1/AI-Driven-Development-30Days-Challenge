# Quick Start Guide

## Prerequisites

Before running the application, you need:

1. **Python 3.8+** installed
2. **OpenAI API Key** - Get one from [OpenAI Platform](https://platform.openai.com/api-keys)

## Installation Steps

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- `streamlit` - Web UI framework
- `openai-agents` - OpenAI Agents SDK
- `pymupdf` - PDF text extraction
- `pydantic` - Data validation
- `python-dotenv` - Environment variables

### 2. Configure API Key

Create a `.env` file in the project root:

```bash
OPENAI_API_KEY=sk-your-actual-api-key-here
```

**Important**: Never commit your `.env` file to version control!

### 3. Run the Application

```bash
streamlit run app.py
```

The app will open automatically in your browser at `http://localhost:8501`

## First Time Usage

1. **Upload a PDF** in the sidebar (max 10MB)
2. **Adjust Settings**:
   - Summary Length: Brief / Standard / Detailed
   - Summary Format: Paragraphs or Bullets
   - Number of Questions: 3-15
   - Question Types: MCQ, True/False, Short Answer
   - Difficulty: Easy / Medium / Hard
3. **Generate Summary** - Click the button and wait ~10-30 seconds
4. **Generate Quiz** - Click the button and wait ~20-60 seconds
5. **Take the Quiz** - Answer questions and submit for instant feedback

## Sample PDFs for Testing

You can test with any PDF that contains text. Good examples:
- Research papers
- Articles
- Reports
- E-books (non-DRM)
- Documentation

**Note**: Scanned PDFs (images) won't work as they require OCR.

## Troubleshooting

### Installation Issues

**Error**: `No module named 'agents'`
```bash
pip install openai-agents
```

**Error**: `No module named 'fitz'`
```bash
pip install pymupdf
```

### Runtime Issues

**Error**: "OpenAI API key not found"
- Create `.env` file with your API key
- Restart the application

**Error**: "Rate limit exceeded"
- You've hit OpenAI API rate limits
- Wait a few minutes and try again
- Consider upgrading your OpenAI plan

**Slow Performance**
- Use smaller PDFs (< 5MB, < 20 pages)
- Select "Brief" summary length
- Reduce number of quiz questions
- Consider using gpt-3.5-turbo (edit `utils/agent.py`, change `model="gpt-4o"` to `model="gpt-3.5-turbo"`)

## Cost Estimation

Approximate costs using GPT-4o:
- **Summary Generation**: $0.02-$0.10 per PDF (depending on length)
- **Quiz Generation**: $0.05-$0.20 per quiz (depending on number of questions)

Using gpt-3.5-turbo is ~10x cheaper but may produce lower quality outputs.

## Features Overview

### PDF Summarization
- Extracts text from PDF files
- Generates summaries in 3 lengths
- Supports bullet points or paragraphs
- Downloads summaries as text files

### Quiz Generation
- Creates interactive quizzes
- Multiple question types (MCQ, T/F, Short Answer)
- Configurable difficulty levels
- Instant scoring with explanations
- Downloads quizzes and results

### Error Handling
- File validation (size, type, content)
- Password-protected PDF detection
- Scanned PDF detection
- Minimum content requirements

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Check [CLAUDE.md](CLAUDE.md) for technical specifications
- Customize agent prompts in `utils/agent.py`
- Adjust limits in `utils/pdf_extractor.py`

## Support

For issues or questions:
- Check the [README.md](README.md) Troubleshooting section
- Review the code in `app.py`, `utils/pdf_extractor.py`, and `utils/agent.py`
- Verify your OpenAI API key is valid and has credits

---

Happy learning! 📚
