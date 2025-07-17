# Homebrew formula for installing Katenary.
# Supports Linux (Intel/ARM) and macOS (Intel).
# Downloads appropriate binary and installs man page and shell completions.

class Katenary < Formula
  version '3.0.0-rc5'

  desc 'Description de votre application Katenary'
  homepage 'https://github.com/katenary/katenary'
  url "https://github.com/Katenary/katenary/archive/refs/tags/#{version}.tar.gz"
  sha256 'a616c2e4a5e28d305c18cab8004b285d9579a9b93e10f51cf79a2ca9da3c91aa'

  on_linux do
    if Hardware::CPU.intel? and Hardware::CPU.is_64_bit?
      url "https://github.com/Katenary/katenary/releases/download/#{version}/katenary-linux-#{version}.amd64.tar"
      sha256 'bfb0208dbe8880305382a9a62c73027d667858d5e2a9c9f7a146d6047d561640'
      def install
        bin.install 'local/bin/katenary'
        man1.install buildpath / 'local/share/man/man1/katenary.1'
        generate_completions_from_executable(bin / 'katenary', 'completion')
      end
    end

    if Hardware::CPU.arm? and Hardware::CPU.is_64_bit?
      url "https://github.com/Katenary/katenary/releases/download/#{version}/katenary-linux-#{version}.arm64.tar"
      sha256 '9eef16941439c7e992ba7c0ff8018d7ccd9de67c211a9d96be4cf14869368900'
      def install
        bin.install 'local/bin/katenary'
        man1.install buildpath / 'local/share/man/man1/katenary.1'
        generate_completions_from_executable(bin / 'katenary', 'completion')
      end
    end
  end

  on_macos do
    if Hardware::CPU.intel? and Hardware::CPU.is_64_bit?
        url "https://github.com/Katenary/katenary/releases/download/#{version}/katenary-darwin-amd64"
        sha256 'df7da7b9e74e86d5dadeed77a8a921aaa29e4fcc8edffdb2b72920672c56fbd4'
        def install
            bin.install 'katenary-darwin-amd64' => 'katenary'
        end
    end

    if Hardware::CPU.arm? and Hardware::CPU.is_64_bit?
        url "https://github.com/Katenary/katenary/releases/download/#{version}/katenary-darwin-arm64"
        sha256 '018232cd63855d344f3907bcaa5ec8ec586817e315e935221d174ce171782d9f'
        def install
            bin.install 'katenary-darwin-arm64' => 'katenary'
        end
    end
  end

  test do
    system "#{bin}/katenary", '--version'
  end
end
