import api from "./api";


export interface RecruiterStats {
  total_jobs: number;
  active_jobs: number;
  total_applications: number;
  shortlisted: number;
  interviews: number;
  hired: number;
}


export interface RecruiterDashboardResponse {
  statistics: RecruiterStats;
}


export interface RecruiterJob {
  job_id: string;
  title: string;
  location: string | null;
  employment_type: string | null;
  status: string;
  created_at: string;

  applicant_count: number;
  shortlisted_count: number;
  interview_count: number;
  hired_count: number;
}


export interface CreateJobPayload {
  title: string;
  description: string;
  required_skills: string;
  preferred_skills: string;
  experience_min: number;
  experience_max: number;
  education: string;
  location: string;
  employment_type: string;
  salary_min: number;
  salary_max: number;
}


export interface CreateJobResponse {
  message: string;
  job_id: string;
  status: string;
  has_embedding: boolean;
}


export interface RankedCandidate {
  candidate_id: string;
  resume_id: string;
  name: string | null;
  email: string | null;

  application_id: string | null;
  application_status: string | null;

  semantic_score: number;
  skill_score: number;
  experience_score: number;
  education_score: number;
  final_score: number;

  ranking_score?: number;

  rank: number;
}


/* =========================================================
   DASHBOARD
   ========================================================= */

export async function getRecruiterDashboard() {
  const response =
    await api.get<RecruiterDashboardResponse>(
      "/recruiter/dashboard/"
    );

  return response.data;
}


/* =========================================================
   JOBS
   ========================================================= */

export async function getRecruiterJobs() {
  const response =
    await api.get<RecruiterJob[]>(
      "/recruiter/dashboard/jobs"
    );

  return response.data;
}


export async function createJob(
  payload: CreateJobPayload
) {
  const response =
    await api.post<CreateJobResponse>(
      "/jobs/",
      payload
    );

  return response.data;
}


export async function publishJob(
  jobId: string
) {
  const response =
    await api.patch(
      `/jobs/${jobId}/publish`
    );

  return response.data;
}


export async function deleteJob(
  jobId: string
) {
  const response =
    await api.delete(
      `/jobs/${jobId}`
    );

  return response.data;
}


/* =========================================================
   AI CANDIDATE RANKING
   ========================================================= */

export async function getAIRankedCandidates(
  jobId: string
) {
  const response =
    await api.get<RankedCandidate[]>(
      `/applications/job/${jobId}/ai-ranking`
    );

  return response.data;
}


/* =========================================================
   APPLICATION STATUS
   ========================================================= */

export async function updateApplicationStatus(
  applicationId: string,
  status: string
) {
  const response =
    await api.patch(
      `/applications/${applicationId}/status`,
      {
        status,
      }
    );

  return response.data;
}