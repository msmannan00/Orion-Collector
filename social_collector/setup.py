import os
import sys
import shutil
import zipfile
import requests
import argostranslate.package
from crawler.constants.constants import LANGUAGE_MODEL_PATH

RAW_DIR = "raw"
MODEL_ZIP_NAME = "ru_en_model.zip"
MODEL_URL = LANGUAGE_MODEL_PATH
EXTRACTED_DIR_NAME = "translate-en_ru-1_9"

class social_setup:
    _instance = None

    @staticmethod
    def get_instance():
        return social_setup()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(social_setup, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        print("[INFO] Initializing Social Setup...")
        self._ensure_raw_dir()
        self._clean_old_zip()
        if self._is_model_folder_valid():
            print("[INFO] Model folder already exists and is valid. Skipping download.")
        else:
            self._delete_model_folder()
            self._download_model()
            self._extract_model()
        self._install_model()
        self.config = self._load_config()

    def load(self):
        pass

    def _ensure_raw_dir(self):
        os.makedirs(RAW_DIR, exist_ok=True)

    def _clean_old_zip(self):
        zip_path = os.path.join(RAW_DIR, MODEL_ZIP_NAME)
        if os.path.exists(zip_path):
            os.remove(zip_path)
            print("[INFO] Old ZIP file removed.")

    def _is_model_folder_valid(self):
        model_dir = os.path.join(RAW_DIR, EXTRACTED_DIR_NAME)
        model_path = os.path.join(model_dir, "model")
        stanza_path = os.path.join(model_dir, "stanza")
        return (
            os.path.isdir(model_dir) and
            os.path.isdir(model_path) and
            os.path.isdir(stanza_path)
        )

    def _delete_model_folder(self):
        model_dir = os.path.join(RAW_DIR, EXTRACTED_DIR_NAME)
        if os.path.exists(model_dir):
            shutil.rmtree(model_dir)
            print("[INFO] Invalid or partial model folder removed.")

    def _download_model(self):
        print("[INFO] Downloading model...")
        zip_path = os.path.join(RAW_DIR, MODEL_ZIP_NAME)
        response = requests.get(MODEL_URL, stream=True)
        response.raise_for_status()

        total_size = int(response.headers.get("Content-Length", 0))
        downloaded = 0
        chunk_size = 8192

        with open(zip_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    done = int(50 * downloaded / total_size) if total_size else 0
                    sys.stdout.write("\r[DOWNLOAD] [{}{}] {:.2f}%".format(
                        "#" * done, "." * (50 - done), 100 * downloaded / total_size if total_size else 0))
                    sys.stdout.flush()

        sys.stdout.write("\n")
        print(f"[INFO] Model downloaded to {zip_path} ({os.path.getsize(zip_path)} bytes)")

    def _extract_model(self):
        zip_path = os.path.join(RAW_DIR, MODEL_ZIP_NAME)
        print("[INFO] Extracting model...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(RAW_DIR)
        os.remove(zip_path)
        print("[INFO] ZIP deleted.")

    def _install_model(self):
        print("[INFO] Checking for .argosmodel files to install...")
        found = False
        for root, _, files in os.walk(RAW_DIR):
            for file in files:
                if file.endswith(".argosmodel"):
                    model_path = os.path.join(root, file)
                    argostranslate.package.install_from_path(model_path)
                    print(f"[INFO] Installed model from: {model_path}")
                    found = True
        if not found:
            print("[INFO] Already Installed — assuming structured model directory is in use, skipping install.")

    def get_model_paths(self):
        base_path = os.path.join(RAW_DIR, EXTRACTED_DIR_NAME)
        model_path = os.path.join(base_path, "model")
        stanza_path = os.path.join(base_path, "stanza")
        return {
            "base": base_path,
            "model": model_path,
            "stanza": stanza_path
        }

    @staticmethod
    def _load_config():
        return {
            "twitter_api_key": "your-key",
            "facebook_app_id": "your-app-id"
        }

    def get_config(self):
        return self.config
