import {
  useEffect,
  useState,
} from "react";

import {
  useQuery,
  useQueryClient,
} from "@tanstack/react-query";

import {
  CheckCircle2,
  Save,
  UserRound,
} from "lucide-react";

import CandidateSidebar
  from "../../components/candidate/CandidateSidebar";


interface ProfileData {
  name: string;
  headline: string;
  location: string;
  phone: string;
  skills: string;
  education: string;
  experience: string;
}


const DEFAULT_PROFILE: ProfileData = {
  name: "",
  headline: "",
  location: "",
  phone: "",
  skills: "",
  education: "",
  experience: "",
};


/* =========================================================
   LOAD PROFILE
   ========================================================= */

function loadProfile(): ProfileData {

  try {

    const stored =
      localStorage.getItem(
        "candidate_profile"
      );

    if (!stored) {
      return DEFAULT_PROFILE;
    }


    const parsed =
      JSON.parse(stored) as Partial<ProfileData>;


    return {
      ...DEFAULT_PROFILE,
      ...parsed,
    };

  } catch (error) {

    console.error(
      "Failed to load profile:",
      error
    );

    return DEFAULT_PROFILE;
  }
}


/* =========================================================
   SAVE PROFILE
   ========================================================= */

function saveProfile(
  profile: ProfileData
): void {

  localStorage.setItem(
    "candidate_profile",
    JSON.stringify(profile)
  );
}


/* =========================================================
   PAGE
   ========================================================= */

export default function CandidateProfilePage() {

  const queryClient =
    useQueryClient();


  /* =======================================================
     REACT QUERY
     ======================================================= */

  const profileQuery =
    useQuery<ProfileData>({
      queryKey: [
        "candidate-profile",
      ],

      queryFn:
        loadProfile,

      staleTime:
        Infinity,

      gcTime:
        30 * 60 * 1000,

      refetchOnWindowFocus:
        false,
    });


  /* =======================================================
     LOCAL FORM STATE
     ======================================================= */

  const [
    profile,
    setProfile,
  ] = useState<ProfileData>(
    DEFAULT_PROFILE
  );


  const [
    savedMessage,
    setSavedMessage,
  ] = useState(false);


  const [
    saving,
    setSaving,
  ] = useState(false);


  /* =======================================================
     LOAD QUERY DATA INTO FORM
     ======================================================= */

  useEffect(() => {

    if (profileQuery.data) {

      setProfile(
        profileQuery.data
      );

    }

  }, [
    profileQuery.data,
  ]);


  /* =======================================================
     UPDATE FIELD
     ======================================================= */

  function updateField(
    field: keyof ProfileData,
    value: string
  ) {

    setProfile(
      (current) => ({
        ...current,
        [field]: value,
      })
    );

    setSavedMessage(false);
  }


  /* =======================================================
     SAVE
     ======================================================= */

  function handleSave() {

    setSaving(true);
    setSavedMessage(false);


    try {

      saveProfile(
        profile
      );


      /*
       * Update React Query cache immediately.
       */

      queryClient.setQueryData<ProfileData>(
        [
          "candidate-profile",
        ],
        profile
      );


      setSavedMessage(
        true
      );


      window.setTimeout(
        () => {
          setSavedMessage(false);
        },
        2500
      );

    } catch (error) {

      console.error(
        "Profile save error:",
        error
      );

    } finally {

      setSaving(false);
    }
  }


  /* =======================================================
     LOADING
     ======================================================= */

  if (
    profileQuery.isLoading &&
    !profileQuery.data
  ) {

    return (
      <div className="flex min-h-screen bg-slate-50">

        <CandidateSidebar />

        <main className="flex-1 p-8">

          <div className="animate-pulse space-y-6">

            <div className="h-10 w-64 rounded-xl bg-slate-200" />

            <div className="h-64 rounded-3xl bg-slate-200" />

            <div className="h-72 rounded-3xl bg-slate-200" />

          </div>

        </main>

      </div>
    );
  }


  /* =======================================================
     PAGE
     ======================================================= */

  return (
    <div className="flex min-h-screen bg-slate-50">

      <CandidateSidebar />


      <main className="min-w-0 flex-1">


        {/* =================================================
            HEADER
            ================================================= */}

        <header className="border-b border-slate-200 bg-white">

          <div className="px-6 py-5 md:px-8">

            <p className="text-sm font-semibold text-teal-600">
              Personal information
            </p>

            <h1 className="mt-1 text-2xl font-bold text-slate-950">
              My Profile
            </h1>

          </div>

        </header>


        <div className="mx-auto max-w-5xl space-y-6 p-6 md:p-8">


          {/* =================================================
              LOAD ERROR
              ================================================= */}

          {profileQuery.error && (

            <div className="rounded-2xl border border-red-200 bg-red-50 px-5 py-4 text-sm text-red-700">

              Unable to load your profile.

            </div>

          )}


          {/* =================================================
              SUCCESS
              ================================================= */}

          {savedMessage && (

            <div className="flex items-center gap-2 rounded-2xl border border-emerald-200 bg-emerald-50 px-5 py-4 text-sm text-emerald-700">

              <CheckCircle2
                size={17}
              />

              Profile saved successfully.

            </div>

          )}


          {/* =================================================
              PERSONAL INFORMATION
              ================================================= */}

          <section className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm md:p-8">

            <div className="flex items-center gap-4">

              <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-slate-950 text-teal-300">

                <UserRound
                  size={25}
                />

              </div>


              <div>

                <p className="text-sm font-semibold text-teal-600">
                  Candidate profile
                </p>

                <h2 className="text-xl font-bold text-slate-950">
                  Tell recruiters about yourself
                </h2>

              </div>

            </div>


            <div className="mt-8 grid gap-5 md:grid-cols-2">


              {/* FULL NAME */}

              <Field
                label="Full name"
                value={
                  profile.name
                }
                onChange={(
                  value
                ) =>
                  updateField(
                    "name",
                    value
                  )
                }
                placeholder="Your full name"
              />


              {/* HEADLINE */}

              <Field
                label="Professional headline"
                value={
                  profile.headline
                }
                onChange={(
                  value
                ) =>
                  updateField(
                    "headline",
                    value
                  )
                }
                placeholder="Python Developer | AI/ML Enthusiast"
              />


              {/* LOCATION */}

              <Field
                label="Location"
                value={
                  profile.location
                }
                onChange={(
                  value
                ) =>
                  updateField(
                    "location",
                    value
                  )
                }
                placeholder="Pune"
              />


              {/* PHONE */}

              <Field
                label="Phone"
                value={
                  profile.phone
                }
                onChange={(
                  value
                ) =>
                  updateField(
                    "phone",
                    value
                  )
                }
                placeholder="+91 XXXXX XXXXX"
              />

            </div>

          </section>


          {/* =================================================
              PROFESSIONAL INFORMATION
              ================================================= */}

          <section className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm md:p-8">

            <h2 className="text-xl font-bold text-slate-950">
              Professional information
            </h2>


            <div className="mt-6 space-y-5">


              {/* SKILLS */}

              <TextArea
                label="Skills"
                value={
                  profile.skills
                }
                onChange={(
                  value
                ) =>
                  updateField(
                    "skills",
                    value
                  )
                }
                placeholder="Python, FastAPI, SQL, React, Machine Learning..."
              />


              {/* EDUCATION */}

              <TextArea
                label="Education"
                value={
                  profile.education
                }
                onChange={(
                  value
                ) =>
                  updateField(
                    "education",
                    value
                  )
                }
                placeholder="B.E. in Electronics and Communication Engineering..."
              />


              {/* EXPERIENCE */}

              <TextArea
                label="Experience"
                value={
                  profile.experience
                }
                onChange={(
                  value
                ) =>
                  updateField(
                    "experience",
                    value
                  )
                }
                placeholder="Describe your experience..."
              />

            </div>

          </section>


          {/* =================================================
              SAVE BUTTON
              ================================================= */}

          <div className="flex justify-end">

            <button

              type="button"

              onClick={
                handleSave
              }

              disabled={
                saving
              }

              className="inline-flex items-center gap-2 rounded-xl bg-slate-950 px-6 py-3 font-semibold text-white transition hover:bg-teal-600 disabled:cursor-not-allowed disabled:opacity-50"

            >

              <Save
                size={17}
              />

              {saving
                ? "Saving..."
                : "Save profile"}

            </button>

          </div>

        </div>

      </main>

    </div>
  );
}


/* =========================================================
   INPUT FIELD
   ========================================================= */

function Field({
  label,
  value,
  onChange,
  placeholder,
}: {
  label: string;
  value: string;
  onChange: (
    value: string
  ) => void;
  placeholder: string;
}) {

  return (
    <div>

      <label className="mb-2 block text-sm font-semibold text-slate-700">

        {label}

      </label>


      <input

        type="text"

        value={
          value
        }

        onChange={(
          event
        ) =>
          onChange(
            event.target.value
          )
        }

        placeholder={
          placeholder
        }

        className="w-full rounded-xl border border-slate-200 bg-white px-4 py-3 text-slate-950 outline-none transition focus:border-teal-500 focus:ring-4 focus:ring-teal-500/10"

      />

    </div>
  );
}


/* =========================================================
   TEXT AREA
   ========================================================= */

function TextArea({
  label,
  value,
  onChange,
  placeholder,
}: {
  label: string;
  value: string;
  onChange: (
    value: string
  ) => void;
  placeholder: string;
}) {

  return (
    <div>

      <label className="mb-2 block text-sm font-semibold text-slate-700">

        {label}

      </label>


      <textarea

        rows={4}

        value={
          value
        }

        onChange={(
          event
        ) =>
          onChange(
            event.target.value
          )
        }

        placeholder={
          placeholder
        }

        className="w-full resize-none rounded-xl border border-slate-200 bg-white px-4 py-3 text-slate-950 outline-none transition focus:border-teal-500 focus:ring-4 focus:ring-teal-500/10"

      />

    </div>
  );
}