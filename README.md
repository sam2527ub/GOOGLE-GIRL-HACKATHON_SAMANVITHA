# PHARMACIST'S ASSISTANT
# Front end :
```
cd webapp
npm install
npm start
```
# Backend :
# Prescription OCR Assistant

This project is a web application that acts as a pharmacist assistant, helping to transcribe handwritten doctors' prescriptions into text. The application allows users to upload images of prescriptions and displays the extracted details and list of medicines found and other medicines that have similar composition in case the medicine user is looking for is not available and creates the order automatically.

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

## Working 

1. Upload the prescription – User uploads an image of the prescription.
2. Extract text from the image – Optical Character Recognition (OCR) is used to extract the prescription text.
3. Identify the prescribed medicine – The extracted text is matched against a medicine database to find the closest match. ( I ensured that matching is highly accurate and efficient. If the extracted text is not matching with any medicine from the database then the medicine in the prescription is not found and that specific medicine order will not be created.)
4. Find alternative medicines – Medicines with similar composition (generic equivalents) are retrieved.
5. Generate an order automatically – An order is created based on the identified or alternative medicines.

## The system is working optimally with high accuracy from extracting the text to placing the order working optimally for edge cases as well. 
## Prescription data is available in data folder where edge cases can be checked. 

## Possible improvements:
User Confirmation: Allow users to confirm or modify the order before finalizing.
Prescription Verification: Include a pharmacist approval step if required by regulations.
If a prescribed medicine is not found in the database, its status is marked as 'Not Found,' preventing order placement. To address this, the system wants to consider contextual information such as the doctor’s specialization and the patient’s symptoms to suggest an available medicine with a similar composition that aligns with the given context, ensuring a suitable alternative is provided. A model should be trained for this.






