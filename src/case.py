import sqlite3
from datetime import datetime, timedelta
import os
import time


conn = None
cursor = None

# Max retries for failed connections
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds


def recreate_connection():
    """Recreate the SQLite connection and cursor."""
    global conn, cursor
    if conn:
        conn.close()
    conn = sqlite3.connect(':memory:')  # Adjust this if you're using a file-based DB
    cursor = conn.cursor()


def retry_on_failure(func):
    """Decorator to retry a function if the connection fails."""
    def wrapper(*args, **kwargs):
        retries = 0
        while retries < MAX_RETRIES:
            try:
                return func(*args, **kwargs)
            except sqlite3.OperationalError as e:
                print(f"Error: {e}. Retrying {retries + 1}/{MAX_RETRIES}...")
                retries += 1
                recreate_connection()  # Recreate connection and cursor
                time.sleep(RETRY_DELAY)
        raise Exception("Max retries reached. Operation failed.")
    return wrapper


# Define the Case entity
class Case:
    def __init__(self, case_name, docs, raw_text, user_id, processed_output, additional_details=None, upload_date=None):
        self.case_name = case_name
        self.docs = docs
        self.raw_text = raw_text.encode('utf-8')  # Convert raw_text to bytes
        self.user_id = user_id
        self.processed_output = processed_output
        self.additional_details = additional_details
        self.upload_date = upload_date or datetime.now()


# Define the RelatedCase entity
class RelatedCase:
    def __init__(self, file_name, base_path='related_cases/'):
        self.file_name = file_name
        self.base_path = base_path
        self.case_data = self.load_case_data(file_name)

    def load_case_data(self, file_name):
        """Load case data from a file in the relative path."""
        file_path = os.path.join(self.base_path, file_name)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File {file_path} not found")

        with open(file_path, 'r') as file:
            data = file.read()
        return data


# Define the PastJudgment entity
class PastJudgment:
    def __init__(self, file_name, base_path='past_judgments/'):
        self.file_name = file_name
        self.base_path = base_path
        self.judgment_data = self.load_judgment_data(file_name)

    def load_judgment_data(self, file_name):
        """Load judgment data from a file in the relative path."""
        file_path = os.path.join(self.base_path, file_name)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File {file_path} not found")

        with open(file_path, 'r') as file:
            data = file.read()
        return data


def boot():
    recreate_connection()

    # Create tables for cases, related cases, and past judgments
    cursor.execute('''
        CREATE TABLE cases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_name TEXT NOT NULL,
            docs BLOB,
            raw_text BLOB,
            user_id INTEGER,
            processed_output TEXT,
            additional_details TEXT,
            upload_date TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE related_cases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_id INTEGER,
            file_name TEXT,
            case_data TEXT,
            FOREIGN KEY (case_id) REFERENCES cases(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE past_judgments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_id INTEGER,
            file_name TEXT,
            judgment_data TEXT,
            FOREIGN KEY (case_id) REFERENCES cases(id)
        )
    ''')


def close_connection():
    global conn
    if conn:
        conn.close()


# Retry applied to the following database-related functions

@retry_on_failure
def insert_case(case):
    cursor.execute('''
        INSERT INTO cases (case_name, docs, raw_text, user_id, processed_output, additional_details, upload_date)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (case.case_name, case.docs, case.raw_text, case.user_id, case.processed_output, case.additional_details,
          case.upload_date.strftime('%Y-%m-%d')))
    conn.commit()
    return cursor.lastrowid  # Return the id of the inserted case


@retry_on_failure
def update_additional_details(case_id, additional_details):
    cursor.execute('''
        UPDATE cases SET additional_details = ? WHERE id = ?
    ''', (additional_details, case_id))
    conn.commit()


@retry_on_failure
def update_processed_output(case_id, processed_output):
    cursor.execute('''
        UPDATE cases SET processed_output = ? WHERE id = ?
    ''', (processed_output, case_id))
    conn.commit()


@retry_on_failure
def insert_related_case(related_case, case_id):
    cursor.execute('''
        INSERT INTO related_cases (case_id, file_name, case_data)
        VALUES (?, ?, ?)
    ''', (case_id, related_case.file_name, related_case.case_data))
    conn.commit()


@retry_on_failure
def insert_past_judgment(past_judgment, case_id):
    cursor.execute('''
        INSERT INTO past_judgments (case_id, file_name, judgment_data)
        VALUES (?, ?, ?)
    ''', (case_id, past_judgment.file_name, past_judgment.judgment_data))
    conn.commit()


@retry_on_failure
def fetch_cases_last_5_days_by_user(user_id):
    five_days_ago = datetime.now() - timedelta(days=5)
    cursor.execute('''
        SELECT * FROM cases WHERE upload_date >= ? AND user_id = ?
    ''', (five_days_ago.strftime('%Y-%m-%d'), user_id))
    return cursor.fetchall()


@retry_on_failure
def get_related_cases(case_id):
    cursor.execute('''
        SELECT * FROM related_cases WHERE case_id = ?
    ''', (case_id,))
    return cursor.fetchall()


@retry_on_failure
def get_past_judgments(case_id):
    cursor.execute('''
        SELECT * FROM past_judgments WHERE case_id = ?
    ''', (case_id,))
    return cursor.fetchall()

@retry_on_failure
def get_case_by_id(case_id):
    cursor.execute('''
        SELECT * FROM cases WHERE id = ?
    ''', (case_id,))
    case = cursor.fetchone()  # Fetch a single result
    if case:
        case_dict = {
            'id': case[0],
            'case_name': case[1],
            'docs': case[2],
            'raw_text': case[3],
            'user_id': case[4],
            'processed_output': case[5],
            'additional_details': case[6],
            'upload_date': case[7]
        }
        return case_dict
    else:
        return None


# Main function to drive the program
def main():
    # Example usage: Create a new Case
    case1 = Case('Case A', b'document content', 'raw case text', 1, 'initial processed output')
    case_id = insert_case(case1)

    # Load related cases from files in the "related_cases" folder
    related_case1 = RelatedCase('case1.txt', base_path='../related_cases/')  # Replace with actual file path
    related_case2 = RelatedCase('case2.txt', base_path='../related_cases/')
    insert_related_case(related_case1, case_id)
    insert_related_case(related_case2, case_id)

    print(get_case_by_id(case_id))

    # Load past judgments from files in the "past_judgments" folder
    past_judgment1 = PastJudgment('judgment_file1.txt', base_path='../past_judgments/')  # Replace with actual file path
    past_judgment2 = PastJudgment('judgment_file2.txt', base_path='../past_judgments/')
    insert_past_judgment(past_judgment1, case_id)
    insert_past_judgment(past_judgment2, case_id)

    # Update additional details for case1
    update_additional_details(case_id, "This case involves a high-profile contract dispute.")

    # Update processed output for case1
    update_processed_output(case_id, "updated processed output.")

    # Fetch related cases for case1
    related_cases = get_related_cases(case_id)
    print(f"Related cases for Case ID {case_id}:")
    for related_case in related_cases:
        print(related_case)

    # Fetch past judgments for case1
    past_judgments = get_past_judgments(case_id)
    print(f"Past judgments for Case ID {case_id}:")
    for past_judgment in past_judgments:
        print(past_judgment)

    # Fetch cases from the last 5 days for user_id = 1
    recent_cases = fetch_cases_last_5_days_by_user(1)
    print("Recent cases for user ID 1:")
    for recent_case in recent_cases:
        print(recent_case)


if __name__ == '__main__':
    boot()
    main()
    close_connection()
