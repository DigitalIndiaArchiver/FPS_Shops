import asyncio
import aiohttp
import json
import os
import glob
import pandas as pd

# Asynchronous function to fetch data from a given URL
async def fetch_data(session, url):
    try:
        async with session.get(url) as response:
            response.raise_for_status()
            return await response.json()
    except aiohttp.ClientError as e:
        print(f"Error fetching data from {url}: {e}")
        return None

# Asynchronous function to fetch tehsils for a given state code
async def fetch_tehsils_for_state(session, state_code):
    url = f"https://impds.nic.in/sale/fairPriceShopDetails?statecode={state_code}"
    return await fetch_data(session, url)

# Asynchronous function to fetch shops for a given tehsil
async def fetch_shops_in_tehsil(session, state_code, district_code, tehsil_code):
    url = f"https://impds.nic.in/sale/FPSDetailsWebService?statecode={state_code}&distcode={district_code}&tehsilname={tehsil_code}"
    return await fetch_data(session, url)

# Main function to scrape all shops
async def scrape_all_shops():
    all_shops = []

    # Create an aiohttp session
    async with aiohttp.ClientSession() as session:
        tasks = []

        # Loop through state codes from 01 to 38
        for state_code in range(1, 39):
            state_code_str = f"{state_code:02}"
            print(f"Processing state code: {state_code_str}")

            # Fetch tehsils for the current state
            tehsils = await fetch_tehsils_for_state(session, state_code_str)
            if not tehsils:
                print(f"Failed to fetch tehsils for state code {state_code_str}")
                continue

            state_shops = []

            # Gather tasks to fetch shops for each tehsil in parallel
            for tehsil in tehsils:
                district_code = tehsil["districtCode"]
                tehsil_code = tehsil["tehsilcode"]
                tehsil_name = tehsil["tehsilname"]
                print(f"  Processing tehsil: {tehsil_name}")

                tasks.append(fetch_shops_in_tehsil(session, state_code_str, district_code, tehsil_code))

            # Run tasks in parallel
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            for result in results:
                if result:
                    state_shops.extend(result)

            # Save shops for the current state to a JSON file
            os.makedirs('states', exist_ok=True)
            state_filename = f"states/state_{state_code_str}_shops.json"
            with open(state_filename, "w", encoding="utf-8") as f:
                json.dump(state_shops, f, ensure_ascii=False, indent=4)
            print(f"Saved shops for state code {state_code_str} to {state_filename}")

            # Append state shops to all_shops list
            all_shops.extend(state_shops)

            # Clear tasks for the next state
            tasks.clear()

    return all_shops

# Function to combine JSON files into a CSV file
def combine_json_to_csv():
    json_files = glob.glob('./states/*.json')
    dfs = []

    for file in json_files:
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            df = pd.json_normalize(data)
            dfs.append(df)

    result = pd.concat(dfs, ignore_index=True)
    result.drop_duplicates(inplace=True)
    ordered_cols = ['fpsCode', 'fpsName', 'address', 'fpsowner', 'villageName', 'villageCode',
                    'tehsilName', 'tehsilCode', 'districtCode', 'districtName', 'stateCode', 
                    'stateName', 'latitude', 'longitude']
    result = result[ordered_cols]
    result.sort_values(by=['stateCode', 'districtCode', 'tehsilCode', 'villageCode','fpsCode'],
                       inplace=True, ascending=[True, True, True, True, True])
    result.to_csv('ConsolidatedShops.csv', index=False, encoding='utf-8')
    print(f"Data combined and saved to ConsolidatedShops.csv")

# Main entry point
if __name__ == "__main__":
    asyncio.run(scrape_all_shops())
    combine_json_to_csv()
