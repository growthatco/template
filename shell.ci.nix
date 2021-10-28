{ sources ? import ./nix { } }:

let
  inherit (sources) nixpkgs growthatpkgs;
in
nixpkgs.mkShell rec {
  name = "ci.template";
  env = nixpkgs.buildEnv {
    name = name;
    paths = buildInputs;
  };
  buildInputs = [
    # <growthatpkgs>
    growthatpkgs.node
  ];
}
