class AgeMcpServer < Formula
  include Language::Python::Virtualenv

  desc "Apache AGE MCP Server"
  homepage "https://github.com/rioriost/homebrew-age-mcp-server/"
  url "https://files.pythonhosted.org/packages/8d/d7/3a48263e5fa6abff8b5ad06cc728fa7b5d90e43cbb656b1197fe6476200a/age_mcp_server-0.2.41.tar.gz"
  sha256 "19c389fca42bea22a8e29e4ec695301beee8764eb4c2fdab259c0ece9e0fcf32"
  license "MIT"

  depends_on "python@3.13"

  resource "agefreighter" do
    url "https://files.pythonhosted.org/packages/5b/df/464573400dbde52d770d77f7b5e9598d60d164057d2b6573c7d46cb60e85/agefreighter-1.0.29.tar.gz"
    sha256 "b7c837cd42bb5e2136c468e3b041efc303c42cd26314fef95ef2e44466c84778"
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
