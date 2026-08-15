import {
  BrowserRouter,
  Navigate,
  Route,
  Routes,
} from "react-router-dom";

import {
  QueryClient,
  QueryClientProvider,
} from "@tanstack/react-query";

import {
  AuthProvider,
} from "./context/AuthContext";

import ProtectedRoute
  from "./components/layout/ProtectedRoute";


/* =========================================================
   PUBLIC
   ========================================================= */

import HomePage
  from "./pages/public/HomePage";

import LoginPage
  from "./pages/auth/LoginPage";

import RegisterPage
  from "./pages/auth/RegisterPage";


/* =========================================================
   CANDIDATE
   ========================================================= */

import CandidateDashboard
  from "./pages/candidate/CandidateDashboard";

import CandidateJobsPage
  from "./pages/candidate/CandidateJobsPage";

import CandidateRecommendationsPage
  from "./pages/candidate/CandidateRecommendationsPage";

import CandidateApplicationsPage
  from "./pages/candidate/CandidateApplicationsPage";

import CandidateResumePage
  from "./pages/candidate/CandidateResumePage";

import CandidateProfilePage
  from "./pages/candidate/CandidateProfilePage";


/* =========================================================
   RECRUITER
   ========================================================= */

import RecruiterDashboard
  from "./pages/recruiter/RecruiterDashboard";

import MyJobsPage
  from "./pages/recruiter/MyJobsPage";

import CreateJobPage
  from "./pages/recruiter/CreateJobPage";

import AIApplicantsPage
  from "./pages/recruiter/AIApplicantsPage";

import RecruiterApplicantsPage
  from "./pages/recruiter/RecruiterApplicantsPage";


/* =========================================================
   REACT QUERY CLIENT
   ========================================================= */

const queryClient = new QueryClient({

  defaultOptions: {

    queries: {

      // Keep successful API data in cache for 60 seconds.
      staleTime: 60 * 1000,

      // Keep unused cached data for 10 minutes.
      gcTime: 10 * 60 * 1000,

      // Don't refetch every time browser window gets focus.
      refetchOnWindowFocus: false,

      // Retry failed requests only once.
      retry: 1,

    },

  },

});


/* =========================================================
   APP
   ========================================================= */

export default function App() {

  return (

    <QueryClientProvider
      client={queryClient}
    >

      <BrowserRouter>

        <AuthProvider>

          <Routes>


            {/* =================================================
                PUBLIC ROUTES
                ================================================= */}

            <Route
              path="/"
              element={
                <HomePage />
              }
            />

            <Route
              path="/login"
              element={
                <LoginPage />
              }
            />

            <Route
              path="/register"
              element={
                <RegisterPage />
              }
            />


            {/* =================================================
                CANDIDATE ROUTES
                ================================================= */}

            <Route
              element={
                <ProtectedRoute
                  allowedRole="candidate"
                />
              }
            >

              {/* Candidate Dashboard */}

              <Route
                path="/candidate/dashboard"
                element={
                  <CandidateDashboard />
                }
              />


              {/* Find Jobs */}

              <Route
                path="/candidate/jobs"
                element={
                  <CandidateJobsPage />
                }
              />


              {/* AI Recommendations */}

              <Route
                path="/candidate/recommendations"
                element={
                  <CandidateRecommendationsPage />
                }
              />


              {/* Applications */}

              <Route
                path="/candidate/applications"
                element={
                  <CandidateApplicationsPage />
                }
              />


              {/* Resume */}

              <Route
                path="/candidate/resume"
                element={
                  <CandidateResumePage />
                }
              />


              {/* Profile */}

              <Route
                path="/candidate/profile"
                element={
                  <CandidateProfilePage />
                }
              />

            </Route>


            {/* =================================================
                RECRUITER ROUTES
                ================================================= */}

            <Route
              element={
                <ProtectedRoute
                  allowedRole="recruiter"
                />
              }
            >

              {/* Recruiter Dashboard */}

              <Route
                path="/recruiter/dashboard"
                element={
                  <RecruiterDashboard />
                }
              />


              {/* My Jobs */}

              <Route
                path="/recruiter/jobs"
                element={
                  <MyJobsPage />
                }
              />


              {/* Create Job */}

              <Route
                path="/recruiter/jobs/create"
                element={
                  <CreateJobPage />
                }
              />


              {/* AI Applicants */}

              <Route
                path="/recruiter/jobs/:jobId/applicants"
                element={
                  <AIApplicantsPage />
                }
              />


              {/* All Applicants */}

              <Route
                path="/recruiter/applicants"
                element={
                  <RecruiterApplicantsPage />
                }
              />

            </Route>


            {/* =================================================
                FALLBACK
                ================================================= */}

            <Route
              path="*"
              element={
                <Navigate
                  to="/"
                  replace
                />
              }
            />

          </Routes>

        </AuthProvider>

      </BrowserRouter>

    </QueryClientProvider>

  );
}