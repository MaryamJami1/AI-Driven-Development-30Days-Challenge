# PDF Summarizer and Quiz Generator Agent

Create an intelligent agent that can summarize PDF documents and generate interactive quizzes from their content.

## Tech Stack

*   **OpenAI Agents SDK**: For the core agent logic and framework. Use Context7 MCP to access up-to-date documentation.
*   **Streamlit**: To build the user interface for file uploads and displaying results.
*   **PyMuPDF (fitz)** or **pdfplumber**: For robust text extraction from PDF files (more reliable than PyPDF2).
*   **Context7 MCP**: Already connected for accessing OpenAI Agents SDK documentation during development.

## Core Requirements

### A. PDF Summarizer

#### User Flow:
1.  **User Uploads a PDF**: Streamlit file uploader (`st.file_uploader`) that accepts `.pdf` files.
2.  **Text Extraction**: Use PyMuPDF or pdfplumber to extract text from all pages.
    *   **File Size Limit**: Handle PDFs up to 10MB
    *   **Page Limit**: Process up to 50 pages (or warn user about processing time)
3.  **Content Validation**: Check that extracted text is at least 100 words. If not, show error message.
4.  **Generate Summary**:
    *   Pass extracted text to the agent
    *   Generate a concise, meaningful summary (200-500 words)
    *   Summary should capture key points, main ideas, and important details
5.  **Display Summary**:
    *   Use `st.container()` or `st.expander()` for clean presentation
    *   Show word count of original text vs summary
    *   Add a loading spinner (`st.spinner()`) during processing

#### Summary Options:
*   **Length Control**: Radio buttons or slider for summary length:
    *   Brief (100-200 words)
    *   Standard (200-500 words)
    *   Detailed (500-800 words)
*   **Format**: Bullet points or paragraph format

### B. Quiz Generator

#### User Flow:
1.  **Create Quiz Button**: After summary is displayed, show a "Generate Quiz" button.
2.  **Quiz Configuration** (optional sidebar controls):
    *   Number of questions: Slider (3-15 questions, default: 5)
    *   Question types:
        *   Multiple Choice Questions (MCQs) - 4 options each
        *   True/False
        *   Short Answer (open-ended)
        *   Mixed (combination of above)
    *   Difficulty level: Easy / Medium / Hard (optional)
3.  **Process Original Content**: Use the full extracted PDF text (NOT the summary) as context for quiz generation.
4.  **Generate Questions**:
    *   Agent creates questions based on key concepts from the PDF
    *   For MCQs: 1 correct answer + 3 plausible distractors
    *   Questions should cover different sections of the PDF
    *   Include clear, unambiguous wording
5.  **Display Quiz**:
    *   Show questions one at a time OR all at once (user preference)
    *   For MCQs: Use `st.radio()` for answer selection
    *   For True/False: Use `st.radio()` with two options
    *   For Short Answer: Use `st.text_area()`
6.  **Answer Key & Scoring**:
    *   Provide correct answers with brief explanations
    *   If interactive mode: Score user responses and show results
    *   Display score as percentage and feedback (e.g., "8/10 - Great job!")
    *   Show which questions were answered correctly/incorrectly

## State Management

Use Streamlit session state to manage:
*   `st.session_state.pdf_text`: Store extracted text
*   `st.session_state.summary`: Store generated summary
*   `st.session_state.quiz`: Store generated quiz questions and answers
*   `st.session_state.user_answers`: Track user's quiz responses
*   `st.session_state.quiz_submitted`: Track if quiz has been submitted

## Error Handling

Handle these scenarios gracefully:
1.  **Invalid File Type**: Only accept `.pdf` files
2.  **Corrupted PDF**: Show error message if text extraction fails
3.  **Password-Protected PDF**: Display error asking user to unlock the file
4.  **Scanned/Image-Only PDF**: Warn user that OCR is not supported (or implement OCR if feasible)
5.  **Empty or Insufficient Content**: Require minimum 100 words for processing
6.  **Token Limits**: If PDF text exceeds model limits (~50,000 tokens):
    *   Truncate intelligently (preserve beginning and end)
    *   OR implement chunking strategy
    *   Warn user that only partial content was processed

## Agent Architecture

### Agent Definition:
*   Create a single agent with two main capabilities:
    1.  **Summarization Tool**: Takes full text, returns structured summary
    2.  **Quiz Generation Tool**: Takes full text and parameters, returns quiz JSON

### Tool Specifications:
```python
# Summarizer Tool
Input: {text: str, length: str, format: str}
Output: {summary: str, word_count: int}

# Quiz Generator Tool
Input: {text: str, num_questions: int, question_types: list, difficulty: str}
Output: {
    questions: [
        {
            question: str,
            type: str,  # 'mcq', 'true_false', 'short_answer'
            options: list (for mcq),
            correct_answer: str,
            explanation: str
        }
    ]
}
```

## UI/UX Guidelines

### Layout:
*   **Sidebar**:
    *   File uploader
    *   Summary settings
    *   Quiz configuration options
    *   "Clear All" button to reset session
*   **Main Area**:
    *   Display uploaded file name and metadata (pages, word count)
    *   Summary section (collapsible)
    *   Quiz section (appears after quiz generation)
    *   Score/results section (after quiz submission)

### User Experience:
*   Show loading indicators for all agent operations
*   Display progress messages ("Extracting text...", "Generating summary...", "Creating quiz...")
*   Add tooltips/help text for configuration options
*   Include download buttons:
    *   Download summary as `.txt` or `.md`
    *   Download quiz as `.txt` or `.json`
    *   Download results/score report

### Visual Design:
*   Use Streamlit's color themes and components for consistency
*   Add icons where appropriate (📄 for PDF, 📝 for summary, 📊 for quiz)
*   Use `st.success()`, `st.error()`, `st.warning()` for user feedback
*   Consider using columns (`st.columns()`) for better layout

## Workflow States

1.  **Initial State**: Show file uploader and instructions
2.  **PDF Uploaded**: Display file info, show "Generate Summary" button
3.  **Summary Generated**: Display summary, show "Generate Quiz" button
4.  **Quiz Generated**: Display quiz questions with input fields, show "Submit Quiz" button
5.  **Quiz Submitted**: Display score, correct answers, and explanations
6.  **Reset Available**: "Start Over" button to clear session and upload new PDF

## Validation & Quality Checks

### For Summaries:
*   Verify summary is coherent and doesn't cut off mid-sentence
*   Ensure key topics from PDF are represented
*   Check that summary length matches user's requested length

### For Quizzes:
*   Verify all questions are clearly worded and unambiguous
*   Ensure MCQ options are distinct and plausible
*   Check that correct answers are actually correct
*   Validate that questions cover different parts of the document
*   Ensure explanations are helpful and reference PDF content

## Optional Enhancements

*   **Multi-language Support**: Detect PDF language and generate summary/quiz in same language
*   **Export Options**: Generate PDF report with summary and quiz
*   **History**: Save previous PDFs and their summaries in session
*   **Difficulty Analysis**: Show estimated difficulty level of quiz questions
*   **Time Tracking**: Optional timer for quiz-taking mode
*   **Quiz Templates**: Allow custom quiz templates (e.g., "Focus on definitions", "Conceptual questions only")
