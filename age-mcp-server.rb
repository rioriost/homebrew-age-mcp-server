class AgeMcpServer < Formula
  include Language::Python::Virtualenv

  desc "Apache AGE MCP Server"
  homepage "https://github.com/rioriost/homebrew-age-mcp-server/"
  url "https://files.pythonhosted.org/packages/04/5f/9f8840c5b8261fb2552f884c097618b605881735ded308b03cd96a083c7c/age_mcp_server-0.2.23.tar.gz"
  sha256 "4e4af5d49d130def72881862bc65838e55475f327b3370e635965fed6c54b3a9"
  license "MIT"

  depends_on "python@3.13"

  resource "agefreighter" do
    url "https://files.pythonhosted.org/packages/9f/c5/3bc644ce773d25032701e5158d89ffc1b8af607a821b370f6ba2cb6b70e1/agefreighter-1.0.11.tar.gz"
    sha256 "d7397a88e4a164e0b903d617130389127acf2f518e775c6c16bd3e5c3dd00b24"
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
