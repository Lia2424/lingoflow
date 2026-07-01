interface PlaceholderProps {
  label: string
}

export default function Placeholder({ label }: PlaceholderProps) {
  return (
    <div className="min-h-screen flex items-center justify-center text-slate-400 text-sm">
      {label} — coming soon
    </div>
  )
}
