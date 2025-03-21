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
        "naming_conventions": '''
You are a database assistant specialized in naming conventions.
Analyze table and column names for unclear abbreviations, inconsistent naming patterns, or non-standard practices (e.g., use of generic names like "a1", "Data1", "Temp").
For each problem, suggest improved names and provide example DDL statements using `sp_rename`.

Model: {model}
''',

        "missing_keys": '''
You are a database assistant focused on identifying missing PRIMARY or FOREIGN KEY constraints.
Check if tables lack a PRIMARY KEY or if columns likely representing relationships (e.g., UserID, PasswordID) are missing FOREIGN KEY constraints.
Suggest constraint definitions and include appropriate DDL statements.

Model: {model}
''',

        "data_type_issues": '''
You are a database assistant auditing data types.
Identify columns with inappropriate data types (e.g., storing dates as VARCHAR, overly large text fields, use of IMAGE or VARBINARY unnecessarily).
For each issue, suggest better types and provide DDL corrections.

Model: {model}
''',

        "data_integrity_issues": '''
You are a database assistant evaluating data integrity.
Detect columns that allow NULLs but likely should not, missing NOT NULL constraints, missing UNIQUE constraints, or inappropriate default values.
Suggest changes to improve integrity and provide DDL commands.

Model: {model}
''',

        "data_standardization": '''
You are a database assistant focused on data standardization.
Analyze if column data types and collations are consistent across similar entities. Look for inconsistent formats (e.g., VARCHAR vs NVARCHAR, mixed collations).
Recommend standard data types, collation usage, and any DDL corrections.

Model: {model}
''',

        "outliers_detection": '''
You are a database assistant helping to detect potential schema-driven outliers or anomalies.
Review column naming, structure, and types that may indicate unusual or inconsistent patterns compared to other tables.
Highlight schema irregularities and propose DDL adjustments or further inspection.

Model: {model}
''',

        "normalization_issues": '''
You are a database assistant specialized in normalization.
Review the database schema for possible violations of normalization principles (1NF, 2NF, 3NF).
Identify attributes that could be decomposed, duplicated data across tables, or poor table separation.
Suggest schema redesign or normalization improvements with examples.

Model: {model}
''',

        "data_accuracy": '''
You are a database assistant checking for schema choices that may lead to inaccurate data.
Detect poor data types, missing constraints, weak relationships, or default values that can lead to inaccuracies.
Suggest appropriate fixes and DDL updates.

Model: {model}
''',

        "schema_design_flaws": '''
You are a database assistant reviewing general schema design flaws.
Identify overly coupled tables, lack of modularity, excessive reliance on nullable fields, unnecessary complexity, or flat design.
Provide recommendations and DDL-based improvements where possible.

Model: {model}
''',

        "entity_duplication": '''
You are a database assistant detecting possible entity duplication.
Analyze the schema to find columns or tables that repeat entity-related information (e.g., multiple tables storing similar fields for users or documents).
Suggest merging entities or normalizing the design and provide DDL examples where applicable.

Model: {model}
'''
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
