from src.common.logger import get_logger
import argparse

log = get_logger()

class UserArguments:

    def __init__(self):
        parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,add_help=False)

        parser.add_argument('-h', '--help', action='help', default=argparse.SUPPRESS, help='Quality Gate Automation for MC')

        required_args = parser.add_argument_group('Required Arguments')
        required_args.add_argument("-id", "--te_id",help='Test Execution ID \n Eg: QGM-225. Supports executing only one TE at a time',type=str, required=True)
        required_args.add_argument("-a", "--action",help='action name \n Eg: EXECUTE TESTRUN or VALIDATE_QG',type=str, required=True)

        config_args = parser.add_argument_group('Optional configuration arguments')
        config_args.add_argument("--log-level",help='Log level for console',type=str,choices=["INFO", "DEBUG","ERROR","WARNING"],default="INFO")

        self.args = parser.parse_args()

    def set_log_level(self):
        log.info(f"Updating log level to {self.args.log_level}")
        log.setLevel(self.args.log_level)