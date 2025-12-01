class AgeMcpServer < Formula
  include Language::Python::Virtualenv

  desc "Apache AGE MCP Server"
  homepage "https://github.com/rioriost/homebrew-age-mcp-server/"
  url "https://files.pythonhosted.org/packages/e2/6f/db2102a7d10cccd774d449599e7714e172c1933e028c6d4cac830990a32e/age_mcp_server-0.2.35.tar.gz"
  sha256 "f37f44435f9b0b86e387989312e0607c2c27a2293784cdbcc4992a85bc85b808"
  license "MIT"

  depends_on "python@3.13"

  resource "agefreighter" do
    url "https://files.pythonhosted.org/packages/64/c8/cb6bf846082cc3551252ce1dfd2eb6a6dc3b00bf3c2014b41ba6c4128150/agefreighter-1.0.23.tar.gz"
    sha256 "70b6e2e096f22e58c0443ccbae807cf7ba9ace1125bfa37dc1d53f85c18f299c"
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
