class AgeMcpServer < Formula
  include Language::Python::Virtualenv

  desc "Apache AGE MCP Server"
  homepage "https://github.com/rioriost/homebrew-age-mcp-server/"
  url "https://files.pythonhosted.org/packages/f4/3d/861483038ec2120266e403a92b37a8429d4934067b0a36cd0dae80eec021/age_mcp_server-0.2.33.tar.gz"
  sha256 "7ff2298f71d9f4593981ee59340ff7d9dfd9a410ab3a1f024cb450678da8ad8a"
  license "MIT"

  depends_on "python@3.13"

  resource "agefreighter" do
    url "https://files.pythonhosted.org/packages/7f/29/486f58ad8b7d291dea537910981e8704b99af0b98fbbea263589fb53471e/agefreighter-1.0.21.tar.gz"
    sha256 "3972346224ca9c15e4862a90f070447dd929719dced375f027aaf82b61c890ce"
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
