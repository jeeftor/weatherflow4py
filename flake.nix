{
  description = "A sample Flake for Home Assistant with Python 3.12 & uv";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

outputs = { self, nixpkgs, flake-utils, ... }:
  flake-utils.lib.eachDefaultSystem (system:
    let
      pkgs = import nixpkgs {
        inherit system;
        overlays = [];
      };
      pythonEnv = pkgs.python312.withPackages (ps: with ps; [

        ps.pip # ensure pip exists
        ps.numpy # Numpy
        uv
        # Include any additional Python packages here
      ]);
    in
    {
      devShell = pkgs.mkShell {
        buildInputs = [
          pythonEnv
          pkgs.autoconf # Add autoconf here
          pkgs.libjpeg_turbo # Add turbojpeg here
          pkgs.ffmpeg
        ];
         shellHook = ''        
        # Remove flake.nix and flake.lock from GIT
        git restore --staged flake.nix
        #git update-index --assume-unchanged flake.lock
        #git update-index --no-skip-worktree flake.lock

        
        export DYLD_LIBRARY_PATH=${pkgs.libjpeg_turbo}/lib:$DYLD_LIBRARY_PATH
        export STARSHIP_CONFIG=$(pwd)/starship.toml
        python -m venv venv 
        source venv/bin/activate 
        ./script/setup

          '';
        };
    });
}
