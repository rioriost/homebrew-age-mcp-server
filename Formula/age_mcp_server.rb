class AgeMcpServer < Formula
  include Language::Python::Virtualenv

  desc "Apache AGE MCP Server"
  homepage "https://github.com/rioriost/age_mcp_server"
  url "https://github.com/rioriost/age_mcp_server/releases/download/0.3.0/age_mcp_server-0.3.0.tar.gz"
  sha256 "77077d3efea4bf5051b64e43f61c2fba244d17365e8ff34ad59c25bf8aa5e464"
  license "MIT"

  depends_on "python@3.13"
  resource "agefreighter" do
    url "https://files.pythonhosted.org/packages/27/f2/3aa26243b7d4615fd2d6b6a2d2bc9614a4780340bcf48265343e4cdeda34/agefreighter-1.0.33-py3-none-any.whl"
    sha256 "4cb593e45b953f68a1073bd5a0cfe64779e5ea81b19f87bd0aeba04b854f10d4"
  end
  resource "aiofiles" do
    url "https://files.pythonhosted.org/packages/bc/8a/340a1555ae33d7354dbca4faa54948d76d89a27ceef032c8c3bc661d003e/aiofiles-25.1.0-py3-none-any.whl"
    sha256 "abe311e527c862958650f9438e859c1fa7568a141b22abcd015e120e86a85695"
  end
  resource "annotated-types" do
    url "https://files.pythonhosted.org/packages/99/91/8acff4f5e50511b911bbccb72b8628a49c68ce14148cd9f6431094859a90/annotated_types-0.8.0-py3-none-any.whl"
    sha256 "f072f4d804ea359e4eaf198b1af7a8b0943881a87f31bb764f8bf219bb9419e0"
  end
  resource "anyio" do
    url "https://files.pythonhosted.org/packages/da/35/f2287558c17e29fafc8ef3daf819bb9834061cfa43bff8014f7df7f63bdc/anyio-4.14.2-py3-none-any.whl"
    sha256 "9f505dda5ac9f0c8309b5e8bd445a8c2bf7246f3ce950121e45ea15bc41d1494"
  end
  resource "argcomplete" do
    url "https://files.pythonhosted.org/packages/12/f6/5b8ec087cd9cfa9449491ec83f76fb6b7006b4dff57d2ba8aaab330fe8e4/argcomplete-3.7.0-py3-none-any.whl"
    sha256 "d8f0f22d2a8a7caa383be1e22b6caf1ecaf0ebd10d8f83cc125e36540c95830c"
  end
  resource "attrs" do
    url "https://files.pythonhosted.org/packages/64/b4/17d4b0b2a2dc85a6df63d1157e028ed19f90d4cd97c36717afef2bc2f395/attrs-26.1.0-py3-none-any.whl"
    sha256 "c647aa4a12dfbad9333ca4e71fe62ddc36f4e63b2d260a37a8b83d2f043ac309"
  end
  resource "click" do
    url "https://files.pythonhosted.org/packages/fb/e2/79c688af8b210d232694e31e59da9f6ec747bae31c3f5946e4e9b98860d5/click-8.4.2-py3-none-any.whl"
    sha256 "e6f9f66136c816745b9d65817da91d61d957fb16e02e4dcd0552553c5a197b76"
  end
  resource "h11" do
    url "https://files.pythonhosted.org/packages/04/4b/29cac41a4d98d144bf5f6d33995617b185d14b22401f75ca86f384e87ff1/h11-0.16.0-py3-none-any.whl"
    sha256 "63cf8bbe7522de3bf65932fda1d9c2772064ffb3dae62d55932da54b31cb6c86"
  end
  resource "httpcore2" do
    url "https://files.pythonhosted.org/packages/9f/fb/46c52b781975c335a2bcf1072c7bbc007cbdc8d674217f5ee1daba2c848b/httpcore2-2.9.1-py3-none-any.whl"
    sha256 "6182472379e855fe4221246a2bb7ecede403bc61c6798062ae1787d051ccde26"
  end
  resource "httpx2" do
    url "https://files.pythonhosted.org/packages/13/b8/cfd91c4ab9134d386d48f0b6ac662ff3d4be6efdee59ee1c67ebc3c0487c/httpx2-2.9.1-py3-none-any.whl"
    sha256 "1820fe14a9ab1107bfeff39259987429450b070ec0ff38cc87eb0d8c97fdc71a"
  end
  resource "idna" do
    url "https://files.pythonhosted.org/packages/1e/5e/d4e9f1a599fb8e573b7b87160658329fbf28d19eac2718f51fc3def3aa5a/idna-3.18-py3-none-any.whl"
    sha256 "7f952cbe720b688055e3f87de14f5c3e5fdaa8bc3928985c4077ca689de849a2"
  end
  resource "jsonschema" do
    url "https://files.pythonhosted.org/packages/69/90/f63fb5873511e014207a475e2bb4e8b2e570d655b00ac19a9a0ca0a385ee/jsonschema-4.26.0-py3-none-any.whl"
    sha256 "d489f15263b8d200f8387e64b4c3a75f06629559fb73deb8fdfb525f2dab50ce"
  end
  resource "jsonschema-specifications" do
    url "https://files.pythonhosted.org/packages/41/45/1a4ed80516f02155c51f51e8cedb3c1902296743db0bbc66608a0db2814f/jsonschema_specifications-2025.9.1-py3-none-any.whl"
    sha256 "98802fee3a11ee76ecaca44429fda8a41bff98b00a0f2838151b113f210cc6fe"
  end
  resource "mcp" do
    url "https://files.pythonhosted.org/packages/67/72/7d7897418912c1d12e87556630dfb7bf0eac71160e9bef8b447960804ee3/mcp-2.0.0-py3-none-any.whl"
    sha256 "1cb4c75d2d2c7b8c1d756355e5d82a39f2822cc7f13e22a2051d7ca3592349d6"
  end
  resource "mcp-types" do
    url "https://files.pythonhosted.org/packages/f5/4c/c78d78c3d52b0ac594ad7cc8ef5972adfe070e3597a8a4c6ce0cd39196ea/mcp_types-2.0.0-py3-none-any.whl"
    sha256 "6b2de797ca2797f568b79529e1b25948e34de511bcc0bd82fef1039a6d1b8eb0"
  end
  resource "numpy" do
    if OS.mac? && Hardware::CPU.arm?
      url "https://files.pythonhosted.org/packages/ab/ab/ddb499fc4f8780354395face5b65c7fd107bcd6e1d667a5f07d046956f6f/numpy-2.5.1-cp313-cp313-macosx_11_0_arm64.whl"
      sha256 "30b44a6b53a7ae63c54c089a8726e5563ed302716c5b7ccc85afade40b0e7ff6"
    elsif OS.mac? && Hardware::CPU.intel?
      url "https://files.pythonhosted.org/packages/eb/07/ec2a3f0c91761581d4b7104a740791800025983f9a4dc4e73f91a99aeac4/numpy-2.5.1-cp313-cp313-macosx_10_13_x86_64.whl"
      sha256 "0bfebd8695f9863592fe744be833a258120b14a9f39da255e8aa8fade2c0ddd1"
    elsif OS.linux?
      url "https://files.pythonhosted.org/packages/ed/a7/2bcd3fdbb87804755c35b729bf8709d62025c5f4cfd7d5b2415997097515/numpy-2.5.1-cp313-cp313-manylinux_2_27_x86_64.manylinux_2_28_x86_64.whl"
      sha256 "9726558e8db4a5bf7929a70ae50f63abda4daf0efe810e3bfbab95976f75fc1a"
    else
      url "https://files.pythonhosted.org/packages/ab/ab/ddb499fc4f8780354395face5b65c7fd107bcd6e1d667a5f07d046956f6f/numpy-2.5.1-cp313-cp313-macosx_11_0_arm64.whl"
      sha256 "30b44a6b53a7ae63c54c089a8726e5563ed302716c5b7ccc85afade40b0e7ff6"
    end
  end
  resource "opentelemetry-api" do
    url "https://files.pythonhosted.org/packages/ca/6f/a04e900f465ff3221ccc395522503e2d10e79fa21f2723c8e177aae1e0d1/opentelemetry_api-1.44.0-py3-none-any.whl"
    sha256 "94b98c893a91b88657eaac1e3ba89618cdb85be6918196705354f34728b2cdef"
  end
  resource "ply" do
    url "https://files.pythonhosted.org/packages/a3/58/35da89ee790598a0700ea49b2a66594140f44dec458c07e8e3d4979137fc/ply-3.11-py2.py3-none-any.whl"
    sha256 "096f9b8350b65ebd2fd1346b12452efe5b9607f7482813ffca50c22722a807ce"
  end
  resource "psycopg" do
    url "https://files.pythonhosted.org/packages/5c/e0/7b3dee031daae7743609ce3c746565d4a3ed7c2c186479eb48e34e838c64/psycopg-3.3.4-py3-none-any.whl"
    sha256 "b6bbc25ccf05c8fad3b061d9db2ef0909a555171b84b07f29458a447253d679a"
  end
  resource "psycopg-pool" do
    url "https://files.pythonhosted.org/packages/37/ed/89c2c620af0e1660354cd8aabf9f5b21f911597ce22acb37c805d6c86bc8/psycopg_pool-3.3.1-py3-none-any.whl"
    sha256 "2af5b432941c4c9ad5c87b3fa410aec910ec8f7c122855897983a06c45f2e4b5"
  end
  resource "pydantic" do
    url "https://files.pythonhosted.org/packages/fd/7b/122376b1fd3c62c1ed9dc80c931ace4844b3c55407b6fb2d199377c9736f/pydantic-2.13.4-py3-none-any.whl"
    sha256 "45a282cde31d808236fd7ea9d919b128653c8b38b393d1c4ab335c62924d9aba"
  end
  resource "pydantic-core" do
    if OS.mac? && Hardware::CPU.arm?
      url "https://files.pythonhosted.org/packages/c1/81/4fa520eaffa8bd7d1525e644cd6d39e7d60b1592bc5b516693c7340b50f1/pydantic_core-2.46.4-cp313-cp313-macosx_11_0_arm64.whl"
      sha256 "c94f0688e7b8d0a67abf40e57a7eaaecd17cc9586706a31b76c031f63df052b4"
    elsif OS.mac? && Hardware::CPU.intel?
      url "https://files.pythonhosted.org/packages/51/a2/5d30b469c5267a17b39dec53208222f76a8d351dfac4af661888c5aee77d/pydantic_core-2.46.4-cp313-cp313-macosx_10_12_x86_64.whl"
      sha256 "5d5902252db0d3cedf8d4a1bc68f70eeb430f7e4c7104c8c476753519b423008"
    elsif OS.linux?
      url "https://files.pythonhosted.org/packages/07/f8/41db9de19d7987d6b04715a02b3b40aea467000275d9d758ffaa31af7d50/pydantic_core-2.46.4-cp313-cp313-manylinux_2_17_x86_64.manylinux2014_x86_64.whl"
      sha256 "9551187363ffc0de2a00b2e47c25aeaeb1020b69b668762966df15fc5659dd5a"
    else
      url "https://files.pythonhosted.org/packages/c1/81/4fa520eaffa8bd7d1525e644cd6d39e7d60b1592bc5b516693c7340b50f1/pydantic_core-2.46.4-cp313-cp313-macosx_11_0_arm64.whl"
      sha256 "c94f0688e7b8d0a67abf40e57a7eaaecd17cc9586706a31b76c031f63df052b4"
    end
  end
  resource "python-multipart" do
    url "https://files.pythonhosted.org/packages/e1/04/e8135ebd1ad02c56ec633277529b2602ff99ff634be76cdba5744cf554fd/python_multipart-0.0.32-py3-none-any.whl"
    sha256 "ff6d3f776f16878c894e52e107296ffc890e913c611b1a4ec6c44e2821fe2e23"
  end
  resource "referencing" do
    url "https://files.pythonhosted.org/packages/2c/58/ca301544e1fa93ed4f80d724bf5b194f6e4b945841c5bfd555878eea9fcb/referencing-0.37.0-py3-none-any.whl"
    sha256 "381329a9f99628c9069361716891d34ad94af76e461dcb0335825aecc7692231"
  end
  resource "rpds-py" do
    if OS.mac? && Hardware::CPU.arm?
      url "https://files.pythonhosted.org/packages/f3/6b/686d9dc4359a8f163cfbbf89ee0b4e586431de22fe8248edb63a8cf50d49/rpds_py-2026.6.3-cp313-cp313-macosx_11_0_arm64.whl"
      sha256 "f4d78253f6996be4901669ad25319f842f740eccf4d58e3c7f3dd39e6dde1d8f"
    elsif OS.mac? && Hardware::CPU.intel?
      url "https://files.pythonhosted.org/packages/a4/9e/b818ee580026ec578138e961027a68820c40afeb1ec8f6819b54fb99e196/rpds_py-2026.6.3-cp313-cp313-macosx_10_12_x86_64.whl"
      sha256 "3cfe765c1da0072636ca06628261e0ea05688e160d5c8a03e0217c3854037223"
    elsif OS.linux?
      url "https://files.pythonhosted.org/packages/57/d7/fe978efc2ae50abe48eb7464668ea99f53c010c60aeebb7b35ad27f23661/rpds_py-2026.6.3-cp313-cp313-manylinux_2_17_x86_64.manylinux2014_x86_64.whl"
      sha256 "acac386b453c2516111b50985d60ce46e7fadb5ea71ae7b25f4c946935bf27cf"
    else
      url "https://files.pythonhosted.org/packages/f3/6b/686d9dc4359a8f163cfbbf89ee0b4e586431de22fe8248edb63a8cf50d49/rpds_py-2026.6.3-cp313-cp313-macosx_11_0_arm64.whl"
      sha256 "f4d78253f6996be4901669ad25319f842f740eccf4d58e3c7f3dd39e6dde1d8f"
    end
  end
  resource "shtab" do
    url "https://files.pythonhosted.org/packages/9f/2f/35d4ec80d8ee39e792cd6e0d4f3dd84ea6783f13b7c47b4c319d9062aaf0/shtab-1.8.1-py3-none-any.whl"
    sha256 "4fc418e0173e66385e4605044a26a4910e73dde2dc23e809acc2f0275e842426"
  end
  resource "sse-starlette" do
    url "https://files.pythonhosted.org/packages/49/36/e10c1d1b7ca881d2625db2ec28508578499187bb1c389952c398474e1834/sse_starlette-3.4.6-py3-none-any.whl"
    sha256 "56217ab4c9a9f9c5db7b21e08732d3e7c2b807f45231ad23de0551a24c4a41f6"
  end
  resource "starlette" do
    url "https://files.pythonhosted.org/packages/ec/bb/2799cc2ede3ed41131f8975621e7213dfc7ef4acbbaadfa440f32500c370/starlette-1.3.1-py3-none-any.whl"
    sha256 "c7372aae11c3c3f26a42df7bd626cec2f47d03483d261d369516a615a53714c6"
  end
  resource "truststore" do
    url "https://files.pythonhosted.org/packages/19/97/56608b2249fe206a67cd573bc93cd9896e1efb9e98bce9c163bcdc704b88/truststore-0.10.4-py3-none-any.whl"
    sha256 "adaeaecf1cbb5f4de3b1959b42d41f6fab57b2b1666adb59e89cb0b53361d981"
  end
  resource "typing-extensions" do
    url "https://files.pythonhosted.org/packages/49/d3/b8441a820a491ddfc024b0b0cf0393375b75ea13866d9c66727e54c2fc80/typing_extensions-4.16.0-py3-none-any.whl"
    sha256 "481caa481374e813c1b176ada14e97f1f67a4539ce9cfeb3f350d78d6370c2e8"
  end
  resource "typing-inspection" do
    url "https://files.pythonhosted.org/packages/dc/9b/47798a6c91d8bdb567fe2698fe81e0c6b7cb7ef4d13da4114b41d239f65d/typing_inspection-0.4.2-py3-none-any.whl"
    sha256 "4ed1cacbdc298c220f1bd249ed5287caa16f34d44ef4e9c3d0cbad5b521545e7"
  end
  resource "uvicorn" do
    url "https://files.pythonhosted.org/packages/45/ec/dbb7e5a6b91f86bfb9eb7d2988a2730907b6a729875b949c7f022e8b88fa/uvicorn-0.51.0-py3-none-any.whl"
    sha256 "5d38af6cd620f2ae3849fb44fd4879e0890aa1febe8d47eb355fb45d93fe6a5b"
  end

  def install
    if OS.mac?
      ENV.append "LDFLAGS", "-Wl,-headerpad_max_install_names"
      ENV.append "RUSTFLAGS", "-C link-arg=-Wl,-headerpad_max_install_names"
    end

    venv = virtualenv_create(libexec, "python3.13")

    resource("agefreighter").stage do
      wheel = Dir["*.whl"].first
      if wheel
        venv.pip_install Pathname(wheel)
      else
        venv.pip_install Pathname.pwd
      end
    end

    resource("aiofiles").stage do
      wheel = Dir["*.whl"].first
      if wheel
        venv.pip_install Pathname(wheel)
      else
        venv.pip_install Pathname.pwd
      end
    end

    resource("annotated-types").stage do
      wheel = Dir["*.whl"].first
      if wheel
        venv.pip_install Pathname(wheel)
      else
        venv.pip_install Pathname.pwd
      end
    end

    resource("anyio").stage do
      wheel = Dir["*.whl"].first
      if wheel
        venv.pip_install Pathname(wheel)
      else
        venv.pip_install Pathname.pwd
      end
    end

    resource("argcomplete").stage do
      wheel = Dir["*.whl"].first
      if wheel
        venv.pip_install Pathname(wheel)
      else
        venv.pip_install Pathname.pwd
      end
    end

    resource("attrs").stage do
      wheel = Dir["*.whl"].first
      if wheel
        venv.pip_install Pathname(wheel)
      else
        venv.pip_install Pathname.pwd
      end
    end

    resource("click").stage do
      wheel = Dir["*.whl"].first
      if wheel
        venv.pip_install Pathname(wheel)
      else
        venv.pip_install Pathname.pwd
      end
    end

    resource("h11").stage do
      wheel = Dir["*.whl"].first
      if wheel
        venv.pip_install Pathname(wheel)
      else
        venv.pip_install Pathname.pwd
      end
    end

    resource("httpcore2").stage do
      wheel = Dir["*.whl"].first
      if wheel
        venv.pip_install Pathname(wheel)
      else
        venv.pip_install Pathname.pwd
      end
    end

    resource("httpx2").stage do
      wheel = Dir["*.whl"].first
      if wheel
        venv.pip_install Pathname(wheel)
      else
        venv.pip_install Pathname.pwd
      end
    end

    resource("idna").stage do
      wheel = Dir["*.whl"].first
      if wheel
        venv.pip_install Pathname(wheel)
      else
        venv.pip_install Pathname.pwd
      end
    end

    resource("jsonschema").stage do
      wheel = Dir["*.whl"].first
      if wheel
        venv.pip_install Pathname(wheel)
      else
        venv.pip_install Pathname.pwd
      end
    end

    resource("jsonschema-specifications").stage do
      wheel = Dir["*.whl"].first
      if wheel
        venv.pip_install Pathname(wheel)
      else
        venv.pip_install Pathname.pwd
      end
    end

    resource("mcp").stage do
      wheel = Dir["*.whl"].first
      if wheel
        venv.pip_install Pathname(wheel)
      else
        venv.pip_install Pathname.pwd
      end
    end

    resource("mcp-types").stage do
      wheel = Dir["*.whl"].first
      if wheel
        venv.pip_install Pathname(wheel)
      else
        venv.pip_install Pathname.pwd
      end
    end

    resource("numpy").stage do
      if OS.mac? && Hardware::CPU.arm?
        venv.pip_install Pathname(Dir["*.whl"].first)
      elsif OS.mac? && Hardware::CPU.intel?
        venv.pip_install Pathname(Dir["*.whl"].first)
      elsif OS.linux?
        venv.pip_install Pathname(Dir["*.whl"].first)
      else
        venv.pip_install Pathname.pwd
      end
    end

    resource("opentelemetry-api").stage do
      wheel = Dir["*.whl"].first
      if wheel
        venv.pip_install Pathname(wheel)
      else
        venv.pip_install Pathname.pwd
      end
    end

    resource("ply").stage do
      wheel = Dir["*.whl"].first
      if wheel
        venv.pip_install Pathname(wheel)
      else
        venv.pip_install Pathname.pwd
      end
    end

    resource("psycopg").stage do
      wheel = Dir["*.whl"].first
      if wheel
        venv.pip_install Pathname(wheel)
      else
        venv.pip_install Pathname.pwd
      end
    end

    resource("psycopg-pool").stage do
      wheel = Dir["*.whl"].first
      if wheel
        venv.pip_install Pathname(wheel)
      else
        venv.pip_install Pathname.pwd
      end
    end

    resource("pydantic").stage do
      wheel = Dir["*.whl"].first
      if wheel
        venv.pip_install Pathname(wheel)
      else
        venv.pip_install Pathname.pwd
      end
    end

    resource("pydantic-core").stage do
      if OS.mac? && Hardware::CPU.arm?
        venv.pip_install Pathname(Dir["*.whl"].first)
      elsif OS.mac? && Hardware::CPU.intel?
        venv.pip_install Pathname(Dir["*.whl"].first)
      elsif OS.linux?
        venv.pip_install Pathname(Dir["*.whl"].first)
      else
        venv.pip_install Pathname.pwd
      end
    end

    resource("python-multipart").stage do
      wheel = Dir["*.whl"].first
      if wheel
        venv.pip_install Pathname(wheel)
      else
        venv.pip_install Pathname.pwd
      end
    end

    resource("referencing").stage do
      wheel = Dir["*.whl"].first
      if wheel
        venv.pip_install Pathname(wheel)
      else
        venv.pip_install Pathname.pwd
      end
    end

    resource("rpds-py").stage do
      if OS.mac? && Hardware::CPU.arm?
        venv.pip_install Pathname(Dir["*.whl"].first)
      elsif OS.mac? && Hardware::CPU.intel?
        venv.pip_install Pathname(Dir["*.whl"].first)
      elsif OS.linux?
        venv.pip_install Pathname(Dir["*.whl"].first)
      else
        venv.pip_install Pathname.pwd
      end
    end

    resource("shtab").stage do
      wheel = Dir["*.whl"].first
      if wheel
        venv.pip_install Pathname(wheel)
      else
        venv.pip_install Pathname.pwd
      end
    end

    resource("sse-starlette").stage do
      wheel = Dir["*.whl"].first
      if wheel
        venv.pip_install Pathname(wheel)
      else
        venv.pip_install Pathname.pwd
      end
    end

    resource("starlette").stage do
      wheel = Dir["*.whl"].first
      if wheel
        venv.pip_install Pathname(wheel)
      else
        venv.pip_install Pathname.pwd
      end
    end

    resource("truststore").stage do
      wheel = Dir["*.whl"].first
      if wheel
        venv.pip_install Pathname(wheel)
      else
        venv.pip_install Pathname.pwd
      end
    end

    resource("typing-extensions").stage do
      wheel = Dir["*.whl"].first
      if wheel
        venv.pip_install Pathname(wheel)
      else
        venv.pip_install Pathname.pwd
      end
    end

    resource("typing-inspection").stage do
      wheel = Dir["*.whl"].first
      if wheel
        venv.pip_install Pathname(wheel)
      else
        venv.pip_install Pathname.pwd
      end
    end

    resource("uvicorn").stage do
      wheel = Dir["*.whl"].first
      if wheel
        venv.pip_install Pathname(wheel)
      else
        venv.pip_install Pathname.pwd
      end
    end

    venv.pip_install buildpath
    bin.install_symlink libexec/"bin/age_mcp_server"
  end

  test do
    system "#{bin}/age_mcp_server", "--help"
  end
end
