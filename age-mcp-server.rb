class AgeMcpServer < Formula
  include Language::Python::Virtualenv

  desc "Apache AGE MCP Server"
  homepage "https://github.com/rioriost/homebrew-age-mcp-server/"
  url "https://files.pythonhosted.org/packages/44/ae/18c75aa5ccbd9de1830b31ebe9669e23a9d0de5358e786c804899613d1de/age_mcp_server-0.2.26.tar.gz"
  sha256 "e0f0c36831e3c8daf13c233eb50dd87bf26e289a61be5cac92128c57bbfb5a4d"
  license "MIT"

  depends_on "python@3.13"

  resource "agefreighter" do
    url "https://files.pythonhosted.org/packages/a5/76/fee760bbffb8fd3ae1b9384e9a4576a29ae720d94d18d86e5cb338633dc1/agefreighter-1.0.15.tar.gz"
    sha256 "040ac380fa0bd6d68bbae316d2fcb6ce731c96a149187e1f0b661c8b22c29e0c"
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
