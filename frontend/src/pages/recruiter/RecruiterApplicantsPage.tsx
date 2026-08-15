import {
  useQuery,
} from "@tanstack/react-query";

import {
  ArrowRight,
  BriefcaseBusiness,
  Search,
  Sparkles,
} from "lucide-react";

import {
  useState,
} from "react";

import {
  Link,
} from "react-router-dom";

import RecruiterSidebar
  from "../../components/recruiter/RecruiterSidebar";

import {
  getRecruiterJobs,
  type RecruiterJob,
} from "../../services/recruiterService";


export default function RecruiterApplicantsPage() {

  const [
    search,
    setSearch,
  ] = useState("");


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


  const jobs =
    jobsQuery.data ?? [];


  const filteredJobs =
    jobs.filter(
      (job) =>
        job.title
          .toLowerCase()
          .includes(
            search
              .toLowerCase()
          )
    );


  return (
    <div className="flex min-h-screen bg-slate-50">

      <RecruiterSidebar />


      <main className="min-w-0 flex-1">


        <header className="border-b border-slate-200 bg-white">

          <div className="px-6 py-5 md:px-8">

            <p className="text-sm font-semibold text-teal-600">
              Recruitment pipeline
            </p>

            <h1 className="mt-1 text-2xl font-bold">
              Applicants
            </h1>

          </div>

        </header>


        <div className="space-y-6 p-6 md:p-8">


          {/* SEARCH */}

          <div className="relative max-w-xl">

            <Search
              size={18}
              className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400"
            />


            <input
              value={
                search
              }
              onChange={(
                event
              ) =>
                setSearch(
                  event.target.value
                )
              }
              placeholder="Search your jobs..."
              className="w-full rounded-2xl border border-slate-200 bg-white py-3.5 pl-11 pr-4 outline-none focus:border-teal-500"
            />

          </div>


          {/* ERROR */}

          {jobsQuery.error && (

            <div className="rounded-2xl border border-red-200 bg-red-50 px-5 py-4 text-sm text-red-700">

              Unable to load jobs.

            </div>

          )}


          {/* LOADING */}

          {jobsQuery.isLoading ? (

            <div className="space-y-4">

              <Skeleton />
              <Skeleton />
              <Skeleton />

            </div>

          ) : filteredJobs.length ===
            0 ? (

            <div className="rounded-3xl border border-dashed border-slate-300 bg-white p-12 text-center">

              <BriefcaseBusiness
                size={34}
                className="mx-auto text-slate-300"
              />


              <h2 className="mt-4 font-bold">
                No matching jobs
              </h2>


              <p className="mt-2 text-sm text-slate-500">
                Try another job title.
              </p>

            </div>

          ) : (

            <div className="grid gap-5 xl:grid-cols-2">

              {filteredJobs.map(
                (job) => (

                  <JobCard
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

      </main>

    </div>
  );
}


/* =========================================================
   JOB CARD
   ========================================================= */

function JobCard({
  job,
}: {
  job: RecruiterJob;
}) {

  return (
    <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">


      <div className="flex items-start justify-between">

        <div>

          <div className="flex items-center gap-2">

            <h2 className="text-xl font-bold">
              {job.title}
            </h2>


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


          <p className="mt-2 text-sm text-slate-500">

            {job.location ||
              "Location not specified"}

          </p>

        </div>


        <Sparkles
          size={20}
          className="text-teal-500"
        />

      </div>


      <div className="mt-6 grid grid-cols-4 gap-2">

        <Metric
          label="Applicants"
          value={
            job.applicant_count
          }
        />

        <Metric
          label="Shortlisted"
          value={
            job.shortlisted_count
          }
        />

        <Metric
          label="Interviews"
          value={
            job.interview_count
          }
        />

        <Metric
          label="Hired"
          value={
            job.hired_count
          }
        />

      </div>


      <Link
        to={`/recruiter/jobs/${job.job_id}/applicants`}
        className="mt-6 flex items-center justify-center gap-2 rounded-xl bg-slate-950 px-4 py-3 text-sm font-semibold text-white hover:bg-teal-600"
      >

        View AI-ranked applicants

        <ArrowRight
          size={17}
        />

      </Link>

    </div>
  );
}


/* =========================================================
   METRIC
   ========================================================= */

function Metric({
  label,
  value,
}: {
  label: string;
  value: number;
}) {

  return (
    <div className="rounded-xl bg-slate-50 p-3 text-center">

      <p className="text-lg font-bold">
        {value}
      </p>

      <p className="text-[10px] uppercase text-slate-500">
        {label}
      </p>

    </div>
  );
}


/* =========================================================
   SKELETON
   ========================================================= */

function Skeleton() {

  return (
    <div className="h-56 animate-pulse rounded-3xl bg-slate-200" />
  );
}