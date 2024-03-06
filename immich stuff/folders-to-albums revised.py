import requests
import os
from collections import defaultdict

# I have photos in subfolders like :
# /mnt/media/Photos/2023-08 Holidays
# /mnt/media/Photos/2023-06 Birthday
# /mnt/media/Photos/2022-12 Christmas
# This script will create 3 albums
# 2023-08 Holidays, 2023-06 Birthday, 2022-12 Christmas
# And populate them with the photos inside
# The script can be run multiple times to update, new albums will be created,
# or new photos added in existing subfolder will be added to corresponding album

# Personnalize here
root_path = "/opt/"
root_url = "http://localhost:2283/api/"
api_key = "Dt5IZ6CWym0BaU2K1ouG5fts50cEubxnknTJrxA4j4"
SPLIT_ALBUMS = True  # if True, will create albums for each subfolder too
# /mnt/albums/2022/birthday
# /mnt/albums/2022/vacation
# /mnt/albums/2023/birthday
# /mnt/albums/2023/vacation
# SPLIT_ALBUMS = True will create 6 total albums : 2022, 2022/birthday, 2022/vacation, 2023, 2023/birthday, 2023/vacation


requests_kwargs = {
    "headers": {
        "x-api-key": api_key,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
}
if root_path[-1] != "/":
    root_path = root_path + "/"
if root_url[-1] != "/":
    root_url = root_url + "/"


print("  1. Requesting all assets")
r = requests.get(root_url + "asset", **requests_kwargs)
assert r.status_code == 200
assets = r.json()
print(len(assets), "photos found")


print("  2. Sorting assets to corresponding albums using folder name")
album_to_assets = defaultdict(list)
for asset in assets:
    asset_path = asset["originalPath"]
    if root_path not in asset_path:
        continue
    album_name = asset_path.replace(root_path, "").split("/")[0]
    album_to_assets[album_name].append(asset["id"])
    if SPLIT_ALBUMS == True:
        album_name_split = "/".join(asset_path.replace(root_path, "").split("/")[:2])
        album_to_assets[album_name_split].append(asset["id"])

album_to_assets = {
    k: v for k, v in sorted(album_to_assets.items(), key=(lambda item: item[0]))
}

print(len(album_to_assets), "albums identified")
print(list(album_to_assets.keys()))
print("Press Enter to continue, Ctrl+C to abort")
input()


album_to_id = {}

print("  3. Listing existing albums on immich")
r = requests.get(root_url + "album", **requests_kwargs)
assert r.status_code == 200
albums = r.json()
album_to_id = {album["albumName"]: album["id"] for album in albums}
print(len(albums), "existing albums identified")


print("  4. Creating albums if needed")
cpt = 0
for album in album_to_assets:
    if album in album_to_id:
        continue
    data = {"albumName": album, "description": album}
    r = requests.post(root_url + "album", json=data, **requests_kwargs)
    assert r.status_code in [200, 201]
    album_to_id[album] = r.json()["id"]
    print(album, "album added!")
    cpt += 1
print(cpt, "albums created")


print("  5. Adding assets to albums")
# Note: immich manage duplicates without problem,
# so we can each time ad all assets to same album, no photo will be duplicated
for album, assets in album_to_assets.items():
    id = album_to_id[album]
    data = {"ids": assets}
    r = requests.put(root_url + f"album/{id}/assets", json=data, **requests_kwargs)
    assert r.status_code in [200, 201]
    response = r.json()

    cpt = 0
    for res in response:
        if not res["success"]:
            if res["error"] != "duplicate":
                print("Warning, error in adding an asset to an album:", res["error"])
        else:
            cpt += 1
    if cpt > 0:
        print(f"{str(cpt).zfill(3)} new assets added to {album}")

print("Done!")
