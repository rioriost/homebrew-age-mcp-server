class AgeMcpServer < Formula
  include Language::Python::Virtualenv

  desc "Apache AGE MCP Server"
  homepage "https://github.com/rioriost/homebrew-age-mcp-server/"
  url "https://files.pythonhosted.org/packages/b2/22/29d995d84ab94e9d139045e6ed7e80484f829cc8bf6c50efd2f68e878b5f/age_mcp_server-0.1.1.tar.gz"
  sha256 "55fd51d723114efecf72a59decac3d034fcfaf8ebba76694077e0361c082e870"
  license "MIT"

  depends_on "python@3.13"

  resource "agefreighter" do
    url "https://files.pythonhosted.org/packages/f0/02/425b548e58ca12abfe71bc8583cc8d0336d6fb17dbc0ca12509f5c232e66/agefreighter-1.0.0a16.tar.gz"
    sha256 "4e19d6a441d170cc0b58fdb418a3ef0d14ed221f29e7f91521ae55890891413c"
  end

  resource "mcp" do
    url "https://files.pythonhosted.org/packages/50/cc/5c5bb19f1a0f8f89a95e25cb608b0b07009e81fd4b031e519335404e1422/mcp-1.4.1.tar.gz"
    sha256 "b9655d2de6313f9d55a7d1df62b3c3fe27a530100cc85bf23729145b0dba4c7a"
  end

  resource "ply" do
    url "https://files.pythonhosted.org/packages/e5/69/882ee5c9d017149285cab114ebeab373308ef0f874fcdac9beb90e0ac4da/ply-3.11.tar.gz"
    sha256 "00c7c1aaa88358b9c765b6d3000c6eec0ba42abca5351b095321aef446081da3"
  end

  def install
    virtualenv_install_with_resources
    system libexec/"bin/python", "-m", "pip", "install", "psycopg[binary,pool]"
  end

  test do
    system "#{bin}/phorganize", "--help"
  end
end
