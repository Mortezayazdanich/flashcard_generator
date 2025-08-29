from transformers import pipeline

# Load the Flan-T5 pipeline on the CPU to ensure compatibility.
# device=-1 forces the use of the CPU, bypassing potential MPS issues.
generator = pipeline("text2text-generation", model="google/flan-t5-large", device=-1)

def generate_flashcards(text, num_questions=5):
    """
    Generates flashcards (question-answer pairs) from a given text using Flan-T5.
    """
    
    # --- Step 1: Summarize the text using Flan-T5 ---
    # Flan-T5 is great at following instructions, so we just tell it what to do.
    summary_prompt = f"Summarize the following text in 1 to 2 paragraphs: {text}"
    # Use max_new_tokens to avoid warnings and be explicit.
    summary_result = generator(summary_prompt, max_new_tokens=150)
    summary = summary_result[0]['generated_text']
    
    print("--- Generated Summary ---")
    print(summary)
    print("-" * 25)

    # --- Step 2: Generate questions from the summary ---
    # We ask the model to generate a numbered list of questions.
    questions_prompt = f"Generate {num_questions} questions based on the following text. Output only the questions in a numbered list:\n\n{summary}"
    
    questions_result = generator(
        questions_prompt, 
        max_new_tokens=128,
        num_beams=num_questions, # Use beams to get diverse questions
        num_return_sequences=1   # We want one cohesive list of questions
    )
    
    # The output is a single string containing a numbered list, so we split it into individual questions.
    generated_questions_text = questions_result[0]['generated_text']
    questions = [q.strip() for q in generated_questions_text.split('\n') if q.strip()]
    
    # Clean up the question numbers (e.g., "1. What is...")
    questions = [q.split('.', 1)[-1].strip() for q in questions]

    print("--- Generated Questions ---")
    print("\n".join(questions))
    print("-" * 25)

    # --- Step 3: Generate an answer for each question ---
    cards = []
    for question in questions:
        # For each question, we create a new prompt asking for the answer based on the summary.
        answer_prompt = f"Based on the text below, answer the following question.\n\nText: {summary}\n\nQuestion: {question}\n\nAnswer:"
        
        answer_result = generator(answer_prompt, max_new_tokens=64)
        answer = answer_result[0]['generated_text']
        
        cards.append({"Question": question, "Answer": answer.strip()})
        
    return cards

# --- Example Usage ---
if __name__ == '__main__':
    example_text = """
    Photosynthesis is a process used by plants, algae, and certain bacteria to convert light energy into 
    chemical energy, through a process that converts carbon dioxide and water into sugars (glucose) and oxygen. 
    This process is crucial for life on Earth as it produces most of the oxygen in the atmosphere and supplies 
    the chemical energy necessary for most living organisms. The process occurs in chloroplasts, which are 
    small organelles found in the cells of plants. Chlorophyll, the green pigment in chloroplasts, is responsible 
    for absorbing the light energy that drives photosynthesis.
    """
    
    flashcards = generate_flashcards(example_text, num_questions=3)
    
    print("\n--- Generated Flashcards ---")
    for i, card in enumerate(flashcards, 1):
        print(f"Card {i}:")
        print(f"  Q: {card['Question']}")
        print(f"  A: {card['Answer']}\n")

