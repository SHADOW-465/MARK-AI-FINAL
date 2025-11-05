<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# Comprehensive Production Flow \& Development Prompt for EduGrade AI (K-5 Grading Platform)

This prompt provides **structured, step-by-step instructions** to build a production-ready EduGrade AI grading application as per your specific requirements and user flow. It covers backend agents, end-to-end processing pipeline, UI buildout with Streamlit, and necessary features for teacher, parent, and admin interactions. Use this as your definitive guide for system development in Cursor or other modern IDEs.

***

## A. Application Flow (Functional Breakdown)

1. **Teacher Upload**
    - Teachers scan student answer sheets using school printers.
    - Supported upload formats: PDF, JPG, PNG.
    - Sheets can be multi-page PDFs or individual images.
    - Upload interface should provide batch upload capability and per-sheet preview.
2. **Preprocessing Agent**
    - Upon upload, files are passed through OpenCV-based preprocessing:
        - Deskew images (±15°)
        - Noise reduction
        - Binarization and contrast enhancement
        - Output cleaned images
3. **Segmentation Agent**
    - Cleaned images are processed using YOLOv8 Tiny segmentation:
        - Detect answer boxes (grid or AI model)
        - Segment each box/question region
        - Assign region/question labels for further processing
4. **AI Grading Agent**
    - Each answer region is forwarded to the grading LLM (Gemini, or similar):
        - Use teacher-provided answer key
        - Grade student answers using string matching, semantic checking, partial credit logic
        - Generate feedback for each answer
        - Return preliminary scores and feedback per question/page
5. **Fact Checking Agent**
    - Parsed answers are sent to Perplexity API:
        - Validate facts beyond answer key (correct but alternate answers, enrichment insights)
        - Provide remarks for improvement or additional knowledge
        - Attach insights to grading feedback for teacher review
6. **Teacher Approval Dashboard**
    - UI enables teacher to:
        - Review AI-graded answer sheets, page by page
        - Accept, override, or edit grades and feedback (per-student, per-question)
        - Approve sheet for final reporting
        - Approved sheets are flagged and queued for parent report generation
7. **Parent Dashboard**
    - Only after teacher approval, parent UI is unlocked:
        - View student report (grades, feedback, insights)
        - Download/print report card
        - Access summary of performance and improvement suggestions
        - Notification and achievement flags (blockchain verified if enabled)

***

## B. Detailed Development Instructions

### 1. Backend \& Agents

**File Upload Endpoint**

- Implement endpoints for secure \& robust batch file upload (`POST /api/v1/submissions/`)
- Support for PDF/JPG/PNG (multiple pages per submission); auto-processing starts after upload.

**Preprocessing Agent - OpenCV**

- Implement all core cleaning steps (deskew, denoise, binarization).
- Use page-by-page processing for multi-page PDFs.

**Segmentation Agent - YOLOv8 Tiny**

- Deploy YOLOv8 Tiny model for on-the-fly segmentation.
- Provide fallback grid detection for sheets with standardized layouts.
- Store extracted answer regions with region metadata (question number, coordinates).

**AI Grading Agent - Gemini AI**

- Accept answer key and answer region images/text.
- Execute grades via string/semantic match and partial credit scoring.
- Generate student-friendly feedback for every answer.
- Store per-question grades with feedback in Firebase.

**Fact Checking Agent - Perplexity API**

- Parse each answer for fact validation via Perplexity Sonar.
- Attach additional remarks/insights (correctness, alternative answers, enrichment).
- Integrate fact-check result into feedback payload.

**Grade Approval Workflow**

- Implement status tracking for each submission (`Pending`, `In Review`, `Approved`, `Flagged`)
- Enable teachers to edit scores, override AI decisions, and approve sheets.

**Database Integration**

- Use Firebase for all app state, results, user/auth management, answer keys.
- Optional: Log approved grades on DevDock blockchain for verification.

**API Endpoints (Core)**

- `/exams/`       : Create exam, upload answer key
- `/submissions/` : Upload scanned answer sheets (PDF/JPG/PNG)
- `/process/`     : Trigger grading and fact-check workflow per submission
- `/grades/{id}/` : Retrieve grades, feedback
- `/approve/{id}/`: Approve grades (teacher dashboard)
- `/reports/{student_id}`: Parent view/report download


### 2. Frontend (Streamlit UI)

**Teacher Dashboard**

- Upload interface for bulk/batch files
- Progress bar/status for preprocessing, grading, segmentation per sheet
- Preview of processed results (original \& cleaned image, segmented answer boxes)
- Table/grid showing grades, feedback, and fact insights for each sheet
- Edit/override tools (score, feedback, manual input)
- Approve button for sheet submission
- Notifications for new uploads and approval actions

**Parent Dashboard**

- Secure login/access per parent
- View student’s report only after teacher approval
- Rich grade breakdown (score, feedback, improvement suggestions)
- Download/print options for report cards

**Admin Features**

- Manage users/roles (teacher, parent, admin)
- System health monitoring
- Audit log access (submission status, approval timestamps)


### 3. App Structure \& Essential Files

```
edugrade-k5/
├── backend/
│   ├── app/
│   │   ├── main.py                # FastAPI API/server
│   │   ├── agents/
│   │   │   ├── preprocessing_agent.py # OpenCV logic
│   │   │   ├── segmentation_agent.py  # YOLOv8 Tiny inference
│   │   │   ├── grading_agent.py       # Gemini AI scoring
│   │   │   └── factcheck_agent.py     # Perplexity API client
│   │   ├── api/
│   │   │   ├── exams.py
│   │   │   ├── submissions.py
│   │   │   └── approvals.py
│   │   ├── services/
│   │   │   ├── firebase_service.py
│   │   │   └── devdock_service.py
│   └── requirements.txt
├── frontend/
│   ├── streamlit_dashboard.py     # Main UI logic
│   └── components/                # UI widgets/utilities
├── data/
│   ├── models/yolov8-tiny.pt      # Segmentation model
│   └── sample_sheets/             # Test uploads
```


### 4. Testing, Maintenance \& Deployment

- Write modular, agent-specific unit tests for all critical flows
- Automate integration tests for API endpoints and UI interactions
- Containerize with Docker for consistent deployment
- Document setup, workflow, and user instructions in README
- Integrate continuous deployment pipeline for new feature rollouts


### 5. User Experience \& Compliance

- Make all UI elements intuitive for teacher/parent use; provide in-app tips and help
- Ensure privacy and security in report access and uploads
- Support error handling and helpdesk requests via dashboard notifications

***

**In summary:**
Build the EduGrade K-5 grading platform according to the above specifications, incorporating all backend agents and database integrations, and crafting a robust, user-friendly, and fully auditable frontend with Streamlit. Ensure teacher approval before parent report release, support all major scan/upload formats, optimize for K-5 handwriting and simple answer structures, and integrate all sponsor and fact-check APIs as described.

Use this prompt as the project master plan for development, review, and deployment.

