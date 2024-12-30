from flask import Flask, request, jsonify, render_template
import nltk
from nltk.tokenize import word_tokenize
import random

app = Flask(__name__)

# Define a list of predefined words
predefined_words = ["love", "life", "happiness", "success", "motivation", "inspiration", "dreams", "goals", "passion", "purpose"]

# Download all required NLTK data at startup
def setup_nltk():
    try:
        # Download both punkt and punkt_tab
        nltk.download('punkt')
        # Alternative tokenization approach if punkt_tab is not available
        return True
    except Exception as e:
        print(f"Error downloading NLTK data: {str(e)}")
        return False

# Initialize NLTK
setup_nltk()

# Define the hashtag suggestion function with fallback tokenization
def suggest_hashtags(text):
    if not isinstance(text, str):
        return []
        
    # Tokenize the input text with error handling
    try:
        # Simple fallback tokenization if NLTK fails
        try:
            tokens = word_tokenize(text.lower())
        except:
            # Fallback to basic string splitting if NLTK tokenization fails
            tokens = text.lower().split()
    except Exception as e:
        print(f"Tokenization error: {str(e)}")
        return []

    # Get words that match predefined words
    common_words = [word for word in tokens if word in predefined_words]
    
    # If no matching words found, return some random combinations from predefined words
    if not common_words:
        common_words = random.sample(predefined_words, min(4, len(predefined_words)))

    # Generate hashtags by combining the words
    hashtags = []
    try:
        for i in range(len(common_words)):
            hashtags.append(f"#{common_words[i]}")
            for j in range(i+1, len(common_words)):
                hashtag = f"#{common_words[i]}_{common_words[j]}"
                hashtags.append(hashtag)
    except Exception as e:
        print(f"Hashtag generation error: {str(e)}")
        return []

    # Return unique hashtags (up to 10)
    return list(set(hashtags))[:10]

# Add a root route that serves a simple HTML form
@app.route('/')
def home():
    return '''
    <html>
        <body>
            <h1>Hashtag Generator</h1>
            <form id="hashtagForm">
                <textarea id="text" rows="4" cols="50" placeholder="Enter your text here..."></textarea><br><br>
                <button type="submit">Generate Hashtags</button>
            </form>
            <div id="results"></div>
            <div id="error" style="color: red;"></div>
            
            <script>
                document.getElementById('hashtagForm').addEventListener('submit', async (e) => {
                    e.preventDefault();
                    const text = document.getElementById('text').value;
                    try {
                        const response = await fetch('/hashtag', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                            },
                            body: JSON.stringify({text: text})
                        });
                        const data = await response.json();
                        if (data.error) {
                            document.getElementById('error').textContent = data.error;
                            document.getElementById('results').innerHTML = '';
                        } else {
                            document.getElementById('error').textContent = '';
                            document.getElementById('results').innerHTML = 
                                '<h3>Generated Hashtags:</h3>' + 
                                (data.hashtags.length ? data.hashtags.join('<br>') : 'No hashtags generated');
                        }
                    } catch (err) {
                        document.getElementById('error').textContent = 'An error occurred while generating hashtags';
                        document.getElementById('results').innerHTML = '';
                    }
                });
            </script>
        </body>
    </html>
    '''

# Define the API endpoint for generating hashtags
@app.route('/hashtag', methods=['POST'])
def generate_hashtags():
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({'error': 'No text provided'}), 400
            
        text = data['text']
        if not text.strip():
            return jsonify({'error': 'Empty text provided'}), 400
            
        hashtags = suggest_hashtags(text)
        if not hashtags:
            return jsonify({'hashtags': ['#inspiration', '#motivation', '#success']}), 200
            
        return jsonify({'hashtags': hashtags})
    except Exception as e:
        print(f"Error in generate_hashtags: {str(e)}")  # Server-side logging
        return jsonify({'error': 'An error occurred while processing your request'}), 500

if __name__ == '__main__':
    app.run(debug=True)