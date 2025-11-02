"use client";

import { ModeToggle } from "@/components/theme-toggle";
import { Logo } from "@/components/logo";
import { Button } from "@/components/ui/button";
import { Card, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { ArrowRight, FileAudio, FileText, Zap, Shield, ChevronDown, Brain, Stethoscope, Activity } from "lucide-react";
import Link from "next/link";

export default function Home() {
  return (
    <div className="min-h-screen bg-muted/20">
      {/* Header */}
      <header className="relative">
        <div className="absolute top-4 left-4 lg:top-6 lg:left-6 z-50">
          <Logo />
        </div>
        <div className="absolute top-4 right-4 lg:top-6 lg:right-6 z-50">
          <ModeToggle />
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative pt-28 pb-20 lg:pt-40 lg:pb-32 min-h-screen flex items-center">
        <div className="absolute inset-0 bg-linear-to-br from-primary/20 via-primary/5 to-accent/20 dark:from-primary/8 dark:via-primary/1 dark:to-accent/8"></div>
        <div className="relative z-10 container mx-auto px-6 lg:px-8 text-center">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 border border-primary/20 mb-8">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
            <span className="text-sm font-medium text-primary">
              Agentic AI-Powered Clinical Documentation
            </span>
          </div>

          <div className="space-y-6 max-w-4xl mx-auto">
            <h1 className="text-5xl font-bold tracking-tight lg:text-7xl bg-linear-to-r from-foreground via-foreground/90 to-foreground/70 bg-clip-text text-transparent">
              Transform Audio into
              <span className="block">
                <span className="bg-linear-to-r from-emerald-500 via-teal-500 to-cyan-500 bg-clip-text text-transparent">
                  Intelligent
                </span>{" "}
                <span className="text-primary">Clinical Notes</span>
              </span>
              <span className="block text-2xl lg:text-4xl font-normal mt-4">
                <span className="text-muted-foreground">Powered by </span>
                <span className="bg-linear-to-r from-emerald-500 via-teal-500 to-cyan-500 bg-clip-text text-transparent font-medium">
                  Agentic AI
                </span>
              </span>
            </h1>

            <p className="text-xl text-muted-foreground lg:text-2xl leading-relaxed max-w-3xl mx-auto">
              Revolutionary agentic AI that thinks, analyzes, and generates like a clinical expert.
              <span className="text-foreground font-medium"> Upload patient encounters</span> and watch our
              autonomous AI agents create structured SOAP notes with clinical reasoning.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center pt-8">
              <Button asChild size="lg" className="text-lg px-8 py-6">
                <Link href="/visit" className="flex items-center gap-2">
                  Get Started <ArrowRight className="h-5 w-5" />
                </Link>
              </Button>
              <Button
                variant="outline"
                size="lg"
                className="text-lg px-8 py-6"
                onClick={() => {
                  document.getElementById('features')?.scrollIntoView({
                    behavior: 'smooth'
                  })
                }}
              >
                Learn More
              </Button>
            </div>
          </div>
        </div>

        {/* Scroll Indicator */}
        <div className="absolute bottom-8 left-1/2 transform -translate-x-1/2 z-10">
          <div className="flex flex-col items-center">
            <span className="text-sm text-muted-foreground mb-2 hidden sm:block">Scroll to explore</span>
            <ChevronDown className="h-5 w-5 text-muted-foreground/60 animate-pulse" />
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 lg:py-32 bg-secondary dark:bg-background">
        <div className="container mx-auto px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold tracking-tight lg:text-4xl mb-4">
              Why Choose TotalScribe&apos;s Agentic AI?
            </h2>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Experience the future of clinical documentation with autonomous AI agents that think, reason, and adapt like expert clinicians
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            <Card className="relative overflow-hidden">
              <CardHeader>
                <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mb-4">
                  <Zap className="h-6 w-6 text-primary" />
                </div>
                <CardTitle>Autonomous Intelligence</CardTitle>
                <CardDescription>
                  Agentic AI processes audio with autonomous reasoning, delivering clinical insights in seconds.
                </CardDescription>
              </CardHeader>
            </Card>

            <Card className="relative overflow-hidden">
              <CardHeader>
                <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mb-4">
                  <Shield className="h-6 w-6 text-primary" />
                </div>
                <CardTitle>HIPAA Compliant</CardTitle>
                <CardDescription>
                  Enterprise-grade security ensures your patient data remains protected and private.
                </CardDescription>
              </CardHeader>
            </Card>

            <Card className="relative overflow-hidden">
              <CardHeader>
                <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mb-4">
                  <FileText className="h-6 w-6 text-primary" />
                </div>
                <CardTitle>Intelligent SOAP Generation</CardTitle>
                <CardDescription>
                  Agentic AI agents autonomously structure clinical notes with medical reasoning and context.
                </CardDescription>
              </CardHeader>
            </Card>

            <Card className="relative overflow-hidden">
              <CardHeader>
                <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mb-4">
                  <Brain className="h-6 w-6 text-primary" />
                </div>
                <CardTitle>Multi-Agent Collaboration</CardTitle>
                <CardDescription>
                  Specialized AI agents work together - transcription, analysis, and clinical reasoning agents collaborate seamlessly.
                </CardDescription>
              </CardHeader>
            </Card>

            <Card className="relative overflow-hidden">
              <CardHeader>
                <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mb-4">
                  <Stethoscope className="h-6 w-6 text-primary" />
                </div>
                <CardTitle>Clinical Context Understanding</CardTitle>
                <CardDescription>
                  Advanced medical knowledge integration ensures accurate interpretation of clinical terminology and context.
                </CardDescription>
              </CardHeader>
            </Card>

            <Card className="relative overflow-hidden">
              <CardHeader>
                <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mb-4">
                  <Activity className="h-6 w-6 text-primary" />
                </div>
                <CardTitle>Real-Time Processing</CardTitle>
                <CardDescription>
                  Watch agentic AI work in real-time with live processing insights and progress tracking for complete transparency.
                </CardDescription>
              </CardHeader>
            </Card>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-20 lg:py-32 bg-muted/40">
        <div className="container mx-auto px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold tracking-tight lg:text-4xl mb-4">
              How Our Agentic AI Works
            </h2>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Watch autonomous AI agents collaborate to transform your audio into intelligent clinical documentation
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-4xl mx-auto">
            <div className="text-center">
              <div className="w-16 h-16 bg-primary rounded-full flex items-center justify-center mx-auto mb-6">
                <FileAudio className="h-8 w-8 text-primary-foreground" />
              </div>
              <h3 className="text-xl font-semibold mb-4">1. Upload Audio</h3>
              <p className="text-muted-foreground">
                Upload your patient encounter recording in any common audio format
              </p>
            </div>

            <div className="text-center">
              <div className="w-16 h-16 bg-primary rounded-full flex items-center justify-center mx-auto mb-6">
                <Zap className="h-8 w-8 text-primary-foreground" />
              </div>
              <h3 className="text-xl font-semibold mb-4">2. Agentic AI Processing</h3>
              <p className="text-muted-foreground">
                Autonomous AI agents collaborate to transcribe, analyze, and reason through clinical content
              </p>
            </div>

            <div className="text-center">
              <div className="w-16 h-16 bg-primary rounded-full flex items-center justify-center mx-auto mb-6">
                <FileText className="h-8 w-8 text-primary-foreground" />
              </div>
              <h3 className="text-xl font-semibold mb-4">3. Intelligent SOAP Note</h3>
              <p className="text-muted-foreground">
                Receive clinically-reasoned SOAP notes with autonomous insights ready for your EMR system
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 lg:py-32">
        <div className="container mx-auto px-6 lg:px-8 text-center">
          <div className="max-w-3xl mx-auto">
            <h2 className="text-3xl font-bold tracking-tight lg:text-4xl mb-6">
              Ready to Experience Agentic AI Clinical Documentation?
            </h2>
            <p className="text-xl text-muted-foreground mb-8">
              Join thousands of healthcare professionals who trust TotalScribe&apos;s autonomous AI agents for intelligent clinical documentation.
            </p>
            <Button asChild size="lg" className="text-lg px-8 py-6">
              <Link href="/visit" className="flex items-center gap-2">
                Experience Agentic AI <ArrowRight className="h-5 w-5" />
              </Link>
            </Button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t bg-background/95 backdrop-blur supports-backdrop-filter:bg-background/60">
        <div className="container mx-auto px-6 lg:px-8 py-8">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4">
            <Logo />
            <p className="text-sm text-muted-foreground">
              © 2025 TotalScribe. Transforming clinical documentation with Agentic AI.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
