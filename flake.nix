{
  description = "Comix Downloader, packaged with uv2nix";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-parts.url = "github:hercules-ci/flake-parts";
    systems.url = "github:nix-systems/default";

    devshell = {
      url = "github:numtide/devshell";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    pyproject-build-systems = {
      url = "github:pyproject-nix/build-system-pkgs";
      inputs.nixpkgs.follows = "nixpkgs";
      inputs.pyproject-nix.follows = "pyproject-nix";
      inputs.uv2nix.follows = "uv2nix";
    };

    pyproject-nix = {
      url = "github:pyproject-nix/pyproject.nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    treefmt-nix = {
      url = "github:numtide/treefmt-nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    uv2nix = {
      url = "github:pyproject-nix/uv2nix";
      inputs.nixpkgs.follows = "nixpkgs";
      inputs.pyproject-nix.follows = "pyproject-nix";
    };
  };

  outputs =
    {
      self,
      flake-parts,
      systems,
      ...
    }@inputs:
    flake-parts.lib.mkFlake { inherit inputs; } {
      systems = import systems;
      imports = [
        inputs.devshell.flakeModule
        inputs.treefmt-nix.flakeModule
      ];

      perSystem =
        { pkgs, system, ... }:
        let
          inherit (pkgs) lib;
          workspace = inputs.uv2nix.lib.workspace.loadWorkspace {
            workspaceRoot = ./.;
          };
          overlay = workspace.mkPyprojectOverlay {
            sourcePreference = "wheel";
          };
          python = pkgs.python312;
          pythonSet =
            (pkgs.callPackage inputs.pyproject-nix.build.packages {
              inherit python;
            }).overrideScope
              (
                lib.composeManyExtensions [
                  inputs.pyproject-build-systems.overlays.wheel
                  overlay
                ]
              );
          runtime = pythonSet.mkVirtualEnv "comix-downloader" workspace.deps.default;
          devRuntime = pythonSet.mkVirtualEnv "comix-downloader-dev" workspace.deps.all;
          browserRuntime = lib.optional (!pkgs.stdenv.hostPlatform.isDarwin) pkgs.chromium;
          cli = pkgs.writeShellApplication {
            name = "comix-downloader";
            # On Darwin, nodriver discovers Chrome/Chromium in /Applications.
            # nixpkgs Chromium is kept for Linux but is not a reliable Darwin
            # runtime dependency on Apple Silicon.
            runtimeInputs = [ runtime ] ++ browserRuntime;
            text = ''
              export PYTHONPATH=${./.}:''${PYTHONPATH:-}
              exec ${runtime}/bin/python ${./main.py} "$@"
            '';
          };
          netscapeCookiesToNodriver = pkgs.writeShellApplication {
            name = "netscape-cookies-to-nodriver";
            runtimeInputs = [ runtime ];
            text = ''
              exec ${runtime}/bin/python ${./scripts/netscape-cookies-to-nodriver.py} "$@"
            '';
          };
        in
        {
          packages = {
            default = cli;
            inherit cli netscapeCookiesToNodriver runtime;
          };

          devshells.default = {
            name = "comix-downloader";
            motd = ''
              Entering the comix-downloader dev shell.
              Run {bold}menu{reset} to list available commands.
            '';
            packages = [
              pkgs.uv
              devRuntime
              pkgs.ruff
            ];
            env = [
              {
                name = "UV_NO_SYNC";
                value = "1";
              }
              {
                name = "UV_PYTHON_DOWNLOADS";
                value = "never";
              }
            ];
            commands = [
              # build
              {
                category = "build";
                name = "build";
                help = "Build the default Nix package";
                command = "nix build";
              }

              # check
              {
                category = "check";
                name = "tests";
                help = "Run the Python test suite";
                command = "pytest";
              }

              # development
              {
                category = "development";
                name = "update-lock";
                help = "Regenerate uv.lock from pyproject.toml";
                command = "uv lock";
              }
            ];
          };

          treefmt = {
            projectRootFile = "flake.nix";
            programs.nixfmt.enable = true;
          };
        };
    };
}
