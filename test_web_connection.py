import requests

# Replace these with actual values
token = "H9Y44LsA"
relative_path = "Spalt-1mm_2020-12-15_O2env-0p1Proz_Volt-10kV_Freq-1kHz_HVpw-1us_Flanke-SF_N2-299sccm_O2-0p3sccm_NrImages-25_Entl-EE_t0-0ns_Gate-500ns_Gain-200_MFIIc_fvar.npy"
url = f"http://127.0.0.1:8050/{token}?filename={relative_path}"

try:
    response = requests.get(url)
    response.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)
    
    # Save the received file
    with open("received_file.npy", "wb") as f:
        f.write(response.content)
    
    print(f"File received successfully. Status Code: {response.status_code}")
    print("File saved as 'received_file.npy'")
except requests.exceptions.RequestException as e:
    print(f"Request failed: {e}")
