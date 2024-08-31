import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from spellchecker import SpellChecker

# Ensure necessary data is downloaded
nltk.download('punkt')
nltk.download('stopwords')


# Define fashion-related categories and keywords
categories = {
    'gender': ['men', 'women', 'unisex', 'male', 'female', 'boy', 'girl'],
    'color': [
        'red', 'blue', 'green', 'black', 'white', 'yellow', 'pink', 'purple', 
        'orange', 'brown', 'gray', 'grey', 'violet', 'indigo', 'turquoise', 
        'beige', 'maroon', 'navy', 'olive', 'lime', 'coral', 'teal', 'gold', 
        'silver', 'bronze', 'peach', 'lavender', 'mint', 'rose', 'champagne', 
        'ivory', 'mustard', 'burgundy', 'charcoal', 'cyan', 'magenta', 'plum', 
        'apricot', 'fuchsia', 'jade', 'khaki', 'crimson', 'copper', 'saffron', 
        'amber', 'mauve', 'ruby', 'emerald', 'sapphire'
    ],
    'type': [
        'shirt', 'pants', 'dress', 'skirt', 'jeans', 'shorts', 'jacket', 'coat', 
        'blouse', 't-shirt', 'sweater', 'sweatshirt', 'hoodie', 'trousers', 
        'suit', 'blazer', 'cardigan', 'vest', 'leggings', 'jumpsuit', 'romper', 
        'gown', 'saree', 'lehenga', 'kurta', 'kurti', 'sherwani', 'dhoti', 
        'salwar', 'churidar', 'ankle boots', 'sandals', 'heels', 'flats', 
        'sneakers', 'loafers', 'moccasins', 'brogues', 'oxfords', 'slippers', 
        'flip-flops', 'footwear', 'shoes'
    ],
    'brand': [
        'nike', 'adidas', 'puma', 'zara', 'h&m', 'uniqlo', 'gucci', 'prada', 
        'levis', 'gap', 'burberry', 'versace', 'armani', 'dolce & gabbana', 
        'louis vuitton', 'chanel', 'hermes', 'ralph lauren', 'tommy hilfiger', 
        'calvin klein', 'lacoste', 'michael kors', 'givenchy', 'valentino', 
        'fendi', 'diesel', 'guess', 'mango', 'superdry', 'jack & jones', 
        'allensolly', 'w', 'biba', 'fabindia', 'wills lifestyle', 'mufti', 
        'killer', 'pepe jeans', 'arrow', 'park avenue', 'raymond', 'blackberrys', 
        'van heusen', 'allen solly', 'spencer', 'john players', 'peter england', 
        'manyavar', 'fabindia'
    ],
    'occasion': [
        'casual', 'formal', 'party', 'work', 'wedding', 'birthday', 'sport', 
        'gym', 'vacation', 'holiday', 'festival', 'interview', 'business', 
        'office', 'evening', 'cocktail', 'date', 'beach', 'travel', 'everyday', 
        'graduation', 'prom', 'homecoming', 'anniversary', 'engagement', 
        'christmas', 'new year', 'halloween', 'diwali', 'eid', 'thanksgiving', 
        'easter', 'baby shower', 'bridal shower', 'baptism', 'bar mitzvah', 
        'retirement', 'farewell', 'reunion', 'concert', 'gala', 'fundraiser', 
        'conference', 'seminar', 'workshop', 'trade show', 'competition', 
        'football', 'soccer', 'basketball', 'cricket', 'tennis', 'baseball', 
        'running', 'jogging', 'cycling', 'yoga', 'hiking', 'skiing', 'snowboarding', 
        'surfing', 'swimming', 'dancing'
    ]
}

# Initialize lemmatizer and spell checker
lemmatizer = WordNetLemmatizer()
spell = SpellChecker()

# Function to correct spelling
def correct_spelling(words):
    corrected_words = [spell.correction(word) if word not in categories else word for word in words]
    return corrected_words

# Function to process query and extract fashion-related keywords
def extract_fashion_keywords(query):
    # Tokenize the query
    words = word_tokenize(query.lower())
    
    # Correct spelling mistakes
    words = correct_spelling(words)
    
    # Remove stop words and punctuation
    stop_words = set(stopwords.words('english'))
    filtered_words = [lemmatizer.lemmatize(word) for word in words if word.isalnum() and word not in stop_words]
    
    # Extract keywords based on categories
    extracted_keywords = {category: [] for category in categories}
    for word in filtered_words:
        for category, keywords in categories.items():
            if word in keywords:
                extracted_keywords[category].append(word)
    
    # Remove empty categories
    extracted_keywords = {k: v for k, v in extracted_keywords.items() if v}
    
    return extracted_keywords

# Function to format extracted keywords into a sentence
def format_keywords(keywords):
    formatted_sentence = ""
    for category in ['gender', 'color', 'brand', 'type', 'occasion']:
        if category in keywords:
            formatted_sentence += ' '.join(keywords[category]) + ' '
    return formatted_sentence.strip()

# Main function to get user query and display extracted keywords
def main():
    while True:
        query = input("Enter your fashion query (or type 'exit' to quit): ")
        if query.lower() == 'exit':
            break
        keywords = extract_fashion_keywords(query)
        formatted_sentence = format_keywords(keywords)
        print("Extracted Fashion Keywords:", keywords)
        print("Formatted Sentence:", formatted_sentence)
        print()

if __name__ == "__main__":
    main()
