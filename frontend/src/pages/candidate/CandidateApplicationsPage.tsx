import {
  useMemo,
  useState,
} from "react";

import {
  useQuery,
} from "@tanstack/react-query";

import {
  BriefcaseBusiness,
  CheckCircle2,
  Clock3,
  FileText,
  Search,
  XCircle,
} from "lucide-react";

import CandidateSidebar
  from "../../components/candidate/CandidateSidebar";

import {
  getMyApplications,
  type Application,
} from "../../services/candidateService";


type FilterStatus =
  | "all"
  | "applied"
  | "reviewing"
  | "shortlisted"
  | "interview"
  | "rejected"
  | "hired";


export default function CandidateApplicationsPage() {

  const [
    filter,
    setFilter,
  ] = useState<FilterStatus>(
    "all"
  );


  const [
    search,
    setSearch,
  ] = useState("");


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


  const applications =
    applicationsQuery.data ?? [];


  const filteredApplications =
    useMemo(
      () => {

        const term =
          search
            .trim()
            .toLowerCase();

        return applications.filter(
          (application) => {

            const statusMatch =
              filter === "all" ||
              application.status ===
                filter;

            const searchMatch =
              !term ||
              (
                application.job_title ||
                ""
              )
                .toLowerCase()
                .includes(term);

            return (
              statusMatch &&
              searchMatch
            );

          }
        );

      },
      [
        applications,
        filter,
        search,
      ]
    );


  return (
    <div className="flex min-h-screen bg-slate-50">

      <CandidateSidebar />

      <main className="min-w-0 flex-1">

        <header className="border-b border-slate-200 bg-white">

          <div className="px-6 py-5 md:px-8">

            <p className="text-sm font-semibold text-teal-600">
              Your activity
            </p>

            <h1 className="mt-1 text-2xl font-bold">
              My Applications
            </h1>

          </div>

        </header>


        <div className="space-y-7 p-6 md:p-8">


          {/* STATS */}

          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">

            <StatCard
              icon={
                <FileText size={19} />
              }
              label="Total"
              value={
                applications.length
              }
            />


            <StatCard
              icon={
                <Clock3 size={19} />
              }
              label="Reviewing"
              value={
                applications.filter(
                  (item) =>
                    item.status ===
                    "reviewing"
                ).length
              }
            />


            <StatCard
              icon={
                <CheckCircle2
                  size={19}
                />
              }
              label="Shortlisted"
              value={
                applications.filter(
                  (item) =>
                    item.status ===
                    "shortlisted"
                ).length
              }
            />


            <StatCard
              icon={
                <BriefcaseBusiness
                  size={19}
                />
              }
              label="Interviews"
              value={
                applications.filter(
                  (item) =>
                    item.status ===
                    "interview"
                ).length
              }
            />

          </div>


          {/* SEARCH */}

          <div className="rounded-3xl border border-slate-200 bg-white p-5">

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
                placeholder="Search your applications..."
                className="w-full rounded-2xl border border-slate-200 bg-slate-50 py-3.5 pl-11 pr-4 outline-none focus:border-teal-500"
              />

            </div>


            <div className="mt-4 flex flex-wrap gap-2">

              {[
                "all",
                "applied",
                "reviewing",
                "shortlisted",
                "interview",
                "rejected",
                "hired",
              ].map(
                (status) => (

                  <button
                    key={
                      status
                    }
                    onClick={() =>
                      setFilter(
                        status as FilterStatus
                      )
                    }
                    className={`rounded-full px-4 py-2 text-xs font-semibold ${
                      filter ===
                      status
                        ? "bg-slate-950 text-white"
                        : "bg-slate-100 text-slate-600"
                    }`}
                  >

                    {status ===
                    "all"
                      ? "All"
                      : status
                          .charAt(
                            0
                          )
                          .toUpperCase() +
                        status.slice(
                          1
                        )}

                  </button>

                )
              )}

            </div>

          </div>


          {/* ERROR */}

          {applicationsQuery.error && (

            <div className="rounded-2xl border border-red-200 bg-red-50 px-5 py-4 text-sm text-red-700">
              Unable to load your applications.
            </div>

          )}


          {/* CONTENT */}

          {applicationsQuery.isLoading ? (

            <div className="space-y-4">

              <Skeleton />
              <Skeleton />
              <Skeleton />

            </div>

          ) : filteredApplications.length ===
            0 ? (

            <div className="rounded-3xl border border-dashed border-slate-300 bg-white p-12 text-center">

              <FileText
                size={34}
                className="mx-auto text-slate-300"
              />

              <h2 className="mt-4 text-lg font-bold">
                No applications found
              </h2>

              <p className="mt-2 text-sm text-slate-500">
                Apply to jobs and your application
                status will appear here.
              </p>

            </div>

          ) : (

            <div className="space-y-4">

              {filteredApplications.map(
                (application) => (

                  <ApplicationCard
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

      </main>

    </div>
  );
}


/* =========================================================
   APPLICATION CARD
   ========================================================= */

function ApplicationCard({
  application,
}: {
  application: Application;
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
    <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">

      <div className="flex flex-col gap-5 sm:flex-row sm:items-center sm:justify-between">


        <div className="flex items-start gap-4">

          <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-slate-950 text-teal-300">

            <BriefcaseBusiness
              size={21}
            />

          </div>


          <div>

            <h2 className="text-lg font-bold">
              {application.job_title}
            </h2>


            <p className="mt-1 text-sm text-slate-500">

              {application.location ||
                "Location not specified"}

              {" · "}

              {application.employment_type ||
                "Full-time"}

            </p>


            {application.applied_at && (

              <p className="mt-2 text-xs text-slate-400">

                Applied{" "}

                {new Date(
                  application.applied_at
                ).toLocaleDateString()}

              </p>

            )}

          </div>

        </div>


        <div className="flex items-center gap-3">

          {application.status ===
            "rejected" && (

            <XCircle
              size={18}
              className="text-red-500"
            />

          )}


          {application.status ===
            "shortlisted" && (

            <CheckCircle2
              size={18}
              className="text-teal-500"
            />

          )}


          <span
            className={`rounded-full px-4 py-2 text-xs font-semibold ${
              styles[
                application.status
              ] ||
              "bg-slate-100 text-slate-700"
            }`}
          >
            {application.status}
          </span>

        </div>

      </div>

    </div>
  );
}


/* =========================================================
   STAT
   ========================================================= */

function StatCard({
  icon,
  label,
  value,
}: {
  icon: React.ReactNode;
  label: string;
  value: number;
}) {

  return (
    <div className="rounded-3xl border border-slate-200 bg-white p-5">

      <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-teal-50 text-teal-600">
        {icon}
      </div>

      <p className="mt-4 text-sm text-slate-500">
        {label}
      </p>

      <p className="mt-1 text-2xl font-bold">
        {value}
      </p>

    </div>
  );
}


/* =========================================================
   SKELETON
   ========================================================= */

function Skeleton() {

  return (
    <div className="h-28 animate-pulse rounded-3xl bg-slate-200" />
  );
}