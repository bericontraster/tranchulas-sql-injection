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
