# data/sample_code.py
# Intentionally contains bugs, quality issues, and performance problems

# --- Bugs ---
def divide_numbers(a, b):
    return a / b  # Bug: no division by zero check

def get_first_item(my_list):
    return my_list[0]  # Bug: crashes if list is empty

def read_file(filename):
    f = open(filename, 'r')
    content = f.read()
    return content  # Bug: file never closed

def find_user(users, name):
    for i in range(len(users) + 1):  # Bug: off-by-one error
        if users[i]["name"] == name:
            return users[i]

# --- Quality Issues ---
def x(a, b, c):             # Bad naming, no docstring
    temp = a + b
    temp2 = temp * c
    return temp2

def process(data):           # Vague name, too many responsibilities
    result = []
    for i in data:
        if i > 0:
            if i % 2 == 0:
                if i < 100:   # Deep nesting
                    result.append(i * 2)
    return result

# --- Performance Issues ---
def find_duplicates(items):
    duplicates = []
    for i in range(len(items)):
        for j in range(len(items)):   # O(n^2) — inefficient
            if i != j and items[i] == items[j]:
                if items[i] not in duplicates:
                    duplicates.append(items[i])
    return duplicates

def get_names(users):
    names = []
    for user in users:
        names.append(user["name"])   # Should use list comprehension
    return names


# --- Security Issues (for security agent testing) ---
import subprocess

def run_command(user_input):
    os.system(user_input)          # Security: command injection risk

def get_user(user_id):
    query = "SELECT * FROM users WHERE id = " + user_id  # Security: SQL injection
    return query

PASSWORD = "admin123"              # Security: hardcoded secret

def unsafe_eval(expression):
    return eval(expression)        # Security: arbitrary code execution