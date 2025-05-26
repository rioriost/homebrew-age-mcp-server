class AgeMcpServer < Formula
  include Language::Python::Virtualenv

  desc "Apache AGE MCP Server"
  homepage "https://github.com/rioriost/homebrew-age-mcp-server/"
  url "https://files.pythonhosted.org/packages/8a/1e/437d70196a92dd154f34471b8cb4fcb1cfb9514bf6c06ffd3852572acfcc/age_mcp_server-0.2.13.tar.gz"
  sha256 "e4f670dc9d6260606f62bf3d1ef574d12970d7ac10e3e0d2e772c7d142b05b7a"
  license "MIT"

  depends_on "python@3.13"

  resource "agefreighter" do
    url "https://files.pythonhosted.org/packages/dc/03/050e44e42654da2c0a612b6d92e46013ac80c8d2aca1a3839c390463b32d/agefreighter-1.0.7.tar.gz"
    sha256 "d00d6acdc744c16b3f8ea104cf2137d50bbc1b54155d297af697387959137213"
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
