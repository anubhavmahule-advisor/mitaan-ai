from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

STATUS_GUIDE = """
IMPORTANT - Status values in database and their plain English meaning:
- COMPLETED or OUT_FOR_DELIVERY = Completed / Delivered
- SENT_BACK_BY_HELP_DESK = Sent back by helpdesk
- SENT_BACK_FROM_GOV_PROCESS = Sent back by government
- IN_PROGRESS_GOV_PROCESS = Pending with government
- REJECTED_GOV_PROCESS = Rejected by government
- CANCELLED or CANCELLED_BY_CITIZEN = Cancelled
- PENDING_FIELD_AGENT_VISIT = Pending field visit
- RESCHEDULE_REQUEST_SYSTEM or RESCHEDULED_BY_CITIZEN = Rescheduled
- COMPLETE_DOCUMENT_SUBMISSION = Document submission done
- COMPLETE_FIELD_AGENT_VISIT = Field visit completed
- IN_PROGRESS_FIELD_AGENT_VISIT = Field visit in progress
- CITIZEN_UNAVAILABLE_FOR_DELIVERY = Citizen unavailable for delivery
- CERTIFICATE_REGEN_REQUEST = Certificate regeneration request

STRICTLY EXCLUDE these statuses from ALL queries - never include them:
- DRAFT_REQUEST
- SAVED_AS_DRAFT
- SLOT_UNAVAILABLE_PENDING_REQUEST
- DOCUMENTS_UNAVAILABLE_PENDING_REQUEST
- ARCHIEVED
"""

SCHEMA = """
Database: mitaan (MySQL)
Main Tables and Key Columns:

Table: application
  - id
  - ticket_number
  - status (see STATUS_GUIDE above)
  - request_type
  - Is_active (1=active, 0=inactive)
  - Is_deleted
  - createdAt
  - updatedAt (timestamp when record was last updated)
  - serviceCategoryId
  - addressId
  - citizenId

Table: eDistrict
  - applicationId
  - e_district_application_id (ARN)
  - appointmentDateTime
  - collectionDateTime
  - submissionDateTime
  - actionDate
  - approvedDateTime
  - sentBackDateTime
  - rejectionDateTime
  - deliveryDateTime
  - reason

Table: serviceMaster
  - id
  - name (service name e.g. Birth Certificate)

Table: serviceCategory
  - id
  - serviceMasterId

Table: ulb
  - id
  - name (ULB/city name e.g. Raipur, Balod)

Table: address
  - id
  - ulbId

Table: citizen
  - id
  - firstName
  - lastName

Key Joins:
- application → serviceCategory: application.serviceCategoryId = serviceCategory.id
- serviceCategory → serviceMaster: serviceCategory.serviceMasterId = serviceMaster.id
- application → address: application.addressId = address.id
- address → ulb: address.ulbId = ulb.id
- application → citizen: application.citizenId = citizen.id
- application → eDistrict: application.id = eDistrict.applicationId
"""

def generate_sql(user_question):
    prompt = f"""
You are an expert MySQL query writer for Mitaan project in Chhattisgarh.

{SCHEMA}

{STATUS_GUIDE}

Write a MySQL query to answer this question:
"{user_question}"

Rules:
- Always filter Is_active = 1 unless user asks for cancelled/inactive
- NEVER include excluded statuses in any query
- Use DISTINCT COUNT for ticket numbers
- Always use proper JOINs as defined in schema
- Return ONLY the SQL query — no explanation, no markdown, no backticks
- Query must be valid MySQL
"""
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    return response.text.strip()

def format_answer(user_question, sql, data):
    prompt = f"""
You are an expert government data analyst for Mitaan project in Chhattisgarh.

User asked: "{user_question}"

SQL that was run: {sql}

Data returned:
{data}

{STATUS_GUIDE}

Now answer the user question clearly based on the data.
- Be specific with numbers
- Keep it concise
- If data is empty say "No records found for this query"
"""
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    return response.text.strip()

def detect_trends(data):
    prompt = f"""
You are an expert government data analyst for Mitaan project in Chhattisgarh.

{STATUS_GUIDE}

Analyze this pending applications data and detect key trends:
{data}

Provide:
1. Top 3 critical observations
2. Which ULB needs urgent attention and why
3. Which service is most problematic
4. Any unusual patterns you notice
5. 2 actionable recommendations

Be specific with numbers. Keep it concise.
"""
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    return response.text.strip()