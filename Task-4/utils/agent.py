"""OpenAI Agents SDK integration for PDF summarization and quiz generation."""

import asyncio
import os
from typing import List, Literal, Optional
from pydantic import BaseModel, Field
from agents import Agent, Runner
from agents.models.openai_chatcompletions import OpenAIChatCompletionsModel
from openai import AsyncOpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


# =============================================================================
# Pydantic Models for Structured Outputs
# =============================================================================

class SummaryOutput(BaseModel):
    """Structured output for document summary."""
    summary: str = Field(description="The generated summary of the document")
    word_count: int = Field(description="Number of words in the summary")
    key_topics: List[str] = Field(description="List of key topics covered in the document")


class QuizQuestion(BaseModel):
    """Structured output for a single quiz question."""
    question: str = Field(description="The question text")
    type: Literal['mcq', 'true_false', 'short_answer'] = Field(description="Type of question")
    options: Optional[List[str]] = Field(
        default=None,
        description="List of 4 options for MCQ (first option is correct), or 2 options for True/False"
    )
    correct_answer: str = Field(description="The correct answer")
    explanation: str = Field(description="Brief explanation of why this is the correct answer")


class QuizOutput(BaseModel):
    """Structured output for quiz generation."""
    questions: List[QuizQuestion] = Field(description="List of generated quiz questions")


# =============================================================================
# Agent Configuration
# =============================================================================

gemini_api_key = os.getenv("GEMINI_API_KEY")
gemini_base_url = os.getenv("Base_URL")

external_client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url=gemini_base_url
)

configured_model = OpenAIChatCompletionsModel(
    model = 'gemini-2.5-flash',
    openai_client = external_client
)

def create_summarizer_agent() -> Agent:
    """
    Create an agent specialized in document summarization.

    Returns:
        Agent configured for summarization tasks
    """
    agent = Agent(
        name="PDF Summarizer",
        instructions="""You are an expert document summarizer. Your role is to:
        1. Read and understand the provided document text
        2. Identify the main topics, key points, and important details
        3. Generate a clear, concise, and coherent summary
        4. Ensure the summary captures the essence of the document
        5. Follow the specified length and format requirements
        6. Do not cut off mid-sentence - complete all thoughts

        When creating summaries:
        - For BRIEF summaries (100-200 words): Focus on the absolute main points only
        - For STANDARD summaries (200-500 words): Cover main topics with moderate detail
        - For DETAILED summaries (500-800 words): Include comprehensive coverage with examples

        For BULLET format: Use clear bullet points with one main idea per bullet
        For PARAGRAPH format: Write flowing, connected paragraphs
        """,
        model=configured_model
    )
    return agent


def create_quiz_agent() -> Agent:
    """
    Create an agent specialized in quiz generation.

    Returns:
        Agent configured for quiz generation tasks
    """
    agent = Agent(
        name="Quiz Generator",
        instructions="""You are an expert quiz creator. Your role is to:
        1. Analyze the document content thoroughly
        2. Identify key concepts, facts, and important information
        3. Create well-structured questions that test comprehension
        4. Ensure questions cover different parts of the document
        5. Make questions clear, unambiguous, and educational

        Question Guidelines:
        - MCQ (Multiple Choice): Create 1 correct answer and 3 plausible but incorrect distractors
        - True/False: Create statements that are clearly true or false based on the document
        - Short Answer: Ask questions that require understanding, not just memorization

        Quality Standards:
        - Questions should be clear and unambiguous
        - Options should be distinct and not overlapping (for MCQ)
        - Correct answers must be verifiable from the document
        - Explanations should reference specific content from the document
        - Avoid trick questions or overly technical language
        - Difficulty should match the requested level
        """,
        model=configured_model
    )
    return agent


# =============================================================================
# Summarization Functions
# =============================================================================

async def generate_summary(
    text: str,
    length: Literal['brief', 'standard', 'detailed'] = 'standard',
    format_type: Literal['bullets', 'paragraphs'] = 'paragraphs'
) -> SummaryOutput:
    """
    Generate a summary of the provided text.

    Args:
        text: The text to summarize
        length: Desired summary length (brief, standard, detailed)
        format_type: Output format (bullets or paragraphs)

    Returns:
        SummaryOutput with the generated summary
    """
    # Define word count ranges
    length_specs = {
        'brief': '100-200',
        'standard': '200-500',
        'detailed': '500-800'
    }

    # Create summarizer agent
    agent = create_summarizer_agent()

    # Construct prompt
    format_instruction = (
        "Format the summary as clear bullet points, one main idea per bullet."
        if format_type == 'bullets'
        else "Format the summary as flowing, well-connected paragraphs."
    )

    prompt = f"""Please summarize the following document.

**Requirements:**
- Length: {length_specs[length]} words ({length})
- Format: {format_instruction}
- Extract and list the key topics covered

**Document Text:**
{text}

**Output Format:**
Provide:
1. The summary (following the length and format requirements)
2. Word count of your summary
3. List of key topics (3-7 topics)

Ensure the summary is complete and doesn't cut off mid-sentence."""

    # Run agent
    result = await Runner.run(agent, input=prompt)

    # Parse the response - the agent will provide structured text
    summary_text = result.final_output
    word_count = len(summary_text.split())

    # Extract key topics from the summary (simple approach)
    # In a real implementation, the agent could return structured data
    key_topics = ["Document Analysis"]  # Placeholder

    return SummaryOutput(
        summary=summary_text,
        word_count=word_count,
        key_topics=key_topics
    )


# =============================================================================
# Quiz Generation Functions
# =============================================================================

async def generate_quiz(
    text: str,
    num_questions: int = 5,
    question_types: List[str] = None,
    difficulty: Literal['easy', 'medium', 'hard'] = 'medium'
) -> QuizOutput:
    """
    Generate a quiz based on the provided text.

    Args:
        text: The text to generate quiz from
        num_questions: Number of questions to generate
        question_types: List of question types to include
        difficulty: Difficulty level of questions

    Returns:
        QuizOutput with the generated questions
    """
    if question_types is None:
        question_types = ['mcq', 'true_false', 'short_answer']

    # Create quiz agent
    agent = create_quiz_agent()

    # Construct prompt
    types_description = ", ".join(question_types)

    prompt = f"""Create a quiz with EXACTLY {num_questions} questions based on the following document.

**Requirements:**
- Generate ALL {num_questions} questions
- Question types to use: {types_description}
- Difficulty level: {difficulty}
- Mix the question types if multiple types are specified
- Cover different parts of the document

**Document Text:**
{text}

**CRITICAL: You MUST generate ALL {num_questions} questions using this EXACT format for EACH question:**

QUESTION 1: [Write the first question here]
TYPE: mcq
OPTIONS: A) first option | B) second option | C) third option | D) fourth option
ANSWER: A
EXPLANATION: [Why A is correct with reference to the document]

===NEXT===

QUESTION 2: [Write the second question here]
TYPE: true_false
OPTIONS: True | False
ANSWER: True
EXPLANATION: [Why this is true with reference to the document]

===NEXT===

[Continue this pattern for ALL {num_questions} questions]

**IMPORTANT NOTES:**
- Use "===NEXT===" to separate each question
- For TYPE, use exactly: mcq, true_false, or short_answer
- For MCQ, provide exactly 4 options separated by " | "
- For True/False, use exactly: "True | False"
- For Short Answer, leave OPTIONS blank
- Generate ALL {num_questions} questions before stopping"""

    # Run agent
    result = await Runner.run(agent, input=prompt)

    # Parse the response into structured questions
    quiz_text = result.final_output
    questions = []

    # Split by question separator
    question_blocks = quiz_text.split('===NEXT===')

    for block in question_blocks:
        if not block.strip():
            continue

        lines = [line.strip() for line in block.strip().split('\n') if line.strip()]

        if len(lines) < 3:  # At least QUESTION, TYPE, and ANSWER
            continue

        # Initialize variables
        question_text = ""
        q_type = "mcq"
        options = []
        correct_answer = ""
        explanation = ""

        # Parse each line
        for line in lines:
            if line.startswith("QUESTION"):
                # Extract question text after the colon
                if ":" in line:
                    question_text = line.split(":", 1)[1].strip()
                else:
                    question_text = line
            elif line.startswith("TYPE:"):
                q_type = line.split(":", 1)[1].strip().lower()
            elif line.startswith("OPTIONS:"):
                opts_text = line.split(":", 1)[1].strip()
                if "|" in opts_text:
                    options = [opt.strip() for opt in opts_text.split("|")]
                    # Clean up option labels (A), B), etc.)
                    cleaned_options = []
                    for opt in options:
                        if ")" in opt:
                            # Remove "A)" or "A." prefix
                            cleaned = opt.split(")", 1)[1].strip()
                        elif "." in opt and len(opt.split(".")[0]) <= 2:
                            cleaned = opt.split(".", 1)[1].strip()
                        else:
                            cleaned = opt
                        cleaned_options.append(cleaned)
                    options = cleaned_options
            elif line.startswith("ANSWER:"):
                answer_text = line.split(":", 1)[1].strip()
                # For MCQ, map letter to actual option
                if q_type == "mcq" and len(answer_text) == 1 and answer_text.upper() in "ABCD":
                    idx = ord(answer_text.upper()) - ord('A')
                    if 0 <= idx < len(options):
                        correct_answer = options[idx]
                    else:
                        correct_answer = options[0] if options else "Option A"
                else:
                    correct_answer = answer_text
            elif line.startswith("EXPLANATION:"):
                explanation = line.split(":", 1)[1].strip()

        # Validate and create question object
        if question_text:
            # Handle different question types
            if q_type == "true_false":
                options = ["True", "False"]
                if correct_answer.lower() not in ["true", "false"]:
                    correct_answer = "True"  # Default
                else:
                    correct_answer = correct_answer.capitalize()
            elif q_type == "mcq":
                if len(options) < 4:
                    # Keep what we have or use defaults
                    while len(options) < 4:
                        options.append(f"Option {len(options) + 1}")
                if not correct_answer or correct_answer == "":
                    correct_answer = options[0]
            elif q_type == "short_answer":
                options = None
                if not correct_answer:
                    correct_answer = "Answer based on document content"

            # Create question object
            question_obj = QuizQuestion(
                question=question_text,
                type=q_type,
                options=options if q_type in ['mcq', 'true_false'] else None,
                correct_answer=correct_answer if correct_answer else "Not specified",
                explanation=explanation if explanation else "Based on the document content."
            )
            questions.append(question_obj)

    # Log for debugging if not enough questions
    if len(questions) < num_questions:
        print(f"Warning: Only parsed {len(questions)} questions out of {num_questions} requested")
        print(f"Raw output length: {len(quiz_text)} characters")

    return QuizOutput(questions=questions if questions else [])


# =============================================================================
# Synchronous Wrappers for Streamlit
# =============================================================================

def generate_summary_sync(
    text: str,
    length: str = 'standard',
    format_type: str = 'paragraphs'
) -> dict:
    """
    Synchronous wrapper for generate_summary.

    Args:
        text: The text to summarize
        length: Desired summary length
        format_type: Output format

    Returns:
        Dictionary with summary data
    """
    try:
        result = asyncio.run(generate_summary(text, length, format_type))
        return {
            'success': True,
            'summary': result.summary,
            'word_count': result.word_count,
            'key_topics': result.key_topics,
            'error': None
        }
    except Exception as e:
        return {
            'success': False,
            'summary': '',
            'word_count': 0,
            'key_topics': [],
            'error': f'Failed to generate summary: {str(e)}'
        }


def generate_quiz_sync(
    text: str,
    num_questions: int = 5,
    question_types: List[str] = None,
    difficulty: str = 'medium'
) -> dict:
    """
    Synchronous wrapper for generate_quiz.

    Args:
        text: The text to generate quiz from
        num_questions: Number of questions
        question_types: List of question types
        difficulty: Difficulty level

    Returns:
        Dictionary with quiz data
    """
    try:
        result = asyncio.run(generate_quiz(text, num_questions, question_types, difficulty))
        return {
            'success': True,
            'questions': [q.model_dump() for q in result.questions],
            'error': None
        }
    except Exception as e:
        return {
            'success': False,
            'questions': [],
            'error': f'Failed to generate quiz: {str(e)}'
        }
