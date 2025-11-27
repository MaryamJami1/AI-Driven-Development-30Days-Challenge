"""
PDF Summarizer and Quiz Generator
A Streamlit application for summarizing PDFs and generating interactive quizzes.
"""

import streamlit as st
import json
import os
from dotenv import load_dotenv
from utils.pdf_extractor import PDFExtractor
from utils.agent import generate_summary_sync, generate_quiz_sync

# Load environment variables
load_dotenv()

# =============================================================================
# Page Configuration
# =============================================================================

st.set_page_config(
    page_title="PDF Summarizer & Quiz Generator",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# Session State Initialization
# =============================================================================

def initialize_session_state():
    """Initialize all session state variables."""
    if 'pdf_text' not in st.session_state:
        st.session_state.pdf_text = None
    if 'pdf_metadata' not in st.session_state:
        st.session_state.pdf_metadata = {}
    if 'summary' not in st.session_state:
        st.session_state.summary = None
    if 'summary_data' not in st.session_state:
        st.session_state.summary_data = {}
    if 'quiz' not in st.session_state:
        st.session_state.quiz = None
    if 'user_answers' not in st.session_state:
        st.session_state.user_answers = {}
    if 'quiz_submitted' not in st.session_state:
        st.session_state.quiz_submitted = False
    if 'quiz_score' not in st.session_state:
        st.session_state.quiz_score = None

initialize_session_state()

# =============================================================================
# Helper Functions
# =============================================================================

def reset_session():
    """Clear all session state and start over."""
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    initialize_session_state()
    st.rerun()


def calculate_score(quiz_questions, user_answers):
    """Calculate quiz score based on user answers."""
    if not quiz_questions or not user_answers:
        return None

    correct = 0
    total = len(quiz_questions)
    results = []

    for i, question in enumerate(quiz_questions):
        user_answer = user_answers.get(i, '')
        correct_answer = question['correct_answer']

        # For MCQ and True/False, exact match
        if question['type'] in ['mcq', 'true_false']:
            is_correct = user_answer == correct_answer
        else:
            # For short answer, we'll mark as correct if answered (simplified)
            # In production, you'd want more sophisticated evaluation
            is_correct = bool(user_answer.strip())

        if is_correct:
            correct += 1

        results.append({
            'question_num': i + 1,
            'correct': is_correct,
            'user_answer': user_answer,
            'correct_answer': correct_answer,
            'explanation': question.get('explanation', '')
        })

    score_percentage = (correct / total) * 100

    return {
        'correct': correct,
        'total': total,
        'percentage': score_percentage,
        'results': results
    }


def get_feedback_message(percentage):
    """Get encouraging feedback based on score percentage."""
    if percentage >= 90:
        return "🌟 Excellent work!"
    elif percentage >= 75:
        return "✨ Great job!"
    elif percentage >= 60:
        return "👍 Good effort!"
    elif percentage >= 50:
        return "📚 Keep practicing!"
    else:
        return "💪 Don't give up, try again!"


# =============================================================================
# Sidebar
# =============================================================================

with st.sidebar:
    st.title("📄 PDF Summarizer & Quiz Generator")
    st.markdown("---")

    # File Upload
    st.subheader("1️⃣ Upload PDF")
    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type=['pdf'],
        help="Upload a PDF document (max 10MB, 50 pages)"
    )

    # Summary Settings
    st.markdown("---")
    st.subheader("2️⃣ Summary Settings")

    summary_length = st.select_slider(
        "Summary Length",
        options=['brief', 'standard', 'detailed'],
        value='standard',
        help="Brief: 100-200 words | Standard: 200-500 words | Detailed: 500-800 words"
    )

    summary_format = st.radio(
        "Format",
        options=['paragraphs', 'bullets'],
        help="Choose between paragraph format or bullet points"
    )

    # Quiz Settings
    st.markdown("---")
    st.subheader("3️⃣ Quiz Settings")

    num_questions = st.slider(
        "Number of Questions",
        min_value=3,
        max_value=15,
        value=5,
        help="How many questions to generate"
    )

    question_types = st.multiselect(
        "Question Types",
        options=['mcq', 'true_false', 'short_answer'],
        default=['mcq', 'true_false'],
        help="Select one or more question types"
    )

    difficulty = st.select_slider(
        "Difficulty Level",
        options=['easy', 'medium', 'hard'],
        value='medium'
    )

    # Clear Button
    st.markdown("---")
    if st.button("🔄 Clear All & Start Over", use_container_width=True):
        reset_session()

    # Info
    st.markdown("---")
    st.info("""
    **How to use:**
    1. Upload a PDF file
    2. Adjust summary settings
    3. Generate summary
    4. Configure quiz options
    5. Generate and take quiz
    """)

# =============================================================================
# Main Content Area
# =============================================================================

st.title("📄 PDF Summarizer & Quiz Generator")
st.markdown("Upload a PDF document to generate summaries and interactive quizzes.")

# =============================================================================
# Step 1: PDF Upload and Text Extraction
# =============================================================================

if uploaded_file is not None:
    # Check if this is a new file
    if st.session_state.pdf_text is None or st.session_state.pdf_metadata.get('filename') != uploaded_file.name:

        # Clear all previous data when new file is uploaded
        st.session_state.pdf_text = None
        st.session_state.pdf_metadata = {}
        st.session_state.summary = None
        st.session_state.summary_data = {}
        st.session_state.quiz = None
        st.session_state.user_answers = {}
        st.session_state.quiz_submitted = False
        st.session_state.quiz_score = None

        with st.spinner("📖 Extracting text from PDF..."):
            # Read file data
            file_data = uploaded_file.read()

            # Validate PDF
            validation = PDFExtractor.validate_pdf(file_data, uploaded_file.name)

            if not validation['valid']:
                st.error(f"❌ {validation['error']}")
            else:
                # Extract text
                extraction_result = PDFExtractor.extract_text(file_data)

                if extraction_result['success']:
                    # Store in session state
                    st.session_state.pdf_text = extraction_result['text']
                    st.session_state.pdf_metadata = {
                        'filename': uploaded_file.name,
                        'page_count': extraction_result['page_count'],
                        'word_count': extraction_result['word_count']
                    }

                    # Check for truncation
                    truncation_result = PDFExtractor.truncate_text(extraction_result['text'])
                    if truncation_result['truncated']:
                        st.session_state.pdf_text = truncation_result['text']
                        st.warning("⚠️ Document was truncated due to length. Processing partial content.")

                    if extraction_result.get('warning'):
                        st.warning(f"⚠️ {extraction_result['warning']}")

                    st.success("✅ Text extracted successfully!")
                else:
                    st.error(f"❌ {extraction_result['error']}")

# Display PDF metadata
if st.session_state.pdf_text:
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📄 Filename", st.session_state.pdf_metadata['filename'])
    with col2:
        st.metric("📑 Pages", st.session_state.pdf_metadata['page_count'])
    with col3:
        st.metric("📝 Words", f"{st.session_state.pdf_metadata['word_count']:,}")

    # =============================================================================
    # Step 2: Generate Summary
    # =============================================================================

    st.markdown("---")
    st.subheader("📝 Document Summary")

    if st.session_state.summary is None:
        if st.button("✨ Generate Summary", type="primary", use_container_width=True):
            with st.spinner("🤖 Generating summary..."):
                summary_result = generate_summary_sync(
                    text=st.session_state.pdf_text,
                    length=summary_length,
                    format_type=summary_format
                )

                if summary_result['success']:
                    st.session_state.summary = summary_result['summary']
                    st.session_state.summary_data = summary_result
                    st.rerun()
                else:
                    st.error(f"❌ {summary_result['error']}")
    else:
        # Display summary
        with st.expander("📋 View Summary", expanded=True):
            st.markdown(st.session_state.summary)

            col1, col2 = st.columns(2)
            with col1:
                st.caption(f"Summary Word Count: {st.session_state.summary_data['word_count']}")
            with col2:
                # Download button for summary
                st.download_button(
                    label="⬇️ Download Summary",
                    data=st.session_state.summary,
                    file_name=f"{st.session_state.pdf_metadata['filename']}_summary.txt",
                    mime="text/plain"
                )

        # =============================================================================
        # Step 3: Generate Quiz
        # =============================================================================

        st.markdown("---")
        st.subheader("📊 Interactive Quiz")

        if st.session_state.quiz is None:
            if st.button("🎯 Generate Quiz", type="primary", use_container_width=True):
                if not question_types:
                    st.warning("⚠️ Please select at least one question type.")
                else:
                    with st.spinner("🤖 Creating quiz questions..."):
                        quiz_result = generate_quiz_sync(
                            text=st.session_state.pdf_text,
                            num_questions=num_questions,
                            question_types=question_types,
                            difficulty=difficulty
                        )

                        if quiz_result['success']:
                            st.session_state.quiz = quiz_result['questions']
                            st.session_state.quiz_submitted = False
                            st.session_state.user_answers = {}
                            st.rerun()
                        else:
                            st.error(f"❌ {quiz_result['error']}")
        else:
            # Display quiz
            if not st.session_state.quiz_submitted:
                st.info("📝 Answer the questions below and click 'Submit Quiz' when done.")

                # Display questions
                for i, question in enumerate(st.session_state.quiz):
                    with st.container():
                        st.markdown(f"**Question {i+1}:** {question['question']}")

                        if question['type'] == 'mcq':
                            answer = st.radio(
                                "Select your answer:",
                                options=question['options'],
                                key=f"q_{i}",
                                index=None
                            )
                            if answer:
                                st.session_state.user_answers[i] = answer

                        elif question['type'] == 'true_false':
                            answer = st.radio(
                                "Select your answer:",
                                options=['True', 'False'],
                                key=f"q_{i}",
                                index=None
                            )
                            if answer:
                                st.session_state.user_answers[i] = answer

                        elif question['type'] == 'short_answer':
                            answer = st.text_area(
                                "Your answer:",
                                key=f"q_{i}",
                                height=100
                            )
                            if answer:
                                st.session_state.user_answers[i] = answer

                        st.markdown("---")

                # Submit button
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ Submit Quiz", type="primary", use_container_width=True):
                        if len(st.session_state.user_answers) < len(st.session_state.quiz):
                            st.warning("⚠️ Please answer all questions before submitting.")
                        else:
                            st.session_state.quiz_score = calculate_score(
                                st.session_state.quiz,
                                st.session_state.user_answers
                            )
                            st.session_state.quiz_submitted = True
                            st.rerun()
                with col2:
                    # Download quiz as JSON
                    quiz_json = json.dumps(st.session_state.quiz, indent=2)
                    st.download_button(
                        label="⬇️ Download Quiz",
                        data=quiz_json,
                        file_name=f"{st.session_state.pdf_metadata['filename']}_quiz.json",
                        mime="application/json"
                    )

            else:
                # Display results
                score = st.session_state.quiz_score
                feedback = get_feedback_message(score['percentage'])

                st.success(f"""
                ### {feedback}
                **Score: {score['correct']}/{score['total']} ({score['percentage']:.1f}%)**
                """)

                # Display detailed results
                st.subheader("📊 Detailed Results")

                for result in score['results']:
                    with st.expander(
                        f"Question {result['question_num']}: "
                        f"{'✅ Correct' if result['correct'] else '❌ Incorrect'}"
                    ):
                        question = st.session_state.quiz[result['question_num'] - 1]
                        st.markdown(f"**Question:** {question['question']}")
                        st.markdown(f"**Your Answer:** {result['user_answer']}")

                        if not result['correct']:
                            st.markdown(f"**Correct Answer:** {result['correct_answer']}")

                        st.info(f"**Explanation:** {result['explanation']}")

                # Action buttons
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🔄 Generate New Quiz", use_container_width=True):
                        st.session_state.quiz = None
                        st.session_state.user_answers = {}
                        st.session_state.quiz_submitted = False
                        st.session_state.quiz_score = None
                        st.rerun()
                with col2:
                    # Download results
                    results_text = f"""Quiz Results
{'='*50}
Score: {score['correct']}/{score['total']} ({score['percentage']:.1f}%)
{feedback}

{'='*50}
Detailed Results:
{'='*50}

"""
                    for result in score['results']:
                        question = st.session_state.quiz[result['question_num'] - 1]
                        results_text += f"""
Question {result['question_num']}: {'✓' if result['correct'] else '✗'}
{question['question']}
Your Answer: {result['user_answer']}
Correct Answer: {result['correct_answer']}
Explanation: {result['explanation']}

{'-'*50}
"""

                    st.download_button(
                        label="⬇️ Download Results",
                        data=results_text,
                        file_name=f"{st.session_state.pdf_metadata['filename']}_results.txt",
                        mime="text/plain"
                    )

else:
    # Initial state - no PDF uploaded
    st.info("👈 Please upload a PDF file from the sidebar to get started.")

    st.markdown("""
    ### ✨ Features

    **📝 PDF Summarization**
    - Extract text from PDF documents
    - Generate summaries in multiple lengths (brief, standard, detailed)
    - Choose between paragraph or bullet point format
    - Download summaries as text files

    **📊 Quiz Generation**
    - Create custom quizzes based on PDF content
    - Multiple question types: MCQ, True/False, Short Answer
    - Adjustable difficulty levels
    - Interactive quiz taking with instant feedback
    - Download quizzes and results

    ### 🚀 How to Use

    1. **Upload** a PDF document (max 10MB, 50 pages)
    2. **Configure** summary and quiz settings in the sidebar
    3. **Generate** a summary of your document
    4. **Create** an interactive quiz
    5. **Take** the quiz and see your results
    6. **Download** summaries, quizzes, and results

    ### 📋 Requirements

    - PDF files must contain extractable text
    - Minimum 100 words required
    - Scanned PDFs (images) are not supported
    """)

# =============================================================================
# Footer
# =============================================================================

st.markdown("---")
st.caption("Built with OpenAI Agents SDK & Streamlit | Made with ❤️")
