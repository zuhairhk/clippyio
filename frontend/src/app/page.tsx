"use client";

import { useState, useRef } from "react";
import { useRouter } from "next/navigation";

const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000";

export default function UploadPage() {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const router = useRouter();

  async function handleUpload() {
    if (!file) return;
    setLoading(true);

    const formData = new FormData();
    formData.append("file", file);

    const res = await fetch(`${API_BASE}/upload`, {
      method: "POST",
      body: formData,
    });

    const data = await res.json();
    router.push(`/jobs/${data.job_id}`);
  }

  function handleDrop(e: React.DragEvent<HTMLDivElement>) {
    e.preventDefault();
    if (e.dataTransfer.files?.[0]) {
      setFile(e.dataTransfer.files[0]);
    }
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-neutral-950 via-neutral-900 to-neutral-950 flex items-center justify-center px-4">
      <div className="w-full max-w-2xl">
        {/* Header */}
        <div className="text-center mb-10">
          <h1 className="text-4xl sm:text-5xl font-semibold text-white tracking-tight">
            ClippyIO
          </h1>
          <p className="mt-3 text-neutral-400 text-base sm:text-lg">
            Upload a video. Get share-ready clips automatically.
          </p>
        </div>

        {/* Upload Card */}
        <div
          onDragOver={e => e.preventDefault()}
          onDrop={handleDrop}
          className="relative rounded-2xl border border-white/10 bg-white/5 backdrop-blur-xl shadow-xl p-8 sm:p-10 transition hover:border-white/20"
        >
          {/* Drop zone */}
          <div
            onClick={() => fileInputRef.current?.click()}
            className="cursor-pointer rounded-xl border-2 border-dashed border-white/15 hover:border-white/30 transition p-10 text-center"
          >
            <div className="flex flex-col items-center gap-4">
              <div className="h-14 w-14 rounded-full bg-white/10 flex items-center justify-center">
                <svg
                  className="h-7 w-7 text-white"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth={1.8}
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M12 16V4m0 0l-4 4m4-4l4 4M4 16v2a2 2 0 002 2h12a2 2 0 002-2v-2"
                  />
                </svg>
              </div>

              {!file ? (
                <>
                  <p className="text-white text-lg font-medium">
                    Drag and drop your video
                  </p>
                  <p className="text-neutral-400 text-sm">
                    or tap to browse
                  </p>
                </>
              ) : (
                <>
                  <p className="text-white font-medium">
                    {file.name}
                  </p>
                  <p className="text-neutral-400 text-sm">
                    {(file.size / (1024 * 1024)).toFixed(1)} MB
                  </p>
                </>
              )}
            </div>

            <input
              ref={fileInputRef}
              type="file"
              accept="video/*"
              hidden
              onChange={e =>
                setFile(e.target.files?.[0] ?? null)
              }
            />
          </div>

          {/* Action */}
          <button
            onClick={handleUpload}
            disabled={!file || loading}
            className="mt-6 w-full rounded-xl bg-white text-neutral-900 font-medium py-3.5 transition
                       hover:bg-neutral-200 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? "Uploading..." : "Upload Video"}
          </button>

          {/* Helper */}
          <p className="mt-4 text-center text-xs text-neutral-500">
            MP4, MOV, or WEBM • No sign-up required
          </p>
        </div>
      </div>
    </main>
  );
}
