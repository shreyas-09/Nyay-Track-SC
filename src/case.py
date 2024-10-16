import sqlite3
from datetime import datetime, timedelta
import os

conn = None
cursor = None

# Define the Case entity
class Case:
    def __init__(self, case_name, docs, raw_text, user_id, processed_output, additional_details=None, defects=None, entity_list=None, upload_date=None, defects_score=None, timeline=None, category=None, sub_category=None, past=None, related=None):
        self.case_name = case_name
        self.docs = docs
        self.raw_text = raw_text.encode('utf-8')  # Convert raw_text to bytes
        self.user_id = user_id
        self.processed_output = processed_output
        self.additional_details = additional_details
        self.defects = defects
        self.entity_list = entity_list
        self.upload_date = upload_date or datetime.now()
        self.defects_score = defects_score
        self.timeline = timeline
        self.category = category
        self.sub_category = sub_category
        self.past = past
        self.related = related


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

# Function to handle reconnection in case of failures
def retry_on_failure(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (sqlite3.OperationalError, sqlite3.DatabaseError):
            print("Database connection failed. Attempting to reconnect...")
            boot()  # Reboot the connection
            return func(*args, **kwargs)
    return wrapper

# Function to create the table
def boot():
    # Create an in-memory SQLite database
    global conn, cursor
    conn = sqlite3.connect('cases.db', check_same_thread = False)
    # conn = sqlite3.connect(':memory:', check_same_thread = False)
    
    cursor = conn.cursor()

    # Create the cases table with defects and entity_list
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS cases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        case_name TEXT NOT NULL,
        docs BLOB,
        raw_text BLOB,
        user_id INTEGER,
        processed_output TEXT,
        additional_details TEXT,
        defects TEXT,  
        entity_list TEXT,
        upload_date TEXT,
        defects_score TEXT,
        timeline TEXT,
        category TEXT,
        sub_category TEXT,
        past TEXT,
        related TEXT
    )
    ''')


    # Create tables for related cases and past judgments
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS related_cases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_id TEXT,
            file_name TEXT,
            case_data TEXT,
            FOREIGN KEY (case_id) REFERENCES cases(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS past_judgments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_id TEXT,
            file_name TEXT,
            judgment_data TEXT,
            FOREIGN KEY (case_id) REFERENCES cases(id)
        )
    ''')

# Close the connection
def close_connection():
    if conn:
        conn.close()

# Function to insert a case into the database
def insert_case(case):
    cursor.execute('''
        INSERT INTO cases (case_name, docs, raw_text, user_id, processed_output, additional_details, defects, entity_list, upload_date, defects_score, timeline, category, sub_category, past, related)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (case.case_name, case.docs, case.raw_text, case.user_id, case.processed_output, case.additional_details,
          case.defects, case.entity_list, case.upload_date, case.defects_score, case.timeline,
          case.category, case.sub_category, case.past, case.related))
    conn.commit()
    return cursor.lastrowid  # Return the id of the inserted case

# Function to get case details by ID, including defects and entity_list
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
            'defects': case[7],  # New field
            'entity_list': case[8],  # New field
            'upload_date': case[9]
        }
        return case_dict
    else:
        return None

@retry_on_failure
def get_cases_by_user_id(user_id):
    cursor.execute('''
        SELECT * FROM cases WHERE user_id = ?
    ''', (user_id,))
    cases = cursor.fetchall()

    if cases:
        case_list = []
        for case in cases:
            case_dict = {
                'id': case[0],
                'case_name': case[1],
                'docs': case[2],
                'raw_text': case[3],
                'user_id': case[4],
                'processed_output': case[5],
                'additional_details': case[6],
                'defects': case[7],  # New field
                'entity_list': case[8],  # New field
                'upload_date': case[9]
            }
            case_list.append(case_dict)
        return case_list
    else:
        return None

@retry_on_failure
def get_last_5_cases_by_user_id(user_id):
    cursor.execute('''
        SELECT * FROM cases WHERE user_id = ? ORDER BY upload_date DESC LIMIT 5
    ''', (user_id,))
    cases = cursor.fetchall()

    if cases:
        case_list = []
        for case in cases:
            case_dict = {
                'id': case[0],
                'case_name': case[1],
                'docs': case[2],
                'raw_text': case[3],
                'user_id': case[4],
                'processed_output': case[5],
                'additional_details': case[6],
                'defects': case[7],  # New field
                'entity_list': case[8],  # New field
                'upload_date': case[9],
                'defects_score': case[10],
                'timeline': case[11],
                'category': case[12],
                'sub_category': case[13],
                'past': case[14],
                'related': case[15]
            }
            case_list.append(case_dict)
        return case_list
    else:
        return None


# Function to add or update additional details of a case
def update_additional_details(case_id, additional_details):
    cursor.execute('''
        UPDATE cases SET additional_details = ? WHERE id = ?
    ''', (additional_details, case_id))
    conn.commit()@retry_on_failure

def get_case_by_name(case_name):
    cursor.execute('''
        SELECT * FROM cases WHERE case_name = ?
    ''', (case_name,))
    case = cursor.fetchone()

    if case:
        case_dict = {
            'id': case[0],
            'case_name': case[1],
            'docs': case[2],
            'raw_text': case[3],
            'user_id': case[4],
            'processed_output': case[5],
            'additional_details': case[6],
            'defects': case[7],
            'entity_list': case[8],
            'upload_date': case[9],
            'defects_score': case[10],
            'timeline': case[11],     
            'category': case[12],     
            'sub_category': case[13], 
            'past': case[14],         
            'related': case[15]
        }
        return case_dict
    else:
        return None


# Function to add or update processed output of a case
def update_processed_output(case_name, processed_output):
    cursor.execute('''
        UPDATE cases SET processed_output = ? WHERE case_name = ?
    ''', (processed_output, case_name))
    conn.commit()

def update_entity_list(case_name, entity_list):
    cursor.execute('''
        UPDATE cases SET entity_list = ? WHERE case_name = ?
    ''', (entity_list, case_name))
    conn.commit()

def update_defects(case_name, defects):
    cursor.execute('''
        UPDATE cases SET defects = ? WHERE case_name = ?
    ''', (defects, case_name))
    conn.commit()

# Function to insert a related case into the database
def insert_related_case(related_case, case_id):
    cursor.execute('''
        INSERT INTO related_cases (case_id, file_name, case_data)
        VALUES (?, ?, ?)
    ''', (case_id, related_case.file_name, related_case.case_data))
    conn.commit()

# Function to insert a past judgment into the database
def insert_past_judgment(past_judgment, case_id):
    cursor.execute('''
        INSERT INTO past_judgments (case_id, file_name, judgment_data)
        VALUES (?, ?, ?)
    ''', (case_id, past_judgment.file_name, past_judgment.judgment_data))
    conn.commit()

# Function to fetch cases from the last 5 days based on user_id
def fetch_cases_last_5_days_by_user(user_id):
    five_days_ago = datetime.now() - timedelta(days=5)
    cursor.execute('''
        SELECT * FROM cases WHERE upload_date >= ? AND user_id = ?
    ''', (five_days_ago.strftime('%Y-%m-%d'), user_id))
    return cursor.fetchall()

# Function to fetch all related cases for a specific case
def get_related_cases(case_id):
    cursor.execute('''
        SELECT * FROM related_cases WHERE case_id = ?
    ''', (case_id,))
    return cursor.fetchall()

# Function to fetch all past judgments for a specific case
def get_past_judgments(case_id):
    cursor.execute('''
        SELECT * FROM past_judgments WHERE case_id = ?
    ''', (case_id,))
    return cursor.fetchall()


# new functions to update the stored results
def update_defects_score(case_name, defects_score):
    cursor.execute('''
        UPDATE cases SET defects_score = ? WHERE case_name = ?
    ''', (defects_score, case_name))
    conn.commit()
def update_timeline(case_name, timeline):
    cursor.execute('''
        UPDATE cases SET timeline = ? WHERE case_name = ?
    ''', (timeline, case_name))
    conn.commit()
def update_category(case_name, category):
    cursor.execute('''
        UPDATE cases SET category = ? WHERE case_name = ?
    ''', (category, case_name))
    conn.commit()
def update_sub_category(case_name, sub_category):
    cursor.execute('''
        UPDATE cases SET sub_category = ? WHERE case_name = ?
    ''', (sub_category, case_name))
    conn.commit()
def update_past(case_name, past):
    cursor.execute('''
        UPDATE cases SET past = ? WHERE case_name = ?
    ''', (past, case_name))
    conn.commit()
def update_related(case_name, related):
    cursor.execute('''
        UPDATE cases SET related = ? WHERE case_name = ?
    ''', (related, case_name))
    conn.commit()


# Main function to drive the program
def main():
    # Boot the database
    boot()

    # Create a new case with defects and entity_list
    case1 = Case('Case A', b'document content', 'raw case text', 1, 'initial processed output', defects="Some defects", entity_list="Entity1, Entity2")
    case_id = insert_case(case1)

    # Fetch case details by ID
    case_details = get_case_by_id(case_id)
    if case_details:
        print(f"Case details for ID {case_id}:")
        print(case_details)

    # Update additional details for case1
    update_additional_details(case_id, "This case involves a high-profile contract dispute.")

    # Update processed output for case1
    update_processed_output(case_id, "updated processed output.")

    # Load related cases and past judgments from files (replace with actual file paths)
    related_case1 = RelatedCase('case1.txt', base_path='../related_cases/')
    related_case2 = RelatedCase('case2.txt', base_path='../related_cases/')
    insert_related_case(related_case1, case_id)
    insert_related_case(related_case2, case_id)

    past_judgment1 = PastJudgment('judgment_file1.txt', base_path='../past_judgments/')
    past_judgment2 = PastJudgment('judgment_file2.txt', base_path='../past_judgments/')
    insert_past_judgment(past_judgment1, case_id)
    insert_past_judgment(past_judgment2, case_id)

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

    # Close the database connection
    close_connection()

if __name__ == "__main__":
    main()