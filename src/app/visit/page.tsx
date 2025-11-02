import VisitPageClient from "./client";
import { fetchSystemInfo, generateSoapNote } from "../actions";
import { ModeToggle } from "@/components/theme-toggle";
import { Logo } from "@/components/logo";

export default async function VisitPage() {
  const systemInfo = await fetchSystemInfo();

  return (
    <main className="h-screen bg-muted/20 py-8 lg:py-10 overflow-hidden">
      <div className="h-full flex flex-col space-y-6 px-6 lg:space-y-8 lg:px-8">
        <div className="absolute top-4 left-4 lg:top-6 lg:left-6">
          <Logo />
        </div>
        <div className="absolute top-4 right-4 lg:top-6 lg:right-6">
          <ModeToggle />
        </div>

        <section className="shrink-0 text-center pt-4">
          <h1 className="text-2xl font-bold tracking-tight lg:text-3xl mb-2">
            Generate SOAP Note
          </h1>
          <p className="text-muted-foreground">
            Upload your patient encounter audio to get started
          </p>
        </section>

        <VisitPageClient
          systemInfo={systemInfo}
          generateSoapNoteAction={generateSoapNote}
        />
      </div>
    </main>
  );
}
