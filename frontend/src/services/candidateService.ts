import api from "./api";


/* =========================================================
   TYPES
   ========================================================= */

export interface RecommendedJob {
  job_id: string;
  title: string;
  description: string;
  required_skills: string | null;
  preferred_skills: string | null;
  education: string | null;

  experience_min: number | null;
  experience_max: number | null;

  location: string | null;
  employment_type: string | null;

  semantic_score: number;
  skill_score: number;
  experience_score: number;
  education_score: number;
  final_score: number;

  ranking_score?: number;
}


export interface ActiveJob {
  id: string;
  title: string;
  description: string;

  required_skills: string | null;
  preferred_skills: string | null;

  experience_min: number | null;
  experience_max: number | null;

  education: string | null;
  location: string | null;

  employment_type: string | null;

  salary_min: number | null;
  salary_max: number | null;
}


export interface Application {
  application_id: string;
  job_id: string;
  job_title: string;
  location: string | null;
  employment_type: string | null;
  status: string;
  applied_at: string;
}


/* =========================================================
   AI RECOMMENDATIONS
   ========================================================= */

export async function getRecommendations() {

  const response =
    await api.get(
      "/jobs/recommendations/me"
    );

  return response.data as RecommendedJob[];
}


/* =========================================================
   ACTIVE JOBS
   ========================================================= */

export async function getActiveJobs() {

  const response =
    await api.get(
      "/jobs/"
    );

  return response.data as ActiveJob[];
}


/* =========================================================
   APPLICATIONS
   ========================================================= */

export async function getMyApplications() {

  const response =
    await api.get(
      "/applications/my"
    );

  return response.data as Application[];
}


export async function applyForJob(
  jobId: string
) {

  const response =
    await api.post(
      "/applications/",
      {
        job_id: jobId,
      }
    );

  return response.data;
}


/* =========================================================
   RESUME
   ========================================================= */

export async function uploadResume(
  file: File
) {

  const formData =
    new FormData();

  formData.append(
    "file",
    file
  );

  const response =
    await api.post(
      "/resumes/upload",
      formData,
      {
        headers: {
          "Content-Type":
            "multipart/form-data",
        },
      }
    );

  return response.data;
}


export async function analyzeResume(
  resumeId: string
) {

  const response =
    await api.post(
      `/resumes/${resumeId}/analyze`
    );

  return response.data;
}