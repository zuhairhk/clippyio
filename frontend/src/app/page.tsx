"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";

const ACCESS_CODE = process.env.NEXT_PUBLIC_ACCESS_CODE;

export default function LandingPage() {
  const router = useRouter();
  const [code, setCode] = useState("");
  const [error, setError] = useState("");

  // If already granted, skip landing
  useEffect(() => {
    if (localStorage.getItem("clippyio_access")) {
      router.replace("/upload");
    }
  }, [router]);

  function handleSubmit() {
    if (code === ACCESS_CODE) {
      localStorage.setItem("clippyio_access", "true");
      router.push("/upload");
    } else {
      setError("Invalid access code");
    }
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-neutral-950 via-neutral-900 to-neutral-950 flex items-center justify-center px-4">
      <div className="w-full max-w-xl text-center">
        {/* Brand */}
        <h1 className="text-4xl sm:text-5xl font-semibold text-white tracking-tight">
          ClippyIO
        </h1>
        <p className="mt-4 text-neutral-400 text-base sm:text-lg">
          Turn long videos into share-ready clips automatically.
        </p>

        {/* Access Card */}
        <div className="mt-10 rounded-2xl border border-white/10 bg-white/5 backdrop-blur-xl shadow-xl p-8">
          <p className="text-white font-medium mb-3">
            Early access
          </p>

          <input
            type="password"
            placeholder="Enter access code"
            value={code}
            onChange={e => setCode(e.target.value)}
            className="w-full rounded-xl bg-neutral-900 border border-white/10 px-4 py-3 text-white placeholder:text-neutral-500 focus:outline-none focus:ring-2 focus:ring-white/20"
          />

          {error && (
            <p className="mt-2 text-sm text-red-400">
              {error}
            </p>
          )}

          <button
            onClick={handleSubmit}
            className="mt-4 w-full rounded-xl bg-white text-neutral-900 font-medium py-3 hover:bg-neutral-200 transition"
          >
            Enter
          </button>

          <p className="mt-4 text-xs text-neutral-500">
            Limited early access • No sign-up yet
          </p>
        </div>
      </div>
    </main>
  );
}
