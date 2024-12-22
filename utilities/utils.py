import glob
import json, os
import logging
import shutil
import socket
import subprocess

from datetime import datetime, timedelta
from enum import Enum

import pickle # to work with binary files

def remember_me(data: dict, path:str):
    with open(path, 'bw') as file:
        pickle.dump(data, file,)

    # file = open(path, 'bw')
    # pickle.dump(data, file, )
    # file.close()

def get_me(path:str):
    if os.path.exists(path):
        with open(path, 'br') as file:
            data = pickle.load(file,)
        return data.copy()
    return False

def sort_dict_keys_with_symbols(data: dict):
    # Extract and group keys based on the same grouping logic
    keys = list(data.keys())
    groups = []
    i = 0
    while i < len(keys):
        if keys[i].startswith('#') or keys[i].startswith('@'):
            if i + 1 < len(keys) and not keys[i + 1].startswith(('#', '@')):
                groups.append([keys[i], keys[i + 1]])
                i += 2
            else:
                groups.append([keys[i]])
                i += 1
        else:
            groups.append([keys[i]])
            i += 1

    # Sort groups with keys starting with `#` or `@`
    sorted_groups = sorted(
        [g for g in groups if g[0].startswith(('#', '@'))],
        key=lambda x: x[0]
    ) + [g for g in groups if not g[0].startswith(('#', '@'))]

    # Flatten the sorted groups back into a list
    sorted_keys = [item for group in sorted_groups for item in group]

    # Recreate the dictionary with sorted keys
    sorted_dict = {key: data[key] for key in sorted_keys}
    return sorted_dict


def sort_symbols_maintain_location(lst: list[str]):
    # Extract items starting with # or @
    symbol_items = [item for item in lst if item.startswith('#') or item.startswith('@')]
    # Sort the extracted items
    sorted_symbols = sorted(symbol_items)

    # Replace the original positions with the sorted items
    result = []
    symbol_index = 0
    for item in lst:
        if item.startswith('#') or item.startswith('@'):
            result.append(sorted_symbols[symbol_index])
            symbol_index += 1
        else:
            result.append(item)
    return result


def add_one_day_to_date(yyyymmdd: str) -> str:
    # Convert integer YYYYMMDD to a datetime object
    date = datetime.strptime(str(yyyymmdd), "%Y%m%d")

    # Add one day to the date
    new_date = date + timedelta(days=1)

    # Convert the new date back to integer YYYYMMDD
    return new_date.strftime("%Y%m%d")


def error_handler(func, logger=None):
    """Decorator to handle exceptions and log errors."""
    logger = logger if logger else logging.getLogger(__name__)

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.exception(f"Error in {func.__name__}: {e}")
            raise e

    return wrapper


def is_empty(name, value):
    if isinstance(value, str) and value.strip() == '':
        raise ValueError(f"{name} cannot be None or empty.")

    if not value:
        raise ValueError(f"{name} cannot be None or empty.")

    return True


def is_type(value, dtype):
    if not isinstance(value, dtype) and isinstance(dtype, Enum):
        return False
    elif not isinstance(value, dtype):
        return False
    else:
        return True


def is_valid_path(path, create=False):
    # Check if the file exists
    if not os.path.exists(path):
        if create:
            os.mkdir(path)
            return True
        return False

    # Check if the file is not empty
    # if os.path.getsize(path) == 0:
    #     return False

    # if file:
    #     # Check if it is a regular file
    #     if not os.path.isfile(path):
    #         return False

    # If all checks pass, the file is valid
    return True


def is_valid_ip_format(ip):
    """
    Check if the provided string is a valid IPv4 address.
    """
    try:
        socket.inet_pton(socket.AF_INET, ip)
        return True
    except socket.error:
        return False


def is_dict_field_missing(value, field_name):
    """Check if a specific field in a value is None or empty."""
    return value.get(field_name) in [None, "", {}, [], ()]


def get_days_between_dates(date1, date2):
    # Convert the date strings to datetime objects
    datetime1 = datetime.strptime(date1, "%Y%m%d").date()
    datetime2 = datetime.strptime(date2, "%Y%m%d").date()

    # Calculate the number of days between the two dates
    num_days = abs((datetime2 - datetime1).days)
    return num_days


def find_base_directory():
    current_file = os.path.abspath(__file__)
    base_directory = os.path.dirname(current_file)
    return base_directory


def load_json_file(path):
    """Return a dictionary structured exactly [dumped] as the JSON file."""
    try:
        with open(path, encoding='utf-8') as file:
            loaded_dict = json.load(file)
        return loaded_dict
    except FileNotFoundError as e:
        raise FileNotFoundError(f"Error: {e}. File not found at path: {path}")
    except json.JSONDecodeError as e:
        raise Exception(f"Error: {e}. Unable to decode JSON file at path: {path}")
    except Exception as e:
        raise Exception(f"Error: {e}. An unexpected error occurred while loading JSON file at path: {path}")


def load_sql_file_queries(path):
    """
    Return a list of queries loaded from the given SQL file and separated by ';'.

    Args:
    - path (str): The path to the SQL file.

    Returns:
    - list: List of SQL queries.
    """
    try:
        with open(path, 'r', encoding='utf-8') as file:
            # Read the file and split queries using ';' while filtering out empty strings
            queries = [query.strip() for query in file.read().split(';') if query.strip()]

        return queries

    except FileNotFoundError as file_not_found_error:
        raise FileNotFoundError(f"Error: {file_not_found_error}. File not found at path: {path}")

    except Exception as e:
        raise Exception(f"Error: {e}. An unexpected error occurred while loading SQL file at path: {path}")


# def custom_json_decoder(jsonConfig):
#     from collections import namedtuple
#     try:
#         return namedtuple('X', jsonConfig.keys())(*jsonConfig.values())
#     except Exception as e:
#         logging.error(e)


def run_terminal_command(command, wait=True):
    try:
        if wait:
            # Run the command and wait for it to complete
            result = subprocess.run(command, shell=True, universal_newlines=True, stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE, check=False)
            # Handle the output based on the success of the command
            if result.returncode == 0:
                return result.stdout
            else:
                print(f"Error: {result.stderr}")
                return False
        else:
            # Run the command without waiting for it to complete
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.DEVNULL,  # Redirect stdout to devnull if not needed
                stderr=subprocess.DEVNULL  # Redirect stderr to devnull if not needed
            )
            return process  # Return the subprocess.Popen instance to allow external management

    except subprocess.CalledProcessError as e:
        # Handle specific subprocess-related errors
        raise e
    except Exception as e:
        # Handle other exceptions
        raise e


# TODO: this should be moved to become a class instead
def recursive_op_files(source, destination, source_pattern, override=False, skip_dir=True, operation='copy'):
    files_count = 0
    try:
        assert source is not None, 'Please specify source path, Current source is None.'
        assert destination is not None, 'Please specify destination path, Current source is None.'

        if not os.path.exists(destination):
            print(f'Creating Dir: {destination}')
            os.mkdir(destination)

        items = glob.glob(os.path.join(source, source_pattern))

        for item in items:

            try:
                if os.path.isdir(item) and not skip_dir:
                    path = os.path.join(destination, os.path.basename(item))
                    # INFO(f'START {operation} FROM {item} TO {path}.')
                    files_count += recursive_op_files(
                        source=item, destination=path,
                        source_pattern=source_pattern, override=override
                    )
                else:
                    file = os.path.join(destination, os.path.basename(item))
                    print(f'START {operation} FROM {item} TO {file}.')
                    if not os.path.exists(file) or override:
                        if operation == 'copy':
                            shutil.copyfile(item, file)
                        elif operation == 'move':
                            shutil.move(item, file)
                        else:
                            raise ValueError(f"Invalid operation: {operation}")
                        files_count += 1
                    else:
                        raise FileExistsError(f'The file {file} already exists int the destination path {destination}.')
            except FileNotFoundError as e_file:
                print(f"File not found error: {e_file}")
            except PermissionError as e_permission:
                print(f"Permission error: {e_permission}")
            except Exception as e_inner:
                print(f"An error occurred: {e_inner}")
    except AssertionError as e_assert:
        print(f"Assertion error: {e_assert}")
    except Exception as e_outer:
        print(f"An error occurred: {e_outer}")
    return files_count


def convert_to_json(items):
    x = json.dumps(items)
    print(x)
