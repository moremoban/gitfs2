import crayons


def error(message):
    print(crayons.white("Error: ", bold=True) + crayons.red(message))


def warn(message):
    print(crayons.white("Warning: ", bold=True) + crayons.yellow(message))


def info(message):
    print(crayons.white("Info: ") + crayons.green(message))
