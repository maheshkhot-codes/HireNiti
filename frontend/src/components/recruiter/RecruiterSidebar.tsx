import {
  BriefcaseBusiness,
  Home,
  LogOut,
  Plus,
  Users,
} from "lucide-react";

import {
  NavLink,
  useNavigate,
} from "react-router-dom";

import { useAuth } from "../../context/AuthContext";

export default function RecruiterSidebar() {

  const { logout } = useAuth();

  const navigate = useNavigate();

  const links = [
    {
      to: "/recruiter/dashboard",
      label: "Overview",
      icon: Home,
    },
    {
      to: "/recruiter/jobs",
      label: "My Jobs",
      icon: BriefcaseBusiness,
    },
    {
      to: "/recruiter/applicants",
      label: "Applicants",
      icon: Users,
    },
  ];

  return (
    <aside className="hidden w-64 shrink-0 border-r border-slate-200 bg-white lg:flex lg:flex-col">

      <div className="border-b border-slate-200 px-6 py-5">

        <div className="flex items-center gap-3">

          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-slate-950 text-teal-400">
            ✦
          </div>

          <div>

            <p className="font-bold text-slate-950">
              HireNiti
            </p>

            <p className="text-xs text-slate-500">
              Recruiter
            </p>

          </div>

        </div>

      </div>


      <div className="p-4">

        <button
          onClick={() =>
            navigate(
              "/recruiter/jobs/create"
            )
          }
          className="flex w-full items-center justify-center gap-2 rounded-xl bg-teal-500 px-4 py-3 text-sm font-semibold text-white transition hover:bg-teal-600"
        >
          <Plus size={17} />
          Create job
        </button>

      </div>


      <nav className="flex-1 space-y-1 px-4">

        {links.map(
          ({
            to,
            label,
            icon: Icon,
          }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                `flex items-center gap-3 rounded-xl px-4 py-3 text-sm font-medium transition ${
                  isActive
                    ? "bg-teal-50 text-teal-700"
                    : "text-slate-600 hover:bg-slate-50 hover:text-slate-950"
                }`
              }
            >
              <Icon size={18} />
              {label}
            </NavLink>
          )
        )}

      </nav>


      <div className="border-t border-slate-200 p-4">

        <button
          onClick={logout}
          className="flex w-full items-center gap-3 rounded-xl px-4 py-3 text-sm font-medium text-slate-500 transition hover:bg-red-50 hover:text-red-600"
        >
          <LogOut size={18} />
          Sign out
        </button>

      </div>

    </aside>
  );
}