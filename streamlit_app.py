import streamlit as st
import urllib.parse
import json
import requests
import json
import sys
import os
import pdb
import gzip
import base64

def generate_link(json_data):
    base_url = "http://api.cache.dweave.net/cache/?path="
    
    # Customize the parameters based on your JSON structure
    params = {
        "urlh": json_data["seed_urlh"],
        "crawl_type": json_data["crawl_type"],
        "crawl_time": json_data["crawl_time"],
        "source": json_data["source"],
    }

    dump_files = json_data.get("dump_files")
    temp = []
    for file in dump_files:
        d = {}
        tag = file.get("tag")
        path = file.get("path")
        bytes_data = path.encode('utf-8')
        base64_encoded = base64.b64encode(bytes_data)
        encoded_string = base64_encoded.decode('utf-8')
    # Encode the parameters and concatenate them to the base URL
        link = base_url + encoded_string
        d["tag"] = tag
        d["link"] = link
        temp.append(d)
        
    return temp

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


def generate_proxy_info():
    proxy_list = []
    country_dict = {}
    proxy_url = 'https://redash.dataweave.com/api/queries/415/results.json?api_key=iS3EUyIIjOBkfLFT4ndXvy4kKE7o07GnR40U9c1b'
    country_provider_url = 'http://api.crawl-modes.dweave.net/workflow/proxy_countries/?proxy_provider='

    resp = requests.get(proxy_url)
    jresp = eval(resp.content)
    for each in jresp['query_result']['data']['rows']:
        proxy_list.append(each.get('proxy_provider'))

    print('total number of proxies found is ' + str(len(proxy_list)) + '\n')

    for each in proxy_list:
        try:
            proxy_name = each
            proxy_resp = requests.get(country_provider_url + proxy_name)
            if proxy_resp.json().get('data') != []:
                country_data = proxy_resp.json().get('data')
                for each in country_data:
                    country = each.get('country_id')
                    country_count = each.get('country_count')
                    if country not in country_dict:
                        country_dict[country] = {}
                    if proxy_name in country_dict[country]:
                        country_dict[country][proxy_name] += country_count
                    else:
                        country_dict[country][proxy_name] = country_count
        except Exception as e:
            print(e)

    with open('/tmp/country_dict.json', 'w+') as file:
        json.dump(country_dict, file)

    return country_dict

def get_proxy_info(proxy_country, use_proxy_file):
    try:

        if not os.path.exists('/tmp/country_dict.json'):
            generate_proxy_info()

        if  not use_proxy_file:
            generate_proxy_info()

        country_dict = json.load(open('/tmp/country_dict.json', 'r'))
        if proxy_country not in country_dict:
            return f"Country not found: {proxy_country}"

        proxy_info = country_dict[proxy_country]
        return json.dumps(proxy_info, indent=2)
    except Exception as e:
        return str(e)

def main():
    st.title("Web Tools")

    # Sidebar navigation
    selected_tab = st.sidebar.radio("Navigation", ["Cache URL Generator", "Number Converter", "Crawl Command Generator", "Proxy Info"])

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
                    for i in link:
                        tag = i.get("tag")
                        link = i.get("link")
                        st.markdown(f"**Tag:** {tag}")
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
            with st.spinner("Generating crawl command... Please wait."):
                crawl_command = generate_crawl_command(job_id_input)
                st.markdown("**Note:** Make sure to add --url by yourself. :wink:")
                st.markdown(f"**Crawl Command:**")
                st.code(crawl_command)
    
    # Section 4: Proxy Information
    elif selected_tab == "Proxy Info":
        st.header("Proxy Information")

        use_proxy_file = st.checkbox("Use Proxy Data from File", True)

        # Add a text input for entering the proxy country
        proxy_country_input = st.text_input("Enter Proxy Country:")

        # Add a "Get Proxy Info" button to retrieve proxy information
        
        if proxy_country_input:
            with st.spinner("Generating Proxy Information... Please wait."):
                proxy_info = get_proxy_info(proxy_country_input, use_proxy_file)

            st.markdown(f"**Proxy Information for {proxy_country_input}:**")
            st.code(proxy_info, language="json")

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
                font-size: 20px;
                font-weight: 900;
            }
            .st-emotion-cache-zq5wmm{
                display: none;
            }
            </style>
            """
    # st.markdown(hide_streamlit_style, unsafe_allow_html=True) 

if __name__ == "__main__":
    main()
