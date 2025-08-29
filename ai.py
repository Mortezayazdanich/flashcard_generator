from transformers import pipeline
import json

# Load the Flan-T5 pipeline. We can use this for all our tasks.
# Using a larger model like 'base' or 'large' will yield better results.
generator = pipeline("text2text-generation", model="google/flan-t5-base")

def generate_summary(text, max_tokens=200):
    # --- Step 1: Summarize the text using Flan-T5 ---
    # Flan-T5 is great at following instructions, so we just tell it what to do.
    summary_prompt = f"Summarize the following text: {text}"
    summary_result = generator(summary_prompt, max_new_tokens=max_tokens, truncation=True)
    summary = summary_result[0]['generated_text']
    
    print("--- Generated Summary ---")
    print(summary)
    print("-" * 25)

def generate_flashcards(text, num_questions=2):
    """
    Generates flashcards (question-answer pairs) from a given text using Flan-T5.
    """

    # --- Step 2: Generate questions from the summary ---
    # Ask for an explicit, numbered list with exactly N items.
    # questions_prompt = (
    #     f"Generate exactly {num_questions} distinct, insightful questions based on the text below.\n"
    #     f"Output only the questions, one per line, numbered 1 to {num_questions}.\n\n{text}"
    # )

    questions_prompt = (
    f"Generate a JSON array of exactly {num_questions} distinct question strings based on the text. "
    "Do not include anything else in your response besides the JSON array.\n"
    'Example format: ["Question 1?", "Question 2?"]\n\n'
    f"Text:\n{text}"
    )    
    
    questions_result = generator(
        questions_prompt, 
        max_new_tokens=256,
        num_beams=num_questions,  # Beam width, not number of outputs
        num_return_sequences=1,   # One sequence containing a list
        truncation=True,
        do_sample=True,
        temperature=0.7
    )

    # The output is a single string containing a numbered list, so we split it into individual questions.
    generated_questions_text = questions_result[0]['generated_text']
    questions = [q.strip() for q in generated_questions_text.split('\n') if q.strip() and len(q.strip()) > 5]
    # Clean numbering like "1. What is..."
    questions = [q.split('.', 1)[-1].strip() for q in questions]
    # Keep only non-empty lines, prefer ones that look like questions
    questions = [q for q in questions if q]
    
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
        answer_prompt = f"Based on the text below, answer the following question with a short explanation.\n\nText: {text}\n\nQuestion: {question}\n\nAnswer:"
        
        answer_result = generator(answer_prompt, max_new_tokens=64, truncation=True)
        answer = answer_result[0]['generated_text']
        cards.append({"Question": question, "Answer": answer.strip()})

    return cards 