{ sources ? import ./nix { } }:

let
  inherit (sources) nixpkgs growthatpkgs;
in
nixpkgs.mkShell rec {
  name = "cd.template";
  env = nixpkgs.buildEnv {
    name = name;
    paths = buildInputs;
  };
  buildInputs = [
    # <growthatpkgs>
    growthatpkgs.nodejs
  ];
}
