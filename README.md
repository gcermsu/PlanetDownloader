# Planet Image Downloader
<img align="right" width="250" alt="Planet Image Downloader" src="https://github.com/user-attachments/assets/ae23f308-96f4-4968-ac77-a825a2d94718" />

Planet Image Downloader is a Python package that simplifies access to PlanetScope SuperDove imagery through the Planet Data API. It provides two main functions:

- Search — query and retrieve metadata of Planet images that intersect a custom area of interest (AOI) within a specific date range.
- Download — automatically activate and download selected assets (e.g., surface reflectance, UDM2 mask, metadata XML) from the search results.

✨ **Features**
  - 🛰️ Search SuperDove images by polygon geometry (GeoJSON or GeoPackage)
  - 🗓️ Filter by date range, cloud cover, and minimum intersection percentage
  - 📦 Retrieve image metadata as a structured JSON file
  - 💾 Download selected assets (e.g., ortho_analytic_8b_sr, ortho_udm2, ortho_analytic_8b_xml)
  - ⚙️ Handles activation and waiting automatically (Planet’s assets must be “activated” before download)
  - 🧭 Output files in GeoTIFF and XML, ready for GIS or machine learning workflows

## Usage

The package requires specific input parameters to run. Below is a list of required parameters and their descriptions. An example of how to use the package is provided in the usage_example folder.

**Input Parameters**

  *- Planet API Key*: To access the Planet API, you need a valid Planet account and API key..

  *- AOI*: Polygon related to the area of interest. The file format can be shp or gpkg.

  *- initial_date*: The starting date for analysis (format: YYYYMMDD).

  *- end_date*: The ending date for analysis (format: YYYYMMDD).

  *- output_directory*: Directory where the processed outputs will be saved.

  *- assets*: Planet assets to be downloaded (https://docs.planet.com/data/imagery/planetscope/).

## Dependencies management and package installation
If you prefer to use an existing conda environment, you can activate it and then install the pacereader package in development mode. This allows you to make changes to the code and test them without needing to reinstall the package. Run the following command from the root of the repository:
```
pip install -e .
```
Alternatively, you can install the package directly from GitHub using the command:
```
pip install git+https://github.com/thaimunhoz/Planet_download
```
