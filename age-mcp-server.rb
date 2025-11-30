class AgeMcpServer < Formula
  include Language::Python::Virtualenv

  desc "Apache AGE MCP Server"
  homepage "https://github.com/rioriost/homebrew-age-mcp-server/"
  url "https://files.pythonhosted.org/packages/ba/af/0f2f6f21fbc90f3c0200509ca75d093bd7485990f9ad43d40bb94ce9aef0/age_mcp_server-0.2.34.tar.gz"
  sha256 "b401b4424691682c5f4ef70442efdda3f08d56aa10866864146624a66b341939"
  license "MIT"

  depends_on "python@3.13"

  resource "agefreighter" do
    url "https://files.pythonhosted.org/packages/ff/46/4eef21caf7e8370ae10111c8b190eb32e9b4e949db5190fae7ec69396f15/agefreighter-1.0.22.tar.gz"
    sha256 "f6be56eed976606b773cb594bd08b7b64777770a5175c111d5dcf1c8ac6864e0"
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
