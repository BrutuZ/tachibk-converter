{
  description = "Nix Flake for Tachibk Converter";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/release-24.11";
    utils = {
      url = "github:numtide/flake-utils";
    };
  };

  outputs = {
    self,
    nixpkgs,
    utils,
  }:
    utils.lib.eachDefaultSystem (
      system: let
        pkgs = import nixpkgs {
          inherit system;
          config.allowUnfree = true;
        };
      in {
        devShells.default = pkgs.mkShell {
          buildInputs = with pkgs; [
            python312
            python312Packages.requests
            python312Packages.protobuf
            python312Packages.varint
          ];
          shellHook = "echo 'Tachibk-Converter Shell Initialized'";
        };
      }
    );
}
