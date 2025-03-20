class AgeMcpServer < Formula
  include Language::Python::Virtualenv

  desc "Apache AGE MCP Server"
  homepage "https://github.com/rioriost/homebrew-age-mcp-server/"
  url "https://files.pythonhosted.org/packages/26/16/1c0933392c2f6e28f7cfc1ffc1a38b042e8c692d5ea7de7e6ed760be89d2/age_mcp_server-0.1.7.tar.gz"
  sha256 "9e0994ec359bc453e0aeb0b29458d1ea5b0817b595d0c4d68f81b2114c442094"
  license "MIT"

  depends_on "python@3.13"

  resource "agefreighter" do
    url "https://files.pythonhosted.org/packages/73/ac/83cf66dd2f687ca91176a44714ca71afabe0a825408c31d4d6989054ac05/agefreighter-1.0.0.tar.gz"
    sha256 "697333974235ac71667023f983b95c2a2aaab2e6f12311b9875bf139c676956c"
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
