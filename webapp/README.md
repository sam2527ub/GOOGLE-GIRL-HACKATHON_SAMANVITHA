# Front end :
```
cd webapp
npm install
npm start
```
# Backend :
# Prescription OCR Assistant

This project is a web application that acts as a pharmacist assistant, helping to transcribe handwritten doctors' prescriptions into text. The application allows users to upload images of prescriptions and displays the extracted details and list of medicines and creates the order automatically.

## Features

- Upload images of prescriptions via drag-and-drop or file explorer.
- Displays prescription details and medicine list after processing the uploaded image.
- Utilizes Optical Character Recognition (OCR) to extract text from images.

## Project Structure

```
prescription-ocr
├── src
│   ├── static
│   │   ├── css
│   │   │   └── styles.css
│   │   └── js
│   │       └── main.js
│   ├── templates
│   │   ├── base.html
│   │   └── index.html
│   ├── app.py
│   └── ocr
│       └── processor.py
├── tests
│   └── test_ocr.py
├── requirements.txt
└── README.md
```

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd prescription-ocr
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Run the Flask application:
   ```
   python src/app.py
   ```

2. Open your web browser and navigate to `http://127.0.0.1:5000`.

3. Upload a prescription image using the provided interface.

4. You get information of the medicines that are found in the database, along with the dosage and it automatically places order for the medicines that are available.
