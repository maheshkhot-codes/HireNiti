import uuid
import json

from fastapi import (
    APIRouter,
    Depends,
    UploadFile,
    File,
    HTTPException
)

from sqlalchemy.orm import Session

from app.resume.analyzer import analyze_resume
from app.database.session import get_db
from app.auth.dependencies import require_role
from app.resume.models import Resume
from app.resume.parser import extract_resume_text
from app.storage.supabase_storage import (
    supabase,
    BUCKET_NAME
)
from app.ml.pipeline.candidate_embedding import (
    save_resume_embedding
)

router = APIRouter(
    prefix="/resumes",
    tags=["Resumes"]
)


ALLOWED_EXTENSIONS = {
    ".pdf",
    ".docx"
}


MAX_FILE_SIZE = 5 * 1024 * 1024


# =========================================================
# UPLOAD RESUME
# =========================================================

@router.post("/upload")
async def upload_resume(
    file: UploadFile = File(...),
    current_user=Depends(
        require_role("candidate")
    ),
    db: Session = Depends(get_db)
):

    # -----------------------------------------------------
    # 1. Validate file name
    # -----------------------------------------------------

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="File name is required"
        )

    filename = file.filename.lower()


    # -----------------------------------------------------
    # 2. Validate extension
    # -----------------------------------------------------

    extension = None

    for allowed in ALLOWED_EXTENSIONS:

        if filename.endswith(allowed):

            extension = allowed

            break


    if not extension:

        raise HTTPException(
            status_code=400,
            detail="Only PDF and DOCX files are allowed"
        )


    # -----------------------------------------------------
    # 3. Read file
    # -----------------------------------------------------

    file_bytes = await file.read()


    # -----------------------------------------------------
    # 4. Validate file size
    # -----------------------------------------------------

    if len(file_bytes) > MAX_FILE_SIZE:

        raise HTTPException(
            status_code=400,
            detail="Maximum file size is 5 MB"
        )


    # -----------------------------------------------------
    # 5. Extract resume text
    # -----------------------------------------------------

    file_type = (
        "pdf"
        if extension == ".pdf"
        else "docx"
    )


    try:

        parsed_text = extract_resume_text(
            file_bytes,
            file_type
        )

    except Exception as error:

        raise HTTPException(
            status_code=400,
            detail=f"Could not parse resume: {error}"
        )


    if not parsed_text:

        raise HTTPException(
            status_code=400,
            detail="Could not extract text from resume"
        )


    # -----------------------------------------------------
    # 6. Create unique storage path
    # -----------------------------------------------------

    unique_name = (
        f"{current_user.id}/"
        f"{uuid.uuid4()}"
        f"{extension}"
    )


    # -----------------------------------------------------
    # 7. Upload to Supabase Storage
    # -----------------------------------------------------

    try:

        supabase.storage \
            .from_(BUCKET_NAME) \
            .upload(
                unique_name,
                file_bytes,
                {
                    "content-type": (
                        "application/pdf"
                        if file_type == "pdf"
                        else "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )
                }
            )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=f"Storage upload failed: {error}"
        )


    # -----------------------------------------------------
    # 8. Save database record
    # -----------------------------------------------------

    resume = Resume(
        candidate_id=current_user.id,
        file_name=file.filename,
        file_url=unique_name,
        parsed_text=parsed_text
    )


    db.add(resume)

    db.commit()

    db.refresh(resume)


    # -----------------------------------------------------
    # 9. Return response
    # -----------------------------------------------------

    return {
        "message": "Resume uploaded successfully",

        "resume_id": str(
            resume.id
        ),

        "file_name": resume.file_name,

        "text_length": len(
            parsed_text
        )
    }


# =========================================================
# ANALYZE RESUME
# =========================================================

@router.post("/{resume_id}/analyze")
def analyze_uploaded_resume(
    resume_id: str,
    current_user=Depends(
        require_role("candidate")
    ),
    db: Session = Depends(get_db)
):

    # -----------------------------------------------------
    # 1. Find resume belonging to current candidate
    # -----------------------------------------------------

    resume = (
        db.query(Resume)
        .filter(
            Resume.id == resume_id,
            Resume.candidate_id == current_user.id
        )
        .first()
    )


    if not resume:

        raise HTTPException(
            status_code=404,
            detail="Resume not found"
        )


    # -----------------------------------------------------
    # 2. Make sure parsed text exists
    # -----------------------------------------------------

    if not resume.parsed_text:

        raise HTTPException(
            status_code=400,
            detail="Resume text is not available"
        )


    # -----------------------------------------------------
    # 3. Analyze resume
    # -----------------------------------------------------

    analysis = analyze_resume(
        resume.parsed_text
    )


    # -----------------------------------------------------
    # 4. Save extracted data
    # -----------------------------------------------------

    resume.skills = ", ".join(
        analysis["skills"]
    )


    resume.education = (
        analysis["education"]
    )


    resume.experience = (
        analysis["experience"]
    )


    # IMPORTANT:
    # projects is a list/dictionary structure,
    # but database column is TEXT.
    #
    # Therefore convert Python object → JSON string.

    resume.projects = json.dumps(
        analysis["projects"],
        ensure_ascii=False
    )


    # -----------------------------------------------------
    # 5. Save to database
    # -----------------------------------------------------

    db.commit()

    db.refresh(resume)
    save_resume_embedding(
    db=db,
    resume=resume
)


    # -----------------------------------------------------
    # 6. Return structured response
    # -----------------------------------------------------

    return {
        "message": "Resume analyzed successfully",

        "resume_id": str(
            resume.id
        ),

        "analysis": analysis
    }


# =========================================================
# GET RESUME
# =========================================================

@router.get("/{resume_id}")
def get_resume(
    resume_id: str,
    current_user=Depends(
        require_role("candidate")
    ),
    db: Session = Depends(get_db)
):

    # -----------------------------------------------------
    # 1. Find resume
    # -----------------------------------------------------

    resume = (
        db.query(Resume)
        .filter(
            Resume.id == resume_id,
            Resume.candidate_id == current_user.id
        )
        .first()
    )


    if not resume:

        raise HTTPException(
            status_code=404,
            detail="Resume not found"
        )


    # -----------------------------------------------------
    # 2. Convert stored JSON back to Python object
    # -----------------------------------------------------

    projects = []

    if resume.projects:

        try:

            projects = json.loads(
                resume.projects
            )

        except json.JSONDecodeError:

            # Backward compatibility for old
            # records that may contain plain text.
            projects = resume.projects


    # -----------------------------------------------------
    # 3. Return resume
    # -----------------------------------------------------

    return {
        "id": str(resume.id),

        "file_name": resume.file_name,

        "skills": resume.skills,

        "education": resume.education,

        "experience": resume.experience,

        "projects": projects
    }