from pathlib import Path
from uuid import uuid4

from PIL import Image
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from backend.config import ALLOWED_EXTENSIONS, UPLOAD_DIR


def save_upload_file(file: FileStorage) -> Path:
    if not file.filename:
        raise ValueError("图片文件不能为空")

    suffix = Path(file.filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise ValueError("仅支持 JPG、JPEG、PNG 格式图片")

    safe_name = secure_filename(file.filename)
    final_name = f"{uuid4().hex}_{safe_name}"
    upload_path = UPLOAD_DIR / final_name
    file.save(upload_path)
    _verify_image(upload_path)
    return upload_path


def _verify_image(upload_path: Path) -> None:
    try:
        with Image.open(upload_path) as image:
            image.verify()
    except Exception as exc:
        upload_path.unlink(missing_ok=True)
        raise ValueError("上传文件不是有效图片，请重新选择。") from exc
