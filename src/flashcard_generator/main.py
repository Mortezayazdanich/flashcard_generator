from .core.ai import generate_flashcards, generate_summary
from .core.storage import clean_dataset, save_flashcards, load_flashcards
from .core.text_processor import text_normalization, segment_into_chunks, filter_segments, filter
from .processing.input_processor import process_input
import logging
import os


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_input():
    """Get input from user - either file path or manual text entry."""
    logger.info("\n=== Flashcard Generator - Phase 0: Input Processing ===")
    logger.info("Choose your input method:")
    logger.info("1. Upload a file (PDF, image, or text file)")
    logger.info("2. Enter text manually")
    
    choice = input("\nEnter your choice (1 or 2): ").strip()
    
    if choice == '1':
        file_path = input("Enter the file path: ").strip()
        if not file_path:
            logger.warning("No file path provided. Switching to manual text entry.")
            # print("No file path provided. Switching to manual text entry.")
            return input("Enter text to generate flashcards: ") # Return the manual text entry
        
        # Expand user path if needed
        file_path = os.path.expanduser(file_path)
        
        try:
            logger.info(f"\nProcessing file: {file_path}")
            return process_input(file_path)
        except Exception as e:
            logger.exception(f"Error processing file: {e}")
            logger.warning("Switching to manual text entry.")
            return input("Enter text to generate flashcards: ") # Return the manual text entry
    
    elif choice == '2':
        return input("\nEnter text to generate flashcards: ")
    
    else:
        logger.warning("Invalid choice. Defaulting to manual text entry.")
        return input("Enter text to generate flashcards: ") # Return the manual text entry


def main():
    """Main function with enhanced input processing."""
    
    # Phase 0: Input Processing (NEW)
    try:
        raw_text = get_input() # Get the input from the user
        
        if not raw_text or not raw_text.strip():
            logger.warning("No text provided. Exiting.")
            return # Exit the function if no text was provided  
            
        logger.info(f"\n✅ Successfully extracted {len(raw_text)} characters of text")
        logger.info("\n=== Proceeding to flashcard generation pipeline ===")
        
    except Exception as e:
        logger.exception(f"Error during input processing: {e}")
        return # Exit the function if there was an error during the input processing
    
    # Phase 1.1: Text Cleaning & Normalization (existing pipeline)
    try:
        normalized_text = text_normalization(raw_text)
        cleaned_text = filter(normalized_text)
        chunks = segment_into_chunks(cleaned_text, target_words=220, overlap_ratio=0.2)
        filtered_segments = filter_segments(chunks, min_length=50)
        
        logger.info(f"Processing {len(filtered_segments)} text segments...")
        
        # Generate summary from cleaned text
        generate_summary(cleaned_text)
        
        # Generate flashcards for each segment
        all_flashcards = []
        for i, segment in enumerate(filtered_segments, 1): # Starting from 1 to match the enumerate syntax for the print statements
            logger.info(f"\n--- Processing segment {i}/{len(filtered_segments)} ---")
            flashcards = generate_flashcards(segment, num_questions=3)
            all_flashcards.extend(flashcards) # Extend the list with the new flashcards list
        
        # Save all flashcards at once
        if all_flashcards:
            save_flashcards(all_flashcards) # Save the all_flashcards list to the flashcards.json file
            clean_dataset()
            
            # Display results
            cards = load_flashcards() # Load the flashcards.json file into a list
            logger.info(f"\n=== Generated {len(cards)} Total Flashcards ===")
            for i, card in enumerate(cards, 1):
                logger.info(f"{i}. Q: {card['Question']}") # Print the question
                logger.info(f"   A: {card['Answer']}\n") # Print the answer
        else:
            logger.info("No flashcards generated.") # Print a message if no flashcards were generated
            
    except Exception as e:
        logger.exception(f"Error during flashcard generation: {e}") # Print an error message if there was an error during the flashcard generation


if __name__ == "__main__":
    main() # Run the main function