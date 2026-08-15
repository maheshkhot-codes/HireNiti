import { Sparkles } from "lucide-react";

interface LogoProps {
  dark?: boolean;
}

export default function Logo({
  dark = false,
}: LogoProps) {

  return (
    <div className="flex items-center gap-3">

      <div
        className={`flex h-10 w-10 items-center justify-center rounded-2xl ${
          dark
            ? "bg-white text-slate-950"
            : "bg-slate-950 text-white"
        }`}
      >
        <Sparkles size={19} />
      </div>

      <span
        className={`text-xl font-bold tracking-tight ${
          dark
            ? "text-white"
            : "text-slate-950"
        }`}
      >
        HireNiti
      </span>

    </div>
  );
}