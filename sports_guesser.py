# ------------------------
# 📁 Import Required Modules
# ------------------------
import os  # For interacting with the file system and environment
from flask import Flask, request, render_template_string  # Flask essentials for handling requests and rendering HTML
from werkzeug.utils import secure_filename  # Ensures uploaded filenames are safe
from dotenv import load_dotenv  # To load environment variables from a .env file

import PyPDF2  # For reading PDF files
import docx  # For reading .docx Word files

# ------------------------
# 🌐 Load Environment Variables from .env File
# ------------------------
load_dotenv()  # Reads the .env file and loads the variables into environment

# ------------------------
# 🔐 Get Config Values from Environment
# ------------------------
UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "uploads")  # Folder to store uploaded files
DEBUG_MODE = os.getenv("DEBUG", "False") == "True"  # Enable or disable debug mode
SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key")  # Flask secret key (used for security features)

# ------------------------
# ✅ Allowed File Extensions
# ------------------------
ALLOWED_EXTENSIONS = {'pdf', 'docx'}  # Only allow PDF and DOCX files to be uploaded

# ------------------------
# 🏅 Keyword-Based Sport Categories
# ------------------------
SPORT_CATEGORIES = {
    'Football': ['football', 'fifa', 'goal', 'kick', 'soccer', 'messi', 'ronaldo'],
    'Cricket': ['cricket', 'bat', 'ball', 'wicket', 'bowler', 'batsman', 'dhoni', 'kohli'],
    'Basketball': ['basketball', 'nba', 'hoop', 'dribble', 'slam dunk', 'lebron', 'curry'],
    'Tennis': ['tennis', 'grand slam', 'wimbledon', 'federer', 'nadal', 'djokovic', 'serve'],
    'Hockey': ['hockey', 'stick', 'puck', 'ice', 'nhl', 'goalie', 'rink'],
}

# ------------------------
# 🚀 Initialize Flask App
# ------------------------
app = Flask(__name__)
app.secret_key = SECRET_KEY  # Required for session-related features
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER  # Configure upload folder

# Create the upload folder if it doesn't already exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# ------------------------
# 📄 Check if File Extension is Allowed
# ------------------------
def allowed_file(filename):
    # Checks if the file has a valid extension
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ------------------------
# 📄 Extract Text from PDF
# ------------------------
def extract_text_from_pdf(filepath):
    text = ""
    with open(filepath, 'rb') as f:
        reader = PyPDF2.PdfReader(f)  # Initialize PDF reader
        for page in reader.pages:
            text += page.extract_text() or ""  # Extract text page by page
    return text

# ------------------------
# 📄 Extract Text from DOCX
# ------------------------
def extract_text_from_docx(filepath):
    doc = docx.Document(filepath)  # Load the DOCX file
    return "\n".join([para.text for para in doc.paragraphs])  # Combine all paragraph texts

# ------------------------
# 🧠 Classify Text Based on Keywords
# ------------------------
def categorize_text(text):
    text_lower = text.lower()  # Convert to lowercase for case-insensitive matching
    scores = {sport: 0 for sport in SPORT_CATEGORIES}  # Initialize keyword scores for each sport

    # Count the number of occurrences of each keyword
    for sport, keywords in SPORT_CATEGORIES.items():
        for keyword in keywords:
            scores[sport] += text_lower.count(keyword)

    # Get the sport with the highest score
    best_sport = max(scores, key=scores.get)

    # Return the sport name if any keyword matched; otherwise return "Unknown"
    return best_sport if scores[best_sport] > 0 else "Unknown"

# ------------------------
# 🌍 Web Route for Uploading Files and Viewing Results
# ------------------------
@app.route('/', methods=['GET', 'POST'])
def upload_file():
    category = None       # Will store the detected category (if any)
    file_text = ""        # Will store extracted text from the file

    if request.method == 'POST':
        # Check if the form submitted has a file
        if 'file' not in request.files:
            category = "No file part"
        else:
            file = request.files['file']

            # Check if a file was actually selected
            if file.filename == '':
                category = "No selected file"

            # Check file type and process it
            elif file and allowed_file(file.filename):
                filename = secure_filename(file.filename)  # Sanitize filename
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)  # Full file path
                file.save(filepath)  # Save uploaded file to disk

                # Extract text based on file type
                if filename.lower().endswith('.pdf'):
                    file_text = extract_text_from_pdf(filepath)
                elif filename.lower().endswith('.docx'):
                    file_text = extract_text_from_docx(filepath)
                else:
                    category = "Unsupported file type"

                # If text was successfully extracted, categorize it
                if file_text:
                    category = categorize_text(file_text)

    # ------------------------
    # 🖥️ Return HTML Form and Result
    # ------------------------
    return render_template_string('''
        <!doctype html>
        <title>Sport Category Detector</title>
        <h2>Upload a PDF or Word document to detect the sport category</h2>
        <form method=post enctype=multipart/form-data>
          <input type=file name=file>
          <input type=submit value=Upload>
        </form>
        {% if category %}
            <h3>Detected Category: {{ category }}</h3>
        {% endif %}
    ''', category=category)

# ------------------------
# 🔁 Run the Flask Development Server
# ------------------------
if __name__ == '__main__':
    # Starts the app only if this file is run directly
    # Never use debug=True in production
    app.run(debug=DEBUG_MODE)

