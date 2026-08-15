import {
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
  CheckCircle2,
  FileText,
  Sparkles,
  Upload,
} from "lucide-react";

import {
  Link,
} from "react-router-dom";

import CandidateSidebar
  from "../../components/candidate/CandidateSidebar";

import {
  analyzeResume,
  applyForJob,
  getMyApplications,
  getRecommendations,
  uploadResume,
  type Application,
  type RecommendedJob,
} from "../../services/candidateService";


export default function CandidateDashboard() {

  const queryClient =
    useQueryClient();


  /* =========================================================
     RECOMMENDATIONS
     ========================================================= */

  const recommendationsQuery =
    useQuery<RecommendedJob[]>({

      queryKey: [
        "candidate-recommendations",
      ],

      queryFn:
        getRecommendations,

      staleTime:
        60 * 1000,

      gcTime:
        10 * 60 * 1000,

      placeholderData:
        (previousData) =>
          previousData,

    });


  /* =========================================================
     APPLICATIONS
     ========================================================= */

  const applicationsQuery =
    useQuery<Application[]>({

      queryKey: [
        "candidate-applications",
      ],

      queryFn:
        getMyApplications,

      staleTime:
        60 * 1000,

      gcTime:
        10 * 60 * 1000,

      placeholderData:
        (previousData) =>
          previousData,

    });


  /* =========================================================
     LOCAL UI STATE
     ========================================================= */

  const [
    selectedFile,
    setSelectedFile,
  ] = useState<File | null>(
    null
  );


  const [
    message,
    setMessage,
  ] = useState("");


  const [
    error,
    setError,
  ] = useState("");


  /* =========================================================
     RESUME UPLOAD
     ========================================================= */

  const uploadMutation =
    useMutation({

      mutationFn:
        async (
          file: File
        ) => {

          const uploadResult =
            await uploadResume(
              file
            );


          const resumeId =
            uploadResult?.resume_id;


          if (!resumeId) {

            throw new Error(
              "Resume ID was not returned by the server."
            );

          }


          return analyzeResume(
            resumeId
          );

        },


      onSuccess:
        async () => {

          setMessage(
            "Resume uploaded and analyzed successfully."
          );


          setSelectedFile(
            null
          );


          /*
           * Resume changed the candidate profile,
           * so recommendations need a refresh.
           */

          await queryClient.invalidateQueries({
            queryKey: [
              "candidate-recommendations",
            ],
          });

        },


      onError:
        (error) => {

          console.error(
            "Resume error:",
            error
          );


          setError(
            error.message ||
            "Unable to process your resume."
          );

        },

    });


  /* =========================================================
     DATA
     ========================================================= */

  const recommendations =
    recommendationsQuery.data ??
    [];


  const applications =
    applicationsQuery.data ??
    [];


  const loading =
    recommendationsQuery.isLoading ||
    applicationsQuery.isLoading;


  /* =========================================================
     APPLY
     ========================================================= */

  async function handleApply(
    jobId: string
  ) {

    setError("");
    setMessage("");


    try {

      await applyForJob(
        jobId
      );


      setMessage(
        "Application submitted successfully."
      );


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

    } catch (error) {

      console.error(
        "Application error:",
        error
      );


      setError(
        "Unable to submit application."
      );

    }

  }


  /* =========================================================
     UPLOAD
     ========================================================= */

  function handleUpload() {

    setError("");
    setMessage("");


    if (!selectedFile) {

      setError(
        "Please select a PDF or DOCX resume."
      );

      return;
    }


    const fileName =
      selectedFile.name.toLowerCase();


    if (
      !fileName.endsWith(
        ".pdf"
      ) &&
      !fileName.endsWith(
        ".docx"
      )
    ) {

      setError(
        "Only PDF and DOCX files are allowed."
      );

      return;
    }


    if (
      selectedFile.size >
      5 * 1024 * 1024
    ) {

      setError(
        "Resume must be smaller than 5 MB."
      );

      return;
    }


    uploadMutation.mutate(
      selectedFile
    );

  }


  return (
    <div className="flex min-h-screen bg-slate-50">

      <CandidateSidebar />


      <main className="min-w-0 flex-1">


        {/* =================================================
            HEADER
            ================================================= */}

        <header className="border-b border-slate-200 bg-white">

          <div className="flex items-center justify-between px-6 py-5 md:px-8">

            <div>

              <p className="text-sm font-semibold text-teal-600">
                Candidate workspace
              </p>

              <h1 className="mt-1 text-2xl font-bold tracking-tight text-slate-950">
                Your career dashboard
              </h1>

            </div>


            <div className="hidden items-center gap-2 rounded-full border border-teal-100 bg-teal-50 px-4 py-2 text-sm font-semibold text-teal-700 sm:flex">

              <Sparkles
                size={16}
              />

              AI matching active

            </div>

          </div>

        </header>


        <div className="space-y-8 p-6 md:p-8">


          {/* =================================================
              ERROR
              ================================================= */}

          {(error ||
            recommendationsQuery.error ||
            applicationsQuery.error) && (

            <div className="rounded-2xl border border-red-200 bg-red-50 px-5 py-4 text-sm text-red-700">

              {error ||
                "Unable to load some dashboard data."}

            </div>

          )}


          {/* =================================================
              SUCCESS
              ================================================= */}

          {message && (

            <div className="rounded-2xl border border-emerald-200 bg-emerald-50 px-5 py-4 text-sm text-emerald-700">

              {message}

            </div>

          )}


          {/* =================================================
              STATS
              ================================================= */}

          <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">


            <StatCard

              icon={
                <BriefcaseBusiness
                  size={20}
                />
              }

              label="AI matches"

              value={
                loading
                  ? "—"
                  : String(
                      recommendations.length
                    )
              }

            />


            <StatCard

              icon={
                <FileText
                  size={20}
                />
              }

              label="Applications"

              value={
                loading
                  ? "—"
                  : String(
                      applications.length
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
                loading
                  ? "—"
                  : String(
                      applications.filter(
                        (application) =>
                          application.status ===
                          "shortlisted"
                      ).length
                    )
              }

            />


            <StatCard

              icon={
                <Sparkles
                  size={20}
                />
              }

              label="Top match"

              value={
                recommendations.length >
                0
                  ? `${Math.round(
                      (
                        recommendations[0]
                          .final_score ??
                        0
                      ) * 100
                    )}%`
                  : "—"
              }

            />

          </section>


          {/* =================================================
              RESUME UPLOAD
              ================================================= */}

          <section className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">

            <div className="flex flex-col gap-5 md:flex-row md:items-center md:justify-between">


              <div>

                <p className="text-sm font-semibold text-teal-600">
                  Resume
                </p>


                <h2 className="mt-1 text-xl font-bold">
                  Keep your profile AI-ready
                </h2>


                <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-500">

                  Upload your latest resume and let HireNiti
                  analyze it for personalized recommendations.

                </p>

              </div>


              <div className="flex flex-col gap-3 sm:flex-row">


                <label className="cursor-pointer rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm font-semibold text-slate-700 transition hover:border-teal-300 hover:bg-teal-50">

                  <input
                    type="file"
                    accept=".pdf,.docx"
                    className="hidden"
                    onChange={(event) => {

                      const file =
                        event.target.files?.[0];


                      if (file) {

                        setSelectedFile(
                          file
                        );

                        setError("");
                        setMessage("");

                      }

                    }}
                  />


                  {selectedFile
                    ? selectedFile.name
                    : "Choose resume"}

                </label>


                <button

                  type="button"

                  onClick={
                    handleUpload
                  }

                  disabled={
                    !selectedFile ||
                    uploadMutation.isPending
                  }

                  className="inline-flex items-center justify-center gap-2 rounded-xl bg-slate-950 px-5 py-3 text-sm font-semibold text-white transition hover:bg-teal-600 disabled:cursor-not-allowed disabled:opacity-40"

                >

                  <Upload
                    size={17}
                  />

                  {uploadMutation.isPending
                    ? "Processing..."
                    : "Upload & analyze"}

                </button>

              </div>

            </div>

          </section>


          {/* =================================================
              RECOMMENDATIONS
              ================================================= */}

          <section>


            <div className="flex items-end justify-between">

              <div>

                <p className="text-sm font-semibold text-teal-600">
                  Personalized for you
                </p>


                <h2 className="mt-1 text-2xl font-bold">
                  AI job recommendations
                </h2>

              </div>


              <Link
                to="/candidate/recommendations"
                className="hidden items-center gap-1 text-sm font-semibold text-slate-600 hover:text-slate-950 sm:flex"
              >

                View all

                <ArrowRight
                  size={16}
                />

              </Link>

            </div>


            <div className="mt-5 grid gap-5 xl:grid-cols-2">


              {recommendationsQuery.isLoading ? (

                <>
                  <SkeletonCard />
                  <SkeletonCard />
                </>

              ) : recommendations.length ===
                0 ? (

                <div className="col-span-full rounded-3xl border border-dashed border-slate-300 bg-white p-10 text-center">

                  <Sparkles
                    className="mx-auto text-teal-500"
                    size={28}
                  />

                  <h3 className="mt-4 font-bold">

                    No AI recommendations yet

                  </h3>

                  <p className="mx-auto mt-2 max-w-lg text-sm leading-6 text-slate-500">

                    Upload and analyze your resume first.

                  </p>

                </div>

              ) : (

                recommendations
                  .slice(
                    0,
                    6
                  )
                  .map(
                    (
                      job
                    ) => (

                      <RecommendationCard

                        key={
                          job.job_id
                        }

                        job={
                          job
                        }

                        applied={
                          applications.some(
                            (
                              application
                            ) =>
                              application.job_id ===
                              job.job_id
                          )
                        }

                        onApply={
                          handleApply
                        }

                      />

                    )
                  )

              )}

            </div>

          </section>


          {/* =================================================
              RECENT APPLICATIONS
              ================================================= */}

          <section>

            <div>

              <p className="text-sm font-semibold text-teal-600">
                Your activity
              </p>

              <h2 className="mt-1 text-2xl font-bold">
                Recent applications
              </h2>

            </div>


            <div className="mt-5 overflow-hidden rounded-3xl border border-slate-200 bg-white">


              {applications.length ===
              0 ? (

                <div className="p-8 text-center text-sm text-slate-500">

                  You haven't applied to any jobs yet.

                </div>

              ) : (

                <div className="divide-y divide-slate-100">

                  {applications
                    .slice(
                      0,
                      6
                    )
                    .map(
                      (
                        application
                      ) => (

                        <ApplicationRow
                          key={
                            application.application_id
                          }
                          application={
                            application
                          }
                        />

                      )
                    )}

                </div>

              )}

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


      <p className="mt-4 text-sm text-slate-500">
        {label}
      </p>


      <p className="mt-1 text-2xl font-bold text-slate-950">
        {value}
      </p>

    </div>
  );
}


/* =========================================================
   RECOMMENDATION CARD
   ========================================================= */

function RecommendationCard({
  job,
  applied,
  onApply,
}: {
  job: RecommendedJob;
  applied: boolean;
  onApply: (
    jobId: string
  ) => void;
}) {

  const score =
    Math.round(
      (
        job.final_score ??
        0
      ) * 100
    );


  return (
    <article className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm transition hover:-translate-y-1 hover:shadow-xl">


      <div className="flex items-start justify-between gap-4">

        <div>

          <p className="text-xs font-semibold uppercase tracking-widest text-teal-600">
            AI matched
          </p>


          <h3 className="mt-2 text-xl font-bold">
            {job.title}
          </h3>


          <p className="mt-1 text-sm text-slate-500">

            {job.location ||
              "Location not specified"}

          </p>

        </div>


        <div className="flex h-14 w-14 shrink-0 items-center justify-center rounded-2xl bg-teal-50">

          <p className="font-black text-teal-700">
            {score}%
          </p>

        </div>

      </div>


      <div className="mt-5 flex flex-wrap gap-2">

        {(job.required_skills || "")
          .split(",")
          .map(
            (
              skill
            ) =>
              skill.trim()
          )
          .filter(Boolean)
          .slice(
            0,
            5
          )
          .map(
            (
              skill
            ) => (

              <span
                key={
                  skill
                }
                className="rounded-full bg-slate-100 px-3 py-1 text-xs text-slate-600"
              >
                {skill}
              </span>

            )
          )}

      </div>


      <button

        type="button"

        disabled={
          applied
        }

        onClick={() =>
          onApply(
            job.job_id
          )
        }

        className={`mt-6 flex w-full items-center justify-center gap-2 rounded-xl px-4 py-3 font-semibold transition ${
          applied
            ? "cursor-default bg-emerald-50 text-emerald-700"
            : "bg-slate-950 text-white hover:bg-teal-600"
        }`}

      >

        {applied
          ? "Applied"
          : "Apply now"}


        {!applied && (

          <ArrowRight
            size={17}
          />

        )}

      </button>

    </article>
  );
}


/* =========================================================
   APPLICATION ROW
   ========================================================= */

function ApplicationRow({
  application,
}: {
  application: Application;
}) {

  return (
    <div className="flex flex-col gap-3 p-5 sm:flex-row sm:items-center sm:justify-between">

      <div>

        <h3 className="font-semibold text-slate-950">
          {application.job_title}
        </h3>


        <p className="mt-1 text-sm text-slate-500">

          {application.location ||
            "Location not specified"}

          {" · "}

          {application.employment_type ||
            "Full-time"}

        </p>

      </div>


      <span className="w-fit rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-700">

        {application.status}

      </span>

    </div>
  );
}


/* =========================================================
   SKELETON
   ========================================================= */

function SkeletonCard() {

  return (
    <div className="h-72 animate-pulse rounded-3xl bg-slate-200" />
  );
}