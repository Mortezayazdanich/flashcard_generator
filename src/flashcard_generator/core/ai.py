from typing import List, Dict, Any, Optional
import logging
from ..utils.model_manager import get_ai_generator
from ..utils.patterns import AIPatterns
from ..config.settings import get_config
from ..utils.exceptions import AIGenerationError

def generate_summary(text: str, max_tokens: Optional[int] = None) -> str:
    """Generate and return a summary of the given text."""
    config = get_config()
    logger = logging.getLogger(__name__)
    
    if max_tokens is None:
        max_tokens = config.MAX_SUMMARY_TOKENS
    
    summary_prompt = f"Summarize the following text: {text}"
    
    try:
        generator = get_ai_generator()
        summary_result = generator(summary_prompt, max_new_tokens=max_tokens, truncation=True)
        summary = summary_result[0]['generated_text']
        
        print("--- Generated Summary ---")
        print(summary)
        print("-" * 25)
        
        return summary
        
    except Exception as e:
        logger.error(f"Summary generation failed: {e}")
        raise AIGenerationError("summary", len(summary_prompt), e)


def generate_flashcards(text: str, num_questions: Optional[int] = None) -> List[Dict[str, str]]:
    """
    Generates flashcards (question-answer pairs) from a given text using optimized AI generation.
    """
    config = get_config()
    logger = logging.getLogger(__name__)
    
    if num_questions is None:
        num_questions = config.DEFAULT_QUESTIONS_PER_SEGMENT
    
    try:
        # Step 1: Generate questions
        questions = _generate_questions(text, num_questions)
        
        # Step 2: Generate answers for each question
        cards = []
        for question in questions:
            try:
                answer = _generate_answer(text, question)
                if _is_valid_qa_pair(question, answer):
                    cards.append({"Question": question.strip(), "Answer": answer.strip()})
            except Exception as e:
                logger.warning(f"Failed to generate answer for question '{question}': {e}")
                continue
        
        return cards
        
    except Exception as e:
        logger.error(f"Flashcard generation failed: {e}")
        raise AIGenerationError("flashcards", len(text), e)


def _generate_questions(text: str, num_questions: int) -> List[str]:
    """Generate questions from text using optimized prompting."""
    config = get_config()
    
    questions_prompt = (
        f"Generate a JSON array of exactly {num_questions} distinct question strings based on the text. "
        "Output only the JSON array with no extra text before or after.\n"
        'Example format: ["Question 1?", "Question 2?"]\n\n'
        f"Text:\n{text}"
    )
    
    generator = get_ai_generator()
    questions_result = generator(
        questions_prompt,
        max_new_tokens=config.MAX_QUESTION_TOKENS,
        num_beams=4,
        num_return_sequences=1,
        truncation=True,
        do_sample=False
    )
    
    # Parse JSON using optimized patterns
    generated_questions_text = questions_result[0]['generated_text'].strip()
    raw_questions = AIPatterns.extract_json_array(generated_questions_text)
    
    # Clean and validate questions
    questions = _clean_and_validate_questions(raw_questions)
    
    # Fallback: generate additional questions if needed
    if len(questions) < num_questions:
        questions.extend(_generate_fallback_questions(text, num_questions - len(questions), questions))
    
    return questions[:num_questions]


def _clean_and_validate_questions(raw_questions: List[Any]) -> List[str]:
    """Clean and validate generated questions."""
    config = get_config()
    normalized_questions = []
    seen = set()
    
    for q in raw_questions:
        if not isinstance(q, str):
            continue
            
        # Normalize question
        qn = str(q).strip().strip('"').strip("'")
        
        # Apply quality filters
        if (len(qn) < config.MIN_QUESTION_LENGTH or 
            '?' not in qn or 
            AIPatterns.is_generic_question(qn)):
            continue
        
        # Check for duplicates
        key = qn.lower()
        if key in seen:
            continue
            
        seen.add(key)
        normalized_questions.append(qn)
    
    return normalized_questions


def _generate_fallback_questions(text: str, needed: int, existing: List[str]) -> List[str]:
    """Generate additional questions one by one as fallback."""
    config = get_config()
    questions = []
    existing_lower = {q.lower() for q in existing}
    
    for _ in range(needed):
        single_prompt = (
            "Generate one distinct, insightful question based on the text below. "
            f"Do not repeat any of these: {list(existing_lower)}. "
            "Output only the question.\n\n"
            f"Text:\n{text}"
        )
        
        try:
            generator = get_ai_generator()
            single_result = generator(
                single_prompt,
                max_new_tokens=64,
                truncation=True,
                do_sample=False,
                num_beams=4
            )
            candidate = single_result[0]['generated_text'].strip()
            normalized = candidate.lower()
            
            if (candidate and 
                normalized not in existing_lower and 
                not AIPatterns.is_generic_question(candidate)):
                questions.append(candidate)
                existing_lower.add(normalized)
            else:
                # Avoid infinite loop
                break
                
        except Exception:
            break
    
    return questions


def _generate_answer(text: str, question: str) -> str:
    """Generate answer for a specific question."""
    config = get_config()
    
    answer_prompt = (
        "Based on the text below, answer the question in one concise sentence. "
        "Output only the answer. Do not repeat the question.\n\n"
        f"Text: {text}\n\nQuestion: {question}\n\nAnswer:"
    )
    
    generator = get_ai_generator()
    answer_result = generator(
        answer_prompt,
        max_new_tokens=config.MAX_ANSWER_TOKENS,
        truncation=True,
        do_sample=False,
        num_beams=4
    )
    
    return answer_result[0]['generated_text'].strip().strip('"').strip("'")


def _is_valid_qa_pair(question: str, answer: str) -> bool:
    """Validate question-answer pair quality."""
    config = get_config()
    
    if not answer or not question:
        return False
    
    # Check answer quality
    answer_words = len(answer.split())
    if (answer_words < config.MIN_ANSWER_WORDS or 
        answer_words > config.MAX_ANSWER_WORDS):
        return False
    
    # Check if answer is too similar to question
    if answer.lower() == question.lower():
        return False
    
    return True


