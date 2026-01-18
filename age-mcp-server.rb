class AgeMcpServer < Formula
  include Language::Python::Virtualenv

  desc "Apache AGE MCP Server"
  homepage "https://github.com/rioriost/homebrew-age-mcp-server/"
  url "https://files.pythonhosted.org/packages/57/41/c9c3306761ce742a247171442ea1678b78b888f7178a84c3884e8f59b01e/age_mcp_server-0.2.39.tar.gz"
  sha256 "9dd0428d4e1e2a9aa19103bc741d0754e15ad6a7b814864693596c48f613d65c"
  license "MIT"

  depends_on "python@3.13"

  resource "agefreighter" do
    url "https://files.pythonhosted.org/packages/c9/c6/96e22cf92f276a815be9b73fc7db7832800d000a3582c69f425c9845c98b/agefreighter-1.0.28.tar.gz"
    sha256 "0b594c5043090048714520d2f62f249361115579671386d0f5bca2685cb50102"
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
