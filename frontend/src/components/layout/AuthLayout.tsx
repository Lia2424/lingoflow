import { Card, CardContent, CardHeader } from '@/components/ui/card'

interface AuthLayoutProps {
  title: string
  subtitle: string
  children: React.ReactNode
}

export default function AuthLayout({ title, subtitle, children }: AuthLayoutProps) {
  return (
    <div className="min-h-screen bg-slate-50 flex flex-col items-center justify-center px-4">
      <div className="mb-8 text-center">
        <h1 className="text-3xl font-bold text-slate-900 tracking-tight">LingoFlow</h1>
        <p className="text-slate-500 text-sm mt-1">Language immersion, rediscovered</p>
      </div>

      <Card className="w-full max-w-md shadow-sm">
        <CardHeader className="pb-4">
          <h2 className="text-xl font-semibold text-slate-900">{title}</h2>
          <p className="text-sm text-slate-500">{subtitle}</p>
        </CardHeader>
        <CardContent>{children}</CardContent>
      </Card>
    </div>
  )
}
