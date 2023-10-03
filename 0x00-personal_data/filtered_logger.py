#!/usr/bin/env python3
""" Regex-ing """
import os
import re
from typing import List
import logging
import mysql.connector

PII_FIELDS = ("name", "email", "phone", "ssn", "password")


def filter_datum(fields: List[str], redaction: str, message: str,
                 separator: str) -> str:
    """ returns the log message obfuscated

    Args:
        fields (List[str]): fields to obfuscate
        redaction (str): string to replace the field
        message (str): log to obfuscate
        separator (str): separator of fields

    Returns:
        str: obfuscated message
    """
    return re.sub(fr'(?<={separator})({"|".join(fields)})=.*?{separator}',
                  rf'\1={redaction}{separator}', message)


class RedactingFormatter(logging.Formatter):
    """ Redacting Formatter class
    """

    REDACTION = "***"
    FORMAT = "[HOLBERTON] %(name)s %(levelname)s %(asctime)-15s: %(message)s"
    SEPARATOR = ";"

    def __init__(self, fields: List[str]):
        super(RedactingFormatter, self).__init__(self.FORMAT)
        self.fields = fields

    def format(self, record: logging.LogRecord) -> str:
        """Filters values in incoming log records using filter_datum
        Args:
            record (logging.LogRecord): Record to be formatted
        Returns:
            str: Formatted log record.
        """
        message = super().format(record)
        return filter_datum(
            self.fields,
            self.REDACTION,
            message,
            self.SEPARATOR
        )


def get_logger() -> logging.Logger:
    """ returns a logging.Logger object
    """
    logger = logging.getLogger('user_data')
    logger.setLevel(logging.INFO)
    logger.propagate = False
    handler = logging.StreamHandler()
    formatter = RedactingFormatter(fields=PII_FIELDS)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


def get_db():
    # Retrieve database credentials from environment variables or use defaults
    db_username = os.environ.get('PERSONAL_DATA_DB_USERNAME', 'root')
    db_password = os.environ.get('PERSONAL_DATA_DB_PASSWORD', '')
    db_host = os.environ.get('PERSONAL_DATA_DB_HOST', 'localhost')
    db_name = os.environ.get('PERSONAL_DATA_DB_NAME')

    # Check if the database name is set
    if db_name is None:
        raise ValueError(
            "PERSONAL_DATA_DB_NAME environment variable is not set")

    try:
        # Create a MySQL connection
        db_connection = mysql.connector.connect(
            user=db_username,
            password=db_password,
            host=db_host,
            database=db_name
        )

        return db_connection

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None


def main():
    """ obtains a database connection using get_db and retrieves all rows
        in the users table and display each row under a filtered format
    """
    cnx = get_db()
    if not cnx:
        print("Error: Unable to connect to the database.")
        return

    cursor = cnx.cursor()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()

    logger = get_logger()
    for user in users:
        log_message = "; ".join(
            f"{field}={value}"
            for field, value in zip(cursor.column_names, user)
        )
        logger.info(log_message)

    cursor.close()
    cnx.close()


if __name__ == "__main__":
    main()
