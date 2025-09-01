from transformers import pipeline
import json, re

# Lazy-load the Flan-T5 pipeline to avoid heavy downloads at import time
_generator = None

def _get_generator():
    global _generator
    if _generator is None:
        _generator = pipeline("text2text-generation", model="google/flan-t5-base")
    return _generator

def generate_summary(text, max_tokens=200):
    """Generate and return a summary of the given text."""
    summary_prompt = f"Summarize the following text: {text}"
    generator = _get_generator()
    summary_result = generator(summary_prompt, max_new_tokens=max_tokens, truncation=True)
    summary = summary_result[0]['generated_text']
    
    print("--- Generated Summary ---")
    print(summary)
    print("-" * 25)
    
    return summary

def generate_flashcards(text, num_questions=2):
    """
    Generates flashcards (question-answer pairs) from a given text using Flan-T5.
    """
    
    # --- Step 2: Generate questions from the text ---
    questions_prompt = (
    f"Generate a JSON array of exactly {num_questions} distinct question strings based on the text. "
    "Output only the JSON array with no extra text before or after.\n"
    'Example format: ["Question 1?", "Question 2?"]\n\n'
    f"Text:\n{text}"
    )    
    
    generator = _get_generator()
    questions_result = generator(
        questions_prompt,
        max_new_tokens=128,
        num_beams=4,
        num_return_sequences=1,
        truncation=True,
        do_sample=False
    )

    # Parse JSON array reliably, with a fallback that extracts the first JSON list found
    generated_questions_text = questions_result[0]['generated_text'].strip()

    def _extract_json_array(text_str):
        try:
            data = json.loads(text_str)
            if isinstance(data, list):
                return data
        except json.JSONDecodeError:
            pass
        import re
        match = re.search(r"\[.*?\]", text_str, flags=re.S)
        if match:
            try:
                data = json.loads(match.group(0))
                if isinstance(data, list):
                    return data
            except json.JSONDecodeError:
                pass
        return []

    raw_questions = _extract_json_array(generated_questions_text)

    # Normalize, deduplicate, and enforce constraints
    def _normalize_question(q):
        return str(q).strip().strip('"').strip("'")

    normalized_questions = []
    seen = set()
    import re as _re
    generic_q_pattern = _re.compile(r"^question\s*\d+\?$", flags=_re.I)

    for q in raw_questions:
        if not isinstance(q, str):
            continue
        qn = _normalize_question(q)
        if len(qn) < 5 or '?' not in qn:
            continue
        if generic_q_pattern.match(qn):
            continue
        key = qn.lower()
        if key in seen:
            continue
        seen.add(key)
        normalized_questions.append(qn)

    questions = normalized_questions[:num_questions]
    
    # Fallback: if fewer than requested, generate additional questions one-by-one
    if len(questions) < num_questions:
        existing_lower = {q.lower() for q in questions}
        while len(questions) < num_questions:
            single_prompt = (
                "Generate one distinct, insightful question based on the text below. "
                f"Do not repeat any of these: {list(existing_lower)}. "
                "Output only the question.\n\n"
                f"Text:\n{text}"
            )
            generator = _get_generator()
            single_result = generator(
                single_prompt,
                max_new_tokens=64,
                truncation=True,
                do_sample=False,
                num_beams=4
            )
            candidate = single_result[0]['generated_text'].strip()
            normalized = candidate.lower()
            if candidate and normalized not in existing_lower and not generic_q_pattern.match(candidate):
                questions.append(candidate)
                existing_lower.add(normalized)
            else:
                # Avoid potential infinite loop if the model keeps repeating
                break


    # --- Step 3: Generate an answer for each question ---
    cards = []
    for question in questions:
        # For each question, we create a constrained prompt asking for only the answer.
        answer_prompt = (
            "Based on the text below, answer the question in one concise sentence. "
            "Output only the answer. Do not repeat the question.\n\n"
            f"Text: {text}\n\nQuestion: {question}\n\nAnswer:"
        )

        generator = _get_generator()
        answer_result = generator(
            answer_prompt,
            max_new_tokens=48,
            truncation=True,
            do_sample=False,
            num_beams=4
        )
        answer = answer_result[0]['generated_text'].strip().strip('"').strip("'")

        # Simple quality filters
        if not answer or answer.lower() == question.lower() or len(answer.split()) < 2:
            continue
        cards.append({"Question": question.strip(), "Answer": answer.strip()})

    return cards 


