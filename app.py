from ai import generate_flashcards, generate_summary
from storage import clean_dataset, save_flashcards, load_flashcards
from textProcessing import *

# text = input("Enter text to generate flashcards: ")

def main():

    text = """
    Photosynthesis is a process used by plants, algae, and certain bacteria to convert light energy into 
    chemical energy, through a process that converts carbon dioxide and water into sugars (glucose) and oxygen. 
    This process is crucial for life on Earth as it produces most of the oxygen in the atmosphere and supplies 
    the chemical energy necessary for most living organisms. The process occurs in chloroplasts, which are 
    small organelles found in the cells of plants. Chlorophyll, the green pigment in chloroplasts, is responsible 
    for absorbing the light energy that drives photosynthesis.
    """

    
    # text_normalization(text)
    # remove_headers_footers(text)

    generate_summary(text)

    sentences = segment_text(text)
    # filter(text)

    for seg in sentences:
        flashcards = generate_flashcards(seg)
        save_flashcards(flashcards)

    clean_dataset()
    cards = load_flashcards()
    for card in cards:
        print(f"Q: {card['Question']}\nA: {card['Answer']}\n")
    

if __name__ == "__main__":
    main()