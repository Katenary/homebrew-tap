from dataclasses import dataclass
from hashlib import sha256

import requests

PREAMBLE = """
  desc 'Description de votre application Katenary'
  homepage 'https://github.com/katenary/katenary'
  url "{SOURCE_URL}"
  sha256 '{SOURCE_SHA}'
"""

LINUX_INSTALL = """
    if Hardware::CPU.{arch}?
      url "{source}"
      sha256 '{sha256}'
      def install
        bin.install 'local/bin/katenary'
        man1.install buildpath / 'local/share/man/man1/katenary.1'
        generate_completions_from_executable(bin / 'katenary', 'completion')
      end
    end
"""

OSX_INSTALL = """
    if Hardware::CPU.intel?
        url "{source}"
        sha256 '{sha256}'
        def install
            bin.install '{filename}' => 'katenary'
        end
    end
"""


TPL = """
# Homebrew formula for installing Katenary.
# Supports Linux (Intel/ARM) and macOS (Intel).
# Downloads appropriate binary and installs man page and shell completions.

class Katenary < Formula
  version '{VERSION}'
{PREAMBLE}
  on_linux do
{LINUX}
  end

  on_macos do
{DARWIN}
  end

  test do
    system "#{{bin}}/katenary", '--version'
  end
end
""".strip("\n")

GITHUB_API_URL = "https://api.github.com/repos/"


@dataclass
class Info:
    source: str
    sha256: str


@dataclass
class Release:
    version: str
    url: str
    source_sha: str
    linux_amd64: Info
    linux_arm64: Info
    osx_amd64: Info


def get_latest_release(source="katenary/katenary") -> dict:
    response = requests.get(f"{GITHUB_API_URL}{source}/releases/latest")
    return response.json()


def get_info(os: str, arch: str, release: dict) -> Info:
    match os:
        case "linux":
            asset = next(
                (
                    asset
                    for asset in release["assets"]
                    if os in asset["name"] and asset["name"].endswith(f"{arch}.tar")
                ),
                None,
            )
            assert asset is not None, (
                f"No asset found for {os} {arch} in release {release['tag_name']}"
            )
        case "darwin":
            asset = next(
                asset
                for asset in release["assets"]
                if os in asset["name"] and arch in asset["name"]
            )
            assert asset is not None, (
                f"No asset found for {os} {arch} in release {release['tag_name']}"
            )

    return Info(
        source=asset.get("browser_download_url", ""),
        sha256=asset.get("digest", "SHA256_NOT_AVAILABLE").split(":")[1],
    )


def build_linux_install(release: Release) -> str:
    linux_amd64 = LINUX_INSTALL.format(
        source=release.linux_amd64.source.replace(release.version, "#{version}"),
        sha256=release.linux_amd64.sha256,
        arch="intel",
    )
    linux_arm64 = LINUX_INSTALL.format(
        source=release.linux_arm64.source.replace(release.version, "#{version}"),
        sha256=release.linux_arm64.sha256,
        arch="arm",
    )

    osx_amd64 = OSX_INSTALL.format(
        source=release.osx_amd64.source.replace(release.version, "#{version}"),
        sha256=release.osx_amd64.sha256,
        filename=release.osx_amd64.source.split("/")[-1],
        arch="intel",
    )

    linux_body = "\n\n".join([linux_amd64.strip("\n"), linux_arm64.strip("\n")])
    darwin_body = osx_amd64.strip("\n")

    preamble = PREAMBLE.format(
        SOURCE_URL=release.url.replace(release.version, "#{version}"),
        SOURCE_SHA=release.source_sha,
    )

    return TPL.format(
        VERSION=release.version,
        PREAMBLE=preamble,
        LINUX=linux_body,
        DARWIN=darwin_body,
    )


def get_sha256_from_url(url: str) -> str:
    content = requests.get(url, allow_redirects=True).content
    hashval = sha256(content).hexdigest()
    return f"{hashval}"


def main(repo="Katenary/katenary"):
    release = get_latest_release(repo)
    if "assets" not in release:
        print("No assets found in the latest release.")
        return
    linux_amd64 = get_info("linux", "amd64", release)
    linux_arm64 = get_info("linux", "arm64", release)
    osx_amd64 = get_info("darwin", "amd64", release)
    source_tarball = (
        f"https://github.com/{repo}/archive/refs/tags/"
        + release["tag_name"]
        + ".tar.gz"
    )
    res = Release(
        url=source_tarball,
        source_sha=get_sha256_from_url(source_tarball),
        version=release["tag_name"],
        linux_amd64=linux_amd64,
        linux_arm64=linux_arm64,
        osx_amd64=osx_amd64,
    )
    linux = build_linux_install(res)
    return linux


if __name__ == "__main__":
    print(main())
