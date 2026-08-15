import {
  useMutation,
  useQueryClient,
} from "@tanstack/react-query";

import {
  ArrowLeft,
  BriefcaseBusiness,
  CheckCircle2,
  Sparkles,
} from "lucide-react";

import {
  useState,
} from "react";

import {
  useNavigate,
} from "react-router-dom";

import RecruiterSidebar
  from "../../components/recruiter/RecruiterSidebar";

import {
  createJob,
  publishJob,
  type CreateJobPayload,
} from "../../services/recruiterService";


const initialForm:
  CreateJobPayload = {

  title: "",

  description: "",

  required_skills: "",

  preferred_skills: "",

  experience_min: 0,

  experience_max: 2,

  education: "",

  location: "",

  employment_type:
    "Full-time",

  salary_min: 0,

  salary_max: 0,

};


export default function CreateJobPage() {

  const navigate =
    useNavigate();

  const queryClient =
    useQueryClient();


  const [form, setForm] =
    useState<CreateJobPayload>(
      initialForm
    );


  const [success, setSuccess] =
    useState("");


  const [error, setError] =
    useState("");


  const createJobMutation =
    useMutation({

      mutationFn:
        createJob,

      onSuccess: async (
        created
      ) => {

        /*
         * Invalidate cached job lists
         * because a new job was created.
         */

        await queryClient.invalidateQueries({
          queryKey: [
            "recruiter-jobs",
          ],
        });


        await queryClient.invalidateQueries({
          queryKey: [
            "recruiter-dashboard",
          ],
        });


        return created;

      },

      onError: (
        error
      ) => {

        console.error(
          error
        );

        setError(
          "Unable to create the job."
        );

      },

    });


  const publishMutation =
    useMutation({

      mutationFn:
        publishJob,

      onSuccess: async () => {

        await queryClient.invalidateQueries({
          queryKey: [
            "recruiter-jobs",
          ],
        });


        await queryClient.invalidateQueries({
          queryKey: [
            "recruiter-dashboard",
          ],
        });

      },

      onError: (
        error
      ) => {

        console.error(
          error
        );

        setError(
          "Job was created, but publishing failed."
        );

      },

    });


  function updateField(
    field:
      keyof CreateJobPayload,
    value:
      string | number
  ) {

    setForm(
      (current) => ({

        ...current,

        [field]:
          value,

      })
    );

  }


  async function submitJob(
    publish: boolean
  ) {

    setError("");
    setSuccess("");


    try {

      const created =
        await createJobMutation.mutateAsync(
          form
        );


      if (publish) {

        await publishMutation.mutateAsync(
          created.job_id
        );


        setSuccess(
          "Job created and published successfully."
        );

      } else {

        setSuccess(
          "Job saved successfully."
        );

      }


      setTimeout(
        () => {

          navigate(
            "/recruiter/jobs"
          );

        },

        700
      );

    } catch {
      /*
       * Individual mutations already
       * display the correct error.
       */
    }

  }


  const loading =
    createJobMutation.isPending ||
    publishMutation.isPending;


  return (
    <div className="flex min-h-screen bg-slate-50">

      <RecruiterSidebar />


      <main className="min-w-0 flex-1">


        <header className="border-b border-slate-200 bg-white">

          <div className="flex items-center gap-4 px-6 py-5 md:px-8">

            <button
              onClick={() =>
                navigate(
                  "/recruiter/jobs"
                )
              }
              className="flex h-10 w-10 items-center justify-center rounded-xl border border-slate-200 text-slate-600"
            >

              <ArrowLeft
                size={18}
              />

            </button>


            <div>

              <p className="text-sm font-semibold text-teal-600">
                New opportunity
              </p>

              <h1 className="mt-1 text-2xl font-bold">
                Create job
              </h1>

            </div>

          </div>

        </header>


        <div className="mx-auto max-w-5xl space-y-6 p-6 md:p-8">


          {/* ERROR */}

          {error && (

            <div className="rounded-2xl border border-red-200 bg-red-50 px-5 py-4 text-sm text-red-700">
              {error}
            </div>

          )}


          {/* SUCCESS */}

          {success && (

            <div className="rounded-2xl border border-emerald-200 bg-emerald-50 px-5 py-4 text-sm text-emerald-700">

              {success}

            </div>

          )}


          {/* AI HEADER */}

          <div className="rounded-3xl bg-slate-950 p-6 md:p-8">

            <div className="flex items-start gap-4">

              <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-teal-400/10 text-teal-300">

                <Sparkles
                  size={23}
                />

              </div>


              <div>

                <p className="text-sm font-semibold text-teal-300">
                  AI-ready job creation
                </p>


                <h2 className="mt-1 text-2xl font-bold text-white">
                  Define the role clearly.
                </h2>


                <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-400">

                  Your job description and requirements
                  are used for semantic candidate matching.

                </p>

              </div>

            </div>

          </div>


          {/* FORM */}

          <section className="rounded-3xl border border-slate-200 bg-white p-6 md:p-8">

            <div className="mb-7 flex items-center gap-3">

              <BriefcaseBusiness
                size={21}
                className="text-teal-600"
              />

              <h2 className="text-xl font-bold">
                Job details
              </h2>

            </div>


            <div className="grid gap-5 md:grid-cols-2">


              <Field
                label="Job title"
                value={
                  form.title
                }
                onChange={(
                  value
                ) =>
                  updateField(
                    "title",
                    value
                  )
                }
                placeholder="Junior Python Developer"
                required
              />


              <Field
                label="Location"
                value={
                  form.location
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


              <Field
                label="Required skills"
                value={
                  form.required_skills
                }
                onChange={(
                  value
                ) =>
                  updateField(
                    "required_skills",
                    value
                  )
                }
                placeholder="Python, FastAPI, SQL"
                required
              />


              <Field
                label="Preferred skills"
                value={
                  form.preferred_skills
                }
                onChange={(
                  value
                ) =>
                  updateField(
                    "preferred_skills",
                    value
                  )
                }
                placeholder="Docker, AWS"
              />


              <Field
                label="Education"
                value={
                  form.education
                }
                onChange={(
                  value
                ) =>
                  updateField(
                    "education",
                    value
                  )
                }
                placeholder="B.E. or B.Tech"
              />


              <div>

                <label className="mb-2 block text-sm font-semibold text-slate-700">
                  Employment type
                </label>


                <select
                  value={
                    form.employment_type
                  }
                  onChange={(
                    event
                  ) =>
                    updateField(
                      "employment_type",
                      event.target.value
                    )
                  }
                  className="w-full rounded-xl border border-slate-200 bg-white px-4 py-3 outline-none focus:border-teal-500"
                >

                  <option>
                    Full-time
                  </option>

                  <option>
                    Part-time
                  </option>

                  <option>
                    Contract
                  </option>

                  <option>
                    Internship
                  </option>

                </select>

              </div>


              <NumberField
                label="Minimum experience"
                value={
                  form.experience_min
                }
                onChange={(
                  value
                ) =>
                  updateField(
                    "experience_min",
                    value
                  )
                }
              />


              <NumberField
                label="Maximum experience"
                value={
                  form.experience_max
                }
                onChange={(
                  value
                ) =>
                  updateField(
                    "experience_max",
                    value
                  )
                }
              />


              <NumberField
                label="Minimum salary"
                value={
                  form.salary_min
                }
                onChange={(
                  value
                ) =>
                  updateField(
                    "salary_min",
                    value
                  )
                }
              />


              <NumberField
                label="Maximum salary"
                value={
                  form.salary_max
                }
                onChange={(
                  value
                ) =>
                  updateField(
                    "salary_max",
                    value
                  )
                }
              />

            </div>


            {/* DESCRIPTION */}

            <div className="mt-5">

              <label className="mb-2 block text-sm font-semibold text-slate-700">
                Job description
              </label>


              <textarea
                value={
                  form.description
                }
                onChange={(
                  event
                ) =>
                  updateField(
                    "description",
                    event.target.value
                  )
                }
                rows={7}
                required
                placeholder="Describe responsibilities, technologies and expectations..."
                className="w-full resize-none rounded-xl border border-slate-200 px-4 py-3 outline-none focus:border-teal-500 focus:ring-4 focus:ring-teal-500/10"
              />

            </div>


            {/* BUTTONS */}

            <div className="mt-8 flex flex-col gap-3 sm:flex-row sm:justify-end">

              <button
                type="button"
                disabled={
                  loading
                }
                onClick={() =>
                  submitJob(
                    false
                  )
                }
                className="rounded-xl border border-slate-200 px-6 py-3 text-sm font-semibold text-slate-700 hover:bg-slate-50 disabled:opacity-50"
              >

                Save draft

              </button>


              <button
                type="button"
                disabled={
                  loading
                }
                onClick={() =>
                  submitJob(
                    true
                  )
                }
                className="inline-flex items-center justify-center gap-2 rounded-xl bg-slate-950 px-6 py-3 text-sm font-semibold text-white hover:bg-teal-600 disabled:opacity-50"
              >

                <CheckCircle2
                  size={17}
                />

                {loading
                  ? "Creating..."
                  : "Create & publish"}

              </button>

            </div>

          </section>

        </div>

      </main>

    </div>
  );
}


/* =========================================================
   TEXT FIELD
   ========================================================= */

function Field({
  label,
  value,
  onChange,
  placeholder,
  required = false,
}: {
  label: string;
  value: string;
  onChange:
    (value: string) => void;
  placeholder: string;
  required?: boolean;
}) {

  return (
    <div>

      <label className="mb-2 block text-sm font-semibold text-slate-700">
        {label}
      </label>

      <input
        value={value}
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
        required={
          required
        }
        className="w-full rounded-xl border border-slate-200 px-4 py-3 outline-none focus:border-teal-500 focus:ring-4 focus:ring-teal-500/10"
      />

    </div>
  );
}


/* =========================================================
   NUMBER FIELD
   ========================================================= */

function NumberField({
  label,
  value,
  onChange,
}: {
  label: string;
  value: number;
  onChange:
    (value: number) => void;
}) {

  return (
    <div>

      <label className="mb-2 block text-sm font-semibold text-slate-700">
        {label}
      </label>

      <input
        type="number"
        min={0}
        value={value}
        onChange={(
          event
        ) =>
          onChange(
            Number(
              event.target.value
            )
          )
        }
        className="w-full rounded-xl border border-slate-200 px-4 py-3 outline-none focus:border-teal-500"
      />

    </div>
  );
}