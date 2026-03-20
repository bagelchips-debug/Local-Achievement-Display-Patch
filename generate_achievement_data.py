"""

## BE AWARE. RUNNING THIS RESETS THE 'chapter' ATTRIBUTE. 
## SORTING BY CHAPTER WILL FAIL IF achievement_data.rpy IS NOT MANUALLY EDITED TO INCLUDE CORRECT CHAPTER.
## USE https://steamcommunity.com/sharedfiles/filedetails/?id=2778007685 AS REFERENCE FOR CORRECT CHAPTER.


import requests
import os

STEAM_KEY = "" # Put your own Steam api key here
APP_ID = "1609230"
SAVE_DIR = "achievement_icons"
OUTPUT_FILE = "achievement_data.rpy"

os.makedirs(SAVE_DIR, exist_ok=True)

# Fetch achievement schema
url = f"https://api.steampowered.com/ISteamUserStats/GetSchemaForGame/v2/?key={STEAM_KEY}&appid={APP_ID}"

try:
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    data = response.json()
except Exception as e:
    print(f"Failed to fetch API data: {e}")
    exit()

achievements = data["game"]["availableGameStats"]["achievements"]

achievement_data = {}

for ach in achievements:
    key = ach["name"]

    name = ach.get("displayName", key)
    description = ach.get("description", "")
    icon_url = ach.get("icon")
    gray_url = ach.get("icongray")

    entry = {
        "name": name,
        "description": description,
        "image": None,
        "image_gray": None
    }

    # Download colored icon
    if icon_url:
        filename = os.path.join(SAVE_DIR, f"{key}.png")
        try:
            if not os.path.exists(filename):
                img_data = requests.get(icon_url, timeout=10).content
                with open(filename, "wb") as f:
                    f.write(img_data)
                print(f"Downloaded {filename}")
            entry["image"] = filename
        except Exception as e:
            print(f"Failed to download icon for {key}: {e}")

    # Download gray icon
    if gray_url:
        filename_gray = os.path.join(SAVE_DIR, f"{key}_gray.png")
        try:
            if not os.path.exists(filename_gray):
                img_data = requests.get(gray_url, timeout=10).content
                with open(filename_gray, "wb") as f:
                    f.write(img_data)
                print(f"Downloaded {filename_gray}")
            entry["image_gray"] = filename_gray
        except Exception as e:
            print(f"Failed to download gray icon for {key}: {e}")

    achievement_data[key] = entry

# Save as .rpy
with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
    file.write("init python:\n")
    file.write("    achievement_data = {\n")
    for key, entry in achievement_data.items():
        file.write(f'        "{key}": {{\n')
        file.write(f'            "name": "{entry["name"]}",\n')
        file.write(f'            "description": "{entry["description"]}",\n')
        # I currently cannot find a way to automatically find which chapter each achievement corresponds to.
        # After running this, achievement_data.rpy must be manually edited to include achievement chapter for sorting by chapter to work.
        file.write(f'            "chapter": "",\n') 
        file.write(f'            "image": "{entry["image"]}",\n')
        file.write(f'            "image_gray": "{entry["image_gray"]}",\n')
        file.write("        },\n")
    file.write("    }\n")
    file.write("\n")


print(f"\nSaved all data to {OUTPUT_FILE}")
print("Done!")

"""