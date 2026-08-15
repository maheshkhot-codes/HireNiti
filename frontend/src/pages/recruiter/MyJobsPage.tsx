import {
  useMutation,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query";

import {
  BriefcaseBusiness,
  Plus,
  Sparkles,
  Trash2,
} from "lucide-react";

import {
  Link,
  useNavigate,
} from "react-router-dom";

import RecruiterSidebar
  from "../../components/recruiter/RecruiterSidebar";

import {
  deleteJob,
  getRecruiterJobs,
  publishJob,
  type RecruiterJob,
} from "../../services/recruiterService";


export default function MyJobsPage() {

  const navigate =
    useNavigate();

  const queryClient =
    useQueryClient();


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


  const publishMutation =
    useMutation({

      mutationFn: (
        jobId: string
      ) =>
        publishJob(
          jobId
        ),

      onSuccess: () => {

        queryClient.invalidateQueries({
          queryKey: [
            "recruiter-jobs",
          ],
        });

        queryClient.invalidateQueries({
          queryKey: [
            "recruiter-dashboard",
          ],
        });

      },

    });


  const deleteMutation =
    useMutation({

      mutationFn: (
        jobId: string
      ) =>
        deleteJob(
          jobId
        ),

      onSuccess: () => {

        queryClient.invalidateQueries({
          queryKey: [
            "recruiter-jobs",
          ],
        });

        queryClient.invalidateQueries({
          queryKey: [
            "recruiter-dashboard",
          ],
        });

      },

    });


  function handleDelete(
    jobId: string
  ) {

    const confirmed =
      window.confirm(
        "Are you sure you want to delete this job?"
      );

    if (!confirmed) {
      return;
    }

    deleteMutation.mutate(
      jobId
    );
  }


  return (
    <div className="flex min-h-screen bg-slate-50">

      <RecruiterSidebar />


      <main className="min-w-0 flex-1">


        <header className="border-b border-slate-200 bg-white">

          <div className="flex items-center justify-between px-6 py-5 md:px-8">

            <div>

              <p className="text-sm font-semibold text-teal-600">
                Hiring pipeline
              </p>

              <h1 className="mt-1 text-2xl font-bold">
                My Jobs
              </h1>

            </div>


            <Link
              to="/recruiter/jobs/create"
              className="inline-flex items-center gap-2 rounded-xl bg-slate-950 px-4 py-2.5 text-sm font-semibold text-white hover:bg-teal-600"
            >

              <Plus
                size={17}
              />

              Create job

            </Link>

          </div>

        </header>


        <div className="space-y-6 p-6 md:p-8">


          {/* ERROR */}

          {(
            jobsQuery.error ||
            publishMutation.error ||
            deleteMutation.error
          ) && (

            <div className="rounded-2xl border border-red-200 bg-red-50 px-5 py-4 text-sm text-red-700">

              {publishMutation.error
                ? "Unable to publish job."
                : deleteMutation.error
                  ? "Unable to delete job."
                  : "Unable to load jobs."}

            </div>

          )}


          {/* LOADING */}

          {jobsQuery.isLoading ? (

            <div className="space-y-4">

              <Skeleton />
              <Skeleton />
              <Skeleton />

            </div>

          ) : jobs.length === 0 ? (

            <div className="rounded-3xl border border-dashed border-slate-300 bg-white p-12 text-center">

              <BriefcaseBusiness
                size={34}
                className="mx-auto text-slate-300"
              />

              <h2 className="mt-4 text-lg font-bold">
                No jobs created yet
              </h2>

              <p className="mt-2 text-sm text-slate-500">
                Create your first job and start receiving applicants.
              </p>

              <Link
                to="/recruiter/jobs/create"
                className="mt-5 inline-flex rounded-xl bg-slate-950 px-5 py-3 text-sm font-semibold text-white"
              >
                Create job
              </Link>

            </div>

          ) : (

            <div className="grid gap-5 xl:grid-cols-2">

              {jobs.map(
                (job) => (

                  <JobCard
                    key={
                      job.job_id
                    }
                    job={
                      job
                    }
                    publishing={
                      publishMutation.isPending &&
                      publishMutation.variables ===
                        job.job_id
                    }
                    deleting={
                      deleteMutation.isPending &&
                      deleteMutation.variables ===
                        job.job_id
                    }
                    onPublish={() =>
                      publishMutation.mutate(
                        job.job_id
                      )
                    }
                    onDelete={() =>
                      handleDelete(
                        job.job_id
                      )
                    }
                    onApplicants={() =>
                      navigate(
                        `/recruiter/jobs/${job.job_id}/applicants`
                      )
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
  publishing,
  deleting,
  onPublish,
  onDelete,
  onApplicants,
}: {
  job: RecruiterJob;
  publishing: boolean;
  deleting: boolean;
  onPublish: () => void;
  onDelete: () => void;
  onApplicants: () => void;
}) {

  return (
    <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">


      <div className="flex items-start justify-between gap-4">

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

            {" · "}

            {job.employment_type ||
              "Full-time"}

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
          label="Interview"
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


      <div className="mt-6 flex flex-wrap gap-2">


        {job.status !==
          "active" && (

          <button

            onClick={
              onPublish
            }

            disabled={
              publishing ||
              deleting
            }

            className="rounded-xl bg-teal-500 px-4 py-2.5 text-sm font-semibold text-white hover:bg-teal-600 disabled:opacity-50"
          >

            {publishing
              ? "Publishing..."
              : "Publish"}

          </button>

        )}


        <button

          onClick={
            onApplicants
          }

          disabled={
            deleting
          }

          className="rounded-xl bg-slate-950 px-4 py-2.5 text-sm font-semibold text-white hover:bg-teal-600 disabled:opacity-50"
        >

          AI applicants

        </button>


        <button

          onClick={
            onDelete
          }

          disabled={
            deleting ||
            publishing
          }

          className="inline-flex items-center gap-2 rounded-xl px-4 py-2.5 text-sm font-semibold text-red-600 hover:bg-red-50 disabled:opacity-50"
        >

          <Trash2
            size={16}
          />

          {deleting
            ? "Deleting..."
            : "Delete"}

        </button>

      </div>

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
    <div className="h-64 animate-pulse rounded-3xl bg-slate-200" />
  );
}