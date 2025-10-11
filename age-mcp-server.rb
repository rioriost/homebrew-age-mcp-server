class AgeMcpServer < Formula
  include Language::Python::Virtualenv

  desc "Apache AGE MCP Server"
  homepage "https://github.com/rioriost/homebrew-age-mcp-server/"
  url "https://files.pythonhosted.org/packages/fa/fd/f6a5e1e4b5173fe0ad3083a54091918d7de1b462184ede3d525e9b9a65e8/age_mcp_server-0.2.28.tar.gz"
  sha256 "5d6e310f45884a7cc7069baea8814f6b05f7ad92896ba8d8980a5cc7a60a5df2"
  license "MIT"

  depends_on "python@3.13"

  resource "agefreighter" do
    url "https://files.pythonhosted.org/packages/f4/1a/9703a6c6d5e915f2829ac1d75527654858ce3bbd35b3f1800333a0f3d1ca/agefreighter-1.0.17.tar.gz"
    sha256 "8df2262cfc8cb1a1772b8204f5fcc9afe7fc02f1d7c1c71a604acd29d67014c0"
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
