import os
import sqlite3

DB_FILE = "library.db"


def setup_database():
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)

    print(f"Creating database: {DB_FILE}")
    connection = sqlite3.connect(DB_FILE)
    db_cursor = connection.cursor()

    db_cursor.execute("""
    CREATE TABLE authors (
        author_id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        country TEXT
    );
    """)

    db_cursor.execute("""
    CREATE TABLE books (
        book_id INTEGER PRIMARY KEY,
        title TEXT NOT NULL,
        author_id INTEGER NOT NULL,
        genre TEXT,
        published_year INTEGER,
        price NUMERIC(10, 2) NOT NULL,
        FOREIGN KEY (author_id) REFERENCES authors (author_id)
    );
    """)

    db_cursor.execute("""
    CREATE TABLE members (
        member_id INTEGER PRIMARY KEY,
        full_name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        city TEXT,
        joined_on TEXT NOT NULL
    );
    """)

    db_cursor.execute("""
    CREATE TABLE loans (
        loan_id INTEGER PRIMARY KEY,
        book_id INTEGER NOT NULL,
        member_id INTEGER NOT NULL,
        loan_date TEXT NOT NULL,
        return_date TEXT,
        FOREIGN KEY (book_id) REFERENCES books (book_id),
        FOREIGN KEY (member_id) REFERENCES members (member_id)
    );
    """)

    author_rows = [
        (1, "Haruki Murakami", "Japan"),
        (2, "Octavia E. Butler", "United States"),
        (3, "Chimamanda Ngozi Adichie", "Nigeria"),
        (4, "Neil Gaiman", "United Kingdom"),
        (5, "Isabel Allende", "Chile"),
    ]
    db_cursor.executemany("INSERT INTO authors VALUES (?, ?, ?);", author_rows)

    book_rows = [
        (1, "Kafka on the Shore", 1, "Magical Realism", 2002, 12.99),
        (2, "Norwegian Wood", 1, "Fiction", 1987, 10.99),
        (3, "Kindred", 2, "Science Fiction", 1979, 11.50),
        (4, "Parable of the Sower", 2, "Science Fiction", 1993, 13.25),
        (5, "Americanah", 3, "Fiction", 2013, 14.75),
        (6, "Neverwhere", 4, "Fantasy", 1996, 9.99),
        (7, "The House of the Spirits", 5, "Magical Realism", 1982, 12.50),
    ]
    db_cursor.executemany("INSERT INTO books VALUES (?, ?, ?, ?, ?, ?);", book_rows)

    member_rows = [
        (1, "Alex Rivera", "alex.rivera@example.com", "New York", "2024-01-15"),
        (2, "Priya Desai", "priya.desai@example.com", "San Francisco", "2024-02-10"),
        (3, "Liam O'Connor", "liam.oconnor@example.com", "Chicago", "2024-03-05"),
        (4, "Sofia Martins", "sofia.martins@example.com", "Austin", "2024-04-18"),
        (5, "Mei Chen", "mei.chen@example.com", "Seattle", "2024-05-09"),
    ]
    db_cursor.executemany("INSERT INTO members VALUES (?, ?, ?, ?, ?);", member_rows)

    loan_rows = [
        (1, 1, 1, "2024-06-01", "2024-06-14"),
        (2, 3, 2, "2024-06-05", "2024-06-19"),
        (3, 4, 3, "2024-06-10", None),
        (4, 6, 4, "2024-06-12", "2024-06-26"),
        (5, 2, 5, "2024-06-15", None),
        (6, 5, 1, "2024-06-20", None),
    ]
    db_cursor.executemany("INSERT INTO loans VALUES (?, ?, ?, ?, ?);", loan_rows)

    connection.commit()
    connection.close()
    print("Database created and populated successfully.")
    print("Tables: authors, books, members, loans")


if __name__ == "__main__":
    setup_database()