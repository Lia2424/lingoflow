function Skeleton({ className }: { className?: string }) {
  return <div className={`animate-pulse rounded-md bg-slate-200 ${className ?? ''}`} />
}

export default function VocabularyCardSkeleton() {
  return (
    <div className="flex flex-col gap-3 rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
      {/* Top row */}
      <div className="flex items-start justify-between gap-2">
        <Skeleton className="h-5 w-32" />
        <div className="flex gap-1.5">
          <Skeleton className="h-5 w-10" />
          <Skeleton className="h-5 w-16" />
        </div>
      </div>
      {/* Definition */}
      <Skeleton className="h-4 w-full" />
      <Skeleton className="h-3 w-2/3" />
      {/* Footer */}
      <div className="flex items-center justify-between border-t border-slate-100 pt-2">
        <Skeleton className="h-3 w-20" />
        <Skeleton className="h-3 w-12" />
      </div>
    </div>
  )
}
