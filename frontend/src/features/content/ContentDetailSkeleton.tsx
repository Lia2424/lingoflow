function Skeleton({ className }: { className?: string }) {
  return <div className={`animate-pulse rounded-md bg-slate-200 ${className ?? ''}`} />
}

export default function ContentDetailSkeleton() {
  return (
    <div className="min-h-screen bg-slate-50">
      {/* Hero / header */}
      <div className="border-b border-slate-200 bg-white px-4 py-6 sm:px-6">
        <div className="mx-auto max-w-4xl space-y-3">
          {/* Badges row */}
          <div className="flex gap-2">
            <Skeleton className="h-5 w-16" />
            <Skeleton className="h-5 w-8" />
            <Skeleton className="h-5 w-10" />
          </div>
          {/* Title */}
          <Skeleton className="h-8 w-3/4" />
          <Skeleton className="h-8 w-1/2" />
          {/* Meta */}
          <Skeleton className="h-4 w-40" />
        </div>
      </div>

      <div className="mx-auto max-w-4xl px-4 py-6 sm:px-6 space-y-6">
        {/* Media */}
        <Skeleton className="aspect-video w-full rounded-xl" />

        {/* Description */}
        <div className="space-y-2">
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-5/6" />
          <Skeleton className="h-4 w-2/3" />
        </div>

        {/* Action bar */}
        <div className="flex gap-3">
          <Skeleton className="h-10 w-24 rounded-lg" />
          <Skeleton className="h-10 w-36 rounded-lg" />
        </div>
      </div>
    </div>
  )
}
