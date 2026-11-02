"""Download the corpus PDFs into data/raw/.

Usage: python scripts/download_corpus.py
"""

import sys

import httpx

from rag_assistant.config import load_settings

BASE_URL = "https://messervices.cyber.gouv.fr/documents-guides"

CORPUS_URLS: dict[str, str] = {
    "windows10_vbs.pdf": f"{BASE_URL}/np_securisation_windows10_securite_reposant_sur_la_virtualisation_v1.pdf",
    "systemes_industriels.pdf": f"{BASE_URL}/Guide_Systemes_industriels__Mesures_detaillees_v2.pdf",
    "architectures_si_sensibles.pdf": (
        f"{BASE_URL}/anssi-guide-recommandations_architectures_systemes_information_sensibles_ou_diffusion_restreinte-v1.2.pdf"
    ),
    "linux_configuration.pdf": f"{BASE_URL}/fr_np_linux_configuration-v2.0.pdf",
    "hygiene_informatique.pdf": f"{BASE_URL}/guide_hygiene_informatique_anssi.pdf",
}


def main() -> None:
    raw_dir = load_settings().raw_dir
    raw_dir.mkdir(parents=True, exist_ok=True)
    downloaded, skipped, failed = [], [], []

    with httpx.Client(follow_redirects=True, timeout=60.0) as client:
        for file_name, url in CORPUS_URLS.items():
            target = raw_dir / file_name
            if target.exists():
                skipped.append(file_name)
                continue
            partial = target.with_suffix(".part")
            try:
                with client.stream("GET", url) as response:
                    response.raise_for_status()
                    with partial.open("wb") as output:
                        for data in response.iter_bytes():
                            output.write(data)
                with partial.open("rb") as written:
                    if written.read(5) != b"%PDF-":
                        raise ValueError("response is not a PDF")
            except (httpx.HTTPError, ValueError) as error:
                partial.unlink(missing_ok=True)
                failed.append(file_name)
                print(f"FAILED {file_name}: {error}", file=sys.stderr)
                continue
            partial.replace(target)
            downloaded.append(file_name)
            print(f"downloaded {file_name} ({target.stat().st_size / 1_000_000:.1f} MB)")

    print(f"Summary: {len(downloaded)} downloaded, {len(skipped)} skipped, {len(failed)} failed")
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
