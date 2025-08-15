{
  description = "A sample Flake for Home Assistant with Python 3.13 & uv";
  
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };
  
  outputs = { self, nixpkgs, flake-utils, ... }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        python = pkgs.python313;
        pythonEnv = python.withPackages (ps: with ps; [
          ps.pip # ensure pip exists
          ps.numpy # Numpy
        ]);
      in
      {
        devShells.default = pkgs.mkShell.override { stdenv = pkgs.stdenvNoCC; shell = "${pkgs.zsh}/bin/zsh"; } {
          packages = [
            python
            pkgs.uv
            python.pkgs.python-lsp-server
            python.pkgs.pytest
            pkgs.zsh
          ];
          
          # Use zsh as the shell
          SHELL = "${pkgs.zsh}/bin/zsh";

          shellHook = ''
            # ZSH compatible shell hook
            # Create a virtual environment with UV
            if [[ ! -d ".venv" ]]; then
              echo "Creating virtual environment with UV..."
              uv venv --python ${python}/bin/python .venv
            fi

            # Activate the virtual environment if it exists
            if [[ -f ".venv/bin/activate" ]]; then
              source .venv/bin/activate

              # Install dependencies with UV directly from pyproject.toml
              if [[ -f "pyproject.toml" ]]; then
                echo "Installing project in development mode with all dependencies..."
                uv pip install -e ".[dev]"
              fi
            else
              echo "Warning: Virtual environment activation failed. Run 'uv venv' manually."
            fi        

            # Display environment info
            echo "UV $(uv --version) activated with Python $(python --version)"
          '';
        };
      });
}