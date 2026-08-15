import { useState } from "react";

import {
  Link,
  useNavigate,
} from "react-router-dom";

import {
  ArrowRight,
  LockKeyhole,
  Mail,
  Sparkles,
} from "lucide-react";

import axios from "axios";

import api from "../../services/api";
import { useAuth } from "../../context/AuthContext";


export default function LoginPage() {

  const navigate = useNavigate();

  const {
    login,
  } = useAuth();


  const [email, setEmail] =
    useState("");

  const [password, setPassword] =
    useState("");


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


    // -----------------------------------------------------
    // Basic validation
    // -----------------------------------------------------

    if (!email.trim()) {

      setError(
        "Please enter your email address."
      );

      setLoading(false);

      return;
    }


    if (!password) {

      setError(
        "Please enter your password."
      );

      setLoading(false);

      return;
    }


    try {

      const response =
        await api.post(
          "/auth/login",
          {
            email: email.trim(),
            password,
          }
        );


      console.log(
        "Login response:",
        response.data
      );


      const {
        access_token,
        role,
      } = response.data;


      // ---------------------------------------------------
      // Make sure backend returned token
      // ---------------------------------------------------

      if (!access_token) {

        setError(
          "Login succeeded but the server did not return an access token."
        );

        return;
      }


      // ---------------------------------------------------
      // Save authentication
      // ---------------------------------------------------

      login(
        access_token,
        role
      );


      // ---------------------------------------------------
      // Redirect according to role
      // ---------------------------------------------------

      if (
        role === "candidate"
      ) {

        navigate(
          "/candidate/dashboard"
        );

      } else if (
        role === "recruiter"
      ) {

        navigate(
          "/recruiter/dashboard"
        );

      } else {

        navigate("/");

      }

    } catch (error) {

      console.error(
        "Login error:",
        error
      );


      // ---------------------------------------------------
      // Axios error
      // ---------------------------------------------------

      if (
        axios.isAxiosError(error)
      ) {

        console.error(
          "Login status:",
          error.response?.status
        );

        console.error(
          "Login response:",
          error.response?.data
        );


        const detail =
          error.response?.data?.detail;


        // FastAPI validation error
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


        } else if (
          error.response?.status === 401
        ) {

          setError(
            "Invalid email or password."
          );


        } else if (
          error.response?.status === 403
        ) {

          setError(
            "You are not authorized to access this account."
          );


        } else if (
          error.response?.status === 404
        ) {

          setError(
            "Login service was not found."
          );


        } else if (
          error.response?.status &&
          error.response.status >= 500
        ) {

          setError(
            "Server error. Please try again later."
          );


        } else {

          setError(
            `Login failed (${error.response?.status || "unknown error"}).`
          );
        }

      } else {

        setError(
          "An unexpected error occurred during login."
        );
      }

    } finally {

      setLoading(false);

    }
  }


  return (
    <div className="min-h-screen bg-slate-50">

      <div className="grid min-h-screen lg:grid-cols-2">


        {/* =================================================
            LEFT PANEL
            ================================================= */}

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

            <div className="max-w-lg">

              <p className="text-sm font-bold uppercase tracking-[0.18em] text-teal-300">
                Welcome back
              </p>


              <h1 className="mt-5 text-5xl font-black leading-tight text-white">

                Your next opportunity
                starts here.

              </h1>


              <p className="mt-6 max-w-md text-lg leading-8 text-slate-400">

                Discover jobs that actually match
                your skills, experience and projects.

              </p>


              {/* AI highlights */}

              <div className="mt-10 space-y-4">

                <div className="flex items-center gap-3">

                  <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-white/10 text-teal-300">

                    <Sparkles
                      size={18}
                    />

                  </div>

                  <span className="text-sm text-slate-300">
                    AI-powered job matching
                  </span>

                </div>


                <div className="flex items-center gap-3">

                  <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-white/10 text-teal-300">

                    <Mail
                      size={18}
                    />

                  </div>

                  <span className="text-sm text-slate-300">
                    Personalized opportunities
                  </span>

                </div>


                <div className="flex items-center gap-3">

                  <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-white/10 text-teal-300">

                    <LockKeyhole
                      size={18}
                    />

                  </div>

                  <span className="text-sm text-slate-300">
                    Secure account access
                  </span>

                </div>

              </div>

            </div>


            <p className="text-sm text-slate-500">
              HireNiti AI Recruitment Platform
            </p>

          </div>

        </div>


        {/* =================================================
            RIGHT PANEL
            ================================================= */}

        <div className="flex items-center justify-center px-6 py-12">

          <div className="w-full max-w-md">


            {/* Mobile logo */}

            <Link
              to="/"
              className="mb-10 inline-flex items-center gap-2 text-sm font-semibold text-slate-600 lg:hidden"
            >

              <span>
                ←
              </span>

              HireNiti

            </Link>


            {/* Heading */}

            <div>

              <p className="text-sm font-semibold text-teal-600">
                Sign in
              </p>


              <h2 className="mt-2 text-4xl font-black tracking-tight text-slate-950">
                Welcome back.
              </h2>


              <p className="mt-3 text-slate-500">
                Sign in to continue to your dashboard.
              </p>

            </div>


            {/* Error */}

            {error && (

              <div className="mt-6 rounded-2xl border border-red-200 bg-red-50 px-4 py-4 text-sm text-red-700">

                <p className="font-semibold">
                  Login failed
                </p>

                <p className="mt-1">
                  {error}
                </p>

              </div>

            )}


            {/* Form */}

            <form
              onSubmit={
                handleSubmit
              }
              className="mt-8 space-y-5"
            >


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

                    autoComplete="email"

                    className="w-full rounded-2xl border border-slate-200 bg-white py-3.5 pl-11 pr-4 outline-none transition focus:border-teal-500 focus:ring-4 focus:ring-teal-500/10"
                  />

                </div>

              </div>


              {/* PASSWORD */}

              <div>

                <div className="mb-2 flex items-center justify-between">

                  <label className="block text-sm font-semibold text-slate-700">
                    Password
                  </label>

                </div>


                <div className="relative">

                  <LockKeyhole
                    size={18}
                    className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400"
                  />


                  <input
                    type="password"

                    value={password}

                    onChange={(event) =>
                      setPassword(
                        event.target.value
                      )
                    }

                    placeholder="Enter your password"

                    required

                    autoComplete="current-password"

                    className="w-full rounded-2xl border border-slate-200 bg-white py-3.5 pl-11 pr-4 outline-none transition focus:border-teal-500 focus:ring-4 focus:ring-teal-500/10"
                  />

                </div>

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
                  ? "Signing in..."
                  : "Sign in"}


                {!loading && (

                  <ArrowRight
                    size={18}
                    className="transition group-hover:translate-x-1"
                  />

                )}

              </button>

            </form>


            {/* REGISTER */}

            <p className="mt-8 text-center text-sm text-slate-500">

              Don't have an account?

              <Link
                to="/register"
                className="ml-1 font-semibold text-teal-600 transition hover:text-teal-700"
              >
                Create account
              </Link>

            </p>

          </div>

        </div>

      </div>

    </div>
  );
}