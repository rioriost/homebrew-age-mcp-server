class AgeMcpServer < Formula
  include Language::Python::Virtualenv

  desc "Apache AGE MCP Server"
  homepage "https://github.com/rioriost/homebrew-age-mcp-server/"
  url "https://files.pythonhosted.org/packages/51/f4/44b09b532db80e1a64caf53ec670c0354d31832ddd0b5042f2302a127774/age_mcp_server-0.2.17.tar.gz"
  sha256 "f003ea7b0e4ae223ebbac9c0ddfefae5271d84bca5cae0779de5ac65e945e775"
  license "MIT"

  depends_on "python@3.13"

  resource "agefreighter" do
    url "https://files.pythonhosted.org/packages/fb/bd/a6a8078e99313ad20799d85dcea9ea2afbdb729f7472fc47b2c9737a8dc7/agefreighter-1.0.9.tar.gz"
    sha256 "17053fb16abd4b79bd6c8da1bb51e9c3c75a0d31b91fc04f62fd6b0bbce475b6"
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
