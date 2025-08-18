# Compare RPCs

## Setup
As for any module in this repository, it is recommended to have nix and direnv installed. By doing so, all dependancies will be installed automatically.

Otherwise, install the python dependancies using `uv` or some other package manager of your choosing.

## Running
Duplicate first the `config.redacted.yml`. to `config.yml` and update the RPC endpoints at the top of the file.
To run the module, from the run `uv run -m compare_rpcs --config config.yml` (or `python -m compare_rpcs config.yml`)
