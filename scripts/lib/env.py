import json

# List used to house final `.env` entries.
_env = []


def json2env(jsonstr: str, key="", _nested=False):
    """
    Reads a stringified json object as input and produces
    escaped shell commands for setting environment variables.
    """

    # Local increment counter
    incr = 0

    # Create a valid json object from the given string.
    val = json.loads(jsonstr)

    for k, v in val.items():
        # Always transform the incoming key to upperace.
        k = k.upper()

        # Replace any dashes with underscores.
        k = k.replace("-", "_")

        # Increment the local counter by 1 to keep track of stage
        # of traversal.
        incr = incr + 1

        if isinstance(v, dict):
            # If the current value in the iteration is a nested
            # object, append the current key with a trailing underscore
            # and call `json2env` recursively.
            dict_key = f"{key}{k}_"
            json2env(json.dumps(v), dict_key, True)

        else:
            # If the value is not a json object, create the environment
            # variable entry, and print.
            env = f"{key}{k}={v}"

            # Add the current entry to the global `_env` array, we'll deconstruct
            # this array via the final recursive complete check below.
            _env.append(env)

        if _nested == False and incr == len(val.items()):
            # Because this is a synchronous call stack, we can check that
            # are finished with the iteration by using the `_nested` flag. If we
            # aren't iterating over a nested object, and we're at the last
            # position of the initial iteration, return the environment variable
            # entries separated by newlines.
            return "\n".join(_env)
