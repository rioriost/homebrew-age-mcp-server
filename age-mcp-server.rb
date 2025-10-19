class AgeMcpServer < Formula
  include Language::Python::Virtualenv

  desc "Apache AGE MCP Server"
  homepage "https://github.com/rioriost/homebrew-age-mcp-server/"
  url "https://files.pythonhosted.org/packages/df/e8/a32013c491a4df9a1fe3b57c0fd237a4f4e14467684ac17aaf6f65f2346c/age_mcp_server-0.2.29.tar.gz"
  sha256 "9abd2c01c4a673750ffdd580d7d4e3ae7aab208efb44628ae9e81198963441d9"
  license "MIT"

  depends_on "python@3.13"

  resource "agefreighter" do
    url "https://files.pythonhosted.org/packages/c6/e5/5038fb1470c2525f5879c9e61d012915a3f46e17ae402ce7eb310ce941ee/agefreighter-1.0.18.tar.gz"
    sha256 "bcbfe8a6c1318847e2075a22287f88851951288326ca9fb75f3009872ccb4b5a"
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
