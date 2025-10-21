import os
import json
import time
import requests
from pathlib import Path
from tqdm import tqdm

class DownloadPlanet:

    ITEM_TYPE = "PSScene"
    ASSETS_TO_DOWNLOAD = [
        "ortho_analytic_8b_sr",  # surface reflectance GeoTIFF
        "ortho_udm2",  # data mask
        "ortho_analytic_8b_xml"  # metadata XML
    ]

    def __init__(self, OUTPUT_DIR, PLANET_API_KEY):
        self.OUTPUT_DIR = OUTPUT_DIR
        self.PLANET_API_KEY = PLANET_API_KEY


        if PLANET_API_KEY is None:
            raise ValueError("⚠️ Please set your Planet API key as environment variable 'PL_API_KEY'.")

        self.auth = (self.PLANET_API_KEY, "")

    def activate_asset(self,assets_url, asset_type):
        """Activate asset if needed."""
        r = requests.get(assets_url, auth=self.auth)
        r.raise_for_status()
        assets = r.json()

        asset_info = assets.get(asset_type)
        if not asset_info:
            print(f"❌ Asset {asset_type} not available at {assets_url}")
            return None

        if asset_info["status"] == "active":
            # Re-fetch to get 'location' link
            print(f"✅ Asset already active: {asset_type}, fetching location link...")
            r2 = requests.get(assets_url, auth=self.auth)
            r2.raise_for_status()
            refreshed_info = r2.json().get(asset_type, {})
            location = refreshed_info.get("location")
            if location:
                return location
            else:
                print(f"⚠️ No 'location' found yet for {asset_type}. Will wait.")
                return None

        print(f"🚀 Activating asset: {asset_type}")
        requests.post(asset_info["_links"]["activate"], auth=self.auth)
        return None


    def wait_until_active(self,assets_url, asset_type, timeout=600, interval=30):
        """Wait until asset is active, polling every interval seconds."""
        start = time.time()
        while time.time() - start < timeout:
            r = requests.get(assets_url, auth=self.auth)
            r.raise_for_status()
            status = r.json().get(asset_type, {}).get("status", "")
            if status == "active":
                return r.json()[asset_type]["_links"]["location"]
            print(f"⏳ Waiting for {asset_type} activation... ({status})")
            time.sleep(interval)
        print(f"⚠️ Timeout waiting for {asset_type} to activate.")
        return None


    def download_file(self,url, output_path):
        """Download a file with a progress bar."""
        with requests.get(url, stream=True, auth=self.auth) as r:
            r.raise_for_status()
            total_size = int(r.headers.get("content-length", 0))
            with open(output_path, "wb") as f, tqdm(
                total=total_size, unit="B", unit_scale=True, desc=output_path.name
            ) as pbar:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        pbar.update(len(chunk))


    def process_scene(self, scene):
        """Process one scene: activate + download SR and UDM2 assets."""
        scene_id = scene["id"]
        instrument = scene.get("properties", {}).get("instrument", "")
        if "PSB.SD" not in instrument:
            print(f"⚠️ Skipping {scene_id}: not SuperDove.")
            return

        assets_url = scene["_links"]["assets"]
        output_folder = Path(self.OUTPUT_DIR) / scene_id
        output_folder.mkdir(parents=True, exist_ok=True)

        print(f"\n📦 Processing scene: {scene_id}")

        for asset_type in self.ASSETS_TO_DOWNLOAD:
            output_path = output_folder / f"{scene_id}_{asset_type}.tif"
            if output_path.exists():
                print(f"⏭️ Skipping {asset_type}: already exists.")
                continue

            # Activate if needed
            location = self.activate_asset(assets_url, asset_type)
            if not location:
                location = self.wait_until_active(assets_url, asset_type)

            if not location:
                print(f"❌ Could not download {asset_type} for {scene_id}")
                continue

            # Download asset
            try:
                self.download_file(location, output_path)
                print(f"✅ Downloaded: {output_path}")
            except Exception as e:
                print(f"❌ Error downloading {asset_type} for {scene_id}: {e}")