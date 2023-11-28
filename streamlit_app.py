import streamlit as st
import urllib.parse
import json

def generate_link(json_data):
    base_url = "http://api.cache.dweave.net/cache/?"
    
    # Customize the parameters based on your JSON structure
    params = {
        "urlh": json_data["seed_urlh"],
        "crawl_type": json_data["crawl_type"],
        "crawl_time": json_data["crawl_time"],
        "source": json_data["source"],
    }

    # Encode the parameters and concatenate them to the base URL
    link = base_url + urllib.parse.urlencode(params)
    return link

def convert_number_format(input_str):
    try:

        if input_str[-1].upper() in ('K', 'M', 'B', 'T'):
            multiplier = {'K': 1e3, 'M': 1e6, 'B': 1e9, 'T': 1e12}[input_str[-1].upper()]
            return str(int(float(input_str[:-1]) * multiplier))
        
        number = float(input_str)
        suffix = ''

        if number >= 1e12:
            number /= 1e12
            suffix = 'T'
        elif number >= 1e9:
            number /= 1e9
            suffix = 'B'
        elif number >= 1e6:
            number /= 1e6
            suffix = 'M'
        elif number >= 1e3:
            number /= 1e3
            suffix = 'K'

        formatted_number = f"{number:.2f}{suffix}" if suffix else str(number)
        return formatted_number
    except ValueError:
        return "Invalid input"

def main():
    st.title("Web Tools")

    # Section 1: Link Generator
    st.header("Cache URL Generator")

    # Add a text area for pasting JSON data
    json_data_str = st.text_area("Paste JSON data here:")

    try:
        if json_data_str:
        # Try to parse the JSON data
            json_data = json.loads(json_data_str)
            # If JSON data is provided, generate and display the link
            if json_data:
                link = generate_link(json_data)
                st.markdown(f"**Generated Link:** {link}")
    except json.JSONDecodeError:
        st.error("Invalid JSON format. Please provide valid JSON data.")
        return

    st.header("Number Converter")

    # Add a text input for entering the number or formatted string
    input_str = st.text_input("Enter a number or formatted string (Ex: 1k or 1000):")

    # Add a "Convert" button to perform the conversion
    if input_str:
        converted_number = convert_number_format(input_str)
        st.markdown(f"**Converted Result:** {converted_number}")

if __name__ == "__main__":
    main()