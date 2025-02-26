import google.generativeai as genai
from PIL import Image
import os
from dotenv import load_dotenv
from pathlib import Path
import json
import csv
import re
from fuzzywuzzy import process, fuzz

# Configure Gemini API
genai.configure(api_key='AIzaSyCP_ooSoINwK60YQEduG5PPOP--i9KL0jg')

# List of generic terms to ignore
GENERIC_TERMS = {
    'tablet', "tab", 'syrup', 'syr', 'capsule', 'cap', 'injection', 'inj', 'cream', 'gel', 'drops', 'spray',
    'mg', 'ml', 'gm', 'g', 'kg', 'l', 'iu', 'mcg', 'microgram', 'milligram', 'gram', 'kilogram', 'liter',
    'oral', 'topical', 'solution', 'suspension', 'powder', 'ointment', 'liquid', 'patch', 'inhaler'
}

# Mapping for replacing abbreviations
ABBREVIATIONS = {
    'tab': 'tablet',
    'cap': 'capsule',
    'syr': 'syrup',
    'inj': 'injection'
}

def extract_drug_name(name):
    """
    Preprocess the drug name by removing numbers, units, and replacing abbreviations.
    
    Args:
        name (str): The medicine name to process.
    
    Returns:
        str: The preprocessed drug name.
    """
    # Replace abbreviations like "T" with "Tablet"
    name = re.sub(r'\bT\b', 'Tablet', name, flags=re.IGNORECASE)
    
    # Remove numbers and units (mg, g, ml, etc.)
    name = re.sub(r'\d+', '', name)  # Remove numbers
    name = re.sub(r'\b(mg|g|ml|gm|kg|l|mcg|iu)\b', '', name, flags=re.IGNORECASE)  # Remove units
    
    # Replace other abbreviations
    for abbrev, full_form in ABBREVIATIONS.items():
        name = re.sub(r'\b' + re.escape(abbrev) + r'\b', full_form, name, flags=re.IGNORECASE)
    
    # Remove special characters and extra spaces
    name = re.sub(r'[^\w\s]', '', name)  # Remove special characters
    name = re.sub(r'\s+', ' ', name).strip()  # Remove extra spaces
    
    return name.lower()

def verify_medicine(medicine_name, threshold=80, length_threshold=5):
    """
    Verify if a medicine exists in the database using fuzzy matching and length-based filtering.
    
    Args:
        medicine_name (str): Name of the medicine to verify.
        threshold (int): Minimum similarity score for a match (0-100).
        length_threshold (int): Maximum allowed length difference between input and matched name.
    
    Returns:
        dict: Verification result with status, info, or suggestions.
    """
    # Preprocess the input medicine name
    processed_name = extract_drug_name(medicine_name)
    print(f"Processed name: {processed_name}")  # Debugging
    
    # Use fuzzywuzzy to find the best match using Token Sort Ratio
    best_match, score = process.extractOne(processed_name, medicine_db.keys(), scorer=fuzz.token_sort_ratio)
    
    # Debugging: Print the best match and score
    print(f"Best match: {best_match}, Score: {score}")  # Debugging
    
    # Calculate the length difference
    input_length = len(processed_name)
    match_length = len(best_match)
    length_difference = abs(input_length - match_length)
    
    # Check if the best match meets the thresholds
    if score >= threshold and length_difference <= length_threshold:
        return {
            'status': 'found',
            'info': medicine_db[best_match],
            'match_score': score,  # Optional: Include the match score for debugging
            'length_difference': length_difference  # Optional: Include the length difference for debugging
        }
    else:
        return {
            'status': 'not found',
            'suggestions': []  # No suggestions for now
        }
def load_medicine_db(csv_file):
    """
    Load medicine database from a CSV file.
    
    Args:
        csv_file (str): Path to the CSV file containing medicine data.
    
    Returns:
        dict: A dictionary containing medicine data.
    """
    medicine_db = {}
    
    try:
        with open(csv_file, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            print("CSV file opened successfully.")  # Debugging
            
            for row in reader:
                # Preprocess the drug name
                key = extract_drug_name(row['name'])
                medicine_db[key] = {
                    'big_name': row['name'],
                    'name': extract_drug_name(row['name']),
                    'short_composition1': row['short_composition1'].split(', ') if row['short_composition1'] else [],
                    'short_composition2': row['short_composition2'].split(', ') if row['short_composition2'] else [],
                }
        
        print("Medicine database loaded successfully.")  # Debugging
        return medicine_db
    
    except FileNotFoundError:
        print(f"Error: The file '{csv_file}' was not found.")
        return {}
    except KeyError as e:
        print(f"Error: Missing expected column in CSV file: {e}")
        return {}
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return {}

# Load medicine database from CSV
medicine_db = load_medicine_db('ocr/data.csv')

# Initialize the model
model = genai.GenerativeModel('gemini-1.5-flash', generation_config={"response_mime_type": "application/json"})



def find_similar_drugs(found_drug, top_n=3):
    """
    Find drugs with similar compositions to the found drug.
    
    Args:
        found_drug (dict): The drug that was found in the database.
        top_n (int): Number of similar drugs to return.
    
    Returns:
        list: A list of similar drugs.
    """
    # Extract compositions of the found drug
    found_composition1 = set(found_drug['short_composition1'])
    found_composition2 = set(found_drug['short_composition2'])
    
    # Calculate similarity scores for all drugs in the database
    similarity_scores = []
    for drug_name, drug_info in medicine_db.items():
        if drug_info['big_name'] == found_drug['big_name']:  # Skip the found drug itself
            continue
        
        # Extract compositions of the current drug
        current_composition1 = set(drug_info['short_composition1'])
        current_composition2 = set(drug_info['short_composition2'])
        
        # Calculate the number of matching compositions
        match_score = len(found_composition1.intersection(current_composition1)) + \
                      len(found_composition2.intersection(current_composition2))
        
        similarity_scores.append((drug_info, match_score))
    
    # Sort by match score in descending order
    similarity_scores.sort(key=lambda x: x[1], reverse=True)
    
    # Return the top N similar drugs
    return [drug_info for drug_info, _ in similarity_scores[:top_n]]

def extract_prescription_text(image):
    """
    Extract text from handwritten medical prescription using Gemini Vision.
    
    Args:
        image: Prescription image.
    
    Returns:
        dict: Extracted prescription details.
    """
    try:
        # Create prompt for better context
        prompt = """
        You are an expert handwriting recognition AI model that has been trained on a large dataset of handwritten medical prescriptions.
        Analyze this medical prescription image and extract all the handwritten and printed text. 
        Format the output in the following manner:
        {"Patient Name": Name,
         "Diagnosis": Diagnosis details,
         "Prescription": [
            [ Medicine name, Dosage Instructions, Dosage count ],
            [ Medicine name, Dosage Instructions, Dosage count ],
            [ Medicine name, Dosage Instructions, Dosage count ] ... 
            ],
        
        Aim to be as precise in the transcription as possible. Do not add any additional information apart from what is written.
        If any information is of the above details are not available, mention it as 'Not Available'.
        The prescription section consists of a list of individual medicines, each with their dosage instructions and dosage count.
        The medicine name , must include the name of the medicine, the type of medication (tablet, capsule, syrup, etc.), and the strength of the medicine (eg. mg per tablet).
        Dosage instructions will consist of number of doses per day and the duration of the doses. Display it in the format of "x/day for y days".
        The number of doses per day may be in multiple formats, either as abbreviations (TDS for thrice daily, BD for twice daily etc.) or as full words (Three times a day) or as markings (1-0-1). It is crucial to correctly interpret the dosage instructions, especially when they are in abbreviations or in the form of the aforementioned markings. When in markings the sum of all numbers is the number of doses a day (eg. 1-0-1 corresponds to 2/day) Show this in the form 3/day, 2/day, etc.
        The duration of the dosage may be given in days or weeks; shorthands for either may be used (eg 3d, 4wks). The duration may also be given as a general duration for all medicines.
        The dosage count must be a single number of the number of doses that must be given by the pharmacy. For tablets this is the numnber of tablets, for syrups this is the volume of the syrup.
        The diagnostic details may include the patient's condition, symptoms, or any other relevant information found in the prescription.
        """
        
        # Generate response from Gemini
        response = model.generate_content([prompt, image])
        print(response.text)
        result = json.loads(response.text)
        
        # Verify each medicine in the prescription
        for medicine in result['Prescription']:
            verification_result = verify_medicine(medicine[0])
            medicine.append(verification_result)
            print(medicine)
        
        return result
    except Exception as e:
        return {"Error": str(e)}
def create_order(prescription):
    """
    Create an order based on the recognized medicines in the prescription.
    If the medicine is found, use the dosage instructions and dosage count from the prescription.
    If dosage is unavailable, default to "1/day for 7 days" and a dosage count of 1.
    
    Args:
        prescription (dict): The extracted prescription details.
    
    Returns:
        dict: The order details with medicines and their dosages.
    """
    order = {
        "Patient Name": prescription.get("Patient Name", "Not Available"),
        "Diagnosis": prescription.get("Diagnosis", "Not Available"),
        "Medicines": []
    }
    
    for medicine in prescription.get("Prescription", []):
        medicine_name = medicine[0]
        dosage_instructions = medicine[1] if len(medicine) > 1 else "1/day for 7 days"  # Default dosage if unavailable
        dosage_count = medicine[2] if len(medicine) > 2 else 1  # Default dosage count if unavailable
        verification_result = verify_medicine(medicine_name)  # Verify the medicine
        
        if verification_result.get("status") == "found":
            # Medicine is found, add to order with dosage details
            order["Medicines"].append({
                "name": verification_result["info"]["big_name"],
                "dosage_instructions": dosage_instructions,
                "dosage_count": dosage_count,
                "status": "available"
            })
        else:
            # Medicine is not found, mark as not available
            order["Medicines"].append({
                "name": medicine_name,
                "dosage_instructions": dosage_instructions,
                "dosage_count": dosage_count,
                "status": "not available"
            })
    
    return order



# Example usage
