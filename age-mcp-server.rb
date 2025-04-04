class AgeMcpServer < Formula
  include Language::Python::Virtualenv

  desc "Apache AGE MCP Server"
  homepage "https://github.com/rioriost/homebrew-age-mcp-server/"
  url "https://files.pythonhosted.org/packages/55/73/3c90d323d3cd9fa5ed97cfe39af84216880bf6fcb44c9e0139fe5a6787c6/age_mcp_server-0.2.7.tar.gz"
  sha256 "b465fd05a57de569dc6030c198eee85caa042bf985c83e3f59a2ef880e744c68"
  license "MIT"

  depends_on "python@3.13"

  resource "agefreighter" do
    url "https://files.pythonhosted.org/packages/cc/63/3c8f14003f438ee59de57d5c4668fea97520cc04ef489479bf0fa5f7b163/agefreighter-1.0.4.tar.gz"
    sha256 "ad4b4883ebd4e40346f56806a383fe9f70d8970dd81d6e2f7b968c0a81c79750"
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
