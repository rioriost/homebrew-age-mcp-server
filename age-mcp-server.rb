class AgeMcpServer < Formula
  include Language::Python::Virtualenv

  desc "Apache AGE MCP Server"
  homepage "https://github.com/rioriost/homebrew-age-mcp-server/"
  url "https://files.pythonhosted.org/packages/90/bc/089e5f314298e469c874fbb384d199b5e128b3e10ebe48b974dd8d2b84ff/age_mcp_server-0.2.36.tar.gz"
  sha256 "c58c4755149728dd638479b0704795165ef9820113cfe1b2e968bc78b821e13a"
  license "MIT"

  depends_on "python@3.13"

  resource "agefreighter" do
    url "https://files.pythonhosted.org/packages/a3/f7/9efc1adf406767386a4dd93b3567adb80b2397d23b716989d2be56e8ce4a/agefreighter-1.0.25.tar.gz"
    sha256 "7ad2ceeb61f7cc97042de0edf733ca8648b56a46f9ec0e1f0e2123a3e73c9653"
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
