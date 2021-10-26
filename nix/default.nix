{ sources ? import ./sources.nix }:

let
  overlay = _: pkgs: { inherit (import sources.niv { }) niv; };
in
rec {
  nixpkgs = import sources.nixpkgs {
    overlays = [ overlay ];
  };

  growthatpkgs = import sources.growthatpkgs { };
}
