class AgeMcpServer < Formula
  include Language::Python::Virtualenv

  desc "Apache AGE MCP Server"
  homepage "https://github.com/rioriost/homebrew-age-mcp-server/"
  url "https://files.pythonhosted.org/packages/2f/29/950655a7c49f14ef84e31d6404682c390f826686138a929d007e579be333/age_mcp_server-0.1.2.tar.gz"
  sha256 "05a2bc50dd30eb5e627c65bd6c86a96a5e8b887747120e581fd0d3dc1f216b96"
  license "MIT"

  depends_on "python@3.13"

  resource "agefreighter" do
    url "https://files.pythonhosted.org/packages/73/ac/83cf66dd2f687ca91176a44714ca71afabe0a825408c31d4d6989054ac05/agefreighter-1.0.0.tar.gz"
    sha256 "697333974235ac71667023f983b95c2a2aaab2e6f12311b9875bf139c676956c"
  end

  resource "mcp" do
    url "https://files.pythonhosted.org/packages/50/cc/5c5bb19f1a0f8f89a95e25cb608b0b07009e81fd4b031e519335404e1422/mcp-1.4.1.tar.gz"
    sha256 "b9655d2de6313f9d55a7d1df62b3c3fe27a530100cc85bf23729145b0dba4c7a"
  end

  resource "ply" do
    url "https://files.pythonhosted.org/packages/e5/69/882ee5c9d017149285cab114ebeab373308ef0f874fcdac9beb90e0ac4da/ply-3.11.tar.gz"
    sha256 "00c7c1aaa88358b9c765b6d3000c6eec0ba42abca5351b095321aef446081da3"
  end

  resource "psycopg" do
    url "https://files.pythonhosted.org/packages/67/97/eea08f74f1c6dd2a02ee81b4ebfe5b558beb468ebbd11031adbf58d31be0/psycopg-3.2.6.tar.gz"
    sha256 "16fa094efa2698f260f2af74f3710f781e4a6f226efe9d1fd0c37f384639ed8a"
  end

  def install
    virtualenv_install_with_resources
  end

  test do
    system "#{bin}/age-mcp-server", "--help"
  end
end
