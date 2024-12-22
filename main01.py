import argparse
import os
import sys

from PyQt6.QtWidgets import QApplication

from apis.messaging import get_email_hook
from controllers.controller import MainApp
from models.db import get_db_hook
from utilities.loggings import MultipurposeLogger
from utilities.utils import load_json_file, is_valid_path
from common import consts
from views.forms import LoginForm


def main():
    config = load_json_file(args.config)
    logger.info(f"Loaded Configs: {config}")

    db_config = config.get('audit')

    connection, factory = get_db_hook(config=db_config, logger=logger, create=True)
    MainApp.DB_CONNECTION = connection
    MainApp.DB_FACTORY = factory

    email_config = config.get('email')
    mailer = get_email_hook(config=email_config, logger=logger)
    MainApp.MAILER = mailer

    app = QApplication([])
    # MainController.store_screen_details(app.primaryScreen())

    try:
        form = LoginForm()
        if not os.path.exists(consts.REMEMBER_ME_FILE_PATH):
            form.show()

    except Exception as e:
        print(e)
        raise e
    finally:
        pass
    code = app.exec()
    sys.exit(code)


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

# if __name__ == "__main__":
#     # print(type(sys.argv))
#     main(sys.argv)
