class AgeMcpServer < Formula
  include Language::Python::Virtualenv

  desc "Apache AGE MCP Server"
  homepage "https://github.com/rioriost/homebrew-age-mcp-server/"
  url "https://files.pythonhosted.org/packages/67/f7/5b5c1c98a3ac9342a652d45a7b4f428d3e67051590ebf9ecec5d4bfd80bd/age_mcp_server-0.2.16.tar.gz"
  sha256 "5973eca03fc6ee2e478e194dbf86ce6454856cdf85fa9026b4276c752a56277c"
  license "MIT"

  depends_on "python@3.13"

  resource "agefreighter" do
    url "https://files.pythonhosted.org/packages/af/37/4a25fb2875477b73b5f54e0b6457613c929d2ddfe66f3984bb91ce1b32c0/agefreighter-1.0.8.tar.gz"
    sha256 "c8097cf4b4d578d6ad737d1ba6f7e740c6f730a538dcba2fd6ece1a94c2bce05"
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
