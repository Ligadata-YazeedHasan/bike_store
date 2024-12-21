# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import argparse
import datetime

from models.consts import AnimalsType
from models.db import get_db_hook
from models.models import Animal
from utilities.loggings import MultipurposeLogger
from utilities.utils import is_valid_path, load_json_file


def main():
    config = load_json_file(args.config)
    logger.info(f"Loaded Configs: {config}")

    db_config = config.get('audit')

    connection, factory = get_db_hook(config=db_config, logger=logger, create=True)

    # df = connection.select("""select * from Persons""")
    # logger.info(f"{df}")
    #
    # df = connection.execute("update Persons set name = 'Ahmad' where name = 'Mohammad01'", commit=True)
    # logger.info(f"{df}")
    #
    # df = connection.select("select * from Persons")
    # logger.info(f"{df}")

    a = Animal(
        name="dodo150",
        dob=datetime.date(year=2001, month=5, day=15),
        type=AnimalsType.LION,
    )
    factory.add(a, commit=True)

    animals = factory.session.query(Animal).filter(Animal.name == 'dodo').all()
    print(animals)

    for idx, animal in enumerate(animals):
        animal.name += str(idx)

    factory.commit()

    factory.close()
    connection.close()

    pass


def cli():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=str, default='configs/config.json', help="The pth to the config file.")
    parser.add_argument('--log', type=str, default='logs', help="The pth to the logs directory.")

    args = parser.parse_args()
    return args


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    args = cli()

    logger = MultipurposeLogger(
        name="DBLogger",
        create=True
    )

    assert args.config.endswith('.json') and is_valid_path(args.config), "Couldn't find the config file."

    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
