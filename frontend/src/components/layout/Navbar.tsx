import { Link } from "react-router-dom";

import Logo from "../ui/Logo";

export default function Navbar() {

  return (
    <header className="sticky top-0 z-50 border-b border-slate-200/70 bg-white/85 backdrop-blur-xl">

      <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">

        <Link to="/">
          <Logo />
        </Link>

        <nav className="hidden items-center gap-8 md:flex">

          <a
            href="#features"
            className="text-sm font-medium text-slate-600 transition hover:text-slate-950"
          >
            Features
          </a>

          <a
            href="#how-it-works"
            className="text-sm font-medium text-slate-600 transition hover:text-slate-950"
          >
            How it works
          </a>

          <a
            href="#for-recruiters"
            className="text-sm font-medium text-slate-600 transition hover:text-slate-950"
          >
            For recruiters
          </a>

        </nav>

        <div className="flex items-center gap-3">

          <Link
            to="/login"
            className="hidden text-sm font-semibold text-slate-700 sm:block"
          >
            Sign in
          </Link>

          <Link
            to="/register"
            className="rounded-xl bg-slate-950 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-slate-800"
          >
            Get started
          </Link>

        </div>

      </div>

    </header>
  );
}