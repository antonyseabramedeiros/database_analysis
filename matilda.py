# audit_request.py
import json


def get_audit_request(config_path="config.json"):
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)
    return config.get("audit_request", "schema_design_flaws")


# database_connection.py
import pyodbc

def connect_to_database(server, database, user, password):
    conn_str = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={server};DATABASE={database};UID={user};PWD={password}"
    )
    return pyodbc.connect(conn_str)


def get_database_metadata(connection):
    cursor = connection.cursor()
    query = '''SELECT TABLE_NAME, COLUMN_NAME, DATA_TYPE, IS_NULLABLE,
                      COLUMN_DEFAULT, COLLATION_NAME
               FROM INFORMATION_SCHEMA.COLUMNS'''
    cursor.execute(query)
    return cursor.fetchall()


# metadata_extractor.py

def extract_metadata(raw_metadata):
    tables = {}
    for row in raw_metadata:
        table, column, dtype, nullable, default, collation = row
        if table not in tables:
            tables[table] = []
        tables[table].append({
            "column": column,
            "data_type": dtype,
            "nullable": nullable,
            "default": default,
            "collation": collation
        })
    return tables


# prompt_library.py

def get_prompt_templates():
    return {
        "naming_conventions": "...",
        "missing_keys": "...",
        "data_type_issues": "...",
        "data_integrity_issues": "...",
        "data_standardization": "...",
        "outliers_detection": "...",
        "normalization_issues": "...",
        "data_accuracy": "...",
        "schema_design_flaws": "...",
        "entity_duplication": "..."
    }


# dynamic_prompt_generator.py
from prompt_library import get_prompt_templates

def generate_prompt(model_schema, audit_request):
    prompts = get_prompt_templates()

    if audit_request in prompts:
        prompt = prompts[audit_request]
    elif audit_request == "naming_and_keys_audit":
        prompt = prompts["naming_conventions"] + "\n" + prompts["missing_keys"]
    elif audit_request == "full_audit":
        prompt = "\n\n".join(prompts.values())
    else:
        prompt = prompts["schema_design_flaws"]

    return prompt.format(model=model_schema)


# llm_analyzer.py
import openai

def analyze_schema_with_llm(prompt, api_key):
    openai.api_key = api_key
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content


# report_generator.py

def generate_audit_report(llm_response):
    with open("audit_report.txt", "w", encoding="utf-8") as f:
        f.write(llm_response)


# main.py
from audit_request import get_audit_request
from database_connection import connect_to_database, get_database_metadata
from metadata_extractor import extract_metadata
from dynamic_prompt_generator import generate_prompt
from llm_analyzer import analyze_schema_with_llm
from report_generator import generate_audit_report


def main():
    audit_request = get_audit_request()
    print(f"Starting audit: {audit_request}")

    server = 'localhost'
    database = 'YourDB'
    user = 'your_user'
    password = 'your_password'
    api_key = 'your_openai_api_key'

    conn = connect_to_database(server, database, user, password)
    raw_metadata = get_database_metadata(conn)
    model_schema = extract_metadata(raw_metadata)

    formatted_schema = ""
    for table, columns in model_schema.items():
        formatted_schema += f"Tabela: {table}\nColunas:\n"
        for col in columns:
            formatted_schema += f"  - Nome: {col['column']}, Tipo: {col['data_type']}, Nula: {col['nullable']}, Default: {col['default']}, Collation: {col['collation']}\n"
        formatted_schema += "\n"

    prompt = generate_prompt(formatted_schema, audit_request)
    response = analyze_schema_with_llm(prompt, api_key)
    generate_audit_report(response)


if __name__ == "__main__":
    main()
