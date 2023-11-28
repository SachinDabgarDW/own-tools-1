import streamlit as st
import urllib.parse
import json
import requests
import simplejson as json
import sys
import os
import pdb
import gzip

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

def generate_crawl_command(job_id):
    try:

        headers = {
            'Accept': '*/*',
            'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8,es;q=0.7,de;q=0.6,zh-CN;q=0.5,zh;q=0.4,ja;q=0.3',
            'Authorization': 'b-ONRWQZLEOVWGK4TWGI5DEMJQGMZDAMRTHI======',
            'Connection': 'keep-alive',
            'Origin': 'http://console.dweave.net',
            'Referer': 'http://console.dweave.net/',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
        }
        job_id_api = f"http://schedulerv2.dweave.net/api/v1/parent-jobs?offset=0&limit=20&id={job_id}"

        resp = requests.get(job_id_api, headers=headers)
        print(resp)
        data = resp.json().get('results')[0]
        crawl_options = data.get('crawl_options', {})
        command =  f'python3.6 crawler_extractor.py -s {data.get("source")} -v {data.get("vertical")} --fresh_data --no_pagination --crawl_type {data.get("crawl_type")}  --test '
        if crawl_options.get('plugin'):
            command+="--plugin "
        if crawl_options.get('browser'):
            command+="--browser "+crawl_options.get('browser')+" "
        if crawl_options.get('variant'):
            command+="--variant "
        if crawl_options.get('ext_method'):
            command+="--ext_method "+crawl_options.get('ext_method')+' '
        if crawl_options.get('crawl_modes'):
            command+="--crawl_modes "
        if crawl_options.get('render_browser'):
            command+="--render_browser "
        if crawl_options.get('proxy'):
            command+="--proxy "+crawl_options.get('proxy')[0]+" "
        if crawl_options.get('with_session'):
            command+="--with_session "
        if crawl_options.get('no_country'):
            command+="--no_session "
        if crawl_options.get('proxy_country'):
            command+="--proxy_country "+crawl_options.get('proxy_country')+" "
        if crawl_options.get('plugin_options'):
            command+="--plugin_options '"+json.dumps(crawl_options.get('plugin_options'))+"' "
        print(command)
        seed_file_resp = requests.get(data.get('local_seed_file', ''), headers=headers)
        # url_dict = json.loads(gzip.decompress(seed_file_resp.content).decode().split('\n')[:4])

        # seed_file_path = f'/tmp/{data.get("source")}_{data.get("crawl_type")}.json'
        # seed_fl = open(seed_file_path, 'w+')
        # [seed_fl.write(line+'\n') for line in gzip.decompress(seed_file_resp.content).decode().split('\n')[:20]]
        # seed_fl.close()
        # command +=   f' --seed_file {seed_file_path}'
    except:
        return "Please check parent job-id"

    return command

def main():
    st.title("Web Tools")

    # Sidebar navigation
    selected_tab = st.sidebar.radio("Navigation", ["Cache URL Generator", "Number Converter", "Crawl Command Generator"])

    # Section 1: Link Generator
    if selected_tab == "Cache URL Generator":
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

    # Section 2: Number Converter
    elif selected_tab == "Number Converter":
        st.header("Number Converter")

        # Add a text input for entering the number or formatted string
        input_str = st.text_input("Enter a number or formatted string (Ex: 1k or 1000):")

        # Add a "Convert" button to perform the conversion
        if input_str:
            converted_number = convert_number_format(input_str)
            st.markdown(f"**Converted Result:** {converted_number}")

    # Section 3: Crawl Command Generator
    elif selected_tab == "Crawl Command Generator":
        st.header("Crawl Command Generator")

        # Add a text input for entering the Job ID
        job_id_input = st.text_input("Enter Job ID:")
        
        # Add a "Generate Command" button to generate the crawl command
        if job_id_input:
            crawl_command = generate_crawl_command(job_id_input)
            st.markdown("**Note:** Make sure to add --url by yourself. :wink:")
            st.markdown(f"**Crawl Command:** {crawl_command}")

    hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            footer:after {
                content:'Made with ❤️ by Sachin Dabgar'; 
                visibility: visible;
                position: relative;
                padding: 5px;
                text-align: center;
                top: 2px;
            }
            .st-emotion-cache-zq5wmm{
                display: none;
            }
            </style>
            """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True) 

if __name__ == "__main__":
    main()
