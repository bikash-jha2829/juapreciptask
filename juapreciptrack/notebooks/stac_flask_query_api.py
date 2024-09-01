from flask import Flask, jsonify, request, Response, abort
import pystac
from datetime import datetime
import json
from dateutil.parser import isoparse
import argparse
import sys

app = Flask(__name__)


def load_catalog(catalog_path):
    """
    Loads the STAC catalog from the provided file path.

    Parameters:
        catalog_path (str): The file path to the STAC catalog JSON.

    Returns:
        pystac.Catalog: The loaded STAC catalog object.
    """
    return pystac.Catalog.from_file(catalog_path)


# Parse command-line arguments
parser = argparse.ArgumentParser(description="Run a Flask API for querying a STAC catalog.")
parser.add_argument("--catalog", type=str, required=True, help="Path to the STAC catalog JSON file.")
args = parser.parse_args()

# Ensure a catalog path is provided, else exit with an error message
if not args.catalog:
    print("Error: No catalog path provided. Use --catalog to specify the catalog JSON file path.")
    sys.exit(1)

# Load the catalog using the provided path
catalog_path = args.catalog
catalog = load_catalog(catalog_path)


@app.route("/", methods=["GET"])
def root():
    """
    Root endpoint of the API. Returns a welcome message.

    Returns:
        JSON: A welcome message indicating the API is running.
    """
    return jsonify({"message": "Welcome to the STAC API with Flask"})


def generate_parquet_paths(datetime_range, h3_index):
    """
    Generates Parquet file paths that match the given H3 index and datetime range.

    Parameters:
        datetime_range (str): The datetime range for filtering items.
        h3_index (str): The H3 index for filtering items.

    Yields:
        str: The path to the Parquet file that matches the filters.
    """
    for child in catalog.get_children():
        collection_items = child.get_items()

        for item in collection_items:
            item_properties = item.properties
            item_h3_indexes = item_properties.get('h3_indexes', [])

            # Filter by H3 index presence
            if h3_index and h3_index not in item_h3_indexes:
                continue

            # Access datetime from item properties
            item_datetime_str = item_properties.get('datetime', None)
            if item_datetime_str:
                try:
                    item_datetime = isoparse(item_datetime_str)
                except ValueError:
                    print(f"Skipping item due to invalid datetime format: {item_datetime_str}")
                    continue
            else:
                print("Skipping item due to missing datetime.")
                continue

            # Filter by datetime range
            if datetime_range:
                start_date, end_date = datetime_range.split('/')
                start_date = isoparse(start_date)
                end_date = isoparse(end_date)

                if not (start_date <= item_datetime <= end_date):
                    print(f"Skipping item outside of datetime range: {item_datetime}")
                    continue

            # Yield the Parquet file path if all filters match
            if 'parquet' in item.assets:
                yield item.assets['parquet'].href

    print("No matching items found.")


@app.route("/search-parquet", methods=["GET"])
def search_parquet():
    """
    API endpoint to search for Parquet file paths based on a datetime range and H3 index.

    Query Parameters:
        datetime_range (str): The datetime range for filtering items.
        h3_index (str): The H3 index for filtering items.

    Returns:
        Response: A JSON array of Parquet file paths that match the filters.
    """
    datetime_range = request.args.get('datetime_range')
    h3_index = request.args.get('h3_index')

    def generate():
        first = True
        yielded_anything = False  # Track if anything was yielded
        yield '['
        for path in generate_parquet_paths(datetime_range, h3_index):
            if not first:
                yield ','
            yield json.dumps(path)
            first = False
            yielded_anything = True  # Mark that we've yielded a result
        if not yielded_anything:
            yield ''  # Handle the case where nothing was found to still complete the array
        yield ']'

    return Response(generate(), mimetype='application/json')


def generate_filtered_h3_indexes(datetime_range, min_precipitation, max_precipitation, filter_type):
    """
    Generates distinct H3 indexes that match the given datetime range and precipitation criteria.

    Parameters:
        datetime_range (str): The datetime range for filtering items.
        min_precipitation (float): The minimum precipitation for filtering items.
        max_precipitation (float): The maximum precipitation for filtering items.
        filter_type (str): The filter type to apply ('min' or 'max').

    Yields:
        str: A distinct H3 index that matches the filters.
    """
    distinct_h3_indexes = set()

    for child in catalog.get_children():
        collection_items = child.get_items()

        for item in collection_items:
            item_properties = item.properties
            item_h3_indexes = item_properties.get('h3_indexes', [])

            # Filter by H3 index presence
            if not item_h3_indexes:
                continue

            # Access datetime from item properties
            item_datetime_str = item_properties.get('datetime', None)
            if item_datetime_str:
                try:
                    item_datetime = isoparse(item_datetime_str)
                except ValueError:
                    continue
            else:
                continue

            # Filter by datetime range
            if datetime_range:
                start_date, end_date = datetime_range.split('/')
                start_date = isoparse(start_date)
                end_date = isoparse(end_date)

                if not (start_date <= item_datetime <= end_date):
                    continue

            # Determine if item meets precipitation criteria
            min_precip = item_properties.get('min_precipitation', None)
            max_precip = item_properties.get('max_precipitation', None)

            if filter_type == "min" and (min_precipitation is not None and min_precip is not None and min_precip > min_precipitation):
                continue
            if filter_type == "max" and (max_precipitation is not None and max_precip is not None and max_precip < max_precipitation):
                continue

            # Add distinct H3 indexes to the set
            for h3 in item_h3_indexes:
                distinct_h3_indexes.add(h3)

    for h3 in distinct_h3_indexes:
        yield h3


@app.route("/search-h3", methods=["GET"])
def search_h3():
    """
    API endpoint to search for distinct H3 indexes based on a datetime range and precipitation criteria.

    Query Parameters:
        datetime_range (str): The datetime range for filtering items.
        min_precipitation (float): The minimum precipitation for filtering items.
        max_precipitation (float): The maximum precipitation for filtering items.
        filter_type (str): The filter type to apply ('min' or 'max').

    Returns:
        Response: A JSON array of distinct H3 indexes that match the filters.
    """
    datetime_range = request.args.get('datetime_range')
    min_precipitation = request.args.get('min_precipitation', type=float)
    max_precipitation = request.args.get('max_precipitation', type=float)
    filter_type = request.args.get('filter_type', default='max')  # 'max' or 'min'

    def generate():
        first = True
        yielded_anything = False  # Track if anything was yielded
        yield '['
        for h3 in generate_filtered_h3_indexes(datetime_range, min_precipitation, max_precipitation, filter_type):
            if not first:
                yield ','
            yield json.dumps(h3)
            first = False
            yielded_anything = True  # Mark that we've yielded a result
        if not yielded_anything:
            yield ''  # Handle the case where nothing was found to still complete the array
        yield ']'

    return Response(generate(), mimetype='application/json')


if __name__ == "__main__":
    from werkzeug.serving import run_simple

    run_simple('localhost', 5000, app)
