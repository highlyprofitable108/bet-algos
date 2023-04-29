import os
import csv
import json
import xml.etree.ElementTree as ET
from typing import List, Dict
from bs4 import BeautifulSoup
import pandas as pd


def read_html_file(file_path: str) -> List[Dict[str, str]]:
    """
    Reads and parses data from an HTML file.

    Args:
        file_path: A string representing the path to the HTML file.

    Returns:
        A list of dictionaries representing the parsed data.
    """
    with open(file_path, 'r') as file:
        soup = BeautifulSoup(file, 'html.parser')
        table = soup.find('table')
        headers = [header.text.strip() for header in table.find_all('th')]
        data = [{headers[i]: cell.text.strip() for i, cell in enumerate(row.find_all('td'))} for row in table.find_all('tr')[1:]]
        return data


def read_csv_file(file_path: str) -> List[Dict[str, str]]:
    """
    Reads and parses data from a CSV file.

    Args:
        file_path: A string representing the path to the CSV file.

    Returns:
        A list of dictionaries representing the parsed data.
    """
    with open(file_path, 'r') as file:
        reader = csv.DictReader(file)
        return [row for row in reader]


def read_xls_file(file_path: str) -> List[Dict[str, str]]:
    """
    Reads and parses data from an XLS file.

    Args:
        file_path: A string representing the path to the XLS file.

    Returns:
        A list of dictionaries representing the parsed data.
    """
    data = pd.read_excel(file_path)
    return data.to_dict(orient='records')


def read_json_file(file_path: str) -> List[Dict[str, str]]:
    """
    Reads and parses data from a JSON file.

    Args:
        file_path: A string representing the path to the JSON file.

    Returns:
        A list of dictionaries representing the parsed data.
    """
    with open(file_path, 'r') as file:
        data = json.load(file)
        return data


def read_xml_file(file_path: str) -> List[Dict[str, str]]:
    """
    Reads and parses data from an XML file.

    Args:
        file_path: A string representing the path to the XML file.

    Returns:
        A list of dictionaries representing the parsed data.
    """
    tree = ET.parse(file_path)
    root = tree.getroot()
    data = [{child.tag: child.text for child in node.getchildren()} for node in root]
    return data


def read_data_file(file_path: str) -> List[Dict[str, str]]:
    """
    Reads and parses data from a file.

    Args:
        file_path: A string representing the path to the data file.

    Returns:
        A list of dictionaries representing the parsed data.

    Raises:
        ValueError: If the file does not exist or the file format is unsupported.
    """
    if not os.path.exists(file_path):
        raise ValueError(f"File does not exist: {file_path}")

    file_extension = os.path.splitext(file_path)[1].lower()

    if file_extension == '.html':
        return read_html_file(file_path)
    elif file_extension == '.csv':
        return read_csv_file(file_path)
    elif file_extension in ['.xls', '.xlsx']:
        return read_xls_file(file_path)
    elif file_extension ==
