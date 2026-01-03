"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";

const ACCESS_CODE = process.env.NEXT_PUBLIC_ACCESS_CODE;

export default function LandingPage() {
  const router = useRouter();
  const [code, setCode] = useState("");
  const [error, setError] = useState("");

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
    <main className="min-h-screen bg-neutral-950 text-white overflow-x-hidden">

      {/* HERO — IMMERSIVE */}
      <section className="relative px-6 pt-36 pb-44 text-center">
        {/* Glow */}
        <div className="absolute inset-0 flex justify-center pointer-events-none">
          <div className="h-[420px] w-[420px] rounded-full bg-purple-500/20 blur-[120px]" />
        </div>

        <h1 className="relative z-10 text-4xl sm:text-6xl font-semibold tracking-tight">
          Turn your videos into
          <span className="block text-neutral-300">
            high-performing clips
          </span>
        </h1>

        <p className="relative z-10 mt-6 max-w-2xl mx-auto text-neutral-400 text-lg">
          ClippyIO automatically finds moments, captions them,
          and delivers clips ready to post.
        </p>

        <div className="relative z-10 mt-10 flex justify-center gap-4">
          <button
            onClick={() =>
              document
                .getElementById("early-access")
                ?.scrollIntoView({ behavior: "smooth" })
            }
            className="rounded-xl bg-white px-6 py-3 font-medium text-neutral-900 hover:bg-neutral-200 transition"
          >
            Try Early Access
          </button>

          <a
            href="https://www.clippyio.com/jobs/e142faa1-8f60-4d2e-91c6-195869e950d3"
            target="_blank"
            className="rounded-xl border border-white/15 px-6 py-3 font-medium text-white/80 hover:border-white/30 transition"
          >
            See Example Output
          </a>
        </div>
      </section>

      {/* PROBLEM → RELIEF */}
      <section className="px-6 py-36">
        <div className="mx-auto max-w-6xl grid grid-cols-1 md:grid-cols-2 gap-24 items-center">
          <div>
            <h2 className="text-3xl font-semibold tracking-tight">
              Editing shouldn’t break momentum
            </h2>
            <ul className="mt-8 space-y-4 text-neutral-400 text-lg">
              <li>• Finding moments takes too long</li>
              <li>• Captions never feel consistent</li>
              <li>• Posting gets delayed</li>
              <li>• Editing drains creative energy</li>
            </ul>
          </div>

          <div className="rounded-3xl border border-white/10 bg-white/5 p-10 backdrop-blur-xl">
            <h3 className="text-2xl font-medium">
              Upload once. We do the rest.
            </h3>
            <p className="mt-6 text-neutral-400 text-lg">
              ClippyIO analyzes your video, detects high-signal moments,
              captions them, and outputs clean clips for TikTok, Reels,
              and Shorts.
            </p>
          </div>
        </div>
      </section>

      {/* FEATURE GRID — REFLECT STYLE */}
      <section className="px-6 py-36 bg-white/[0.02]">
        <div className="mx-auto max-w-6xl">
          <div className="max-w-2xl mb-20">
            <p className="text-sm uppercase tracking-wider text-neutral-500">
              Built for creators & teams
            </p>
            <h2 className="mt-4 text-3xl sm:text-4xl font-semibold tracking-tight">
              Everything you need to ship clips faster
            </h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {[
              {
                title: "Automatic moment detection",
                desc: "Finds high-signal segments without scrubbing timelines.",
              },
              {
                title: "Short-form optimized captions",
                desc: "Readable, engaging captions designed for retention.",
              },
              {
                title: "Async processing",
                desc: "Upload and come back later — no waiting.",
              },
              {
                title: "Multi-platform ready",
                desc: "Clips formatted for TikTok, Reels, and Shorts.",
              },
              {
                title: "Consistent output",
                desc: "Every clip follows the same clean visual style.",
              },
              {
                title: "Zero editing required",
                desc: "No timelines. No keyframes. No tweaking.",
              },
            ].map((f, i) => (
              <div
                key={i}
                className="rounded-2xl border border-white/10 bg-white/5 p-8"
              >
                <h3 className="text-lg font-medium">{f.title}</h3>
                <p className="mt-3 text-neutral-400">
                  {f.desc}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* TESTIMONIALS */}
      <section className="px-6 py-36">
        <div className="mx-auto max-w-6xl">
          <h2 className="text-3xl font-semibold text-center tracking-tight">
            Trusted by early creators & teams
          </h2>

          <div className="mt-20 grid grid-cols-1 md:grid-cols-3 gap-8">
            {[
              {
                quote: "ClippyIO cut our editing time by more than half.",
                author: "Content Lead",
                org: "Podcast Studio",
              },
              {
                quote: "The captions are shockingly good. We post faster now.",
                author: "Founder",
                org: "Media Startup",
              },
              {
                quote: "Perfect for turning long interviews into daily clips.",
                author: "Marketing Manager",
                org: "Content Team",
              },
            ].map((t, i) => (
              <div
                key={i}
                className="rounded-2xl border border-white/10 bg-white/5 p-8"
              >
                <p className="text-neutral-300 text-lg">
                  “{t.quote}”
                </p>
                <p className="mt-6 text-sm text-neutral-500">
                  — {t.author}, {t.org}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* EARLY ACCESS */}
      <section id="early-access" className="px-6 py-40 flex justify-center">
        <div className="w-full max-w-xl rounded-3xl border border-white/10 bg-white/5 p-10 backdrop-blur-xl">
          <h3 className="text-2xl font-semibold text-center">
            Get early access
          </h3>

          <p className="mt-4 text-center text-neutral-400">
            ClippyIO is currently in private beta.
          </p>

          <input
            type="password"
            placeholder="Enter access code"
            value={code}
            onChange={e => setCode(e.target.value)}
            className="mt-8 w-full rounded-xl bg-neutral-900 border border-white/10 px-4 py-3 text-white placeholder:text-neutral-500 focus:outline-none focus:ring-2 focus:ring-white/20"
          />

          {error && (
            <p className="mt-3 text-sm text-amber-400">
              {error}
            </p>
          )}

          <button
            onClick={handleSubmit}
            className="mt-6 w-full rounded-xl bg-white text-neutral-900 font-medium py-3 hover:bg-neutral-200 transition"
          >
            Enter Early Access
          </button>

          <div className="mt-8 text-center text-sm text-neutral-400">
            <p>Don’t have a code?</p>
            <p className="mt-2">
              <a
                href="mailto:zuhairhk@gmail.com"
                className="underline hover:text-white"
              >
                Email me
              </a>{" "}
              or{" "}
              <a
                href="https://www.linkedin.com/in/zuhairhkhan/"
                target="_blank"
                className="underline hover:text-white"
              >
                message me on LinkedIn
              </a>
            </p>
          </div>
        </div>
      </section>
    </main>
  );
}
