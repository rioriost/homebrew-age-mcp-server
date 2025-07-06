class AgeMcpServer < Formula
  include Language::Python::Virtualenv

  desc "Apache AGE MCP Server"
  homepage "https://github.com/rioriost/homebrew-age-mcp-server/"
  url "https://files.pythonhosted.org/packages/ba/64/1fa2e34f0421abe7e4945e5c79000c2d42301b11ac67fc78676fcd2c76e4/age_mcp_server-0.2.18.tar.gz"
  sha256 "cf9a5e31f6e225be8d28f76dd00fc9ec330a3c3426b3137bd96ba19c614ca033"
  license "MIT"

  depends_on "python@3.13"

  resource "agefreighter" do
    url "https://files.pythonhosted.org/packages/49/24/e61ad001fc4df20393dbf18fab864d3b2688ea9cf4417499eea7366a7d17/agefreighter-1.0.10.tar.gz"
    sha256 "68e0974662946415fbb4dc592bd419aac80fb56e6badd2deffaeaefbb43a6409"
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
