class AgeMcpServer < Formula
  include Language::Python::Virtualenv

  desc "Apache AGE MCP Server"
  homepage "https://github.com/rioriost/homebrew-age-mcp-server/"
  url "https://files.pythonhosted.org/packages/42/cf/dcab0c2eea39e011fc9237fc289b77982e5ac1ff1447770fffbf802e7859/age_mcp_server-0.2.11.tar.gz"
  sha256 "ce094744f0f8a13a4049de44a21f627db26cb42dbcb7ea7976b9730801c73bf7"
  license "MIT"

  depends_on "python@3.13"

  resource "agefreighter" do
    url "https://files.pythonhosted.org/packages/6b/d0/1fd2be529e5886a74210af459fc24419ab2742cbfac965d9740d2f1e3448/agefreighter-1.0.6.tar.gz"
    sha256 "1d5b2a0dd6c8976ac4a8ff44d3a223f506fbf6bfb52ebc702277946d3752c87d"
  end

  resource "ply" do
    url "https://files.pythonhosted.org/packages/e5/69/882ee5c9d017149285cab114ebeab373308ef0f874fcdac9beb90e0ac4da/ply-3.11.tar.gz"
    sha256 "00c7c1aaa88358b9c765b6d3000c6eec0ba42abca5351b095321aef446081da3"
  end

  def install
    virtualenv_install_with_resources
    system libexec/"bin/python", "-m", "pip", "install", "psycopg[binary,pool]", "mcp"
  end

  test do
    system "#{bin}/age-mcp-server", "--help"
  end
end
