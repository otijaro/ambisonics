import { cn } from '@/lib/utils'

export function Logo({ className }: { className?: string }) {
  return (
    <span className={cn('flex items-center gap-2.5', className)}>
      <span className="relative flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-primary to-violet glow-purple">
        <svg viewBox="0 0 24 24" className="h-5 w-5 text-primary-foreground" aria-hidden="true">
          <circle cx="12" cy="12" r="8.5" fill="none" stroke="currentColor" strokeWidth="1.6" opacity="0.9" />
          <ellipse cx="12" cy="12" rx="8.5" ry="3.4" fill="none" stroke="currentColor" strokeWidth="1.4" opacity="0.55" />
          <circle cx="12" cy="12" r="2.4" fill="currentColor" />
        </svg>
      </span>
      <span className="text-lg font-semibold tracking-tight">Ambisonic</span>
    </span>
  )
}
