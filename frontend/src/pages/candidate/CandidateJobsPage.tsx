import {
  useMemo,
  useState,
} from "react";

import {
  useMutation,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query";

import {
  ArrowRight,
  BriefcaseBusiness,
  MapPin,
  Search,
  Sparkles,
} from "lucide-react";

import CandidateSidebar
  from "../../components/candidate/CandidateSidebar";

import {
  applyForJob,
  getActiveJobs,
  getMyApplications,
  getRecommendations,
  type ActiveJob,
} from "../../services/candidateService";


export default function CandidateJobsPage() {

  const queryClient =
    useQueryClient();


  const [
    search,
    setSearch,
  ] = useState("");


  const [
    location,
    setLocation,
  ] = useState("");


  const jobsQuery =
    useQuery({

      queryKey: [
        "candidate-jobs",
      ],

      queryFn:
        getActiveJobs,

      staleTime:
        60 * 1000,

      placeholderData:
        (previousData) =>
          previousData,

    });


  const applicationsQuery =
    useQuery({

      queryKey: [
        "candidate-applications",
      ],

      queryFn:
        getMyApplications,

      staleTime:
        60 * 1000,

      placeholderData:
        (previousData) =>
          previousData,

    });


  const recommendationsQuery =
    useQuery({

      queryKey: [
        "candidate-recommendations",
      ],

      queryFn:
        getRecommendations,

      staleTime:
        60 * 1000,

      placeholderData:
        (previousData) =>
          previousData,

    });


  const applyMutation =
    useMutation({

      mutationFn:
        (jobId: string) =>
          applyForJob(
            jobId
          ),

      onSuccess:
        async () => {

          await queryClient.invalidateQueries({
            queryKey: [
              "candidate-applications",
            ],
          });

          await queryClient.invalidateQueries({
            queryKey: [
              "candidate-recommendations",
            ],
          });

        },

    });


  const jobs =
    jobsQuery.data ?? [];


  const applications =
    applicationsQuery.data ?? [];


  const recommendedIds =
    useMemo(
      () =>
        new Set(
          (
            recommendationsQuery.data ??
            []
          ).map(
            (job) =>
              job.job_id
          )
        ),
      [
        recommendationsQuery.data,
      ]
    );


  const locations =
    useMemo(
      () =>
        Array.from(
          new Set(
            jobs
              .map(
                (job) =>
                  job.location
              )
              .filter(
                Boolean
              )
          )
        )
          .sort() as string[],
      [jobs]
    );


  const filteredJobs =
    useMemo(
      () => {

        const term =
          search
            .trim()
            .toLowerCase();

        return jobs.filter(
          (job) => {

            const matchesSearch =
              !term ||
              job.title
                .toLowerCase()
                .includes(term) ||
              job.description
                .toLowerCase()
                .includes(term) ||
              (
                job.required_skills ||
                ""
              )
                .toLowerCase()
                .includes(term);


            const matchesLocation =
              !location ||
              job.location ===
                location;


            return (
              matchesSearch &&
              matchesLocation
            );

          }
        );

      },
      [
        jobs,
        search,
        location,
      ]
    );


  return (
    <div className="flex min-h-screen bg-slate-50">

      <CandidateSidebar />

      <main className="min-w-0 flex-1">

        <header className="border-b border-slate-200 bg-white">

          <div className="flex items-center justify-between px-6 py-5 md:px-8">

            <div>

              <p className="text-sm font-semibold text-teal-600">
                Explore opportunities
              </p>

              <h1 className="mt-1 text-2xl font-bold">
                Find your next job
              </h1>

            </div>

            <div className="hidden items-center gap-2 rounded-full border border-teal-100 bg-teal-50 px-4 py-2 text-sm font-semibold text-teal-700 sm:flex">

              <Sparkles size={16} />

              AI matching active

            </div>

          </div>

        </header>


        <div className="space-y-7 p-6 md:p-8">


          {/* SEARCH */}

          <section className="rounded-3xl border border-slate-200 bg-white p-5">

            <div className="grid gap-3 lg:grid-cols-[1fr_220px]">

              <div className="relative">

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
                  placeholder="Search title, skill or technology..."
                  className="w-full rounded-2xl border border-slate-200 bg-slate-50 py-3.5 pl-11 pr-4 outline-none focus:border-teal-500"
                />

              </div>


              <select
                value={
                  location
                }
                onChange={(
                  event
                ) =>
                  setLocation(
                    event.target.value
                  )
                }
                className="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3.5 outline-none focus:border-teal-500"
              >

                <option value="">
                  All locations
                </option>

                {locations.map(
                  (item) => (
                    <option
                      key={item}
                      value={item}
                    >
                      {item}
                    </option>
                  )
                )}

              </select>

            </div>

          </section>


          {applyMutation.error && (

            <div className="rounded-2xl border border-red-200 bg-red-50 px-5 py-4 text-sm text-red-700">
              Unable to apply for this job.
            </div>

          )}


          <section>

            <div className="flex items-end justify-between">

              <div>

                <p className="text-sm font-semibold text-teal-600">
                  Opportunities
                </p>

                <h2 className="mt-1 text-2xl font-bold">
                  Available jobs
                </h2>

              </div>

              <p className="text-sm text-slate-500">
                {filteredJobs.length} jobs
              </p>

            </div>


            <div className="mt-5 grid gap-5 xl:grid-cols-2">

              {jobsQuery.isLoading ? (

                <>
                  <Skeleton />
                  <Skeleton />
                  <Skeleton />
                  <Skeleton />
                </>

              ) : filteredJobs.length ===
                0 ? (

                <div className="col-span-full rounded-3xl border border-dashed border-slate-300 bg-white p-12 text-center">

                  <BriefcaseBusiness
                    size={34}
                    className="mx-auto text-slate-300"
                  />

                  <h3 className="mt-4 font-bold">
                    No jobs found
                  </h3>

                  <p className="mt-2 text-sm text-slate-500">
                    Try another title, skill or location.
                  </p>

                </div>

              ) : (

                filteredJobs.map(
                  (job) => {

                    const applied =
                      applications.some(
                        (application) =>
                          application.job_id ===
                          job.id
                      );


                    return (
                      <JobCard

                        key={
                          job.id
                        }

                        job={
                          job
                        }

                        recommended={
                          recommendedIds.has(
                            job.id
                          )
                        }

                        applied={
                          applied
                        }

                        applying={
                          applyMutation.isPending &&
                          applyMutation.variables ===
                            job.id
                        }

                        onApply={() =>
                          applyMutation.mutate(
                            job.id
                          )
                        }

                      />
                    );

                  }
                )

              )}

            </div>

          </section>

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
  recommended,
  applied,
  applying,
  onApply,
}: {
  job: ActiveJob;
  recommended: boolean;
  applied: boolean;
  applying: boolean;
  onApply: () => void;
}) {

  return (
    <article className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm transition hover:-translate-y-1 hover:shadow-xl">

      <div className="flex items-start justify-between gap-4">

        <div>

          <div className="flex flex-wrap items-center gap-2">

            {recommended && (

              <span className="inline-flex items-center gap-1 rounded-full bg-teal-50 px-3 py-1 text-xs font-bold text-teal-700">

                <Sparkles size={13} />

                AI match

              </span>

            )}

            <span className="rounded-full bg-slate-100 px-3 py-1 text-xs text-slate-600">
              {job.employment_type ||
                "Full-time"}
            </span>

          </div>


          <h3 className="mt-3 text-xl font-bold">
            {job.title}
          </h3>


          <div className="mt-2 flex flex-wrap gap-3 text-sm text-slate-500">

            <span className="inline-flex items-center gap-1">

              <MapPin size={15} />

              {job.location ||
                "Location not specified"}

            </span>

          </div>

        </div>


        <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-slate-950 text-teal-300">

          <BriefcaseBusiness
            size={19}
          />

        </div>

      </div>


      <p className="mt-5 line-clamp-3 text-sm leading-6 text-slate-600">
        {job.description}
      </p>


      <div className="mt-5 flex flex-wrap gap-2">

        {(job.required_skills || "")
          .split(",")
          .map(
            (skill) =>
              skill.trim()
          )
          .filter(Boolean)
          .slice(0, 6)
          .map(
            (skill) => (
              <span
                key={skill}
                className="rounded-full bg-slate-100 px-3 py-1 text-xs text-slate-600"
              >
                {skill}
              </span>
            )
          )}

      </div>


      <button
        disabled={
          applied ||
          applying
        }
        onClick={
          onApply
        }
        className={`mt-6 flex w-full items-center justify-center gap-2 rounded-xl px-4 py-3 font-semibold ${
          applied
            ? "bg-emerald-50 text-emerald-700"
            : "bg-slate-950 text-white hover:bg-teal-600"
        }`}
      >

        {applied
          ? "Applied"
          : applying
            ? "Applying..."
            : "Apply now"}

        {!applied &&
          !applying && (
            <ArrowRight
              size={17}
            />
          )}

      </button>

    </article>
  );
}


/* =========================================================
   SKELETON
   ========================================================= */

function Skeleton() {

  return (
    <div className="h-80 animate-pulse rounded-3xl bg-slate-200" />
  );
}