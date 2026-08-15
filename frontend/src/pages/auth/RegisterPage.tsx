import { useState } from "react";

import {
  Link,
  useNavigate,
} from "react-router-dom";

import {
  ArrowRight,
  BriefcaseBusiness,
  Check,
  Mail,
  ShieldCheck,
  Sparkles,
  UserRound,
} from "lucide-react";

import axios from "axios";

import api from "../../services/api";
import { useAuth } from "../../context/AuthContext";


type Role =
  | "candidate"
  | "recruiter";


export default function RegisterPage() {

  const navigate = useNavigate();

  const { login } = useAuth();


  const [name, setName] =
    useState("");

  const [email, setEmail] =
    useState("");

  const [password, setPassword] =
    useState("");

  const [role, setRole] =
    useState<Role>("candidate");


  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState("");


  async function handleSubmit(
    event: React.FormEvent
  ) {

    event.preventDefault();

    setLoading(true);
    setError("");


    // Basic frontend validation
    if (name.trim().length < 2) {

      setError(
        "Please enter your full name."
      );

      setLoading(false);

      return;
    }


    if (!email.trim()) {

      setError(
        "Please enter your email address."
      );

      setLoading(false);

      return;
    }


    if (password.length < 8) {

      setError(
        "Password must contain at least 8 characters."
      );

      setLoading(false);

      return;
    }


    try {

      const response =
        await api.post(
          "/auth/register",
          {
            name: name.trim(),
            email: email.trim(),
            password,
            role,
          }
        );


      console.log(
        "Registration response:",
        response.data
      );


      const {
        access_token,
        role: returnedRole,
      } = response.data;


      if (!access_token) {

        setError(
          "Registration succeeded but no access token was returned by the server."
        );

        return;
      }


      login(
        access_token,
        returnedRole
      );


      if (
        returnedRole === "candidate"
      ) {

        navigate(
          "/candidate/dashboard"
        );

      } else if (
        returnedRole === "recruiter"
      ) {

        navigate(
          "/recruiter/dashboard"
        );

      } else {

        navigate("/");

      }

    } catch (error) {

      console.error(
        "Registration error:",
        error
      );


      if (
        axios.isAxiosError(error)
      ) {

        console.error(
          "Status:",
          error.response?.status
        );

        console.error(
          "Response:",
          error.response?.data
        );


        const detail =
          error.response?.data?.detail;


        // FastAPI validation errors
        if (
          Array.isArray(detail)
        ) {

          const messages =
            detail
              .map(
                (item: {
                  msg?: string;
                }) =>
                  item.msg ||
                  "Validation error"
              )
              .join(", ");


          setError(
            messages
          );


        } else if (detail) {

          setError(
            String(detail)
          );


        } else {

          setError(
            `Registration failed (${error.response?.status || "unknown error"}).`
          );
        }

      } else {

        setError(
          "An unexpected error occurred during registration."
        );
      }

    } finally {

      setLoading(false);

    }
  }


  return (
    <div className="min-h-screen bg-slate-50">

      <div className="grid min-h-screen lg:grid-cols-[0.85fr_1.15fr]">


        {/* =====================================================
            LEFT PANEL
            ===================================================== */}

        <div className="hidden bg-slate-950 lg:flex">

          <div className="flex w-full flex-col justify-between p-10">


            {/* Logo */}

            <Link
              to="/"
              className="inline-flex w-fit items-center gap-3"
            >

              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-white text-slate-950">

                <Sparkles
                  size={19}
                />

              </div>


              <span className="text-xl font-bold text-white">
                HireNiti
              </span>

            </Link>


            {/* Hero */}

            <div>

              <p className="text-sm font-bold uppercase tracking-[0.18em] text-teal-300">
                Get started
              </p>


              <h1 className="mt-5 text-5xl font-black leading-tight text-white">

                One platform.

                <span className="block text-teal-400">
                  Smarter hiring.
                </span>

              </h1>


              <p className="mt-6 max-w-md text-lg leading-8 text-slate-400">

                Whether you're building your career
                or your team, HireNiti helps you
                find a better match.

              </p>


              <div className="mt-10 space-y-4">

                <Benefit
                  icon={
                    <ShieldCheck
                      size={18}
                    />
                  }
                  text="AI-powered semantic matching"
                />


                <Benefit
                  icon={
                    <Sparkles
                      size={18}
                    />
                  }
                  text="Personalized recommendations"
                />


                <Benefit
                  icon={
                    <Check
                      size={18}
                    />
                  }
                  text="Secure recruitment workflow"
                />

              </div>

            </div>


            <p className="text-sm text-slate-500">
              HireNiti AI Recruitment Platform
            </p>

          </div>

        </div>


        {/* =====================================================
            RIGHT PANEL
            ===================================================== */}

        <div className="flex items-center justify-center px-6 py-10">

          <div className="w-full max-w-xl">


            {/* Mobile logo */}

            <Link
              to="/"
              className="mb-8 inline-flex items-center gap-2 text-sm font-semibold text-slate-600 lg:hidden"
            >

              <span>
                ←
              </span>

              HireNiti

            </Link>


            <p className="text-sm font-semibold text-teal-600">
              Create your account
            </p>


            <h2 className="mt-2 text-4xl font-black tracking-tight">
              Start your journey.
            </h2>


            <p className="mt-3 text-slate-500">
              Choose how you want to use HireNiti.
            </p>


            {/* ERROR */}

            {error && (

              <div className="mt-6 rounded-2xl border border-red-200 bg-red-50 px-4 py-4 text-sm text-red-700">

                <p className="font-semibold">
                  Registration failed
                </p>

                <p className="mt-1">
                  {error}
                </p>

              </div>

            )}


            {/* FORM */}

            <form
              onSubmit={handleSubmit}
              className="mt-8 space-y-5"
            >


              {/* ROLE */}

              <div>

                <label className="mb-3 block text-sm font-semibold text-slate-700">
                  I want to
                </label>


                <div className="grid gap-3 sm:grid-cols-2">


                  <RoleCard
                    selected={
                      role === "candidate"
                    }

                    icon={
                      <UserRound
                        size={21}
                      />
                    }

                    title="Find a job"

                    description="Discover AI-matched opportunities"

                    onClick={() =>
                      setRole(
                        "candidate"
                      )
                    }
                  />


                  <RoleCard
                    selected={
                      role === "recruiter"
                    }

                    icon={
                      <BriefcaseBusiness
                        size={21}
                      />
                    }

                    title="Hire talent"

                    description="Find and rank the best candidates"

                    onClick={() =>
                      setRole(
                        "recruiter"
                      )
                    }
                  />

                </div>

              </div>


              {/* NAME */}

              <div>

                <label className="mb-2 block text-sm font-semibold text-slate-700">
                  Full name
                </label>


                <input
                  type="text"

                  value={name}

                  onChange={(event) =>
                    setName(
                      event.target.value
                    )
                  }

                  placeholder="Mahesh Khot"

                  required

                  className="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3.5 outline-none transition focus:border-teal-500 focus:ring-4 focus:ring-teal-500/10"
                />

              </div>


              {/* EMAIL */}

              <div>

                <label className="mb-2 block text-sm font-semibold text-slate-700">
                  Email address
                </label>


                <div className="relative">

                  <Mail
                    size={18}
                    className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400"
                  />


                  <input
                    type="email"

                    value={email}

                    onChange={(event) =>
                      setEmail(
                        event.target.value
                      )
                    }

                    placeholder="you@example.com"

                    required

                    className="w-full rounded-2xl border border-slate-200 bg-white py-3.5 pl-11 pr-4 outline-none transition focus:border-teal-500 focus:ring-4 focus:ring-teal-500/10"
                  />

                </div>

              </div>


              {/* PASSWORD */}

              <div>

                <label className="mb-2 block text-sm font-semibold text-slate-700">
                  Password
                </label>


                <input
                  type="password"

                  value={password}

                  onChange={(event) =>
                    setPassword(
                      event.target.value
                    )
                  }

                  placeholder="At least 8 characters"

                  minLength={8}

                  required

                  className="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3.5 outline-none transition focus:border-teal-500 focus:ring-4 focus:ring-teal-500/10"
                />

              </div>


              {/* SUBMIT */}

              <button
                type="submit"

                disabled={
                  loading
                }

                className="group flex w-full items-center justify-center gap-2 rounded-2xl bg-slate-950 px-5 py-4 font-semibold text-white transition hover:bg-teal-600 disabled:cursor-not-allowed disabled:opacity-50"
              >

                {loading
                  ? "Creating account..."
                  : "Create account"}


                {!loading && (

                  <ArrowRight
                    size={18}
                    className="transition group-hover:translate-x-1"
                  />

                )}

              </button>

            </form>


            {/* LOGIN LINK */}

            <p className="mt-8 text-center text-sm text-slate-500">

              Already have an account?

              <Link
                to="/login"
                className="ml-1 font-semibold text-teal-600 hover:text-teal-700"
              >
                Sign in
              </Link>

            </p>

          </div>

        </div>

      </div>

    </div>
  );
}


/* =========================================================
   ROLE CARD
   ========================================================= */

function RoleCard({
  selected,
  icon,
  title,
  description,
  onClick,
}: {
  selected: boolean;
  icon: React.ReactNode;
  title: string;
  description: string;
  onClick: () => void;
}) {

  return (

    <button
      type="button"

      onClick={onClick}

      className={`rounded-2xl border p-4 text-left transition ${
        selected
          ? "border-teal-500 bg-teal-50 ring-2 ring-teal-500/10"
          : "border-slate-200 bg-white hover:border-slate-300"
      }`}
    >

      <div className="flex items-start gap-3">


        <div
          className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-xl ${
            selected
              ? "bg-teal-500 text-white"
              : "bg-slate-100 text-slate-600"
          }`}
        >

          {icon}

        </div>


        <div>

          <p className="font-semibold text-slate-950">
            {title}
          </p>


          <p className="mt-1 text-xs leading-5 text-slate-500">
            {description}
          </p>

        </div>

      </div>

    </button>

  );
}


/* =========================================================
   BENEFIT
   ========================================================= */

function Benefit({
  icon,
  text,
}: {
  icon: React.ReactNode;
  text: string;
}) {

  return (

    <div className="flex items-center gap-3 text-slate-300">

      <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-white/10 text-teal-300">

        {icon}

      </div>


      <span className="text-sm">
        {text}
      </span>

    </div>

  );
}