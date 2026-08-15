import {
  ArrowRight,
  BrainCircuit,
  Search,
  ShieldCheck,
  Sparkles,
  Users,
} from "lucide-react";

import { Link } from "react-router-dom";

import Navbar from "../../components/layout/Navbar";

export default function HomePage() {

  return (
    <div className="min-h-screen bg-slate-50 text-slate-950">

      <Navbar />

      {/* HERO */}

      <section className="relative overflow-hidden">

        <div className="absolute inset-0 bg-[radial-gradient(circle_at_15%_20%,rgba(20,184,166,0.14),transparent_30%),radial-gradient(circle_at_85%_15%,rgba(59,130,246,0.12),transparent_30%)]" />

        <div className="relative mx-auto max-w-7xl px-6 pb-24 pt-20 md:pb-32 md:pt-28">

          <div className="mx-auto max-w-4xl text-center">

            <div className="mx-auto inline-flex items-center gap-2 rounded-full border border-teal-200 bg-white/80 px-4 py-2 text-sm font-medium shadow-sm">

              <Sparkles
                size={16}
                className="text-teal-600"
              />

              AI-powered recruitment platform

            </div>

            <h1 className="mt-8 text-5xl font-black tracking-tight md:text-7xl">

              Find the right role.

              <span className="block text-teal-500">
                Hire the right talent.
              </span>

            </h1>

            <p className="mx-auto mt-7 max-w-2xl text-lg leading-8 text-slate-600 md:text-xl">

              HireNiti uses semantic matching and
              AI ranking to connect candidates with
              opportunities and recruiters with the
              best-fit talent.

            </p>

            <div className="mt-9 flex flex-col justify-center gap-3 sm:flex-row">

              <Link
                to="/register"
                className="group inline-flex items-center justify-center gap-2 rounded-2xl bg-teal-500 px-7 py-4 font-semibold text-white shadow-lg shadow-teal-500/20 transition hover:-translate-y-1 hover:bg-teal-600"
              >
                Find your next role

                <ArrowRight
                  size={18}
                  className="transition group-hover:translate-x-1"
                />

              </Link>

              <Link
                to="/register"
                className="inline-flex items-center justify-center rounded-2xl border border-slate-200 bg-white px-7 py-4 font-semibold text-slate-800 shadow-sm transition hover:-translate-y-1 hover:border-slate-300"
              >
                Start hiring
              </Link>

            </div>

          </div>


          {/* DASHBOARD PREVIEW */}

          <div className="mx-auto mt-16 max-w-5xl">

            <div className="rounded-[2rem] border border-slate-200 bg-white p-3 shadow-2xl shadow-slate-300/30">

              <div className="rounded-[1.5rem] bg-slate-950 p-6 md:p-8">

                <div className="flex items-center justify-between">

                  <div>

                    <p className="text-sm text-slate-400">
                      AI Matching Engine
                    </p>

                    <h2 className="mt-1 text-lg font-semibold text-white">
                      Recommended opportunities
                    </h2>

                  </div>

                  <span className="rounded-full bg-teal-400/10 px-3 py-1 text-xs font-bold text-teal-300">
                    AI MATCHING
                  </span>

                </div>

                <div className="mt-8 grid gap-4 md:grid-cols-3">

                  <PreviewCard
                    title="Python Developer"
                    score="94%"
                  />

                  <PreviewCard
                    title="AI Engineer"
                    score="89%"
                  />

                  <PreviewCard
                    title="FastAPI Developer"
                    score="86%"
                  />

                </div>

              </div>

            </div>

          </div>

        </div>

      </section>


      {/* FEATURES */}

      <section
        id="features"
        className="border-y border-slate-200 bg-white"
      >

        <div className="mx-auto max-w-7xl px-6 py-20">

          <div className="mx-auto max-w-2xl text-center">

            <p className="text-sm font-bold uppercase tracking-[0.18em] text-teal-600">
              Built for modern hiring
            </p>

            <h2 className="mt-3 text-3xl font-bold tracking-tight md:text-4xl">
              Intelligence at every step.
            </h2>

          </div>


          <div className="mt-12 grid gap-5 md:grid-cols-3">

            <FeatureCard
              icon={
                <BrainCircuit size={20} />
              }
              title="Semantic matching"
              description="Understand the meaning behind resumes and job descriptions instead of relying only on keywords."
            />

            <FeatureCard
              icon={
                <Users size={20} />
              }
              title="AI ranking"
              description="Rank opportunities for candidates and applicants for recruiters using multiple signals."
            />

            <FeatureCard
              icon={
                <ShieldCheck size={20} />
              }
              title="Secure workflow"
              description="Protected APIs, role-based access and private resume storage."
            />

          </div>

        </div>

      </section>


      {/* HOW IT WORKS */}

      <section
        id="how-it-works"
        className="bg-slate-50"
      >

        <div className="mx-auto max-w-7xl px-6 py-20">

          <div className="max-w-xl">

            <p className="text-sm font-bold uppercase tracking-[0.18em] text-teal-600">
              How it works
            </p>

            <h2 className="mt-3 text-3xl font-bold md:text-4xl">
              From resume to intelligent match.
            </h2>

          </div>


          <div className="mt-12 grid gap-5 md:grid-cols-3">

            <StepCard
              number="01"
              title="Upload"
              description="Upload your resume and let HireNiti extract your skills, education, experience and projects."
            />

            <StepCard
              number="02"
              title="Understand"
              description="Semantic embeddings understand the relationship between candidate profiles and job requirements."
            />

            <StepCard
              number="03"
              title="Match"
              description="AI ranking combines semantic similarity, skills, experience and education to surface the best matches."
            />

          </div>

        </div>

      </section>


      {/* RECRUITER CTA */}

      <section
        id="for-recruiters"
        className="bg-slate-950"
      >

        <div className="mx-auto max-w-7xl px-6 py-20">

          <div className="grid items-center gap-12 md:grid-cols-2">

            <div>

              <p className="text-sm font-bold uppercase tracking-[0.18em] text-teal-300">
                For recruiters
              </p>

              <h2 className="mt-4 text-4xl font-bold tracking-tight text-white md:text-5xl">
                Stop searching through hundreds of resumes.
              </h2>

              <p className="mt-5 max-w-xl leading-8 text-slate-400">
                Let AI surface the strongest candidates,
                explain the match and help your team shortlist faster.
              </p>

              <Link
                to="/register"
                className="mt-8 inline-flex items-center gap-2 rounded-xl bg-teal-500 px-6 py-3.5 font-semibold text-white transition hover:bg-teal-600"
              >
                Start hiring

                <ArrowRight size={18} />

              </Link>

            </div>


            <div className="grid gap-4 sm:grid-cols-2">

              <MetricCard
                icon={<Search size={20} />}
                title="Semantic"
                text="Meaning-aware matching"
              />

              <MetricCard
                icon={<BrainCircuit size={20} />}
                title="AI ranked"
                text="Candidates ordered by fit"
              />

              <MetricCard
                icon={<Users size={20} />}
                title="Candidate-first"
                text="Personalized opportunities"
              />

              <MetricCard
                icon={<ShieldCheck size={20} />}
                title="Secure"
                text="Protected recruitment workflow"
              />

            </div>

          </div>

        </div>

      </section>

    </div>
  );
}


function PreviewCard({
  title,
  score,
}: {
  title: string;
  score: string;
}) {

  return (
    <div className="rounded-2xl border border-white/10 bg-white/5 p-5">

      <div className="flex items-center justify-between">

        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-white/10">

          <Search
            size={18}
            className="text-teal-300"
          />

        </div>

        <span className="rounded-full bg-teal-400/10 px-3 py-1 text-xs font-bold text-teal-300">
          {score}
        </span>

      </div>

      <h3 className="mt-5 font-semibold text-white">
        {title}
      </h3>

      <p className="mt-2 text-sm text-slate-400">
        Semantic + skills + experience
      </p>

    </div>
  );
}


function FeatureCard({
  icon,
  title,
  description,
}: {
  icon: React.ReactNode;
  title: string;
  description: string;
}) {

  return (
    <div className="rounded-3xl border border-slate-200 bg-slate-50 p-7 transition hover:-translate-y-1 hover:shadow-xl">

      <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-teal-500 text-white">
        {icon}
      </div>

      <h3 className="mt-6 text-lg font-bold">
        {title}
      </h3>

      <p className="mt-3 leading-7 text-slate-600">
        {description}
      </p>

    </div>
  );
}


function StepCard({
  number,
  title,
  description,
}: {
  number: string;
  title: string;
  description: string;
}) {

  return (
    <div className="rounded-3xl border border-slate-200 bg-white p-7">

      <span className="text-sm font-bold text-teal-600">
        {number}
      </span>

      <h3 className="mt-5 text-xl font-bold">
        {title}
      </h3>

      <p className="mt-3 leading-7 text-slate-600">
        {description}
      </p>

    </div>
  );
}


function MetricCard({
  icon,
  title,
  text,
}: {
  icon: React.ReactNode;
  title: string;
  text: string;
}) {

  return (
    <div className="rounded-2xl border border-white/10 bg-white/5 p-6">

      <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-teal-400/10 text-teal-300">
        {icon}
      </div>

      <p className="mt-5 font-semibold text-white">
        {title}
      </p>

      <p className="mt-1 text-sm text-slate-400">
        {text}
      </p>

    </div>
  );
}