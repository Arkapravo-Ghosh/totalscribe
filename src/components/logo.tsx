"use client"

import { HeartPulse } from "lucide-react"
import Link from "next/link"

export function Logo() {
  return (
    <Link href="/" className="flex items-center gap-2 hover:opacity-80 transition-opacity cursor-pointer">
      <div className="flex items-center justify-center w-8 h-8 bg-primary rounded-lg">
        <HeartPulse className="h-5 w-5 text-primary-foreground" />
      </div>
      <div className="flex flex-col">
        <span className="text-lg font-bold tracking-tight">TotalScribe</span>
        <span className="text-xs text-muted-foreground -mt-1">AI Clinical Assistant</span>
      </div>
    </Link>
  )
}
