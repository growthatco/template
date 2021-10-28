{ sources ? import ./nix { } }:

let
  inherit (sources) nixpkgs growthatpkgs;
in
nixpkgs.mkShell rec {
  name = "template";
  env = nixpkgs.buildEnv {
    name = name;
    paths = buildInputs;
  };
  buildInputs = [
    # <growthatpkgs>
    growthatpkgs.act
    growthatpkgs.nodejs
    growthatpkgs.poetry
    growthatpkgs.python
    growthatpkgs.rnix-lsp
    growthatpkgs.shfmt
    # <nixpkgs>
    nixpkgs.gitflow
  ];
  shellHook = ''
    unset PYTHONPATH
  '';
}
