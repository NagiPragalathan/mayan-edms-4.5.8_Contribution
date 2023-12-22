def load_env_file(filename='config.env', skip_local_config=False):
    result = {}
    with open(file=filename) as file_object:
        for line in file_object:
            if not line.startswith('#'):
                key, value = line.strip().split('=')

                result[key] = value

    if filename != 'config-local.env' and not skip_local_config:
        try:
            result.update(
                load_env_file(filename='config-local.env')
            )
        except FileNotFoundError:
            """
            Non fatal. Just means this deployment does not overrides the
            default `config.env` file values.
            """

    return result
