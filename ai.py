from transformers import pipeline
import json, re

# Global generator to avoid reloading model
_generator = None

def get_generator():
    """Get the text generation pipeline, loading it once if needed."""
    global _generator
    if _generator is None:
        _generator = pipeline("text2text-generation", model="google/flan-t5-base")
    return _generator

def generate_summary(text, max_tokens=200):
    """Generate and return a summary of the given text."""
    generator = get_generator()
    summary_prompt = f"Summarize the following text: {text}"
    summary_result = generator(summary_prompt, max_new_tokens=max_tokens, truncation=True)
    summary = summary_result[0]['generated_text']
    
    print("--- Generated Summary ---")
    print(summary)
    print("-" * 25)
    
    return summary

def generate_flashcards(text, num_questions=5):
    """
    Generates flashcards (question-answer pairs) from a given text using Flan-T5.
    """
    generator = get_generator()
    
    # --- Step 2: Generate questions from the text ---
    questions_prompt = (
    f"Generate a JSON array of exactly {num_questions} distinct question strings based on the text. "
    "Do not include anything else in your response besides the JSON array.\n"
    'Example format: ["Question 1?", "Question 2?"]\n\n'
    f"Text:\n{text}"
    )    
    
    questions_result = generator(
        questions_prompt, 
        max_new_tokens=128,
        num_beams=4,  # Beam width, not number of outputs
        num_return_sequences=1,   # One sequence containing a list
        truncation=True,
        do_sample=True,
        temperature=0.7
    )

    # The output is a single string containing a numbered list, so we split it into individual questions.
    generated_questions_text = questions_result[0]['generated_text'].strip()
    questions = extract_json_array(generated_questions_text) or []

    normalized = []
    seen = set()
    for q in questions:
        if not isinstance(q, str):
            continue
        qn = normalize_q(q)
        if len(qn) < 5 or '?' not in qn:
            continue
        key = qn.lower()
        if key not in seen:
            seen.add(key)
            normalized.append(qn)

    questions = normalized[:num_questions]
    
    # Fallback: if fewer than requested, generate additional questions one-by-one
    if len(questions) < num_questions:
        existing_lower = {q.lower() for q in questions}
        while len(questions) < num_questions:
            single_prompt = (
                            "Generate one distinct, insightful question based on the text below. "
                            "Output only the question, no numbering, no quotes, do not repeat prior questions.\n\n"
                            f"Prior questions: {list(existing_lower)}\n\n"
                            f"Text:\n{text}"
                            )
            single_result = generator(
                single_prompt,
                max_new_tokens=64,
                truncation=True,
                do_sample=True,
                temperature=0.8
            )
            candidate = single_result[0]['generated_text'].strip()
            normalized = candidate.lower()
            if candidate and normalized not in existing_lower:
                questions.append(candidate)
                existing_lower.add(normalized)
            else:
                # Avoid potential infinite loop if the model keeps repeating
                break


    # --- Step 3: Generate an answer for each question ---
    cards = []
    for question in questions:
        # For each question, we create a new prompt asking for the answer based on the summary.
        answer_prompt = (
                        "Based on the text below, answer the question in one concise sentence. "
                        "Output only the answer. Do not repeat the question.\n\n"
                        f"Text:\n{text}\n\nQuestion: {question}\n\nAnswer:"
                        )
        answer_result = generator(
                                answer_prompt,
                                max_new_tokens=48,
                                do_sample=False,
                                num_beams=4
                                )
        answer = answer_result[0]['generated_text']
        cards.append({"Question": question.strip(), "Answer": answer.strip()})

    return cards 


def extract_json_array(text: str):
    try:
        data = json.loads(text)
        if isinstance(data, list):
            return data
    except json.JSONDecodeError:
        pass
    match = re.search(r'\[.*?\]', text, flags=re.S)
    if match:
        try:
            data = json.loads(match.group(0))
            if isinstance(data, list):
                return data
        except json.JSONDecodeError:
            pass
    return None


def normalize_q(q: str) -> str:
    return q.strip().strip('"').strip()