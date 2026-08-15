import {
  useMutation,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query";

import {
  ArrowRight,
  MapPin,
  Sparkles,
} from "lucide-react";

import CandidateSidebar
  from "../../components/candidate/CandidateSidebar";

import {
  applyForJob,
  getMyApplications,
  getRecommendations,
  type RecommendedJob,
} from "../../services/candidateService";


export default function CandidateRecommendationsPage() {

  const queryClient =
    useQueryClient();


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


  const recommendations =
    [
      ...(recommendationsQuery.data ??
        []),
    ].sort(
      (a, b) =>
        (
          b.ranking_score ??
          b.final_score ??
          0
        ) -
        (
          a.ranking_score ??
          a.final_score ??
          0
        )
    );


  const applications =
    applicationsQuery.data ??
    [];


  return (
    <div className="flex min-h-screen bg-slate-50">

      <CandidateSidebar />

      <main className="min-w-0 flex-1">

        <header className="border-b border-slate-200 bg-white">

          <div className="px-6 py-5 md:px-8">

            <p className="text-sm font-semibold text-teal-600">
              Personalized for you
            </p>

            <h1 className="mt-1 text-2xl font-bold">
              AI Recommendations
            </h1>

          </div>

        </header>


        <div className="space-y-7 p-6 md:p-8">


          <section className="rounded-3xl bg-slate-950 p-6 md:p-8">

            <div className="flex items-start gap-4">

              <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-teal-400/10 text-teal-300">

                <Sparkles
                  size={24}
                />

              </div>


              <div>

                <p className="text-sm font-semibold text-teal-300">
                  AI MATCHING ENGINE
                </p>

                <h2 className="mt-2 text-3xl font-bold text-white">
                  Jobs ranked for your profile.
                </h2>

                <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-400">
                  Recommendations combine semantic similarity,
                  skills, experience and education.
                </p>

              </div>

            </div>

          </section>


          {applyMutation.error && (
            <div className="rounded-2xl border border-red-200 bg-red-50 px-5 py-4 text-sm text-red-700">
              Unable to submit application.
            </div>
          )}


          {recommendationsQuery.error && (
            <div className="rounded-2xl border border-red-200 bg-red-50 px-5 py-4 text-sm text-red-700">
              Unable to load recommendations.
            </div>
          )}


          {recommendationsQuery.isLoading ? (

            <div className="grid gap-5 xl:grid-cols-2">

              <Skeleton />
              <Skeleton />
              <Skeleton />
              <Skeleton />

            </div>

          ) : recommendations.length ===
            0 ? (

            <div className="rounded-3xl border border-dashed border-slate-300 bg-white p-12 text-center">

              <Sparkles
                size={35}
                className="mx-auto text-slate-300"
              />

              <h2 className="mt-4 text-lg font-bold">
                No recommendations yet
              </h2>

              <p className="mt-2 text-sm text-slate-500">
                Analyze your resume first so HireNiti
                can generate personalized matches.
              </p>

            </div>

          ) : (

            <div className="grid gap-5 xl:grid-cols-2">

              {recommendations.map(
                (job, index) => (

                  <RecommendationCard
                    key={
                      job.job_id
                    }
                    job={
                      job
                    }
                    rank={
                      index + 1
                    }
                    applied={
                      applications.some(
                        (application) =>
                          application.job_id ===
                          job.job_id
                      )
                    }
                    applying={
                      applyMutation.isPending &&
                      applyMutation.variables ===
                        job.job_id
                    }
                    onApply={() =>
                      applyMutation.mutate(
                        job.job_id
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
   CARD
   ========================================================= */

function RecommendationCard({
  job,
  rank,
  applied,
  applying,
  onApply,
}: {
  job: RecommendedJob;
  rank: number;
  applied: boolean;
  applying: boolean;
  onApply: () => void;
}) {

  const score =
    Math.round(
      (job.final_score ?? 0) *
      100
    );


  return (
    <article className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm transition hover:-translate-y-1 hover:shadow-xl">

      <div className="flex items-start justify-between gap-4">

        <div>

          <span className="inline-flex items-center gap-1 rounded-full bg-teal-50 px-3 py-1 text-xs font-bold text-teal-700">

            <Sparkles
              size={13}
            />

            Match #{rank}

          </span>


          <h2 className="mt-3 text-xl font-bold">
            {job.title}
          </h2>


          <div className="mt-2 flex flex-wrap gap-3 text-sm text-slate-500">

            <span className="inline-flex items-center gap-1">

              <MapPin
                size={14}
              />

              {job.location ||
                "Location not specified"}

            </span>

          </div>

        </div>


        <div className="flex h-16 w-16 shrink-0 items-center justify-center rounded-2xl bg-teal-50">

          <p className="text-lg font-black text-teal-700">
            {score}%
          </p>

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


      <div className="mt-5 grid grid-cols-3 gap-3">

        <Score
          label="Semantic"
          value={
            job.semantic_score
          }
        />

        <Score
          label="Skills"
          value={
            job.skill_score
          }
        />

        <Score
          label="Experience"
          value={
            job.experience_score
          }
        />

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
   SCORE
   ========================================================= */

function Score({
  label,
  value,
}: {
  label: string;
  value: number;
}) {

  return (
    <div className="rounded-xl bg-slate-50 p-3">

      <p className="text-[11px] uppercase text-slate-500">
        {label}
      </p>

      <p className="mt-1 font-bold">
        {Math.round(
          (value ?? 0) * 100
        )}%
      </p>

    </div>
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