# 📄 PDF Summarizer & Quiz Generator

An intelligent agent-powered application that summarizes PDF documents and generates interactive quizzes from their content using the OpenAI Agents SDK and Streamlit.

## Here is the Project Link: https://ai-driven-development-30days-challenge.streamlit.app/

## ✨ Features

### 📝 PDF Summarization
- **Text Extraction**: Robust text extraction from PDFs using PyMuPDF
- **Multiple Summary Lengths**: Brief (100-200 words), Standard (200-500 words), Detailed (500-800 words)
- **Flexible Formatting**: Choose between paragraph or bullet point format
- **Smart Validation**: Handles file size limits, page limits, and content validation
- **Download Support**: Export summaries as text files

### 📊 Quiz Generation
- **Multiple Question Types**: MCQ, True/False, and Short Answer questions
- **Configurable Settings**: Adjust number of questions (3-15), difficulty level, and question types
- **Interactive Quiz Taking**: User-friendly interface for answering questions
- **Instant Feedback**: Automatic scoring with detailed explanations
- **Export Options**: Download quizzes as JSON and results as text files

### 🛡️ Error Handling
- File type validation (PDF only)
- File size limits (up to 10MB)
- Page limits (up to 50 pages)
- Minimum content requirements (100+ words)
- Password-protected PDF detection
- Scanned/image-only PDF detection
- Token limit handling with smart truncation

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- OpenAI API key
- pip (Python package manager)

### Installation

1. **Clone or navigate to the project directory:**
   ```bash
   cd Task-4
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment:**
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Set up environment variables:**
   - Copy `.env.example` to `.env`:
     ```bash
     copy .env.example .env
     ```
   - Edit `.env` and add your OpenAI API key:
     ```
     OPENAI_API_KEY=your_actual_api_key_here
     ```

### Running the Application

1. **Start the Streamlit app:**
   ```bash
   streamlit run app.py
   ```

2. **Open your browser:**
   - The app will automatically open at `http://localhost:8501`
   - If not, navigate to the URL shown in the terminal

## 📖 Usage Guide

### Step 1: Upload a PDF
1. Click the file uploader in the sidebar
2. Select a PDF file (max 10MB, 50 pages)
3. Wait for text extraction to complete

### Step 2: Generate Summary
1. Configure summary settings in the sidebar:
   - **Summary Length**: Brief, Standard, or Detailed
   - **Format**: Paragraphs or Bullets
2. Click "✨ Generate Summary" button
3. View the summary and download if needed

### Step 3: Generate Quiz
1. Configure quiz settings in the sidebar:
   - **Number of Questions**: 3-15 questions
   - **Question Types**: MCQ, True/False, Short Answer
   - **Difficulty Level**: Easy, Medium, or Hard
2. Click "🎯 Generate Quiz" button
3. Wait for quiz generation to complete

### Step 4: Take the Quiz
1. Answer all questions in the quiz
2. Click "✅ Submit Quiz" when done
3. View your score and detailed feedback
4. Download results if needed

### Step 5: Start Over (Optional)
- Click "🔄 Clear All & Start Over" to reset and upload a new PDF

## 🏗️ Project Structure

```
Task-4/
├── app.py                      # Main Streamlit application
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
├── .gitignore                 # Git ignore rules
├── README.md                  # This file
├── CLAUDE.md                  # Detailed specifications
├── utils/
│   ├── __init__.py           # Package initialization
│   ├── pdf_extractor.py      # PDF text extraction utility
│   └── agent.py              # OpenAI Agents SDK integration
```

## 🛠️ Technology Stack

- **[Streamlit](https://streamlit.io/)**: Web UI framework
- **[OpenAI Agents SDK](https://github.com/openai/openai-agents-python)**: Agent orchestration
- **[PyMuPDF (fitz)](https://pymupdf.readthedocs.io/)**: PDF text extraction
- **[Pydantic](https://docs.pydantic.dev/)**: Data validation
- **[Python-dotenv](https://pypi.org/project/python-dotenv/)**: Environment variable management

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
OPENAI_API_KEY=your_openai_api_key
```

### Customization

You can modify the following constants in the code:

**PDF Extraction Limits** (`utils/pdf_extractor.py`):
- `MAX_FILE_SIZE`: Default 10MB
- `MAX_PAGES`: Default 50 pages
- `MIN_WORD_COUNT`: Default 100 words

**Agent Configuration** (`utils/agent.py`):
- `model`: Default "gpt-4o" (can change to "gpt-3.5-turbo" for faster/cheaper processing)

## 📊 Example Workflow

1. **Upload** a research paper PDF (e.g., 15 pages, 5000 words)
2. **Generate** a detailed summary (500-800 words) in bullet format
3. **Create** a 10-question quiz with mixed question types (MCQ + True/False) at medium difficulty
4. **Take** the quiz and receive instant feedback
5. **Download** the summary and quiz results for future reference

## ⚠️ Limitations & Considerations

1. **PDF Requirements**:
   - Must contain extractable text (not scanned images)
   - Maximum 10MB file size
   - Maximum 50 pages processed
   - Minimum 100 words required

2. **API Usage**:
   - Requires OpenAI API key with credits
   - Costs depend on model usage (gpt-4o is more expensive than gpt-3.5-turbo)
   - Large documents consume more tokens

3. **Processing Time**:
   - Summary generation: 10-30 seconds
   - Quiz generation: 20-60 seconds
   - Time varies based on document length and settings

4. **Quiz Limitations**:
   - Short answer questions are marked as correct if answered (simplified evaluation)
   - For production use, implement more sophisticated answer validation

## 🐛 Troubleshooting

### Issue: "No module named 'agents'"
**Solution**: Install the OpenAI Agents SDK:
```bash
pip install openai-agents
```

### Issue: "No module named 'fitz'"
**Solution**: Install PyMuPDF:
```bash
pip install pymupdf
```

### Issue: "OpenAI API key not found"
**Solution**:
1. Create a `.env` file in the project root
2. Add: `OPENAI_API_KEY=your_key_here`
3. Restart the application

### Issue: "PDF is password-protected"
**Solution**: Unlock the PDF using a PDF reader and export an unlocked version

### Issue: "No text found in PDF"
**Solution**:
- The PDF may be scanned/image-only
- Use a PDF with extractable text or apply OCR first

### Issue: Application is slow
**Solution**:
- Use smaller PDFs
- Select "brief" summary length
- Reduce number of quiz questions
- Consider using "gpt-3.5-turbo" model instead of "gpt-4o"

## 🤝 Contributing

Suggestions and improvements are welcome! Areas for enhancement:

1. **OCR Support**: Add support for scanned PDFs
2. **Multi-language**: Support for non-English documents
3. **Advanced Scoring**: Implement semantic similarity for short answers
4. **Quiz Templates**: Add pre-defined quiz templates
5. **Export Formats**: Add PDF and DOCX export options
6. **History**: Save previous sessions and results

## 📄 License

This project is part of the AIDD Challenge Task-4.

## 🙏 Acknowledgments

- OpenAI for the Agents SDK
- Streamlit for the UI framework
- PyMuPDF for PDF processing capabilities

---

**Made with ❤️ using OpenAI Agents SDK & Streamlit**
