import {
  ArrowRight,
  BriefcaseBusiness,
  CheckCircle2,
  Clock3,
  Plus,
  Sparkles,
  Users,
} from "lucide-react";

import {
  Link,
} from "react-router-dom";

import {
  useQuery,
} from "@tanstack/react-query";

import RecruiterSidebar
  from "../../components/recruiter/RecruiterSidebar";

import {
  getRecruiterDashboard,
  getRecruiterJobs,
  type RecruiterJob,
  type RecruiterStats,
} from "../../services/recruiterService";


export default function RecruiterDashboard() {

  const dashboardQuery =
    useQuery({
      queryKey: [
        "recruiter-dashboard",
      ],

      queryFn:
        getRecruiterDashboard,

      staleTime:
        60 * 1000,

      placeholderData:
        (previousData) =>
          previousData,
    });


  const jobsQuery =
    useQuery({
      queryKey: [
        "recruiter-jobs",
      ],

      queryFn:
        getRecruiterJobs,

      staleTime:
        60 * 1000,

      placeholderData:
        (previousData) =>
          previousData,
    });


  const stats:
    RecruiterStats | null =
    dashboardQuery.data?.statistics ??
    null;


  const jobs:
    RecruiterJob[] =
    jobsQuery.data ?? [];


  const isLoading =
    dashboardQuery.isLoading ||
    jobsQuery.isLoading;


  const error =
    dashboardQuery.error ||
    jobsQuery.error;


  return (
    <div className="flex min-h-screen bg-slate-50">

      <RecruiterSidebar />


      <main className="min-w-0 flex-1">

        {/* =====================================================
            HEADER
            ===================================================== */}

        <header className="border-b border-slate-200 bg-white">

          <div className="flex items-center justify-between px-6 py-5 md:px-8">

            <div>

              <p className="text-sm font-semibold text-teal-600">
                Recruiter workspace
              </p>

              <h1 className="mt-1 text-2xl font-bold tracking-tight">
                Hiring dashboard
              </h1>

            </div>


            <div className="hidden items-center gap-2 rounded-full border border-teal-100 bg-teal-50 px-4 py-2 text-sm font-semibold text-teal-700 sm:flex">

              <Sparkles size={16} />

              AI ranking active

            </div>

          </div>

        </header>


        <div className="space-y-8 p-6 md:p-8">


          {/* =====================================================
              ERROR
              ===================================================== */}

          {error && (

            <div className="rounded-2xl border border-red-200 bg-red-50 px-5 py-4 text-sm text-red-700">

              Unable to load recruiter dashboard.

            </div>

          )}


          {/* =====================================================
              STATISTICS
              ===================================================== */}

          <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">

            <StatCard
              icon={
                <BriefcaseBusiness
                  size={20}
                />
              }
              label="Total jobs"
              value={
                isLoading
                  ? "—"
                  : String(
                      stats?.total_jobs ?? 0
                    )
              }
            />


            <StatCard
              icon={
                <Users size={20} />
              }
              label="Applications"
              value={
                isLoading
                  ? "—"
                  : String(
                      stats?.total_applications ?? 0
                    )
              }
            />


            <StatCard
              icon={
                <CheckCircle2
                  size={20}
                />
              }
              label="Shortlisted"
              value={
                isLoading
                  ? "—"
                  : String(
                      stats?.shortlisted ?? 0
                    )
              }
            />


            <StatCard
              icon={
                <Clock3 size={20} />
              }
              label="Interviews"
              value={
                isLoading
                  ? "—"
                  : String(
                      stats?.interviews ?? 0
                    )
              }
            />

          </section>


          {/* =====================================================
              JOBS
              ===================================================== */}

          <section>

            <div className="flex items-end justify-between">

              <div>

                <p className="text-sm font-semibold text-teal-600">
                  Hiring pipeline
                </p>

                <h2 className="mt-1 text-2xl font-bold">
                  Your jobs
                </h2>

              </div>


              <Link
                to="/recruiter/jobs/create"
                className="inline-flex items-center gap-2 rounded-xl bg-slate-950 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-teal-600"
              >

                <Plus size={17} />

                Create job

              </Link>

            </div>


            <div className="mt-5 overflow-hidden rounded-3xl border border-slate-200 bg-white">

              {isLoading ? (

                <div className="space-y-3 p-5">

                  <SkeletonRow />
                  <SkeletonRow />
                  <SkeletonRow />

                </div>

              ) : jobs.length === 0 ? (

                <EmptyJobs />

              ) : (

                <div className="divide-y divide-slate-100">

                  {jobs
                    .slice(0, 8)
                    .map(
                      (job) => (

                        <JobRow
                          key={
                            job.job_id
                          }
                          job={
                            job
                          }
                        />

                      )
                    )}

                </div>

              )}

            </div>

          </section>


          {/* =====================================================
              AI PANEL
              ===================================================== */}

          <section className="rounded-3xl bg-slate-950 p-6 md:p-8">

            <div className="grid gap-8 md:grid-cols-[1fr_auto] md:items-center">

              <div>

                <div className="inline-flex items-center gap-2 rounded-full bg-teal-400/10 px-3 py-1.5 text-xs font-bold text-teal-300">

                  <Sparkles size={14} />

                  AI CANDIDATE RANKING

                </div>


                <h2 className="mt-5 text-3xl font-bold text-white">
                  Find your strongest applicants faster.
                </h2>


                <p className="mt-4 max-w-2xl leading-7 text-slate-400">

                  HireNiti combines semantic similarity,
                  skills, experience and education to rank
                  applicants for each role.

                </p>

              </div>


              <div className="rounded-2xl border border-white/10 bg-white/5 p-6">

                <p className="text-sm text-slate-400">
                  Matching signals
                </p>


                <div className="mt-4 space-y-3">

                  <Signal
                    label="Semantic"
                    value="55%"
                  />

                  <Signal
                    label="Skills"
                    value="25%"
                  />

                  <Signal
                    label="Experience"
                    value="10%"
                  />

                  <Signal
                    label="Education"
                    value="10%"
                  />

                </div>

              </div>

            </div>

          </section>

        </div>

      </main>

    </div>
  );
}


/* =========================================================
   STAT CARD
   ========================================================= */

function StatCard({
  icon,
  label,
  value,
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
}) {

  return (
    <div className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">

      <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-teal-50 text-teal-600">
        {icon}
      </div>

      <p className="mt-5 text-sm text-slate-500">
        {label}
      </p>

      <p className="mt-1 text-2xl font-bold">
        {value}
      </p>

    </div>
  );
}


/* =========================================================
   JOB ROW
   ========================================================= */

function JobRow({
  job,
}: {
  job: RecruiterJob;
}) {

  return (
    <div className="flex flex-col gap-5 p-5 xl:flex-row xl:items-center xl:justify-between">

      <div>

        <div className="flex flex-wrap items-center gap-3">

          <h3 className="font-semibold">
            {job.title}
          </h3>


          <span
            className={`rounded-full px-3 py-1 text-xs font-semibold ${
              job.status === "active"
                ? "bg-emerald-50 text-emerald-700"
                : "bg-slate-100 text-slate-600"
            }`}
          >
            {job.status}
          </span>

        </div>


        <p className="mt-1 text-sm text-slate-500">

          {job.location ||
            "Location not specified"}

          {" · "}

          {job.employment_type ||
            "Full-time"}

        </p>

      </div>


      <div className="grid grid-cols-4 gap-2">

        <PipelineMetric
          label="Applicants"
          value={
            job.applicant_count
          }
        />

        <PipelineMetric
          label="Shortlisted"
          value={
            job.shortlisted_count
          }
        />

        <PipelineMetric
          label="Interviews"
          value={
            job.interview_count
          }
        />

        <PipelineMetric
          label="Hired"
          value={
            job.hired_count
          }
        />

      </div>


      <Link
        to={`/recruiter/jobs/${job.job_id}/applicants`}
        className="inline-flex items-center justify-center gap-2 rounded-xl border border-slate-200 px-4 py-2.5 text-sm font-semibold transition hover:border-teal-300 hover:text-teal-700"
      >

        View applicants

        <ArrowRight
          size={16}
        />

      </Link>

    </div>
  );
}


/* =========================================================
   PIPELINE METRIC
   ========================================================= */

function PipelineMetric({
  label,
  value,
}: {
  label: string;
  value: number;
}) {

  return (
    <div className="rounded-xl bg-slate-50 px-3 py-2 text-center">

      <p className="text-lg font-bold">
        {value}
      </p>

      <p className="text-[10px] uppercase tracking-wide text-slate-500">
        {label}
      </p>

    </div>
  );
}


/* =========================================================
   SIGNAL
   ========================================================= */

function Signal({
  label,
  value,
}: {
  label: string;
  value: string;
}) {

  return (
    <div className="flex items-center justify-between text-sm">

      <span className="text-slate-300">
        {label}
      </span>

      <span className="font-bold text-teal-300">
        {value}
      </span>

    </div>
  );
}


/* =========================================================
   EMPTY JOBS
   ========================================================= */

function EmptyJobs() {

  return (
    <div className="p-10 text-center">

      <BriefcaseBusiness
        className="mx-auto text-slate-300"
        size={32}
      />

      <h3 className="mt-4 font-bold">
        No jobs yet
      </h3>

      <p className="mt-2 text-sm text-slate-500">
        Create your first job to start hiring.
      </p>

      <Link
        to="/recruiter/jobs/create"
        className="mt-5 inline-flex rounded-xl bg-slate-950 px-5 py-3 text-sm font-semibold text-white"
      >
        Create job
      </Link>

    </div>
  );
}


/* =========================================================
   SKELETON
   ========================================================= */

function SkeletonRow() {

  return (
    <div className="h-24 animate-pulse rounded-2xl bg-slate-100" />
  );
}