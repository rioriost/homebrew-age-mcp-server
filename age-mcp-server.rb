class AgeMcpServer < Formula
  include Language::Python::Virtualenv

  desc "Apache AGE MCP Server"
  homepage "https://github.com/rioriost/homebrew-age-mcp-server/"
  url "https://files.pythonhosted.org/packages/a2/c5/da5925114553e7cef41ec768bb42fa2ed5f78c11663948e960e295022e32/age_mcp_server-0.2.24.tar.gz"
  sha256 "e490478cabe2caf1eca1ea62c1a4c3b68902e5b3721d99d7ef24965f249ed8bb"
  license "MIT"

  depends_on "python@3.13"

  resource "agefreighter" do
    url "https://files.pythonhosted.org/packages/4d/42/70415f1a0b954d9223a67dfb0c3b3426c0c461eb14ce9ac80ff13c2a13ee/agefreighter-1.0.12.tar.gz"
    sha256 "6413a4c54bc7a6aea65357fef40a41fc6967c855929e4ac3ee11f564e6df30d5"
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
