class AgeMcpServer < Formula
  include Language::Python::Virtualenv

  desc "Apache AGE MCP Server"
  homepage "https://github.com/rioriost/homebrew-age-mcp-server/"
  url "https://files.pythonhosted.org/packages/62/f7/1808eb1456e22905e178eb23d5acc2c09caa83e5023b0dcdfd1646f8c5f6/age_mcp_server-0.2.38.tar.gz"
  sha256 "770d750d63feaa2a3f61d70749b51dd3fa375ddaf03a63e4d8b43502dcf7c2c6"
  license "MIT"

  depends_on "python@3.13"

  resource "agefreighter" do
    url "https://files.pythonhosted.org/packages/6d/81/abcfdd1d004730a33071c3fca17799219fcf1149010491cd276471f1953f/agefreighter-1.0.27.tar.gz"
    sha256 "82607629534514a03394107d2fcbcb4b8e95640eb4a68c5686ddbe5365d40e0c"
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
