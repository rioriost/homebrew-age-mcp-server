class AgeMcpServer < Formula
  include Language::Python::Virtualenv

  desc "Apache AGE MCP Server"
  homepage "https://github.com/rioriost/homebrew-age-mcp-server/"
  url "https://files.pythonhosted.org/packages/0a/77/a17a67624a526115d864bd42640b48b3d0f3966a879113377be35bd1bbba/age_mcp_server-0.2.37.tar.gz"
  sha256 "249f4193f264603159fc0de529cd227a10e7946709c309c54a486f293f6ae8cb"
  license "MIT"

  depends_on "python@3.13"

  resource "agefreighter" do
    url "https://files.pythonhosted.org/packages/fd/25/a95a52b86ae5ce75581ff232088e0346173cd13b87be9ca9142c2e847e3d/agefreighter-1.0.26.tar.gz"
    sha256 "0dd57a454ee10da86b33b151a1dfe0fef03bbf93b7fa456c8408ce1c192eaaa5"
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
