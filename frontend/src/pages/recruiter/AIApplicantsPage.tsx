import {
  useMutation,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query";

import {
  ArrowLeft,
  CheckCircle2,
  GraduationCap,
  MessageSquare,
  Search,
  Sparkles,
  UserRound,
  XCircle,
} from "lucide-react";

import {
  useNavigate,
  useParams,
} from "react-router-dom";

import RecruiterSidebar
  from "../../components/recruiter/RecruiterSidebar";

import {
  getAIRankedCandidates,
  updateApplicationStatus,
  type RankedCandidate,
} from "../../services/recruiterService";


export default function AIApplicantsPage() {

  const {
    jobId,
  } = useParams();


  const navigate =
    useNavigate();


  const queryClient =
    useQueryClient();


  const candidatesQuery =
    useQuery({

      queryKey: [
        "recruiter-ai-applicants",
        jobId,
      ],

      queryFn: () =>
        getAIRankedCandidates(
          jobId as string
        ),

      enabled:
        Boolean(jobId),

      staleTime:
        60 * 1000,

      placeholderData:
        (previousData) =>
          previousData,

    });


  const statusMutation =
    useMutation({

      mutationFn: ({
        applicationId,
        status,
      }: {
        applicationId: string;
        status: string;
      }) =>
        updateApplicationStatus(
          applicationId,
          status
        ),


      onSuccess: async () => {

        await queryClient.invalidateQueries({

          queryKey: [
            "recruiter-ai-applicants",
            jobId,
          ],

        });


        await queryClient.invalidateQueries({

          queryKey: [
            "recruiter-dashboard",
          ],

        });


        await queryClient.invalidateQueries({

          queryKey: [
            "recruiter-jobs",
          ],

        });

      },

    });


  const candidates =
    candidatesQuery.data ??
    [];


  function handleStatusChange(
    applicationId:
      string | null,
    status: string
  ) {

    if (!applicationId) {
      return;
    }


    statusMutation.mutate({

      applicationId,

      status,

    });

  }


  return (
    <div className="flex min-h-screen bg-slate-50">

      <RecruiterSidebar />


      <main className="min-w-0 flex-1">


        {/* HEADER */}

        <header className="border-b border-slate-200 bg-white">

          <div className="flex items-center gap-4 px-6 py-5 md:px-8">

            <button
              onClick={() =>
                navigate(
                  "/recruiter/dashboard"
                )
              }
              className="flex h-10 w-10 items-center justify-center rounded-xl border border-slate-200 text-slate-600 transition hover:bg-slate-50"
            >

              <ArrowLeft
                size={18}
              />

            </button>


            <div>

              <p className="text-sm font-semibold text-teal-600">
                AI recruitment
              </p>

              <h1 className="mt-1 text-2xl font-bold">
                Candidate ranking
              </h1>

            </div>

          </div>

        </header>


        <div className="space-y-7 p-6 md:p-8">


          {/* AI HEADER */}

          <section className="rounded-3xl bg-slate-950 p-6 md:p-8">

            <div className="flex flex-col gap-5 md:flex-row md:items-center md:justify-between">


              <div>

                <div className="inline-flex items-center gap-2 rounded-full bg-teal-400/10 px-3 py-1.5 text-xs font-bold text-teal-300">

                  <Sparkles
                    size={14}
                  />

                  AI RANKING

                </div>


                <h2 className="mt-4 text-3xl font-bold text-white">
                  Best-fit candidates
                </h2>


                <p className="mt-3 max-w-2xl leading-7 text-slate-400">

                  Candidates are ranked using semantic similarity,
                  required skills, experience and education.

                </p>

              </div>


              <div className="rounded-2xl border border-white/10 bg-white/5 px-6 py-5">

                <p className="text-sm text-slate-400">
                  Candidates
                </p>


                <p className="mt-1 text-3xl font-black text-white">
                  {candidates.length}
                </p>

              </div>

            </div>

          </section>


          {/* ERROR */}

          {candidatesQuery.error && (

            <div className="rounded-2xl border border-red-200 bg-red-50 px-5 py-4 text-sm text-red-700">

              Unable to load AI-ranked candidates.

            </div>

          )}


          {statusMutation.error && (

            <div className="rounded-2xl border border-red-200 bg-red-50 px-5 py-4 text-sm text-red-700">

              Unable to update application status.

            </div>

          )}


          {/* LOADING */}

          {candidatesQuery.isLoading ? (

            <div className="space-y-4">

              <CandidateSkeleton />
              <CandidateSkeleton />
              <CandidateSkeleton />

            </div>

          ) : candidates.length ===
            0 ? (

            <div className="rounded-3xl border border-dashed border-slate-300 bg-white p-12 text-center">

              <Search
                size={32}
                className="mx-auto text-slate-300"
              />

              <h3 className="mt-4 text-lg font-bold">
                No applicants found
              </h3>

              <p className="mx-auto mt-2 max-w-md text-sm leading-6 text-slate-500">

                Applicants will appear here once candidates
                apply for this job.

              </p>

            </div>

          ) : (

            <div className="space-y-4">

              {candidates.map(
                (candidate) => (

                  <CandidateCard

                    key={
                      candidate.application_id ||
                      candidate.candidate_id
                    }

                    candidate={
                      candidate
                    }

                    updatingId={
                      statusMutation.isPending
                        ? statusMutation.variables
                            ?.applicationId ??
                          null
                        : null
                    }

                    onStatusChange={
                      handleStatusChange
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
   CANDIDATE CARD
   ========================================================= */

function CandidateCard({
  candidate,
  updatingId,
  onStatusChange,
}: {
  candidate: RankedCandidate;

  updatingId:
    string | null;

  onStatusChange: (
    applicationId:
      string | null,
    status: string
  ) => void;
}) {

  const finalScore =
    Math.round(
      (
        candidate.final_score ??
        0
      ) * 100
    );


  const isUpdating =
    updatingId ===
    candidate.application_id;


  return (
    <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm transition hover:shadow-lg">

      <div className="flex flex-col gap-6 xl:flex-row xl:items-start">


        {/* CANDIDATE */}

        <div className="min-w-0 flex-1">

          <div className="flex items-start gap-4">

            <div className="flex h-14 w-14 shrink-0 items-center justify-center rounded-2xl bg-slate-950 text-teal-300">

              <UserRound
                size={25}
              />

            </div>


            <div className="min-w-0">

              <div className="flex flex-wrap items-center gap-3">

                <span className="rounded-full bg-teal-50 px-3 py-1 text-xs font-bold text-teal-700">

                  #{candidate.rank}

                </span>


                <h3 className="text-xl font-bold">

                  {candidate.name ||
                    "Candidate"}

                </h3>

              </div>


              {candidate.email && (

                <p className="mt-1 text-sm text-slate-500">
                  {candidate.email}
                </p>

              )}


              <div className="mt-3">

                <StatusBadge
                  status={
                    candidate.application_status
                  }
                />

              </div>

            </div>

          </div>


          {/* SCORE SIGNALS */}

          <div className="mt-6 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">

            <ScoreCard
              icon={
                <Sparkles
                  size={16}
                />
              }
              label="Semantic"
              value={
                candidate.semantic_score
              }
            />


            <ScoreCard
              icon={
                <Search
                  size={16}
                />
              }
              label="Skills"
              value={
                candidate.skill_score
              }
            />


            <ScoreCard
              icon={
                <CheckCircle2
                  size={16}
                />
              }
              label="Experience"
              value={
                candidate.experience_score
              }
            />


            <ScoreCard
              icon={
                <GraduationCap
                  size={16}
                />
              }
              label="Education"
              value={
                candidate.education_score
              }
            />

          </div>

        </div>


        {/* SCORE + ACTIONS */}

        <div className="w-full xl:w-56">


          <div className="rounded-2xl bg-teal-50 p-5 text-center">

            <p className="text-xs font-bold uppercase tracking-wider text-teal-700">
              AI Match
            </p>


            <p className="mt-1 text-4xl font-black text-teal-700">
              {finalScore}%
            </p>


            <p className="mt-1 text-xs text-teal-600">
              Overall fit
            </p>

          </div>


          <div className="mt-4 grid gap-2">


            <button

              disabled={
                !candidate.application_id ||
                isUpdating
              }

              onClick={() =>
                onStatusChange(
                  candidate.application_id,
                  "shortlisted"
                )
              }

              className="flex items-center justify-center gap-2 rounded-xl bg-slate-950 px-4 py-3 text-sm font-semibold text-white transition hover:bg-teal-600 disabled:opacity-50"
            >

              <CheckCircle2
                size={16}
              />

              {isUpdating
                ? "Updating..."
                : "Shortlist"}

            </button>


            <button

              disabled={
                !candidate.application_id ||
                isUpdating
              }

              onClick={() =>
                onStatusChange(
                  candidate.application_id,
                  "interview"
                )
              }

              className="flex items-center justify-center gap-2 rounded-xl border border-slate-200 px-4 py-3 text-sm font-semibold text-slate-700 transition hover:border-teal-300 hover:text-teal-700 disabled:opacity-50"
            >

              <MessageSquare
                size={16}
              />

              Interview

            </button>


            <button

              disabled={
                !candidate.application_id ||
                isUpdating
              }

              onClick={() =>
                onStatusChange(
                  candidate.application_id,
                  "rejected"
                )
              }

              className="flex items-center justify-center gap-2 rounded-xl px-4 py-3 text-sm font-semibold text-red-600 transition hover:bg-red-50 disabled:opacity-50"
            >

              <XCircle
                size={16}
              />

              Reject

            </button>

          </div>

        </div>

      </div>

    </div>
  );
}


/* =========================================================
   SCORE CARD
   ========================================================= */

function ScoreCard({
  icon,
  label,
  value,
}: {
  icon: React.ReactNode;
  label: string;
  value: number;
}) {

  return (
    <div className="rounded-2xl bg-slate-50 p-4">

      <div className="flex items-center gap-2 text-slate-500">

        {icon}

        <span className="text-xs font-medium">
          {label}
        </span>

      </div>


      <p className="mt-2 text-xl font-bold">

        {Math.round(
          (
            value ?? 0
          ) * 100
        )}%

      </p>

    </div>
  );
}


/* =========================================================
   STATUS BADGE
   ========================================================= */

function StatusBadge({
  status,
}: {
  status:
    | string
    | null;
}) {

  const styles:
    Record<
      string,
      string
    > = {

    applied:
      "bg-slate-100 text-slate-700",

    reviewing:
      "bg-blue-50 text-blue-700",

    shortlisted:
      "bg-teal-50 text-teal-700",

    interview:
      "bg-violet-50 text-violet-700",

    rejected:
      "bg-red-50 text-red-700",

    hired:
      "bg-emerald-50 text-emerald-700",

  };


  return (

    <span
      className={`inline-flex rounded-full px-3 py-1 text-xs font-semibold ${
        styles[
          status || "applied"
        ] ||
        "bg-slate-100 text-slate-700"
      }`}
    >

      {status || "applied"}

    </span>

  );
}


/* =========================================================
   SKELETON
   ========================================================= */

function CandidateSkeleton() {

  return (
    <div className="h-64 animate-pulse rounded-3xl bg-slate-200" />
  );
}