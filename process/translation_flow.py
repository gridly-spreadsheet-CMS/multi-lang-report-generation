import os 
from bs4 import BeautifulSoup
import uuid
import pandas as pd

def extract(input, is_file=True, selectors=None):
    """
    Extracts text from specified HTML elements identified by CSS selectors.
    
    Args:
        input (str): Either a path to the HTML file or an HTML string.
        is_file (bool): Flag indicating whether the input is a file path (True) or HTML string (False).
        selectors (dict): Dictionary where each key-value pair represents the type ('tag', 'class', 'id') and their respective list of names.
    
    Returns:
        list of dict: List containing dictionaries with unique IDs and text content.
    """

    if not selectors:
        raise ValueError("The 'selectors' parameter is required and cannot be empty.")

    # Load HTML content from file or string
    if is_file:
        with open(input, 'r', encoding='utf-8') as file:
            html_content = file.read()
    else:
        html_content = input

    soup = BeautifulSoup(html_content, 'lxml')
    all_data = []

    # Process each selector type provided
    for selector_type, values in selectors.items():
        if selector_type in ['tags', 'classes', 'ids']:
            elements = []
            if selector_type == 'tags':
                elements = soup.find_all(values)
            elif selector_type == 'classes':
                elements = soup.find_all(class_=values)
            elif selector_type == 'ids':
                elements = [soup.find(id=value) for value in values if soup.find(id=value)]

            for element in elements:
                if element:
                    text = element.get_text(strip=True)
                    if text:
                        unique_id = str(uuid.uuid4())
                        all_data.append({'id': unique_id, 'content': text})
                        # Add or update the 'id' attribute in the HTML element
                        element['id'] = unique_id

    # Return the data and the modified HTML
    return all_data, str(soup)

def save_to_csv(data, file_name):
    df = pd.DataFrame(data)
    df.to_csv(file_name, index=False, encoding='utf-8')

def load_translations_by_language(translated_text_path, target_languages):
    translations_df = pd.read_csv(translated_text_path)
    language_dictionaries = {}
    for language in target_languages:
        if language in translations_df.columns:
            translations_dict = dict(zip(translations_df['id'], translations_df[language]))
            language_dictionaries[language] = translations_dict
        else:
            print(f"Warning: {language} column not found in CSV.")
    return language_dictionaries

def update_html_with_translations(html_content, translations_dict):
    soup = BeautifulSoup(html_content, 'html.parser')

    # Iterate over each item in the translations dictionary
    for element_id, translation in translations_dict.items():
        # Find element by ID
        element = soup.find(id=element_id)
        if element:
            # Check if translation is not NaN and is a string
            if pd.notna(translation):
                # Set the text of the element to the translation
                element.string = str(translation)
            else:
                print(f"No valid translation available for element with ID {element_id}. Skipping...")
        else:
            print(f"Element with ID {element_id} not found in the HTML.")

    # Convert the modified soup object back to a string
    updated_html_content = str(soup)
    return updated_html_content

def create_translated_html_files(source_html_path, translations_csv_path, output_directory, target_languages):
    # Load translations for all specified languages
    translations_by_language = load_translations_by_language(translations_csv_path, target_languages)
    
    # Read the source HTML file
    with open(source_html_path, 'r', encoding='utf-8') as file:
        html_content = file.read()
    
    paths = []
    # Generate a translated HTML file for each target language
    for language, translations_dict in translations_by_language.items():
        updated_html_content = update_html_with_translations(html_content, translations_dict)
        output_html_path = os.path.join(output_directory, f'{language.replace(' ', '_').lower()}_report.html')
        
        paths.append(output_html_path)

        with open(output_html_path, 'w', encoding='utf-8') as file:
            file.write(updated_html_content)
        
        print(f"Translated HTML file for {language} has been saved to {output_html_path}")

    return paths


