import {
  useMutation,
  useQueryClient,
} from "@tanstack/react-query";

import {
  useState,
} from "react";

import {
  CheckCircle2,
  FileText,
  GraduationCap,
  Sparkles,
  Upload,
} from "lucide-react";

import CandidateSidebar
  from "../../components/candidate/CandidateSidebar";

import {
  analyzeResume,
  uploadResume,
} from "../../services/candidateService";


interface ResumeAnalysis {
  skills: string[];
  education: string;
  experience: string;
}


interface AnalysisResponse {
  analysis?: {
    skills?: unknown;
    education?: unknown;
    experience?: unknown;
  };
}


export default function CandidateResumePage() {

  const queryClient =
    useQueryClient();


  const [
    file,
    setFile,
  ] = useState<File | null>(
    null
  );


  const [
    analysis,
    setAnalysis,
  ] = useState<ResumeAnalysis | null>(
    null
  );


  const [
    error,
    setError,
  ] = useState("");


  const [
    success,
    setSuccess,
  ] = useState("");


  const uploadMutation =
    useMutation<
      AnalysisResponse,
      Error,
      File
    >({

      mutationFn:
        async (
          selectedFile
        ) => {

          const uploadResult =
            await uploadResume(
              selectedFile
            );


          const resumeId =
            uploadResult?.resume_id;


          if (!resumeId) {

            throw new Error(
              "Resume ID was not returned by the server."
            );

          }


          const result =
            await analyzeResume(
              resumeId
            );


          return result as AnalysisResponse;
        },


      onSuccess:
        async (
          result
        ) => {

          const data =
            result.analysis;


          if (!data) {

            throw new Error(
              "Resume analysis was not returned by the server."
            );

          }


          const skills =
            Array.isArray(
              data.skills
            )
              ? data.skills
                  .filter(
                    (
                      skill
                    ): skill is string =>
                      typeof skill ===
                      "string"
                  )
                  .map(
                    (
                      skill
                    ) =>
                      skill.trim()
                  )
                  .filter(
                    Boolean
                  )
              : [];


          const education =
            typeof data.education ===
            "string"
              ? data.education.trim()
              : "";


          const experience =
            typeof data.experience ===
            "string"
              ? data.experience.trim()
              : "";


          setAnalysis({

            skills,

            education,

            experience,

          });


          setFile(null);


          setSuccess(
            "Resume uploaded and analyzed successfully."
          );


          await queryClient.invalidateQueries({
            queryKey: [
              "candidate-recommendations",
            ],
          });


          await queryClient.invalidateQueries({
            queryKey: [
              "candidate-dashboard",
            ],
          });

        },


      onError:
        (mutationError) => {

          console.error(
            "Resume processing error:",
            mutationError
          );


          setError(
            mutationError.message ||
            "Unable to process your resume."
          );

        },

    });


  function handleFileChange(
    selectedFile: File | undefined
  ) {

    if (!selectedFile) {
      return;
    }


    setError("");
    setSuccess("");
    setAnalysis(null);


    const fileName =
      selectedFile.name.toLowerCase();


    const validExtension =
      fileName.endsWith(
        ".pdf"
      ) ||
      fileName.endsWith(
        ".docx"
      );


    if (!validExtension) {

      setFile(null);

      setError(
        "Only PDF and DOCX files are allowed."
      );

      return;
    }


    const maxSize =
      5 * 1024 * 1024;


    if (
      selectedFile.size >
      maxSize
    ) {

      setFile(null);

      setError(
        "Resume must be smaller than 5 MB."
      );

      return;
    }


    setFile(
      selectedFile
    );
  }


  function handleUpload() {

    if (!file) {

      setError(
        "Please select a PDF or DOCX resume."
      );

      return;
    }


    setError("");
    setSuccess("");


    uploadMutation.mutate(
      file
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

          <div className="px-6 py-5 md:px-8">

            <p className="text-sm font-semibold text-teal-600">
              Candidate profile
            </p>

            <h1 className="mt-1 text-2xl font-bold text-slate-950">
              My Resume
            </h1>

          </div>

        </header>


        <div className="space-y-7 p-6 md:p-8">


          {/* =================================================
              UPLOAD
              ================================================= */}

          <section className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm md:p-8">

            <div className="grid gap-8 md:grid-cols-[1fr_auto] md:items-center">


              <div>

                <div className="flex items-center gap-3">

                  <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-teal-50 text-teal-600">

                    <FileText
                      size={21}
                    />

                  </div>


                  <div>

                    <p className="text-sm font-semibold text-teal-600">
                      Resume intelligence
                    </p>

                    <h2 className="text-xl font-bold text-slate-950">
                      Upload your latest resume
                    </h2>

                  </div>

                </div>


                <p className="mt-4 max-w-2xl text-sm leading-6 text-slate-500">

                  HireNiti will extract your skills,
                  education and experience.

                </p>


                <p className="mt-2 text-xs text-slate-400">
                  Supported: PDF, DOCX · Maximum 5 MB
                </p>

              </div>


              <div className="flex flex-col gap-3">


                <label className="cursor-pointer rounded-2xl border border-slate-200 bg-slate-50 px-5 py-4 text-center text-sm font-semibold text-slate-700 transition hover:border-teal-300 hover:bg-teal-50">

                  <input
                    type="file"
                    accept=".pdf,.docx"
                    className="hidden"
                    onChange={(event) =>
                      handleFileChange(
                        event.target.files?.[0]
                      )
                    }
                  />

                  {file
                    ? file.name
                    : "Choose PDF or DOCX"}

                </label>


                <button
                  type="button"
                  onClick={
                    handleUpload
                  }
                  disabled={
                    !file ||
                    uploadMutation.isPending
                  }
                  className="inline-flex items-center justify-center gap-2 rounded-2xl bg-slate-950 px-5 py-3.5 text-sm font-semibold text-white transition hover:bg-teal-600 disabled:cursor-not-allowed disabled:opacity-40"
                >

                  <Upload
                    size={17}
                  />

                  {uploadMutation.isPending
                    ? "Analyzing..."
                    : "Upload & analyze"}

                </button>

              </div>

            </div>

          </section>


          {/* =================================================
              ERROR
              ================================================= */}

          {error && (

            <div className="rounded-2xl border border-red-200 bg-red-50 px-5 py-4 text-sm text-red-700">

              {error}

            </div>

          )}


          {/* =================================================
              SUCCESS
              ================================================= */}

          {success && (

            <div className="flex items-center gap-2 rounded-2xl border border-emerald-200 bg-emerald-50 px-5 py-4 text-sm text-emerald-700">

              <CheckCircle2
                size={17}
              />

              {success}

            </div>

          )}


          {/* =================================================
              ANALYSIS
              ================================================= */}

          {analysis && (

            <section className="space-y-5">


              <div>

                <p className="text-sm font-semibold text-teal-600">
                  AI analysis
                </p>

                <h2 className="mt-1 text-2xl font-bold text-slate-950">
                  Extracted profile
                </h2>

              </div>


              <div className="grid gap-5 lg:grid-cols-2">


                {/* =================================================
                    SKILLS
                    ================================================= */}

                <AnalysisCard
                  icon={
                    <Sparkles
                      size={20}
                    />
                  }
                  title="Skills"
                  content={

                    analysis.skills.length >
                    0 ? (

                      <div className="flex flex-wrap gap-2">

                        {analysis.skills.map(
                          (
                            skill,
                            index
                          ) => (

                            <span
                              key={`${skill}-${index}`}
                              className="rounded-full bg-teal-50 px-3 py-1.5 text-xs font-semibold text-teal-700"
                            >
                              {skill}
                            </span>

                          )
                        )}

                      </div>

                    ) : (

                      <p className="text-sm text-slate-500">
                        No skills were extracted.
                      </p>

                    )

                  }
                />


                {/* =================================================
                    EDUCATION
                    ================================================= */}

                <AnalysisCard
                  icon={
                    <GraduationCap
                      size={20}
                    />
                  }
                  title="Education"
                  content={

                    <p className="whitespace-pre-line text-sm leading-6 text-slate-600">

                      {analysis.education ||
                        "Not available"}

                    </p>

                  }
                />


                {/* =================================================
                    EXPERIENCE
                    ================================================= */}

                <AnalysisCard
                  icon={
                    <CheckCircle2
                      size={20}
                    />
                  }
                  title="Experience"
                  content={

                    <p className="whitespace-pre-line text-sm leading-6 text-slate-600">

                      {analysis.experience ||
                        "Not available"}

                    </p>

                  }
                />

              </div>

            </section>

          )}

        </div>

      </main>

    </div>
  );
}


/* =========================================================
   ANALYSIS CARD
   ========================================================= */

function AnalysisCard({
  icon,
  title,
  content,
}: {
  icon: React.ReactNode;
  title: string;
  content: React.ReactNode;
}) {

  return (

    <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">

      <div className="flex items-center gap-3">

        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-slate-950 text-teal-300">

          {icon}

        </div>


        <h3 className="font-bold text-slate-950">
          {title}
        </h3>

      </div>


      <div className="mt-5">
        {content}
      </div>

    </div>
  );
}