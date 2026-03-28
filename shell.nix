{ pkgs ? import <nixpkgs> { } }:

let
  pythonEnv = pkgs.python313.withPackages (ps: with ps; [
    ps.pip
    ps.numpy
    ps.uv
    
    # Include any additional Python packages here
  ]);
in
pkgs.mkShell {
  buildInputs = [
    pythonEnv
  ];

  shellHook = ''
    # Create a virtual environment with UV if it doesn't exist
    if [ ! -d ".venv" ]; then
      echo "Creating virtual environment with UV..."
      uv venv --python ${pythonEnv}/bin/python .venv
    fi

    # Activate the virtual environment
    source .venv/bin/activate

    # Install dependencies with UV directly from pyproject.toml
    if [ -f "pyproject.toml" ]; then
      echo "Installing dependencies from pyproject.toml..."
      uv pip install -e ".[dev]"
    fi

    echo "UV environment activated with Python $(python --version)"
  ''; 
}
