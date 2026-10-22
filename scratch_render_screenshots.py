import subprocess
import tempfile
from pathlib import Path

ARTIFACT_DIR = Path("/Users/caiquecoelho/.gemini/antigravity/brain/bd608ae0-4bdf-4dd6-ac9a-79f71d837a11")
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

cards = [
    ("feedback_card1_falas_cidadaos.html", "feedback_card1_falas_cidadaos.png"),
    ("feedback_card2_aprovacao_voto_2022.html", "feedback_card2_aprovacao_voto_2022.png"),
    ("feedback_card3_renda_preocupacoes.html", "feedback_card3_renda_preocupacoes.png"),
]

for html_name, png_name in cards:
    html_p = ARTIFACT_DIR / html_name
    png_p = ARTIFACT_DIR / png_name
    print(f"Rendering {html_name} -> {png_name}...")
    with tempfile.TemporaryDirectory() as profile:
        cmd = [
            CHROME,
            "--headless=new",
            "--disable-gpu",
            "--no-first-run",
            "--no-default-browser-check",
            f"--user-data-dir={profile}",
            "--window-size=1200,675",
            f"--screenshot={png_p}",
            html_p.as_uri()
        ]
        try:
            subprocess.run(cmd, check=True, timeout=15)
        except subprocess.CalledProcessError as e:
            print(f"Chrome exited with {e.returncode}, checking if png exists...")
        except subprocess.TimeoutExpired:
            print("Timeout, checking if png exists...")
            
    print(f"Result for {png_name}: exists={png_p.exists()}, size={png_p.stat().st_size if png_p.exists() else 0} bytes")
