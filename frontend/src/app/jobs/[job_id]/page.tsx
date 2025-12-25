"use client";

import { useEffect, useRef, useState } from "react";
import { useParams, useRouter } from "next/navigation";

type JobStatus = "queued" | "processing" | "done" | "failed";

type Clip = {
  start: number;
  end: number;
  duration: number;
  url: string;
};

type Results = {
  job_id: string;
  summary: string | null;
  caption: string | null;
  clips: Clip[];
};

const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000";

export default function JobPage() {
  const { job_id } = useParams<{ job_id: string }>();
  const router = useRouter();

  const [status, setStatus] = useState<JobStatus>("queued");
  const [results, setResults] = useState<Results | null>(null);
  const [activeClip, setActiveClip] = useState(0);

  const pollRef = useRef<NodeJS.Timeout | null>(null);

  // ---------------- Poll job status ----------------
  useEffect(() => {
    if (!job_id) return;

    async function poll() {
      try {
        const res = await fetch(`${API_BASE}/jobs/${job_id}/status`);
        if (!res.ok) throw new Error();
        const data = await res.json();

        setStatus(data.status);

        if (data.status === "done") {
          clearInterval(pollRef.current!);
          fetchResults();
        }

        if (data.status === "failed") {
          clearInterval(pollRef.current!);
        }
      } catch {}
    }

    poll();
    pollRef.current = setInterval(poll, 2500);

    return () => {
      if (pollRef.current) clearInterval(pollRef.current);
    };
  }, [job_id]);

  // ---------------- Fetch results ----------------
  async function fetchResults() {
    try {
      const res = await fetch(`${API_BASE}/jobs/${job_id}/results`);
      if (!res.ok) throw new Error();
      const data = await res.json();
      setResults(data);
      setActiveClip(0);
    } catch {
      setStatus("failed");
    }
  }

  // ---------------- Shared layout ----------------
  function PageShell({ children }: { children: React.ReactNode }) {
    return (
      <main className="min-h-screen bg-gradient-to-br from-neutral-950 via-neutral-900 to-neutral-950 flex justify-center px-4 py-8">
        <div className="w-full max-w-4xl">
          <h1 className="text-center text-4xl font-semibold text-white tracking-tight mb-8">
            ClippyIO
          </h1>
          {children}
        </div>
      </main>
    );
  }

  // ---------------- Processing ----------------
  if (status === "queued" || status === "processing") {
    return (
      <PageShell>
        <div className="rounded-2xl border border-white/10 bg-white/5 backdrop-blur-xl shadow-xl p-8 text-center">
          <div className="mx-auto mb-6 h-12 w-12 rounded-full border-2 border-white/20 border-t-white animate-spin" />
          <p className="text-white text-lg font-medium">
            Processing your video
          </p>
          <p className="mt-2 text-neutral-400 text-sm capitalize">
            Status: {status}
          </p>
          <p className="mt-4 text-neutral-500 text-sm">
            This usually takes 1-5 minutes
          </p>
        </div>
      </PageShell>
    );
  }

  // ---------------- Failed ----------------
  if (status === "failed") {
    return (
      <PageShell>
        <div className="rounded-2xl border border-red-500/20 bg-red-500/5 backdrop-blur-xl shadow-xl p-8 text-center">
          <p className="text-red-400 text-lg font-medium">
            Something went wrong
          </p>
          <p className="mt-2 text-neutral-400 text-sm">
            The job failed to process
          </p>

          <button
            onClick={() => router.push("/upload")}
            className="mt-6 rounded-full bg-white text-neutral-900 font-medium px-6 py-3 hover:bg-neutral-200 transition"
          >
            Upload another video
          </button>
        </div>
      </PageShell>
    );
  }

  // ---------------- Results ----------------
  if (!results) return null;

  const clip = results.clips[activeClip];

  return (
    <PageShell>
      {/* Summary + Caption */}
      <section className="grid md:grid-cols-2 gap-4 mb-6">
        <div className="rounded-2xl border border-white/10 bg-white/5 backdrop-blur-xl shadow-xl p-5">
          <h2 className="text-white font-medium mb-2">Summary</h2>
          <p className="text-neutral-300 text-sm leading-relaxed">
            {results.summary ?? "No summary generated."}
          </p>
        </div>

        <div className="rounded-2xl border border-white/10 bg-white/5 backdrop-blur-xl shadow-xl p-5">
          <h2 className="text-white font-medium mb-2">Caption</h2>
          <p className="text-neutral-300 text-sm">
            {results.caption ?? "No caption generated."}
          </p>
        </div>
      </section>

      {/* Clip Viewer */}
      {results.clips.length > 0 && (
        <section className="rounded-2xl border border-white/10 bg-white/5 backdrop-blur-xl shadow-xl p-6">
          {/* Video stage */}
          <div className="relative rounded-xl bg-neutral-800/60 flex items-center justify-center overflow-hidden">
            <video
              key={activeClip}
              src={clip.url}
              controls
              preload="metadata"
              className="
                max-h-[60vh]
                w-auto
                max-w-full
                rounded-lg
                object-contain
                shadow-2xl
              "
            />
          </div>

          {/* Controls */}
          <div className="mt-4 flex items-center justify-between text-sm">
            <button
              onClick={() => setActiveClip(i => Math.max(i - 1, 0))}
              disabled={activeClip === 0}
              className="
                px-4 py-2 rounded-full
                bg-white/10 text-white
                hover:bg-white/20
                disabled:opacity-40
                transition
              "
            >
              Prev
            </button>

            <span className="text-neutral-400">
              Clip {activeClip + 1} of {results.clips.length}
            </span>

            <button
              onClick={() =>
                setActiveClip(i =>
                  Math.min(i + 1, results.clips.length - 1)
                )
              }
              disabled={activeClip === results.clips.length - 1}
              className="
                px-4 py-2 rounded-full
                bg-white/10 text-white
                hover:bg-white/20
                disabled:opacity-40
                transition
              "
            >
              Next
            </button>
          </div>

          {/* Download */}
          <div className="mt-4 text-center">
            <a
              href={clip.url}
              target="_blank"
              rel="noreferrer"
              className="text-white underline text-sm"
            >
              Download clip
            </a>
            <span className="text-neutral-500 text-xs ml-2">
              {clip.duration.toFixed(1)}s
            </span>
          </div>
        </section>
      )}

      {/* Footer Action */}
      <div className="mt-8 text-center">
        <button
          onClick={() => router.push("/upload")}
          className="rounded-full bg-white text-neutral-900 font-medium px-6 py-3 hover:bg-neutral-200 transition cursor-pointer"
        >
          Upload another video
        </button>
      </div>
    </PageShell>
  );
}
