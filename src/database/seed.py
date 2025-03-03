from sqlalchemy.orm import Session
from src.models import entities
from datetime import datetime, timedelta, UTC
import random

def seed_database(db: Session):
    # Create admin user
    admin = entities.User(
        email="admin@company.com",
        hashed_password=entities.User.hash_password("admin123"),
        role=entities.UserRole.ADMIN
    )
    db.add(admin)
    db.commit()

    # Create sample companies
    companies = [
        entities.Company(
            name="Tech Innovators Inc",
            industry="Technology",
            location="San Francisco, CA",
            website="https://techinnovators.com",
            description="Leading technology company focused on AI and ML solutions",
            created_by=admin
        ),
        entities.Company(
            name="Global Solutions Ltd",
            industry="Consulting",
            location="New York, NY",
            website="https://globalsolutions.com",
            description="International consulting firm",
            created_by=admin
        ),
        entities.Company(
            name="Future Systems",
            industry="Software",
            location="Austin, TX",
            website="https://futuresystems.com",
            description="Enterprise software solutions provider",
            created_by=admin
        )
    ]
    db.add_all(companies)
    db.commit()

    # Create interview templates
    templates = [
        entities.InterviewTemplate(
            name="Standard Technical Interview",
            description="Standard technical interview process for software engineers",
            created_by=admin,
            steps=[
                entities.InterviewTemplateStep(
                    name="Initial Screening",
                    description="Basic technical screening call",
                    step_type=entities.InterviewStepType.SCREENING,
                    order=1,
                    duration_minutes=30,
                    required_participants="[\"HR\", \"Technical Lead\"]",
                    evaluation_criteria="[\"Communication\", \"Basic Technical Knowledge\"]",
                    passing_score=7,
                    created_by=admin
                ),
                entities.InterviewTemplateStep(
                    name="Technical Assessment",
                    description="In-depth technical interview",
                    step_type=entities.InterviewStepType.TECHNICAL,
                    order=2,
                    duration_minutes=60,
                    required_participants="[\"Senior Engineer\", \"Technical Lead\"]",
                    evaluation_criteria="[\"Problem Solving\", \"Code Quality\", \"System Design\"]",
                    passing_score=8,
                    created_by=admin
                ),
                entities.InterviewTemplateStep(
                    name="Culture Fit",
                    description="Team and culture fit interview",
                    step_type=entities.InterviewStepType.CULTURE_FIT,
                    order=3,
                    duration_minutes=45,
                    required_participants="[\"HR\", \"Team Lead\"]",
                    evaluation_criteria="[\"Team Fit\", \"Culture Alignment\"]",
                    passing_score=7,
                    created_by=admin
                )
            ]
        )
    ]
    db.add_all(templates)
    db.commit()

    # Create job openings
    job_openings = [
        entities.JobOpening(
            title="Senior Software Engineer",
            company=companies[0],
            description="Looking for an experienced software engineer...",
            requirements="5+ years of experience in Python, cloud technologies...",
            location="San Francisco, CA",
            salary_range="$130,000 - $180,000",
            job_type="full-time",
            experience_level="Senior",
            interview_template=templates[0],
            created_by=admin
        ),
        entities.JobOpening(
            title="Full Stack Developer",
            company=companies[1],
            description="Full stack developer position...",
            requirements="3+ years of experience with React and Node.js...",
            location="New York, NY",
            salary_range="$100,000 - $140,000",
            job_type="full-time",
            experience_level="Mid-level",
            interview_template=templates[0],
            created_by=admin
        )
    ]
    db.add_all(job_openings)
    db.commit()

    # Create sample candidates
    candidates = []
    for i in range(5):
        user = entities.User(
            email=f"candidate{i+1}@example.com",
            hashed_password=entities.User.hash_password("password123"),
            role=entities.UserRole.CANDIDATE
        )
        db.add(user)
        db.commit()

        candidate = entities.Candidate(
            user=user,
            first_name=f"John{i+1}",
            last_name=f"Doe{i+1}",
            email=f"candidate{i+1}@example.com",
            phone=f"+1555000{i:04d}",
            skills="Python, JavaScript, React, AWS",
            experience_years=random.randint(3, 10),
            current_company="Previous Corp",
            current_position="Software Engineer",
            education="{\"degree\": \"Bachelor's in Computer Science\", \"university\": \"Tech University\"}",
            created_by=admin
        )
        candidates.append(candidate)
    
    db.add_all(candidates)
    db.commit()

    # Create sample applications
    applications = []
    for candidate in candidates[:3]:  # First 3 candidates apply
        application = entities.Application(
            candidate=candidate,
            job_opening=random.choice(job_openings),
            status=entities.ApplicationStatus.APPLIED,
            applied_date=datetime.now(UTC) - timedelta(days=random.randint(1, 30)),
            resume_version="1.0",
            cover_letter="I am very interested in this position...",
            created_by=admin
        )
        applications.append(application)
    
    db.add_all(applications)
    db.commit()

    # Create email templates
    email_templates = [
        entities.EmailTemplate(
            name="Interview Success Template",
            description="Template for successful interview results",
            subject_template="Congratulations! {{ interview_type }} Interview Passed",
            html_content="""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body { font-family: Arial, sans-serif; line-height: 1.6; }
                    .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                    .header { background-color: #28a745; color: white; padding: 20px; text-align: center; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h2>Congratulations!</h2>
                    </div>
                    <p>Dear {{ candidate_name }},</p>
                    <p>We're pleased to inform you that you have successfully passed the {{ interview_type }} interview.</p>
                    <p>{{ feedback }}</p>
                    {% if is_final_step %}
                    <p>We will contact you soon with the next steps.</p>
                    {% else %}
                    <p>We will schedule your next interview soon.</p>
                    {% endif %}
                </div>
            </body>
            </html>
            """,
            type="interview_success",
            created_by=admin
        ),
        entities.EmailTemplate(
            name="Interview Failure Template",
            description="Template for unsuccessful interview results",
            subject_template="Interview Results: {{ interview_type }}",
            html_content="""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body { font-family: Arial, sans-serif; line-height: 1.6; }
                    .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                    .header { background-color: #6c757d; color: white; padding: 20px; text-align: center; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h2>Interview Results</h2>
                    </div>
                    <p>Dear {{ candidate_name }},</p>
                    <p>Thank you for participating in the {{ interview_type }} interview.</p>
                    <p>After careful consideration, we regret to inform you that we will not be moving forward with your application.</p>
                    <p>{{ feedback }}</p>
                    <p>We wish you the best in your future endeavors.</p>
                </div>
            </body>
            </html>
            """,
            type="interview_failure",
            created_by=admin
        )
    ]
    db.add_all(email_templates)
    db.commit() 