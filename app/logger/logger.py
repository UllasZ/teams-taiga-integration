import logging
from pathlib import Path
from app.utils.utils import create_folder


class Logger:
    project_base_path = Path(__file__).parent.parent.parent
    log_file_path = f"{project_base_path}/logs"
    create_folder(file_path=log_file_path)

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
        filename=f"{log_file_path}/teams_taiga_integration.log",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


logger = Logger()
log = logging
log.info("Logger initiated!")
